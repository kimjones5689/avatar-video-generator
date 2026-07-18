"""
Talking Photo AI
Storage Service

Handles file operations for uploads, outputs, and temporary files.
"""

from pathlib import Path
from typing import Optional
import shutil


class StorageService:
    """
    Manages file operations and directory organization.
    """

    def __init__(
        self,
        upload_directory: Path,
        output_directory: Path,
        temp_directory: Path,
    ):
        self.upload_directory = Path(upload_directory)
        self.output_directory = Path(output_directory)
        self.temp_directory = Path(temp_directory)

        for directory in [
            self.upload_directory,
            self.output_directory,
            self.temp_directory,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    # ────────────────────────────────────────────────────────

    def get_upload_path(self, filename: str) -> Path:
        """
        Return the full path for an uploaded file.
        """
        return self.upload_directory / filename

    def get_output_path(self, filename: str) -> Path:
        """
        Return the full path for an output file.
        """
        return self.output_directory / filename

    def get_temp_path(self, filename: str) -> Path:
        """
        Return the full path for a temporary file.
        """
        return self.temp_directory / filename

    # ────────────────────────────────────────────────────────

    def file_exists(self, path: Path) -> bool:
        """
        Check if a file exists.
        """
        return path.exists() and path.is_file()

    def delete_file(self, path: Path) -> bool:
        """
        Delete a file. Return True if successful.
        """
        try:
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def cleanup_temp(self) -> int:
        """
        Delete all files in the temp directory.
        Return the number of files deleted.
        """
        count = 0
        for file in self.temp_directory.glob("*"):
            if file.is_file():
                if self.delete_file(file):
                    count += 1
        return count
