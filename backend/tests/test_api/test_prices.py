"""Tests for prices API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def company_with_price(client: AsyncClient, sample_company_data: dict, sample_price_plan_data: dict):
    """Create a company with a price plan for testing."""
    # Create company
    company_response = await client.post("/api/v1/companies", json=sample_company_data)
    company = company_response.json()

    # Create price plan
    price_data = {**sample_price_plan_data, "company_id": company["id"]}
    price_response = await client.post("/api/v1/prices", json=price_data)
    price = price_response.json()

    return {"company": company, "price": price}


@pytest.mark.asyncio
async def test_create_price_plan(
    client: AsyncClient, sample_company_data: dict, sample_price_plan_data: dict
):
    """Test creating a new price plan."""
    # First create a company
    company_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = company_response.json()["id"]

    # Create price plan
    price_data = {**sample_price_plan_data, "company_id": company_id}
    response = await client.post("/api/v1/prices", json=price_data)

    assert response.status_code == 201
    data = response.json()
    assert data["plan_code"] == sample_price_plan_data["plan_code"]
    assert data["company_id"] == company_id
    assert data["is_current"] is True


@pytest.mark.asyncio
async def test_list_prices(client: AsyncClient, company_with_price: dict):
    """Test listing price plans."""
    response = await client.get("/api/v1/prices")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_prices_filter_by_company(client: AsyncClient, company_with_price: dict):
    """Test filtering prices by company."""
    company_id = company_with_price["company"]["id"]

    response = await client.get("/api/v1/prices", params={"company_id": company_id})

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["company_id"] == company_id


@pytest.mark.asyncio
async def test_list_prices_filter_current_only(client: AsyncClient, company_with_price: dict):
    """Test filtering to current prices only."""
    response = await client.get("/api/v1/prices", params={"is_current": True})

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["is_current"] is True


@pytest.mark.asyncio
async def test_get_price(client: AsyncClient, company_with_price: dict):
    """Test getting a specific price plan."""
    price_id = company_with_price["price"]["id"]

    response = await client.get(f"/api/v1/prices/{price_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == price_id


@pytest.mark.asyncio
async def test_get_price_not_found(client: AsyncClient):
    """Test getting a non-existent price returns 404."""
    response = await client.get("/api/v1/prices/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_price_history(client: AsyncClient, company_with_price: dict):
    """Test getting price history."""
    price_id = company_with_price["price"]["id"]

    response = await client.get(f"/api/v1/prices/{price_id}/history")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_compare_prices(
    client: AsyncClient, sample_company_data: dict, sample_price_plan_data: dict
):
    """Test comparing prices across plans."""
    # Create two companies with different prices
    company1 = await client.post("/api/v1/companies", json=sample_company_data)
    company1_id = company1.json()["id"]

    company2_data = {
        **sample_company_data,
        "code": "chubu",
        "name_ja": "中部電力",
        "name_en": "Chubu Electric Power",
    }
    company2 = await client.post("/api/v1/companies", json=company2_data)
    company2_id = company2.json()["id"]

    # Create price plans
    price1_data = {**sample_price_plan_data, "company_id": company1_id, "unit_price": 26.48}
    price1 = await client.post("/api/v1/prices", json=price1_data)
    price1_id = price1.json()["id"]

    price2_data = {
        **sample_price_plan_data,
        "company_id": company2_id,
        "plan_code": "従量電灯B-2",
        "unit_price": 25.80,
    }
    price2 = await client.post("/api/v1/prices", json=price2_data)
    price2_id = price2.json()["id"]

    # Compare prices
    compare_data = {"plan_ids": [price1_id, price2_id], "usage_kwh": 300}
    response = await client.post("/api/v1/prices/compare", json=compare_data)

    assert response.status_code == 200
    data = response.json()
    assert "comparisons" in data
    assert len(data["comparisons"]) == 2
    for comparison in data["comparisons"]:
        assert "plan_id" in comparison
        assert "total_cost" in comparison
        assert "base_charge" in comparison
        assert "usage_charge" in comparison


@pytest.mark.asyncio
async def test_compare_prices_empty_list(client: AsyncClient):
    """Test comparing with empty plan list fails."""
    compare_data = {"plan_ids": [], "usage_kwh": 300}
    response = await client.post("/api/v1/prices/compare", json=compare_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_price_tiers(
    client: AsyncClient, sample_company_data: dict
):
    """Test price plan with tiered pricing."""
    # Create company
    company_response = await client.post("/api/v1/companies", json=sample_company_data)
    company_id = company_response.json()["id"]

    # Create price plan with tiers
    price_data = {
        "company_id": company_id,
        "plan_code": "従量電灯B-tiered",
        "plan_name_ja": "従量電灯B",
        "plan_type": "residential",
        "base_charge": 858.00,
        "tier1_limit": 120,
        "tier1_price": 19.88,
        "tier2_limit": 300,
        "tier2_price": 26.48,
        "tier3_price": 30.57,
    }
    response = await client.post("/api/v1/prices", json=price_data)

    assert response.status_code == 201
    data = response.json()
    assert data["tier1_limit"] == 120
    assert data["tier1_price"] == 19.88
    assert data["tier2_limit"] == 300
    assert data["tier2_price"] == 26.48
    assert data["tier3_price"] == 30.57
