from pathlib import Path
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import (
    HOST,
    PORT,
    DEBUG,
    UPLOAD_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    LOG_FILE,
    LOG_LEVEL,
)
from backend.routes.jobs import jobs_bp
from backend.services.job_service import JobService
from backend.services.queue_service import QueueService
from backend.services.storage_service import StorageService
from backend.services.video_service import VideoService

# ────────────────────────────────────────────────────────
# Application Factory
# ────────────────────────────────────────────────────────

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Responsibilities:
    - Initialize Flask
    - Configure CORS
    - Create service instances
    - Register blueprints
    - Set up error handlers
    """
    app = Flask(__name__)
    CORS(app)

    # ────────────────────────────────────────────────────────
    # Services
    # ────────────────────────────────────────────────────────

    storage = StorageService(
        upload_directory=UPLOAD_DIR,
        output_directory=OUTPUT_DIR,
        temp_directory=TEMP_DIR,
    )
    jobs = JobService()
    queue = QueueService()
    videos = VideoService(
        output_directory=OUTPUT_DIR,
    )

    # Dependency injection via app.config
    app.config["JOB_SERVICE"] = jobs
    app.config["QUEUE_SERVICE"] = queue
    app.config["STORAGE_SERVICE"] = storage
    app.config["VIDEO_SERVICE"] = videos

    # ────────────────────────────────────────────────────────
    # Blueprints
    # ────────────────────────────────────────────────────────

    app.register_blueprint(jobs_bp)

    # ────────────────────────────────────────────────────────
    # Routes
    # ────────────────────────────────────────────────────────

    @app.get("/")
    def root():
        return jsonify(
            {
                "application": "Talking Photo AI",
                "status": "running",
                "version": "1.0.0",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"})

    return app


# ────────────────────────────────────────────────────────
# Application Instance
# ────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )
