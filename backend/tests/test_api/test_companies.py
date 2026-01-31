"""Tests for companies API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient, sample_company_data: dict):
    """Test creating a new company."""
    response = await client.post("/api/v1/companies", json=sample_company_data)

    assert response.status_code == 201
    data = response.json()
    assert data["code"] == sample_company_data["code"]
    assert data["name_ja"] == sample_company_data["name_ja"]
    assert data["name_en"] == sample_company_data["name_en"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_company_duplicate_code(
    client: AsyncClient, sample_company_data: dict
):
    """Test creating a company with duplicate code fails."""
    # Create first company
    response = await client.post("/api/v1/companies", json=sample_company_data)
    assert response.status_code == 201

    # Try to create duplicate
    response = await client.post("/api/v1/companies", json=sample_company_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient, sample_company_data: dict):
    """Test listing companies."""
    # Create a company first
    await client.post("/api/v1/companies", json=sample_company_data)

    response = await client.get("/api/v1/companies")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_companies_filter_active(
    client: AsyncClient, sample_company_data: dict
):
    """Test listing companies with active filter."""
    # Create a company
    await client.post("/api/v1/companies", json=sample_company_data)

    # Filter active companies
    response = await client.get("/api/v1/companies", params={"is_active": True})

    assert response.status_code == 200
    data = response.json()
    for company in data["items"]:
        assert company["is_active"] is True


@pytest.mark.asyncio
async def test_get_company(client: AsyncClient, sample_company_data: dict):
    """Test getting a specific company."""
    # Create a company
    create_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/companies/{company_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == company_id
    assert data["code"] == sample_company_data["code"]


@pytest.mark.asyncio
async def test_get_company_not_found(client: AsyncClient):
    """Test getting a non-existent company returns 404."""
    response = await client.get("/api/v1/companies/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_company(client: AsyncClient, sample_company_data: dict):
    """Test updating a company."""
    # Create a company
    create_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = create_response.json()["id"]

    # Update the company
    update_data = {"name_ko": "동경전력 (수정)"}
    response = await client.patch(f"/api/v1/companies/{company_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name_ko"] == update_data["name_ko"]
    # Other fields should remain unchanged
    assert data["code"] == sample_company_data["code"]


@pytest.mark.asyncio
async def test_update_company_deactivate(client: AsyncClient, sample_company_data: dict):
    """Test deactivating a company."""
    # Create a company
    create_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = create_response.json()["id"]

    # Deactivate the company
    response = await client.patch(
        f"/api/v1/companies/{company_id}", json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient, sample_company_data: dict):
    """Test deleting a company."""
    # Create a company
    create_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = create_response.json()["id"]

    # Delete the company
    response = await client.delete(f"/api/v1/companies/{company_id}")

    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(f"/api/v1/companies/{company_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_company_pagination(client: AsyncClient):
    """Test company list pagination."""
    # Create multiple companies
    for i in range(5):
        company_data = {
            "code": f"company{i}",
            "name_ja": f"会社{i}",
            "name_en": f"Company {i}",
            "website_url": f"https://company{i}.example.com",
        }
        await client.post("/api/v1/companies", json=company_data)

    # Test pagination
    response = await client.get("/api/v1/companies", params={"page": 1, "page_size": 2})

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["page_size"] == 2
