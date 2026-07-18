"""
Tests for the job service.
"""

import pytest
from pathlib import Path
from backend.services.job_service import JobService, JobStatus


@pytest.mark.unit
class TestJobService:
    """
    Unit tests for JobService.
    """

    def test_create_job(self, job_service):
        """
        Test creating a new job.
        """
        image_path = Path("test.jpg")
        script = "Hello world"
        duration = 60

        job = job_service.create_job(
            image_path=image_path,
            script=script,
            duration=duration,
        )

        assert job.id is not None
        assert job.image_path == image_path
        assert job.script == script
        assert job.duration == duration
        assert job.status == JobStatus.QUEUED
        assert job.progress == 0

    def test_get_job(self, job_service):
        """
        Test retrieving a job by ID.
        """
        image_path = Path("test.jpg")
        job = job_service.create_job(
            image_path=image_path,
            script="Hello",
            duration=60,
        )

        retrieved = job_service.get_job(job.id)
        assert retrieved is not None
        assert retrieved.id == job.id

    def test_get_nonexistent_job(self, job_service):
        """
        Test retrieving a nonexistent job.
        """
        job = job_service.get_job("nonexistent")
        assert job is None

    def test_update_progress(self, job_service):
        """
        Test updating job progress.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        job_service.update_progress(job.id, 50)
        updated_job = job_service.get_job(job.id)
        assert updated_job.progress == 50

    def test_progress_clamped(self, job_service):
        """
        Test that progress is clamped to 0-100.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        job_service.update_progress(job.id, 150)
        updated_job = job_service.get_job(job.id)
        assert updated_job.progress == 100

        job_service.update_progress(job.id, -10)
        updated_job = job_service.get_job(job.id)
        assert updated_job.progress == 0

    def test_mark_running(self, job_service):
        """
        Test marking a job as running.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        job_service.mark_running(job.id)
        updated_job = job_service.get_job(job.id)
        assert updated_job.status == JobStatus.RUNNING
        assert updated_job.started_at is not None

    def test_mark_completed(self, job_service):
        """
        Test marking a job as completed.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        output_path = Path("output.mp4")
        job_service.mark_completed(job.id, output_path)

        updated_job = job_service.get_job(job.id)
        assert updated_job.status == JobStatus.COMPLETED
        assert updated_job.progress == 100
        assert updated_job.output_video == output_path
        assert updated_job.completed_at is not None

    def test_mark_failed(self, job_service):
        """
        Test marking a job as failed.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        error_msg = "Test error"
        job_service.mark_failed(job.id, error_msg)

        updated_job = job_service.get_job(job.id)
        assert updated_job.status == JobStatus.FAILED
        assert updated_job.error == error_msg
        assert updated_job.completed_at is not None

    def test_cancel_job(self, job_service):
        """
        Test cancelling a job.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        result = job_service.cancel(job.id)
        assert result is True

        updated_job = job_service.get_job(job.id)
        assert updated_job.status == JobStatus.CANCELLED

    def test_cannot_cancel_completed_job(self, job_service):
        """
        Test that completed jobs cannot be cancelled.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        job_service.mark_completed(job.id, Path("output.mp4"))
        result = job_service.cancel(job.id)
        assert result is False

    def test_delete_job(self, job_service):
        """
        Test deleting a job.
        """
        job = job_service.create_job(
            image_path=Path("test.jpg"),
            script="Hello",
            duration=60,
        )

        result = job_service.delete(job.id)
        assert result is True

        retrieved = job_service.get_job(job.id)
        assert retrieved is None

    def test_list_jobs(self, job_service):
        """
        Test listing all jobs.
        """
        job1 = job_service.create_job(
            image_path=Path("test1.jpg"),
            script="Hello",
            duration=60,
        )
        job2 = job_service.create_job(
            image_path=Path("test2.jpg"),
            script="World",
            duration=120,
        )

        jobs = job_service.list_jobs()
        assert len(jobs) == 2
        assert job1 in jobs
        assert job2 in jobs

    def test_stats(self, job_service):
        """
        Test job statistics.
        """
        # Create multiple jobs with different statuses
        job1 = job_service.create_job(
            image_path=Path("test1.jpg"),
            script="Hello",
            duration=60,
        )
        job2 = job_service.create_job(
            image_path=Path("test2.jpg"),
            script="World",
            duration=120,
        )

        job_service.mark_running(job2.id)

        stats = job_service.stats()
        assert stats["total"] == 2
        assert stats["queued"] == 1
        assert stats["running"] == 1
        assert stats["completed"] == 0
