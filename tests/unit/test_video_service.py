"""
Tests for the video service.
"""

import pytest
from pathlib import Path
from backend.services.video_service import VideoService, VideoRequest


@pytest.mark.unit
class TestVideoService:
    """
    Unit tests for VideoService.
    """

    def test_generate_returns_result(self, video_service):
        """
        Test that generate returns a VideoResult.
        """
        request = VideoRequest(
            image_path=Path("test.jpg"),
            script="Hello world",
            duration=60,
        )

        result = video_service.generate(request)

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "output_path")
        assert hasattr(result, "message")

    def test_generate_output_path_in_output_dir(self, video_service, temp_dirs):
        """
        Test that generated video path is in output directory.
        """
        request = VideoRequest(
            image_path=Path("test.jpg"),
            script="Hello world",
            duration=60,
        )

        result = video_service.generate(request)

        assert result.output_path is not None
        assert temp_dirs["output"] in result.output_path.parents or result.output_path.parent == temp_dirs["output"]
