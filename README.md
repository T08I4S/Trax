# Trax - Document & Media Converter for NotebookLM

Trax is a modern, lightweight, and powerful desktop application written in Python (CustomTkinter) designed to act as a universal bridge for Google NotebookLM, as well as a standalone media utility tool.

It effortlessly converts unsupported or complex formats (like PowerPoint presentations, Word documents, Videos, Audios, and multi-page Images) into clean, standard formats (`.pdf`, `.mp3`, `.wav`) optimized for AI ingestion or personal use.

## ✨ Features

- **⭐ NotebookLM Optimization**: Instantly convert robust documents ensuring text is fully readable by Google NotebookLM.
- **🖼️ Image Processing**: Convert single images to PNG/JPG/WEBP or merge multiple images into single PDF documents.
- **🎬 Video & Audio Extraction**: Strip audio tracks from video files (supports `.mp4`, `.avi`, `.mov`) and compress audio formats natively into `.mp3` or `.wav` at selectable bitrates.
- **📄 Advanced Document Support**: 
  - **PPTX**: Converts slides to PDF and extracts embedded audio/media from the presentation into sequential audio files.
  - **DOCX**: Extracts textual data safely and securely to PDF format natively without requiring Microsoft Office COM objects.
  - **Scanned PDF (OCR)**: Automatically detects scanned, non-searchable PDF pages and applies Tesseract OCR to extract the raw text.
- **⚡ Fast & Responsive**: Fully asynchronous GUI using drag-and-drop operations without locking the interface.

## 🚀 Download & Usage (Standalone)

For normal users, no installation or Python environments are required! 
Just download the single standalone executable file and run it.

1. Go to the [Releases](../../releases) page.
2. Download `Trax.exe`.
3. Double click and start converting! (All dependencies are bundled inside).

## 💻 Development & Building from Source

If you want to contribute, edit the code, or build the executable yourself:

### Prerequisites

- Microsoft Windows 10/11
- Python 3.10+
- (Optional but recommended for OCR) [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Trax.git
   cd Trax
   ```
2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally
To run the app directly through Python:
```bash
python main.py
```

### Building the Executable (.exe)
To compile the project into a single `Trax.exe` for distribution, simply run the included batch script:
```bash
.\build.bat
```
The compiled standalone executable will be generated inside the `dist/` folder.

## 🛠️ Architecture

- `gui/app.py`: Handles the CustomTkinter UI, Drag & Drop components, and window management.
- `core/converters.py`: Contains the logic for processing PPTX, DOCX, Video, OCR, and integrations.
- `core/controller.py`: The multithreading dispatcher handling parallel worker jobs.

## 📄 License
This project is open-source and available under the MIT License.
