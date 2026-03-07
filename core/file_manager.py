import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import List

class FileManager:
    def __init__(self):
        self.app_temp_dir = os.path.join(tempfile.gettempdir(), "Trax")
        self.ensure_temp_dir()

    def ensure_temp_dir(self):
        if not os.path.exists(self.app_temp_dir):
            os.makedirs(self.app_temp_dir, exist_ok=True)

    def get_temp_filepath(self, filename: str) -> str:
        """Returns a path for a file inside the Trax temp directory."""
        self.ensure_temp_dir()
        return os.path.join(self.app_temp_dir, filename)

    def clean_temp_dir(self):
        """Removes all files in the Trax temp directory."""
        if os.path.exists(self.app_temp_dir):
            shutil.rmtree(self.app_temp_dir, ignore_errors=True)
            self.ensure_temp_dir()

    def create_export_zip(self, file_paths: List[str], output_dir: str) -> str:
        """Creates a zip file containing the specified files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        zip_filename = f"Trax_export_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
                    
        return zip_path

file_manager = FileManager()
