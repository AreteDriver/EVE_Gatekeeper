"""Integration tests for health check endpoint."""

import pytest


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, test_client):
        """Test health check returns healthy status."""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info."""
        response = test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestStatusEndpoint:
    """Tests for /api/v1/status endpoint."""

    def test_status_endpoint(self, test_client):
        """Test status endpoint returns detailed info."""
        response = test_client.get("/api/v1/status/")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "uptime_formatted" in data
        assert "environment" in data
        assert "checks" in data
        assert "features" in data

    def test_status_has_feature_flags(self, test_client):
        """Test status includes feature flags."""
        response = test_client.get("/api/v1/status/")
        data = response.json()

        features = data["features"]
        assert "rate_limiting" in features
        assert "api_key_auth" in features
        assert "metrics" in features
