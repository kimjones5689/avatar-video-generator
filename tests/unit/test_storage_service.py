"""
Tests for the storage service.
"""

import pytest
from pathlib import Path
from backend.services.storage_service import StorageService


@pytest.mark.unit
class TestStorageService:
    """
    Unit tests for StorageService.
    """

    def test_get_upload_path(self, storage_service, temp_dirs):
        """
        Test getting upload file path.
        """
        filename = "test.jpg"
        path = storage_service.get_upload_path(filename)
        assert path == temp_dirs["uploads"] / filename

    def test_get_output_path(self, storage_service, temp_dirs):
        """
        Test getting output file path.
        """
        filename = "output.mp4"
        path = storage_service.get_output_path(filename)
        assert path == temp_dirs["output"] / filename

    def test_get_temp_path(self, storage_service, temp_dirs):
        """
        Test getting temporary file path.
        """
        filename = "temp.wav"
        path = storage_service.get_temp_path(filename)
        assert path == temp_dirs["temp"] / filename

    def test_file_exists(self, storage_service, temp_dirs):
        """
        Test checking if a file exists.
        """
        # Create a test file
        test_file = temp_dirs["uploads"] / "test.txt"
        test_file.write_text("test content")

        assert storage_service.file_exists(test_file) is True
        assert storage_service.file_exists(temp_dirs["uploads"] / "nonexistent.txt") is False

    def test_delete_file(self, storage_service, temp_dirs):
        """
        Test deleting a file.
        """
        # Create a test file
        test_file = temp_dirs["uploads"] / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        result = storage_service.delete_file(test_file)
        assert result is True
        assert not test_file.exists()

    def test_delete_nonexistent_file(self, storage_service, temp_dirs):
        """
        Test deleting a nonexistent file.
        """
        nonexistent = temp_dirs["uploads"] / "nonexistent.txt"
        result = storage_service.delete_file(nonexistent)
        assert result is False

    def test_cleanup_temp(self, storage_service, temp_dirs):
        """
        Test cleaning up temporary files.
        """
        # Create some test files
        for i in range(3):
            temp_file = temp_dirs["temp"] / f"temp_{i}.txt"
            temp_file.write_text("temp content")

        count = storage_service.cleanup_temp()
        assert count == 3
        assert len(list(temp_dirs["temp"].glob("*"))) == 0
