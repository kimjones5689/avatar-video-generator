"""
Talking Photo AI
Health & Status Routes

Provides liveness and readiness probes, queue status,
and system information.
"""

from pathlib import Path
from flask import Blueprint, current_app, jsonify
from backend.services.job_service import JobStatus
import os

health_bp = Blueprint(
    "health",
    __name__,
    url_prefix="/api/v1/health"
)


def get_job_service():
    return current_app.config["JOB_SERVICE"]


def get_queue_service():
    return current_app.config["QUEUE_SERVICE"]


@health_bp.get("/live")
def liveness():
    """
    Kubernetes liveness probe.
    Returns 200 if the application is running.
    """
    return jsonify({"status": "alive"}), 200


@health_bp.get("/ready")
def readiness():
    """
    Kubernetes readiness probe.
    Returns 200 if the application is ready to serve requests.
    """
    return jsonify({"status": "ready"}), 200


@health_bp.get("/status")
def status():
    """
    Detailed status information.
    """
    job_service = get_job_service()
    queue_service = get_queue_service()
    stats = job_service.stats()

    return jsonify(
        {
            "status": "healthy",
            "jobs": stats,
            "queue_depth": queue_service.size(),
            "version": "1.0.0",
        }
    )
