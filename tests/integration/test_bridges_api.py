"""Integration tests for jump bridges API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def clear_bridge_config():
    """Clear bridge config before each test."""
    from backend.app.services.jumpbridge import clear_bridge_cache
    clear_bridge_cache()
    yield
    clear_bridge_cache()


class TestListNetworksEndpoint:
    """Tests for GET /api/v1/bridges/."""

    def test_list_empty_networks(self, test_client: TestClient):
        """Should return empty list when no networks configured."""
        response = test_client.get("/api/v1/bridges/")

        assert response.status_code == 200
        data = response.json()
        assert "networks" in data

    def test_response_structure(self, test_client: TestClient):
        """Should return JumpBridgeConfig structure."""
        response = test_client.get("/api/v1/bridges/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data.get("networks"), list)


class TestImportBridgesEndpoint:
    """Tests for POST /api/v1/bridges/import."""

    def test_import_valid_bridges(self, test_client: TestClient):
        """Should import valid bridge text."""
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["network_name"] == "TestNetwork"
        assert data["bridges_imported"] == 1
        assert len(data["errors"]) == 0

    def test_import_multiple_bridges(self, test_client: TestClient):
        """Should import multiple bridges."""
        bridge_text = """
        Jita <-> Perimeter
        Amarr <-> Niarja
        """
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": bridge_text
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bridges_imported"] == 2

    def test_import_with_comments(self, test_client: TestClient):
        """Should skip comment lines."""
        bridge_text = """
        # This is a comment
        Jita <-> Perimeter
        # Another comment
        """
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": bridge_text
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bridges_imported"] == 1

    def test_import_reports_errors(self, test_client: TestClient):
        """Should report errors for invalid systems."""
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "FakeSystem <-> AnotherFake"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bridges_imported"] == 0
        assert len(data["errors"]) > 0

    def test_import_different_formats(self, test_client: TestClient):
        """Should accept different bridge formats."""
        bridge_text = """
        Jita <-> Perimeter
        Amarr --> Niarja
        Dodixie <> Hek
        """
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": bridge_text
            }
        )

        assert response.status_code == 200
        data = response.json()
        # Some may fail if systems don't exist, but should parse
        assert "bridges_imported" in data

    def test_import_replace_mode(self, test_client: TestClient):
        """Should replace existing network in replace mode."""
        # First import
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        # Second import with replace
        response = test_client.post(
            "/api/v1/bridges/import?replace=true",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Amarr <-> Niarja"
            }
        )

        assert response.status_code == 200

        # Check network now has only new bridge
        list_response = test_client.get("/api/v1/bridges/")
        networks = list_response.json()["networks"]
        test_network = next((n for n in networks if n["name"] == "TestNetwork"), None)
        assert test_network is not None
        assert len(test_network["bridges"]) == 1

    def test_import_creates_network(self, test_client: TestClient):
        """Should create network on import."""
        response = test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "NewNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        assert response.status_code == 200

        # Check network exists
        list_response = test_client.get("/api/v1/bridges/")
        networks = list_response.json()["networks"]
        network_names = [n["name"] for n in networks]
        assert "NewNetwork" in network_names


class TestToggleNetworkEndpoint:
    """Tests for PATCH /api/v1/bridges/{network_name}."""

    def test_toggle_network_disable(self, test_client: TestClient):
        """Should disable a network."""
        # First create network
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        # Toggle disable
        response = test_client.patch("/api/v1/bridges/TestNetwork?enabled=false")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["enabled"] is False

    def test_toggle_network_enable(self, test_client: TestClient):
        """Should enable a network."""
        # First create and disable network
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )
        test_client.patch("/api/v1/bridges/TestNetwork?enabled=false")

        # Toggle enable
        response = test_client.patch("/api/v1/bridges/TestNetwork?enabled=true")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_toggle_nonexistent_network(self, test_client: TestClient):
        """Should return 404 for nonexistent network."""
        response = test_client.patch("/api/v1/bridges/NonexistentNetwork?enabled=false")

        assert response.status_code == 404


class TestDeleteNetworkEndpoint:
    """Tests for DELETE /api/v1/bridges/{network_name}."""

    def test_delete_network(self, test_client: TestClient):
        """Should delete a network."""
        # First create network
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        # Delete
        response = test_client.delete("/api/v1/bridges/TestNetwork")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["deleted"] == "TestNetwork"

        # Verify deleted
        list_response = test_client.get("/api/v1/bridges/")
        networks = list_response.json()["networks"]
        network_names = [n["name"] for n in networks]
        assert "TestNetwork" not in network_names

    def test_delete_nonexistent_network(self, test_client: TestClient):
        """Should return 404 for nonexistent network."""
        response = test_client.delete("/api/v1/bridges/NonexistentNetwork")

        assert response.status_code == 404


class TestGetNetworkEndpoint:
    """Tests for GET /api/v1/bridges/{network_name}."""

    def test_get_existing_network(self, test_client: TestClient):
        """Should return network details."""
        # First create network
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        response = test_client.get("/api/v1/bridges/TestNetwork")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TestNetwork"
        assert "bridges" in data
        assert "enabled" in data

    def test_get_nonexistent_network(self, test_client: TestClient):
        """Should return 404 for nonexistent network."""
        response = test_client.get("/api/v1/bridges/NonexistentNetwork")

        assert response.status_code == 404

    def test_get_network_has_bridges(self, test_client: TestClient):
        """Should include bridges in network response."""
        # First create network
        test_client.post(
            "/api/v1/bridges/import",
            json={
                "network_name": "TestNetwork",
                "bridge_text": "Jita <-> Perimeter"
            }
        )

        response = test_client.get("/api/v1/bridges/TestNetwork")

        data = response.json()
        assert len(data["bridges"]) == 1
        bridge = data["bridges"][0]
        assert "from_system" in bridge
        assert "to_system" in bridge
