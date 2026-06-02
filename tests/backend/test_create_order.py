"""
Tests for the POST /api/orders endpoint (restock order submission).
"""
from datetime import datetime

import pytest


@pytest.fixture
def restock_payload():
    """Sample restock order request body."""
    return {
        "items": [
            {"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 150, "unit_price": 12.5},
            {"sku": "BRG-102", "name": "Precision Bearing", "quantity": 40, "unit_price": 30.0},
        ]
    }


class TestCreateOrderEndpoint:
    """Test suite for submitting restock orders."""

    def test_create_order_returns_201(self, client, restock_payload):
        """Submitting a valid restock order returns 201 with a full order body."""
        response = client.post("/api/orders", json=restock_payload)
        assert response.status_code == 201

        order = response.json()
        for field in (
            "id", "order_number", "customer", "items", "status",
            "order_date", "expected_delivery", "total_value",
        ):
            assert field in order

    def test_create_order_status_is_submitted(self, client, restock_payload):
        """New restock orders are created with the 'Submitted' status."""
        response = client.post("/api/orders", json=restock_payload)
        assert response.json()["status"] == "Submitted"

    def test_create_order_number_uses_rst_prefix(self, client, restock_payload):
        """Restock orders get an RST-prefixed order number to distinguish them."""
        response = client.post("/api/orders", json=restock_payload)
        assert response.json()["order_number"].startswith("RST-")

    def test_create_order_default_customer(self, client, restock_payload):
        """When no customer is supplied, it defaults to 'Internal Restock'."""
        response = client.post("/api/orders", json=restock_payload)
        assert response.json()["customer"] == "Internal Restock"

    def test_create_order_lead_time_is_14_days(self, client, restock_payload):
        """Expected delivery is exactly the 14-day lead time after the order date."""
        response = client.post("/api/orders", json=restock_payload)
        order = response.json()

        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        lead_days = (expected_delivery - order_date).days
        assert lead_days == 14

    def test_create_order_total_value_calculation(self, client, restock_payload):
        """total_value equals the sum of quantity * unit_price across items."""
        response = client.post("/api/orders", json=restock_payload)
        order = response.json()

        expected_total = sum(
            item["quantity"] * item["unit_price"] for item in restock_payload["items"]
        )
        assert abs(order["total_value"] - expected_total) < 0.01

    def test_submitted_order_appears_in_get_orders(self, client, restock_payload):
        """A submitted order is retrievable via GET /api/orders filtered by status."""
        created = client.post("/api/orders", json=restock_payload).json()

        response = client.get("/api/orders?status=Submitted")
        assert response.status_code == 200

        submitted = response.json()
        assert isinstance(submitted, list)
        assert any(o["id"] == created["id"] for o in submitted)
        # Every returned order really is Submitted
        for order in submitted:
            assert order["status"].lower() == "submitted"

    def test_submitted_order_retrievable_by_id(self, client, restock_payload):
        """The created order can be fetched individually by its new id."""
        created = client.post("/api/orders", json=restock_payload).json()

        response = client.get(f"/api/orders/{created['id']}")
        assert response.status_code == 200
        assert response.json()["order_number"] == created["order_number"]

    def test_create_order_empty_items_rejected(self, client):
        """An order with no items is rejected with a 400."""
        response = client.post("/api/orders", json={"items": []})
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_create_order_missing_items_validation_error(self, client):
        """A request body missing the required 'items' field returns 422."""
        response = client.post("/api/orders", json={})
        assert response.status_code == 422
