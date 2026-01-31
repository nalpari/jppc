"""Tests for crawling API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_crawl_status(client: AsyncClient):
    """Test getting crawl status."""
    response = await client.get("/api/v1/crawling/status")

    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "current_job" in data
    assert "last_run" in data


@pytest.mark.asyncio
async def test_start_crawl(client: AsyncClient, sample_company_data: dict):
    """Test starting a crawl job."""
    # Create a company first
    company_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = company_response.json()["id"]

    # Start crawl
    response = await client.post(
        "/api/v1/crawling/start", json={"company_ids": [company_id]}
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_start_crawl_all_companies(client: AsyncClient, sample_company_data: dict):
    """Test starting a crawl for all companies."""
    # Create a company
    await client.post("/api/v1/companies", json=sample_company_data)

    # Start crawl for all
    response = await client.post("/api/v1/crawling/start", json={})

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data


@pytest.mark.asyncio
async def test_stop_crawl(client: AsyncClient):
    """Test stopping a crawl job."""
    response = await client.post("/api/v1/crawling/stop")

    # Should succeed even if no job is running
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_get_crawl_logs(client: AsyncClient):
    """Test getting crawl logs."""
    response = await client.get("/api/v1/crawling/logs")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_crawl_logs_filter_status(client: AsyncClient):
    """Test filtering crawl logs by status."""
    response = await client.get("/api/v1/crawling/logs", params={"status": "success"})

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "success"


@pytest.mark.asyncio
async def test_get_crawl_logs_filter_company(client: AsyncClient, sample_company_data: dict):
    """Test filtering crawl logs by company."""
    # Create a company
    company_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = company_response.json()["id"]

    response = await client.get(
        "/api/v1/crawling/logs", params={"company_id": company_id}
    )

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["company_id"] == company_id


@pytest.mark.asyncio
async def test_get_crawl_log_detail(client: AsyncClient, sample_company_data: dict):
    """Test getting a specific crawl log."""
    # This test assumes there might not be logs initially
    response = await client.get("/api/v1/crawling/logs/1")

    # Either not found or success
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_schedule(client: AsyncClient):
    """Test getting schedule configuration."""
    response = await client.get("/api/v1/crawling/schedule")

    assert response.status_code == 200
    data = response.json()
    assert "is_enabled" in data
    assert "day_of_week" in data
    assert "hour" in data
    assert "minute" in data


@pytest.mark.asyncio
async def test_update_schedule(client: AsyncClient):
    """Test updating schedule configuration."""
    schedule_data = {
        "is_enabled": True,
        "day_of_week": 0,  # Monday
        "hour": 3,
        "minute": 0,
    }
    response = await client.put("/api/v1/crawling/schedule", json=schedule_data)

    assert response.status_code == 200
    data = response.json()
    assert data["is_enabled"] == schedule_data["is_enabled"]
    assert data["day_of_week"] == schedule_data["day_of_week"]
    assert data["hour"] == schedule_data["hour"]
    assert data["minute"] == schedule_data["minute"]


@pytest.mark.asyncio
async def test_update_schedule_invalid_time(client: AsyncClient):
    """Test updating schedule with invalid time fails."""
    schedule_data = {
        "is_enabled": True,
        "day_of_week": 0,
        "hour": 25,  # Invalid hour
        "minute": 0,
    }
    response = await client.put("/api/v1/crawling/schedule", json=schedule_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_schedule_invalid_day(client: AsyncClient):
    """Test updating schedule with invalid day fails."""
    schedule_data = {
        "is_enabled": True,
        "day_of_week": 7,  # Invalid day (0-6)
        "hour": 3,
        "minute": 0,
    }
    response = await client.put("/api/v1/crawling/schedule", json=schedule_data)

    assert response.status_code == 422  # Validation error
