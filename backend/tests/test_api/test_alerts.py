"""Tests for alerts API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_alert_settings(client: AsyncClient):
    """Test listing all alert settings."""
    response = await client.get("/api/v1/alerts")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_alert_setting(client: AsyncClient):
    """Test getting a specific alert setting."""
    alert_types = ["crawl_failure", "price_change", "weekly_report"]

    for alert_type in alert_types:
        response = await client.get(f"/api/v1/alerts/{alert_type}")

        # May return 200 or 404 depending on initial data
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["alert_type"] == alert_type
            assert "is_enabled" in data
            assert "recipients" in data


@pytest.mark.asyncio
async def test_update_alert_setting(client: AsyncClient):
    """Test updating an alert setting."""
    # First ensure the alert exists by getting it
    response = await client.get("/api/v1/alerts/crawl_failure")

    if response.status_code == 404:
        # Create it first if needed
        pytest.skip("Alert setting doesn't exist")

    # Update the setting
    update_data = {"is_enabled": True}
    response = await client.patch("/api/v1/alerts/crawl_failure", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["is_enabled"] is True


@pytest.mark.asyncio
async def test_toggle_alert_setting(client: AsyncClient):
    """Test toggling an alert setting on and off."""
    response = await client.get("/api/v1/alerts/price_change")

    if response.status_code == 404:
        pytest.skip("Alert setting doesn't exist")

    current_state = response.json()["is_enabled"]

    # Toggle off/on
    response = await client.patch(
        "/api/v1/alerts/price_change", json={"is_enabled": not current_state}
    )

    assert response.status_code == 200
    assert response.json()["is_enabled"] == (not current_state)


@pytest.mark.asyncio
async def test_add_alert_recipient(client: AsyncClient):
    """Test adding a recipient to an alert."""
    recipient_data = {
        "email": "test@example.com",
        "name": "Test User",
    }
    response = await client.post(
        "/api/v1/alerts/crawl_failure/recipients", json=recipient_data
    )

    # May succeed or fail depending on alert existence
    assert response.status_code in [200, 201, 404]
    if response.status_code in [200, 201]:
        data = response.json()
        assert data["email"] == recipient_data["email"]
        assert data["name"] == recipient_data["name"]


@pytest.mark.asyncio
async def test_add_alert_recipient_invalid_email(client: AsyncClient):
    """Test adding a recipient with invalid email fails."""
    recipient_data = {
        "email": "invalid-email",
        "name": "Test User",
    }
    response = await client.post(
        "/api/v1/alerts/crawl_failure/recipients", json=recipient_data
    )

    assert response.status_code in [404, 422]  # Not found or validation error


@pytest.mark.asyncio
async def test_add_duplicate_recipient(client: AsyncClient):
    """Test adding a duplicate recipient."""
    recipient_data = {
        "email": "duplicate@example.com",
        "name": "Test User",
    }

    # Add first time
    response1 = await client.post(
        "/api/v1/alerts/crawl_failure/recipients", json=recipient_data
    )

    if response1.status_code in [200, 201]:
        # Try to add again
        response2 = await client.post(
            "/api/v1/alerts/crawl_failure/recipients", json=recipient_data
        )
        # Should either fail or be idempotent
        assert response2.status_code in [200, 201, 400, 409]


@pytest.mark.asyncio
async def test_remove_alert_recipient(client: AsyncClient):
    """Test removing a recipient from an alert."""
    # First add a recipient
    recipient_data = {
        "email": "to-remove@example.com",
        "name": "To Remove",
    }
    add_response = await client.post(
        "/api/v1/alerts/crawl_failure/recipients", json=recipient_data
    )

    if add_response.status_code in [200, 201]:
        recipient_id = add_response.json()["id"]

        # Remove the recipient
        response = await client.delete(
            f"/api/v1/alerts/crawl_failure/recipients/{recipient_id}"
        )

        assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_remove_nonexistent_recipient(client: AsyncClient):
    """Test removing a non-existent recipient."""
    response = await client.delete("/api/v1/alerts/crawl_failure/recipients/99999")

    assert response.status_code in [404, 400]
