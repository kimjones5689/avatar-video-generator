"""
Integration tests for job routes.
"""

import pytest
import json


@pytest.mark.integration
class TestJobRoutes:
    """
    Integration tests for job routes.
    """

    def test_create_job(self, client):
        """
        Test creating a job via the API.
        """
        payload = {
            "image": "test.jpg",
            "script": "Hello world",
            "duration": 60,
        }

        response = client.post(
            "/api/v1/jobs",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 202
        data = response.get_json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_create_job_missing_image(self, client):
        """
        Test creating a job without an image.
        """
        payload = {
            "script": "Hello world",
            "duration": 60,
        }

        response = client.post(
            "/api/v1/jobs",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_create_job_missing_script(self, client):
        """
        Test creating a job without a script.
        """
        payload = {
            "image": "test.jpg",
            "duration": 60,
        }

        response = client.post(
            "/api/v1/jobs",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_list_jobs(self, client):
        """
        Test listing jobs.
        """
        # Create a job first
        payload = {
            "image": "test.jpg",
            "script": "Hello world",
            "duration": 60,
        }

        client.post(
            "/api/v1/jobs",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # List jobs
        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_job(self, client):
        """
        Test getting a specific job.
        """
        # Create a job first
        payload = {
            "image": "test.jpg",
            "script": "Hello world",
            "duration": 60,
        }

        response = client.post(
            "/api/v1/jobs",
            data=json.dumps(payload),
            content_type="application/json",
        )
        job_id = response.get_json()["job_id"]

        # Get the job
        response = client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == job_id
        assert data["status"] == "queued"

    def test_get_nonexistent_job(self, client):
        """
        Test getting a nonexistent job.
        """
        response = client.get("/api/v1/jobs/nonexistent")
        assert response.status_code == 404
