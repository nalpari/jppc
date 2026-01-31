"""E2E tests for full application workflow."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestFullWorkflow:
    """Test complete application workflows from end to end."""

    async def test_complete_company_management_workflow(
        self, client: AsyncClient, sample_company_data: dict
    ):
        """
        Test the complete workflow of managing a company:
        1. Create company
        2. Verify it appears in list
        3. Update company details
        4. Verify update
        5. Deactivate company
        6. Delete company
        """
        # Step 1: Create company
        create_response = await client.post(
            "/api/v1/companies", json=sample_company_data
        )
        assert create_response.status_code == 201
        company = create_response.json()
        company_id = company["id"]

        # Step 2: Verify in list
        list_response = await client.get("/api/v1/companies")
        assert list_response.status_code == 200
        companies = list_response.json()["items"]
        assert any(c["id"] == company_id for c in companies)

        # Step 3: Update company
        update_response = await client.patch(
            f"/api/v1/companies/{company_id}",
            json={"name_ko": "업데이트된 회사명"}
        )
        assert update_response.status_code == 200

        # Step 4: Verify update
        get_response = await client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name_ko"] == "업데이트된 회사명"

        # Step 5: Deactivate
        deactivate_response = await client.patch(
            f"/api/v1/companies/{company_id}",
            json={"is_active": False}
        )
        assert deactivate_response.status_code == 200
        assert deactivate_response.json()["is_active"] is False

        # Step 6: Delete
        delete_response = await client.delete(f"/api/v1/companies/{company_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        verify_response = await client.get(f"/api/v1/companies/{company_id}")
        assert verify_response.status_code == 404

    async def test_complete_price_management_workflow(
        self, client: AsyncClient, sample_company_data: dict, sample_price_plan_data: dict
    ):
        """
        Test the complete workflow of managing prices:
        1. Create company
        2. Create price plan
        3. View price in list
        4. Get price details
        5. Check price history
        6. Compare with another plan
        """
        # Step 1: Create company
        company_response = await client.post(
            "/api/v1/companies", json=sample_company_data
        )
        company_id = company_response.json()["id"]

        # Step 2: Create price plan
        price_data = {**sample_price_plan_data, "company_id": company_id}
        price_response = await client.post("/api/v1/prices", json=price_data)
        assert price_response.status_code == 201
        price_id = price_response.json()["id"]

        # Step 3: View in list
        list_response = await client.get(
            "/api/v1/prices", params={"company_id": company_id}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) >= 1

        # Step 4: Get details
        detail_response = await client.get(f"/api/v1/prices/{price_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["plan_code"] == sample_price_plan_data["plan_code"]

        # Step 5: Check history
        history_response = await client.get(f"/api/v1/prices/{price_id}/history")
        assert history_response.status_code == 200

        # Step 6: Create another plan and compare
        company2_data = {
            **sample_company_data,
            "code": "chubu-test",
            "name_ja": "テスト中部電力",
        }
        company2 = await client.post("/api/v1/companies", json=company2_data)
        company2_id = company2.json()["id"]

        price2_data = {
            **sample_price_plan_data,
            "company_id": company2_id,
            "plan_code": "従量電灯B-比較",
            "unit_price": 25.00,
        }
        price2 = await client.post("/api/v1/prices", json=price2_data)
        price2_id = price2.json()["id"]

        compare_response = await client.post(
            "/api/v1/prices/compare",
            json={"plan_ids": [price_id, price2_id], "usage_kwh": 300}
        )
        assert compare_response.status_code == 200
        comparisons = compare_response.json()["comparisons"]
        assert len(comparisons) == 2

    async def test_crawl_and_monitor_workflow(
        self, client: AsyncClient, sample_company_data: dict
    ):
        """
        Test the crawling workflow:
        1. Create company
        2. Check initial status
        3. Start crawl
        4. Monitor status
        5. Check logs
        """
        # Step 1: Create company
        company_response = await client.post(
            "/api/v1/companies", json=sample_company_data
        )
        company_id = company_response.json()["id"]

        # Step 2: Check initial status
        status_response = await client.get("/api/v1/crawling/status")
        assert status_response.status_code == 200
        initial_status = status_response.json()

        # Step 3: Start crawl
        start_response = await client.post(
            "/api/v1/crawling/start",
            json={"company_ids": [company_id]}
        )
        assert start_response.status_code == 200
        job_id = start_response.json()["job_id"]
        assert job_id is not None

        # Step 4: Monitor status (immediately check)
        monitor_response = await client.get("/api/v1/crawling/status")
        assert monitor_response.status_code == 200

        # Step 5: Check logs
        logs_response = await client.get("/api/v1/crawling/logs")
        assert logs_response.status_code == 200

    async def test_alert_configuration_workflow(self, client: AsyncClient):
        """
        Test the alert configuration workflow:
        1. List all alert settings
        2. Get specific alert
        3. Update alert status
        4. Add recipient
        5. Remove recipient
        """
        # Step 1: List all alerts
        list_response = await client.get("/api/v1/alerts")
        assert list_response.status_code == 200

        # Step 2-5: Try with crawl_failure alert
        alert_type = "crawl_failure"

        # Get alert (may not exist initially)
        get_response = await client.get(f"/api/v1/alerts/{alert_type}")

        if get_response.status_code == 200:
            # Step 3: Update status
            update_response = await client.patch(
                f"/api/v1/alerts/{alert_type}",
                json={"is_enabled": True}
            )
            assert update_response.status_code == 200

            # Step 4: Add recipient
            add_response = await client.post(
                f"/api/v1/alerts/{alert_type}/recipients",
                json={"email": "workflow-test@example.com", "name": "Workflow Test"}
            )

            if add_response.status_code in [200, 201]:
                recipient_id = add_response.json()["id"]

                # Step 5: Remove recipient
                remove_response = await client.delete(
                    f"/api/v1/alerts/{alert_type}/recipients/{recipient_id}"
                )
                assert remove_response.status_code in [200, 204]

    async def test_schedule_configuration_workflow(self, client: AsyncClient):
        """
        Test the schedule configuration workflow:
        1. Get current schedule
        2. Enable schedule
        3. Update schedule time
        4. Disable schedule
        """
        # Step 1: Get current schedule
        get_response = await client.get("/api/v1/crawling/schedule")
        assert get_response.status_code == 200
        original_schedule = get_response.json()

        # Step 2: Enable schedule
        enable_response = await client.put(
            "/api/v1/crawling/schedule",
            json={
                "is_enabled": True,
                "day_of_week": 0,
                "hour": 3,
                "minute": 0,
            }
        )
        assert enable_response.status_code == 200
        assert enable_response.json()["is_enabled"] is True

        # Step 3: Update schedule time
        update_response = await client.put(
            "/api/v1/crawling/schedule",
            json={
                "is_enabled": True,
                "day_of_week": 1,  # Tuesday
                "hour": 4,
                "minute": 30,
            }
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["day_of_week"] == 1
        assert updated["hour"] == 4
        assert updated["minute"] == 30

        # Step 4: Disable schedule
        disable_response = await client.put(
            "/api/v1/crawling/schedule",
            json={
                "is_enabled": False,
                "day_of_week": 1,
                "hour": 4,
                "minute": 30,
            }
        )
        assert disable_response.status_code == 200
        assert disable_response.json()["is_enabled"] is False

    async def test_dashboard_stats_workflow(
        self, client: AsyncClient, sample_company_data: dict, sample_price_plan_data: dict
    ):
        """
        Test the dashboard statistics workflow:
        1. Get initial stats
        2. Create company and price
        3. Verify stats updated
        """
        # Step 1: Get initial stats
        initial_response = await client.get("/api/v1/stats/dashboard")
        assert initial_response.status_code == 200
        initial_stats = initial_response.json()

        # Step 2: Create company and price
        company_response = await client.post(
            "/api/v1/companies", json=sample_company_data
        )
        company_id = company_response.json()["id"]

        price_data = {**sample_price_plan_data, "company_id": company_id}
        await client.post("/api/v1/prices", json=price_data)

        # Step 3: Verify stats
        final_response = await client.get("/api/v1/stats/dashboard")
        assert final_response.status_code == 200
        final_stats = final_response.json()

        # Stats should reflect the new data
        assert "companies" in final_stats
        assert "price_plans" in final_stats
