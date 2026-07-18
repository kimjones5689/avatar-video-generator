"""
Talking Photo AI
Background Worker

Processes queued avatar-generation jobs.

Responsibilities:
- Poll the job queue
- Update job status
- Coordinate services
- Report progress
- Handle failures
- Support graceful shutdown

This worker intentionally orchestrates the application's
services. The avatar generation backend should be a
user-authorized implementation plugged into VideoService.
"""

from __future__ import annotations
import signal
import threading
import time
from pathlib import Path
from typing import Optional
from backend.services.job_service import (
    JobService,
    JobStatus,
)
from backend.services.video_service import (
    VideoService,
    VideoRequest,
)
from backend.services.storage_service import StorageService


class Worker:
    POLL_INTERVAL = 1.0

    def __init__(
        self,
        job_service: JobService,
        video_service: VideoService,
        storage_service: StorageService,
    ):
        self.job_service = job_service
        self.video_service = video_service
        self.storage_service = storage_service
        self._shutdown = threading.Event()

    # ────────────────────────────────────────────────────────

    def start(self):
        print("Worker started.")
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        while not self._shutdown.is_set():
            self.process_jobs()
            time.sleep(self.POLL_INTERVAL)

        print("Worker stopped.")

    # ────────────────────────────────────────────────────────

    def stop(self, *_):
        print("Shutdown requested...")
        self._shutdown.set()

    # ────────────────────────────────────────────────────────

    def process_jobs(self):
        for job in self.job_service.list_jobs():
            if job.status != JobStatus.QUEUED:
                continue
            self.run_job(job)

    # ────────────────────────────────────────────────────────

    def run_job(self, job):
        try:
            self.job_service.mark_running(job.id)
            self.job_service.update_progress(job.id, 5)

            request = VideoRequest(
                image_path=job.image_path,
                script=job.script,
                duration=job.duration,
            )

            self.job_service.update_progress(job.id, 25)

            result = self.video_service.generate(request)

            if not result.success:
                self.job_service.mark_failed(
                    job.id,
                    result.message,
                )
                return

            self.job_service.update_progress(job.id, 95)

            self.job_service.mark_completed(
                job.id,
                result.output_path,
            )
        except Exception as exc:
            self.job_service.mark_failed(
                job.id,
                str(exc),
            )


# ────────────────────────────────────────────────────────
# Development entry point
# ───────���────────────────────────────────────────────────

if __name__ == "__main__":
    from backend.services.storage_service import StorageService

    uploads = Path("uploads")
    output = Path("output")
    temp = Path("temp")

    storage = StorageService(
        upload_directory=uploads,
        output_directory=output,
        temp_directory=temp,
    )
    jobs = JobService()
    videos = VideoService(output)

    worker = Worker(
        job_service=jobs,
        video_service=videos,
        storage_service=storage,
    )
    worker.start()
