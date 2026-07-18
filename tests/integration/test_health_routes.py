"""
Integration tests for health routes.
"""

import pytest


@pytest.mark.integration
class TestHealthRoutes:
    """
    Integration tests for health routes.
    """

    def test_liveness_probe(self, client):
        """
        Test the liveness probe endpoint.
        """
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "alive"

    def test_readiness_probe(self, client):
        """
        Test the readiness probe endpoint.
        """
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ready"

    def test_status_endpoint(self, client):
        """
        Test the status endpoint.
        """
        response = client.get("/api/v1/health/status")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "jobs" in data
        assert "queue_depth" in data
        assert "version" in data
