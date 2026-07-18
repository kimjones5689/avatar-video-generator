"""
Talking Photo AI
Job Routes

REST endpoints for creating, monitoring,
listing, and cancelling generation jobs.
"""

from pathlib import Path
from flask import Blueprint, current_app, jsonify, request
from backend.services.job_service import JobService
from backend.services.video_service import VideoRequest

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/v1/jobs")


def get_job_service() -> JobService:
    return current_app.config["JOB_SERVICE"]


@jobs_bp.post("")
def create_job():
    data = request.get_json(silent=True) or {}
    image = data.get("image")
    script = data.get("script", "").strip()

    if not image:
        return jsonify({"error": "Missing image."}), 400

    if not script:
        return jsonify({"error": "Missing script."}), 400

    duration = int(data.get("duration", 120))
    job_service = get_job_service()

    job = job_service.create_job(
        image_path=Path(image),
        script=script,
        duration=duration,
    )

    # Build the orchestration request.
    # A background worker will consume this later.
    video_request = VideoRequest(
        image_path=job.image_path,
        script=job.script,
        duration=job.duration,
        blink=data.get("blink", True),
        head_movement=data.get("head_movement", True),
        idle_animation=data.get("idle_animation", True),
    )

    # Placeholder for future queue integration.
    current_app.logger.info(
        "Queued video request for job %s",
        job.id,
    )

    return jsonify(
        {
            "job_id": job.id,
            "status": job.status.value,
            "message": "Job queued.",
        }
    ), 202


@jobs_bp.get("")
def list_jobs():
    jobs = get_job_service().list_jobs()
    return jsonify(
        [
            {
                "id": job.id,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ]
    )


@jobs_bp.get("/<job_id>")
def get_job(job_id: str):
    job = get_job_service().get_job(job_id)
    if job is None:
        return jsonify({"error": "Job not found."}), 404

    return jsonify(
        {
            "id": job.id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": (
                job.started_at.isoformat()
                if job.started_at
                else None
            ),
            "completed_at": (
                job.completed_at.isoformat()
                if job.completed_at
                else None
            ),
            "output_video": (
                str(job.output_video)
                if job.output_video
                else None
            ),
            "error": job.error,
        }
    )


@jobs_bp.delete("/<job_id>")
def cancel_job(job_id: str):
    cancelled = get_job_service().cancel(job_id)
    if not cancelled:
        return jsonify(
            {"error": "Job could not be cancelled."}
        ), 400

    return jsonify(
        {
            "status": "cancelled",
            "job_id": job_id,
        }
    )


@jobs_bp.get("/stats")
def stats():
    return jsonify(
        get_job_service().stats()
    )
