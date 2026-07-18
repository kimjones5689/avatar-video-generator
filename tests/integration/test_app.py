"""
Integration tests for the Flask application.
"""

import pytest


@pytest.mark.integration
class TestApp:
    """
    Integration tests for the Flask application.
    """

    def test_app_created(self, app):
        """
        Test that the app is created.
        """
        assert app is not None
        assert app.config["TESTING"] is True

    def test_root_endpoint(self, client):
        """
        Test the root endpoint.
        """
        response = client.get("/")
        assert response.status_code == 200
        data = response.get_json()
        assert data["application"] == "Talking Photo AI"
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """
        Test the health endpoint.
        """
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
