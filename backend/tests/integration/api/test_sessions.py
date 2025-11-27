"""Integration tests for Session API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_session_integration(async_client: AsyncClient):
    """Test creating a session via API against real database."""
    response = await async_client.post("/sessions")

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "active"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_session_integration(async_client: AsyncClient):
    """Test retrieving a session via API against real database."""
    # 1. Create session
    create_res = await async_client.post("/sessions")
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # 2. Get session
    get_res = await async_client.get(f"/sessions/{session_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == session_id
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_nonexistent_session_integration(async_client: AsyncClient):
    """Test 404 for missing session."""
    import uuid
    fake_id = str(uuid.uuid4())

    response = await async_client.get(f"/sessions/{fake_id}")
    assert response.status_code == 404
