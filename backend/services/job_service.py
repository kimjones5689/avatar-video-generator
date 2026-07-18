"""
Talking Photo AI
Job Service

Responsible for:
- Creating generation jobs
- Tracking progress
- Reporting status
- Storing results
- Cancelling jobs

This implementation keeps everything in memory.
A future version can replace the in-memory store
with Redis, PostgreSQL, Celery, or another queue.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Dict, Optional
import uuid


# ────────────────────────────────────────────────────────
# Job Status
# ────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ────────────────────────────────────────────────────────
# Job Model
# ────────────────────────────────────────────────────────

@dataclass
class Job:
    id: str
    image_path: Path
    script: str
    duration: int
    created_at: datetime = field(
        default_factory=datetime.utcnow
    )
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    output_video: Optional[Path] = None
    error: Optional[str] = None


# ────────────────────────────────────────────────────────
# Service
# ────────────────────────────────────────────────────────

class JobService:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = Lock()

    # ────────────────────────────────────────────────────────

    def create_job(
        self,
        image_path: Path,
        script: str,
        duration: int,
    ) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            image_path=image_path,
            script=script,
            duration=duration,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    # ────────────────────────────────────────────────────────

    def get_job(
        self,
        job_id: str,
    ) -> Optional[Job]:
        return self._jobs.get(job_id)

    # ────────────────────────────────────────────────────────

    def update_progress(
        self,
        job_id: str,
        progress: int,
    ):
        job = self.get_job(job_id)
        if not job:
            return
        job.progress = max(
            0,
            min(progress, 100)
        )

    # ────────────────────────────────────────────────────────

    def mark_running(
        self,
        job_id: str,
    ):
        job = self.get_job(job_id)
        if not job:
            return
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()

    # ────────────────────────────────────────────────────────

    def mark_completed(
        self,
        job_id: str,
        output_video: Path,
    ):
        job = self.get_job(job_id)
        if not job:
            return
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.output_video = output_video
        job.completed_at = datetime.utcnow()

    # ──────────────────────────────��─────────────────────────

    def mark_failed(
        self,
        job_id: str,
        error: str,
    ):
        job = self.get_job(job_id)
        if not job:
            return
        job.status = JobStatus.FAILED
        job.error = error
        job.completed_at = datetime.utcnow()

    # ────────────────────────────────────────────────────────

    def cancel(
        self,
        job_id: str,
    ) -> bool:
        job = self.get_job(job_id)
        if not job:
            return False
        if job.status in (
            JobStatus.COMPLETED,
            JobStatus.CANCELLED,
        ):
            return False
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        return True

    # ────────────────────────────────────────────────────────

    def delete(
        self,
        job_id: str,
    ) -> bool:
        with self._lock:
            if job_id not in self._jobs:
                return False
            del self._jobs[job_id]
            return True

    # ────────────────────────────────────────────────────────

    def list_jobs(self):
        return list(self._jobs.values())

    # ────────────────────────────────────────────────────────

    def stats(self):
        jobs = list(self._jobs.values())
        return {
            "total": len(jobs),
            "queued": sum(
                j.status == JobStatus.QUEUED
                for j in jobs
            ),
            "running": sum(
                j.status == JobStatus.RUNNING
                for j in jobs
            ),
            "completed": sum(
                j.status == JobStatus.COMPLETED
                for j in jobs
            ),
            "failed": sum(
                j.status == JobStatus.FAILED
                for j in jobs
            ),
            "cancelled": sum(
                j.status == JobStatus.CANCELLED
                for j in jobs
            ),
        }
