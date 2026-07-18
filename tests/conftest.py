"""
Testing configuration and fixtures.
"""

import pytest
from pathlib import Path
from backend.app import create_app
from backend.services.job_service import JobService
from backend.services.queue_service import QueueService
from backend.services.storage_service import StorageService
from backend.services.video_service import VideoService
import tempfile
import shutil


@pytest.fixture
def temp_dirs():
    """
    Create temporary directories for testing.
    """
    temp_root = Path(tempfile.mkdtemp())
    upload_dir = temp_root / "uploads"
    output_dir = temp_root / "output"
    temp_dir = temp_root / "temp"

    upload_dir.mkdir()
    output_dir.mkdir()
    temp_dir.mkdir()

    yield {
        "root": temp_root,
        "uploads": upload_dir,
        "output": output_dir,
        "temp": temp_dir,
    }

    # Cleanup
    shutil.rmtree(temp_root, ignore_errors=True)


@pytest.fixture
def storage_service(temp_dirs):
    """
    Create a StorageService instance with temporary directories.
    """
    return StorageService(
        upload_directory=temp_dirs["uploads"],
        output_directory=temp_dirs["output"],
        temp_directory=temp_dirs["temp"],
    )


@pytest.fixture
def job_service():
    """
    Create a JobService instance.
    """
    return JobService()


@pytest.fixture
def queue_service():
    """
    Create a QueueService instance.
    """
    return QueueService()


@pytest.fixture
def video_service(temp_dirs):
    """
    Create a VideoService instance.
    """
    return VideoService(output_directory=temp_dirs["output"])


@pytest.fixture
def app(temp_dirs):
    """
    Create a Flask app instance for testing.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["UPLOAD_DIR"] = temp_dirs["uploads"]
    app.config["OUTPUT_DIR"] = temp_dirs["output"]
    app.config["TEMP_DIR"] = temp_dirs["temp"]
    return app


@pytest.fixture
def client(app):
    """
    Create a test client.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a CLI runner for testing.
    """
    return app.test_cli_runner()
