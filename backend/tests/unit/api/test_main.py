"""Unit tests for FastAPI application."""

from fastapi.testclient import TestClient


def test_health_endpoint() -> None:
    """Test health check endpoint returns healthy status."""
    from backend.app.api.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "service" in response.json()


def test_root_endpoint() -> None:
    """Test root endpoint returns API information."""
    from backend.app.api.main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_cors_headers() -> None:
    """Test that CORS headers are present."""
    from backend.app.api.main import app

    client = TestClient(app)
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    # CORS middleware should add access-control headers
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_openapi_docs_available() -> None:
    """Test that OpenAPI documentation is available."""
    from backend.app.api.main import app

    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200
