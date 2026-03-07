import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from .file_manager import file_manager
from .converters import (
    convert_video_to_audio, convert_audio_to_mp3,
    convert_images_to_pdf, convert_docx_to_pdf,
    process_pdf_ocr, convert_pptx_full
)

class ConversionController:
    def __init__(self, update_callback=None, completion_callback=None, error_callback=None):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.update_callback = update_callback  # (file_id, status, progress, result_paths)
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        self.tasks = {}
        self.lock = Lock()

    def set_callbacks(self, update_cb, completion_cb, error_cb):
        self.update_callback = update_cb
        self.completion_callback = completion_cb
        self.error_callback = error_cb

    def _notify_update(self, file_id, status, progress=0, result_paths=None):
        if self.update_callback:
            self.update_callback(file_id, status, progress, result_paths)

    def process_file_task(self, file_id, file_path, file_type, extra_args=None):
        try:
            self._notify_update(file_id, "In elaborazione...", 0)
            output_dir = file_manager.app_temp_dir
            results = []

            if file_type == 'pptx':
                pdf, mp3 = convert_pptx_full(file_path, output_dir)
                if pdf: results.append(pdf)
                if mp3: results.append(mp3)

            elif file_type == 'docx':
                pdf = convert_docx_to_pdf(file_path, output_dir)
                if pdf: results.append(pdf)

            elif file_type == 'image_single':
                fmt = extra_args.get("format", "pdf") if isinstance(extra_args, dict) else "pdf"
                
                # Handling quality mapping
                quality_str = extra_args.get("quality", "Alta") if isinstance(extra_args, dict) else "Alta"
                qual_map = {"Alta": 95, "Media": 75, "Bassa": 50}
                q_val = qual_map.get(quality_str, 95)
                
                if fmt in ["png", "jpg", "jpeg", "webp"]:
                    from PIL import Image
                    output_path = file_manager.get_temp_filepath(f"{get_base_name(file_path)}.{fmt}")
                    img = Image.open(file_path)
                    if img.mode != "RGB" and fmt in ["jpg", "jpeg"]:
                        img = img.convert("RGB")
                        
                    save_kwargs = {}
                    if fmt in ["jpg", "jpeg", "webp"]:
                        save_kwargs["quality"] = q_val
                        
                    img.save(output_path, fmt.upper() if fmt != "jpg" else "JPEG", **save_kwargs)
                    results.append(output_path)
                else:
                    pdf = convert_images_to_pdf([file_path], output_dir)
                    if pdf: results.extend(pdf)

            elif file_type == 'image_multi':
                # extra_args contains the list of image paths or a dict
                paths = extra_args.get("paths", extra_args) if isinstance(extra_args, dict) else extra_args
                # Right now, img2pdf handles PDF natively without quality reduction, keeping it standard.
                pdf = convert_images_to_pdf(paths, output_dir)
                if pdf: results.extend(pdf)

            elif file_type == 'video':
                fmt = extra_args.get("format", "mp3") if isinstance(extra_args, dict) else "mp3"
                bitrate_str = extra_args.get("bitrate", "128k") if isinstance(extra_args, dict) else "128k"
                
                if fmt == "mp3":
                    mp3 = convert_video_to_audio(file_path, output_dir, bitrate=bitrate_str)
                    if mp3: results.append(mp3)
                elif fmt == "wav":
                    from moviepy import VideoFileClip
                    output_path = os.path.join(output_dir, f"{get_base_name(file_path)}_audio.wav")
                    video = VideoFileClip(file_path)
                    video.audio.write_audiofile(output_path, logger=None)
                    video.close()
                    results.append(output_path)

            elif file_type == 'audio':
                fmt = extra_args.get("format", "mp3") if isinstance(extra_args, dict) else "mp3"
                bitrate_str = extra_args.get("bitrate", "128k") if isinstance(extra_args, dict) else "128k"
                
                from pydub import AudioSegment
                output_path = os.path.join(output_dir, f"{get_base_name(file_path)}.{fmt}")
                audio = AudioSegment.from_file(file_path)
                
                if fmt == "mp3":
                    audio.export(output_path, format=fmt, bitrate=bitrate_str)
                else:
                    audio.export(output_path, format=fmt)
                results.append(output_path)

            elif file_type == 'pdf':
                pdf = process_pdf_ocr(file_path, output_dir)
                if pdf: results.append(pdf)

            else:
                raise ValueError("Tipo file non supportato.")

            self._notify_update(file_id, "Completato", 100, results)

        except Exception as e:
            if self.error_callback:
                self.error_callback(file_id, str(e))
            self._notify_update(file_id, f"Errore: {str(e)}", 0, None)

    def add_task(self, file_id, file_path, file_type, extra_args=None):
        self._notify_update(file_id, "In attesa...", 0)
        self.executor.submit(self.process_file_task, file_id, file_path, file_type, extra_args)

    def create_zip_export(self, file_paths, output_dir):
        return file_manager.create_export_zip(file_paths, output_dir)

    def clean_temp(self):
        file_manager.clean_temp_dir()
