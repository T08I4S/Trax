import os
import zipfile
from moviepy import VideoFileClip
from pydub import AudioSegment
import img2pdf
from PIL import Image
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from docx2pdf import convert as docx_convert
import comtypes.client

from .file_manager import file_manager

def get_base_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def convert_video_to_audio(file_path, output_dir, bitrate="128k"):
    base_name = get_base_name(file_path)
    output_path = os.path.join(output_dir, f"{base_name}_audio.mp3")
    try:
        video = VideoFileClip(file_path)
        video.audio.write_audiofile(output_path, bitrate=bitrate, logger=None)
        video.close()
        return output_path
    except Exception as e:
        raise Exception(f"Errore estrazione audio da video: {str(e)}")

def convert_audio_to_mp3(file_path, output_dir):
    base_name = get_base_name(file_path)
    output_path = os.path.join(output_dir, f"{base_name}.mp3")
    try:
        audio = AudioSegment.from_file(file_path)
        # downmix to standard if needed or just export
        audio.export(output_path, format="mp3")
        return output_path
    except Exception as e:
        raise Exception(f"Errore conversione audio: {str(e)}")

def convert_images_to_pdf(file_paths, output_dir, single_output_name=None):
    if len(file_paths) == 1:
        base_name = get_base_name(file_paths[0])
        output_path = os.path.join(output_dir, f"{base_name}.pdf")
    else:
        output_path = os.path.join(output_dir, single_output_name or "raccolta_immagini.pdf")
        
    try:
        valid_paths = []
        for p in file_paths:
            try:
                img = Image.open(p)
                if img.mode != "RGB":
                    temp_img_path = file_manager.get_temp_filepath(f"temp_{os.path.basename(p)}.jpg")
                    img.convert("RGB").save(temp_img_path, "JPEG")
                    valid_paths.append(temp_img_path)
                else:
                    valid_paths.append(p)
            except Exception:
                pass
                
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(valid_paths))
        return [output_path]
    except Exception as e:
        raise Exception(f"Errore conversione immagini: {str(e)}")

def convert_docx_to_pdf(file_path, output_dir):
    base_name = get_base_name(file_path)
    output_path = os.path.join(output_dir, f"{base_name}.pdf")
    abs_in = os.path.normpath(os.path.abspath(file_path))
    abs_out = os.path.normpath(os.path.abspath(output_path))
    
    try:
        import subprocess
        import sys
        
        # In a pyinstaller bundle, sys.executable is the app itself. We need to use 'pythonw' or equivalent to run docx2pdf.
        # docx_convert(abs_in, abs_out) directly tends to hang.
        import string
        from docx2pdf import convert
        convert(abs_in, abs_out)
        
        if os.path.exists(abs_out):
            return output_path
        else:
            raise Exception("File PDF non generato da docx2pdf")
            
    except Exception as e:
        # Fallback to python-docx + reportlab purely textual text extraction
        try:
            import docx
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            doc = docx.Document(abs_in)
            c = canvas.Canvas(abs_out, pagesize=A4)
            width, height = A4
            y = height - 50
            
            import textwrap
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                # Line wrap to fit approx 80 characters per line
                lines = textwrap.wrap(text, width=80) 
                for line in lines:
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    c.drawString(50, y, line)
                    y -= 15
                y -= 10
            c.save()
            return output_path
            
        except Exception as fallback_e:
            raise Exception(f"Errore conversione Word: Impossibile convertire (docx2pdf fallito e fallback testuale fallito). Dettagli:\n{str(e)}\n{str(fallback_e)}")

def process_pdf_ocr(file_path, output_dir):
    base_name = get_base_name(file_path)
    try:
        reader = PdfReader(file_path)
        has_text = False
        for page in reader.pages[:3]:
            if page.extract_text().strip():
                has_text = True
                break
                
        if has_text:
            return file_path
            
        output_path = os.path.join(output_dir, f"{base_name}_ocr.pdf")
        
        # NOTE: this requires poppler installed, we might want to catch it specifically
        images = convert_from_path(file_path)
        
        # pytesseract returns single pdf page bytes
        pdf_pages = []
        for img in images:
            pdf_pages.append(pytesseract.image_to_pdf_or_hocr(img, extension='pdf'))
            
        # Combine PDFs using PyPDF or simple concatenation? simple concatenation of Tesseract PDF bytes might not produce a valid full PDF
        # To be safe, let's write each to temp and merge
        from pypdf import PdfWriter
        merger = PdfWriter()
        for i, p_bytes in enumerate(pdf_pages):
            tmp_pdf = file_manager.get_temp_filepath(f"temp_ocr_{i}.pdf")
            with open(tmp_pdf, "wb") as f:
                f.write(p_bytes)
            merger.append(tmp_pdf)
            
        merger.write(output_path)
        merger.close()
        
        return output_path
    except Exception as e:
        raise Exception(f"Errore elaborazione PDF OCR (assicurati di avere Tesseract e Poppler): {str(e)}")

def convert_pptx_full(file_path, output_dir):
    base_name = get_base_name(file_path)
    pdf_path = os.path.join(output_dir, f"{base_name}_slides.pdf")
    mp3_path = os.path.join(output_dir, f"{base_name}_audio.mp3")
    
    try:
        import pythoncom
        pythoncom.CoInitialize()
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        abs_in = os.path.normpath(os.path.abspath(file_path))
        abs_out = os.path.normpath(os.path.abspath(pdf_path))
        # WithWindow=False might fail in some Office versions, fallback if needed
        deck = powerpoint.Presentations.Open(abs_in, WithWindow=False)
        deck.SaveAs(abs_out, 32)
        deck.Close()
        powerpoint.Quit()
    except Exception as e:
        try:
            powerpoint.Quit()
        except:
            pass
        raise Exception(f"Errore conversione PPTX in PDF: {str(e)}\nAssicurati di avere MS Office installato.")
        
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            media_files = [f for f in zip_ref.namelist() if f.startswith('ppt/media/') and f.lower().endswith(('.wav', '.m4a', '.mp3', '.wma', '.aac'))]
            
            if not media_files:
                return pdf_path, None
                
            temp_ext_dir = os.path.join(output_dir, "pptx_media")
            os.makedirs(temp_ext_dir, exist_ok=True)
            
            import re
            def get_num(name):
                match = re.search(r'\d+', name)
                return int(match.group()) if match else 0
                
            media_files.sort(key=get_num)
            
            combined = AudioSegment.empty()
            silence = AudioSegment.silent(duration=500)
            
            found_audio = False
            for m in media_files:
                ext_path = zip_ref.extract(m, temp_ext_dir)
                try:
                    seg = AudioSegment.from_file(ext_path)
                    if found_audio:
                        combined += silence
                    combined += seg
                    found_audio = True
                except:
                    pass
                    
            if found_audio:
                combined.export(mp3_path, format="mp3")
                return pdf_path, mp3_path
            else:
                return pdf_path, None
                
    except Exception:
        return pdf_path, None
