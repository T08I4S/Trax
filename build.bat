@echo off
echo Generazione eseguibile Trax in corso...
call venv\Scripts\activate.bat
pyinstaller --onefile --windowed --name=Trax --collect-data customtkinter --collect-all tkinterdnd2 --copy-metadata imageio --hidden-import comtypes --hidden-import docx2pdf main.py
echo Generazione completata. L'eseguibile si trova nella cartella 'dist'.
pause
