import sys
import os

# Aggiunge il path corrente per garantire importazioni corrette
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.app import App
from core.file_manager import file_manager

def main():
    app = App()
    
    # Cleanup on exit
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
    
    app.mainloop()

def on_closing(app):
    file_manager.clean_temp_dir()
    app.destroy()

if __name__ == "__main__":
    main()
