import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

from core.controller import ConversionController

class TkDnDApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class App(TkDnDApp):
    def __init__(self):
        super().__init__()
        
        self.title("Trax - NotebookLM Source Converter")
        self.geometry("900x700")
        
        # Tema e Colori
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1a1a2e")
        self.accent_color = "#0096FF"
        ctk.set_default_color_theme("blue")
        
        self.controller = ConversionController()
        self.controller.set_callbacks(self.on_progress_update, self.on_task_complete, self.on_task_error)
        
        # State
        self.files_data = {}  # id -> dict with UI elements and paths
        self.output_files = {} # result path -> dict
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Top Menu ---
        self.menu_frame = ctk.CTkFrame(self, fg_color="#121220", corner_radius=0, height=50)
        self.menu_frame.pack(side="top", fill="x")
        
        menus = ["🖼️ Foto", "🎬 Video/Audio", "📄 Documenti", "⭐ NotebookLM", "⚙️ Impostazioni", "❓ Aiuto"]
        for m in menus:
            btn = ctk.CTkButton(self.menu_frame, text=m, fg_color="transparent", hover_color="#2a2a40",
                                text_color="white", font=("Segoe UI", 12, "bold" if "NotebookLM" in m else "normal"),
                                command=lambda txt=m: self.on_menu_click(txt))
            if "NotebookLM" in m:
                btn.configure(fg_color=self.accent_color, hover_color="#007ACC")
            btn.pack(side="left", padx=5, pady=5)
            
        # --- Main Content (NotebookLM View) ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titolo
        self.title_label = ctk.CTkLabel(self.content_frame, text="⭐ NotebookLM Converter", font=("Segoe UI", 24, "bold"), text_color="white")
        self.title_label.pack(pady=(0, 20))
        
        # Options Area (Hidden by default)
        self.options_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.options_label = ctk.CTkLabel(self.options_frame, text="Formato di output:", font=("Segoe UI", 14))
        self.options_label.pack(side="left", padx=10)
        self.options_combo = ctk.CTkComboBox(self.options_frame, values=["PDF"], width=100)
        self.options_combo.pack(side="left")

        # Settings Area (Hidden by default)
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="#121220", corner_radius=10)
        ctk.CTkLabel(self.settings_frame, text="⚙️ Impostazioni", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=20)
        
        # Grid layout for settings
        set_grid = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        set_grid.pack(pady=10, padx=20, fill="x")
        set_grid.grid_columnconfigure(0, weight=1)
        set_grid.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(set_grid, text="Tema Applicazione:", font=("Segoe UI", 14), anchor="e").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.theme_switch = ctk.CTkSwitch(set_grid, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.select()
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(set_grid, text="Bitrate Audio (MP3):", font=("Segoe UI", 14), anchor="e").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.audio_bitrate_var = tk.StringVar(value="128k")
        ctk.CTkComboBox(set_grid, values=["128k", "192k", "256k", "320k"], variable=self.audio_bitrate_var, width=120).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(set_grid, text="Qualità Compressione Foto:", font=("Segoe UI", 14), anchor="e").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.image_quality_var = tk.StringVar(value="Alta")
        ctk.CTkComboBox(set_grid, values=["Alta", "Media", "Bassa"], variable=self.image_quality_var, width=120).grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Help Area (Hidden by default)
        self.help_frame = ctk.CTkFrame(self.content_frame, fg_color="#121220", corner_radius=10)
        ctk.CTkLabel(self.help_frame, text="❓ Aiuto e Informazioni", font=("Segoe UI", 20, "bold"), text_color="white").pack(pady=20)
        help_text = "Trax Converter\n\n⭐ NotebookLM: Converte documenti/video/audio in formati leggibili (PDF/MP3).\n🖼️ Foto: Converte/Fonde immagini in PNG/JPG/WEBP/PDF.\n🎬 Video/Audio: Convertitore ed estrattore media MP3/WAV.\n📄 Documenti: Conversione Office in PDF estraendo il testo."
        ctk.CTkLabel(self.help_frame, text=help_text, justify="left", font=("Segoe UI", 14)).pack(pady=20, padx=20)
        
        # Drag & Drop Area
        self.drop_area = ctk.CTkFrame(self.content_frame, fg_color="#23233b", corner_radius=10, height=120)
        self.drop_area.pack(fill="x", pady=(0, 20))
        self.drop_area.pack_propagate(False)
        
        self.drop_label = ctk.CTkLabel(self.drop_area, text="Trascina i file qui oppure clicca per selezionarli", 
                                       font=("Segoe UI", 14), text_color="#aaaaaa")
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Hover events
        self.drop_area.bind("<Enter>", lambda e: self.drop_area.configure(fg_color="#303050"))
        self.drop_area.bind("<Leave>", lambda e: self.drop_area.configure(fg_color="#23233b"))
        self.drop_area.bind("<Button-1>", self.open_file_dialog)
        self.drop_label.bind("<Button-1>", self.open_file_dialog)
        
        # DnD setup
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        
        # File List Area
        self.list_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#1e1e32", corner_radius=10, height=180)
        self.list_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Progress Bar Area (Hidden by default)
        self.progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Elaborazione...", font=("Segoe UI", 12))
        self.progress_label.pack(side="left", padx=(0, 10))
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, progress_color=self.accent_color)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)
        
        # Output Panel
        self.output_frame = ctk.CTkFrame(self.content_frame, fg_color="#121220", corner_radius=10)
        self.output_frame.pack(fill="x", side="bottom")
        
        out_top = ctk.CTkFrame(self.output_frame, fg_color="transparent")
        out_top.pack(fill="x", padx=10, pady=10)
        
        self.out_label = ctk.CTkLabel(out_top, text="⬇️ Output pronti", font=("Segoe UI", 16, "bold"), text_color="white")
        self.out_label.pack(side="left")
        
        self.btn_clear = ctk.CTkButton(out_top, text="🗑️ Pulisci lista", width=120, fg_color="#555", hover_color="#777",
                                       command=self.clear_outputs)
        self.btn_clear.pack(side="right", padx=(10, 0))
        
        self.btn_download_all = ctk.CTkButton(out_top, text="📦 Scarica tutto (.zip)", width=160, fg_color=self.accent_color, hover_color="#007ACC",
                                              command=self.download_all)
        self.btn_download_all.pack(side="right")
        
        self.outputs_list_frame = ctk.CTkScrollableFrame(self.output_frame, fg_color="transparent", height=120)
        self.outputs_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.toast_label = ctk.CTkLabel(self, text="", fg_color="#333", text_color="white", corner_radius=5, padx=10, pady=5)

    def toggle_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() == 1 else "light")

    def on_menu_click(self, txt):
        self.current_mode = txt
        self.title_label.configure(text=f"{txt} Converter" if "NotebookLM" not in txt else "⭐ NotebookLM Converter")
        # Update colors
        for child in self.menu_frame.winfo_children():
            if isinstance(child, ctk.CTkButton):
                if child.cget("text") == txt:
                    child.configure(fg_color=self.accent_color, hover_color="#007ACC")
                else:
                    child.configure(fg_color="transparent", hover_color="#2a2a40")
                    
        self.drop_area.pack_forget()
        self.list_frame.pack_forget()
        self.output_frame.pack_forget()
        self.options_frame.pack_forget()
        if hasattr(self, 'settings_frame'): self.settings_frame.pack_forget()
        if hasattr(self, 'help_frame'): self.help_frame.pack_forget()
        
        if "Impostazioni" in txt:
            self.settings_frame.pack(fill="both", expand=True)
        elif "Aiuto" in txt:
            self.help_frame.pack(fill="both", expand=True)
        else:
            if "Foto" in txt:
                self.options_combo.configure(values=["PDF", "PNG", "JPG", "WEBP"])
                self.options_combo.set("PDF")
                self.options_frame.pack(fill="x", pady=(0, 10))
            elif "Video/Audio" in txt:
                self.options_combo.configure(values=["MP3", "WAV"])
                self.options_combo.set("MP3")
                self.options_frame.pack(fill="x", pady=(0, 10))
            elif "Documenti" in txt:
                self.options_combo.configure(values=["PDF"])
                self.options_combo.set("PDF")
                self.options_frame.pack(fill="x", pady=(0, 10))
                
            self.drop_area.pack(fill="x", pady=(0, 20))
            self.list_frame.pack(fill="both", expand=True, pady=(0, 20))
            self.output_frame.pack(fill="x", side="bottom")

    def show_toast(self, message):
        self.toast_label.configure(text=message)
        self.toast_label.place(relx=0.98, rely=0.95, anchor="se")
        self.after(3000, lambda: self.toast_label.place_forget())

    def open_file_dialog(self, event=None):
        files = filedialog.askopenfilenames()
        if files:
            self.process_dropped_files(files)
            
    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.process_dropped_files(files)
        
    def get_file_type(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pptx': return 'pptx'
        if ext == '.docx': return 'docx'
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']: return 'image'
        if ext in ['.mp4', '.avi', '.mov', '.mkv']: return 'video'
        if ext in ['.mp3', '.wav', '.m4a', '.aac', '.ogg']: return 'audio'
        if ext == '.pdf': return 'pdf'
        return None

    def process_dropped_files(self, paths):
        mode = getattr(self, "current_mode", "⭐ NotebookLM")
        
        allowed_types = {
            "🖼️ Foto": ["image"],
            "🎬 Video/Audio": ["video", "audio"],
            "📄 Documenti": ["docx", "pdf", "pptx"],
            "⭐ NotebookLM": ["image", "video", "audio", "docx", "pdf", "pptx"]
        }
        
        valid_map = allowed_types.get(mode, [])
        format_sel = self.options_combo.get().lower() if getattr(self, "options_frame", None) and self.options_frame.winfo_ismapped() else "notebooklm"
        
        extra_settings = {
            "format": format_sel,
            "bitrate": self.audio_bitrate_var.get(),
            "quality": self.image_quality_var.get()
        }
        
        images_paths = []
        for p in paths:
            t = self.get_file_type(p)
            if t == 'image' and 'image' in valid_map: images_paths.append(p)

        if len(images_paths) > 1:
            ans = messagebox.askyesno("Immagini Multiple", "Hai caricato più immagini. Vuoi unirle in un unico file multi-pagina?\n(Scegli No per convertire ogni immagine singolarmente)")
            if ans:
                # Add a single batch task
                fid = f"img_batch_{id(images_paths)}"
                self.add_ui_file_row(fid, "Raccolta Immagini", "Multi-page", "N/A")
                
                batch_args = extra_settings.copy()
                batch_args["paths"] = images_paths
                self.controller.add_task(fid, None, "image_multi", batch_args)
                for pr in images_paths:
                    paths = [x for x in paths if x != pr] # remove from single tasks
            
        for path in paths:
            t = self.get_file_type(path)
            if not t or t not in valid_map: 
                self.show_toast(f"File ignorato ({mode}): {os.path.basename(path)}")
                continue
            
            fid = f"file_{id(path)}_{os.path.basename(path)}"
            size_kb = os.path.getsize(path) / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{(size_kb/1024):.1f} MB"
            
            # Map specific type for single image
            type_str = "image_single" if t == 'image' else t
            
            self.add_ui_file_row(fid, os.path.basename(path), t.upper(), size_str)
            self.controller.add_task(fid, path, type_str, extra_settings)
            
        self.progress_frame.pack(fill="x", pady=(0, 10))

    def add_ui_file_row(self, fid, name, typ, size):
        row = ctk.CTkFrame(self.list_frame, fg_color="#2a2a40", corner_radius=5)
        row.pack(fill="x", pady=2, padx=2)
        
        lbl_name = ctk.CTkLabel(row, text=name, width=250, anchor="w", font=("Segoe UI", 12))
        lbl_name.pack(side="left", padx=10)
        
        lbl_type = ctk.CTkLabel(row, text=typ, width=80)
        lbl_type.pack(side="left")
        
        lbl_size = ctk.CTkLabel(row, text=size, width=80)
        lbl_size.pack(side="left")
        
        lbl_status = ctk.CTkLabel(row, text="🟡 In attesa", width=120)
        lbl_status.pack(side="right", padx=10)
        
        self.files_data[fid] = {"row": row, "status_lbl": lbl_status, "name": name}

    def add_output_row(self, out_path):
        if out_path in self.output_files: return
        
        row = ctk.CTkFrame(self.outputs_list_frame, fg_color="#2a2a40", corner_radius=5)
        row.pack(fill="x", pady=2, padx=2)
        
        name = os.path.basename(out_path)
        size_kb = os.path.getsize(out_path) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{(size_kb/1024):.1f} MB"
        
        lbl_name = ctk.CTkLabel(row, text=name, width=250, anchor="w")
        lbl_name.pack(side="left", padx=10)
        
        lbl_size = ctk.CTkLabel(row, text=size_str, width=80)
        lbl_size.pack(side="left")
        
        btn_dl = ctk.CTkButton(row, text="⬇️ Scarica", width=80, fg_color="#00A36C", hover_color="#008055",
                               command=lambda p=out_path: self.download_single(p))
        btn_dl.pack(side="right", padx=10, pady=5)
        
        self.output_files[out_path] = row
        self.show_toast(f"Completato: {name}")

    def on_progress_update(self, fid, status, progress, result_paths=None):
        def update():
            if fid in self.files_data:
                lbl = self.files_data[fid]["status_lbl"]
                if "In elaborazione" in status:
                    lbl.configure(text="🔵 Elaborazione...", text_color="#0096FF")
                    self.progress_label.configure(text=f"Elaborazione: {self.files_data[fid]['name']}")
                    self.progress_bar.set(0.5)
                elif "Errore" in status:
                    lbl.configure(text=f"🔴 {status}", text_color="#ff4444")
                    self.progress_bar.set(0)
                elif "Completato" in status:
                    lbl.configure(text="🟢 Completato", text_color="#00A36C")
                    if result_paths:
                        for p in result_paths:
                            self.add_output_row(p)
                            
        # update GUI thread-safely
        self.after(0, update)

    def on_task_complete(self, fid, result):
        pass # Handle in update

    def on_task_error(self, fid, error):
        pass # Handle in update

    def download_single(self, filepath):
        if not os.path.exists(filepath):
            messagebox.showerror("Errore", "File non trovato.")
            return
            
        save_path = filedialog.asksaveasfilename(initialfile=os.path.basename(filepath),
                                                 defaultextension=".*")
        if save_path:
            shutil.copy2(filepath, save_path)
            self.show_toast("Download completato.")

    def download_all(self):
        if not self.output_files:
            messagebox.showinfo("Info", "Nessun output pronto.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".zip", 
                                                 filetypes=[("Zip files", "*.zip")],
                                                 initialfile="Trax_export.zip")
        if save_path:
            out_dir = os.path.dirname(save_path)
            paths = list(self.output_files.keys())
            
            # create zip at temp, then copy
            temp_zip = self.controller.create_zip_export(paths, self.controller.file_manager.app_temp_dir if hasattr(self.controller, 'file_manager') else os.path.dirname(paths[0]))
            shutil.copy2(temp_zip, save_path)
            self.show_toast("Zip scaricato con successo.")

    def clear_outputs(self):
        for path, row in self.output_files.items():
            row.destroy()
        self.output_files.clear()
        
        for fid, data in self.files_data.items():
            data["row"].destroy()
        self.files_data.clear()
        
        self.progress_frame.pack_forget()
        self.controller.clean_temp()

if __name__ == "__main__":
    app = App()
    app.mainloop()
