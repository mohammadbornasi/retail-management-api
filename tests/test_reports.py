import pytest
from security import create_access_token
from datetime import date, datetime, UTC, timedelta



@pytest.fixture
def auth_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def create_customer(auth_client, index=1):
    response = auth_client.post(
        "/customers/",
        json={
            "name": f"Customer {index}",
            "email": f"customer{index}@example.com",
            "phone": f"091200000{index:02d}",
        },
    )

    assert response.status_code == 200

    return response.json()


def create_product(auth_client, index=1, price=100000, stock=100):
    response = auth_client.post(
        "/products/",
        json={
            "name": f"Product {index}",
            "price": price,
            "stock": stock,
        },
    )

    assert response.status_code == 200

    return response.json()


def create_order(
    auth_client,
    customer_id,
    product_id,
    quantity=1,
):
    if isinstance(customer_id, dict):
        customer_id = customer_id["id"]

    if isinstance(product_id, dict):
        product_id = product_id["id"]

    response = auth_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )

    assert response.status_code == 200

    return response.json()["order_id"]


def update_order_status(auth_client, order_id, new_status):
    response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={
            "new_status": new_status,
        },
    )

    assert response.status_code == 200

    return response.json()


def test_sales_summary_empty(auth_client):
    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 0
    assert data["total_orders"] == 0
    assert data["average_order_value"] == 0
    assert data["total_items_sold"] == 0


def test_sales_summary_confirmed_order(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 200000
    assert data["total_orders"] == 1
    assert data["average_order_value"] == 200000
    assert data["total_items_sold"] == 2


def test_sales_summary_multiple_orders(auth_client):
    customer1 = create_customer(auth_client, index=1)
    customer2 = create_customer(auth_client, index=2)

    product1 = create_product(
        auth_client,
        index=1,
        price=100000,
        stock=100,
    )

    product2 = create_product(
        auth_client,
        index=2,
        price=250000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product1["id"],
        quantity=2,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product2["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order2,
        "confirmed",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 950000
    assert data["total_orders"] == 2
    assert data["average_order_value"] == 475000
    assert data["total_items_sold"] == 5


def test_sales_summary_ignores_pending_orders(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 0
    assert data["total_orders"] == 0
    assert data["average_order_value"] == 0
    assert data["total_items_sold"] == 0


def test_sales_summary_ignores_cancelled_orders(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 0
    assert data["total_orders"] == 0
    assert data["average_order_value"] == 0
    assert data["total_items_sold"] == 0


def test_sales_summary_includes_processing_orders(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=150000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "processing",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 300000
    assert data["total_orders"] == 1
    assert data["average_order_value"] == 300000
    assert data["total_items_sold"] == 2


def test_sales_summary_includes_shipped_orders(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=200000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "processing",
    )

    update_order_status(
        auth_client,
        order_id,
        "shipped",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 400000
    assert data["total_orders"] == 1
    assert data["average_order_value"] == 400000
    assert data["total_items_sold"] == 2


def test_sales_summary_includes_delivered_orders(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=250000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "processing",
    )

    update_order_status(
        auth_client,
        order_id,
        "shipped",
    )

    update_order_status(
        auth_client,
        order_id,
        "delivered",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 500000
    assert data["total_orders"] == 1
    assert data["average_order_value"] == 500000
    assert data["total_items_sold"] == 2


def test_sales_summary_average_order_value_rounding(auth_client):
    customer1 = create_customer(auth_client, index=1)
    customer2 = create_customer(auth_client, index=2)
    customer3 = create_customer(auth_client, index=3)

    product1 = create_product(
        auth_client,
        index=1,
        price=100,
        stock=100,
    )

    product2 = create_product(
        auth_client,
        index=2,
        price=200,
        stock=100,
    )

    product3 = create_product(
        auth_client,
        index=3,
        price=300,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product1["id"],
        quantity=1,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product2["id"],
        quantity=1,
    )

    order3 = create_order(
        auth_client,
        customer_id=customer3["id"],
        product_id=product3["id"],
        quantity=1,
    )

    update_order_status(
        auth_client,
        order1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order2,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order3,
        "confirmed",
    )

    response = auth_client.get("/reports/sales/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 600
    assert data["total_orders"] == 3
    assert data["average_order_value"] == 200
    assert data["total_items_sold"] == 3


def test_sales_summary_from_date(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    today = date.today()

    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "from_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 200000
    assert data["total_orders"] == 1
    assert data["total_items_sold"] == 2


def test_sales_summary_to_date(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    today = date.today()

    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "to_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 200000
    assert data["total_orders"] == 1
    assert data["total_items_sold"] == 2


def test_sales_summary_date_range(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    today = date.today()

    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "from_date": today.isoformat(),
            "to_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 200000
    assert data["total_orders"] == 1
    assert data["average_order_value"] == 200000
    assert data["total_items_sold"] == 2


def test_sales_summary_future_date_range_returns_empty(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    tomorrow = date.today() + timedelta(days=1)

    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "from_date": tomorrow.isoformat(),
            "to_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 0
    assert data["total_orders"] == 0
    assert data["average_order_value"] == 0
    assert data["total_items_sold"] == 0


def test_sales_summary_past_to_date_returns_empty(auth_client):
    customer = create_customer(auth_client)
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    yesterday = date.today() - timedelta(days=1)

    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "to_date": yesterday.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_sales"] == 0
    assert data["total_orders"] == 0
    assert data["average_order_value"] == 0
    assert data["total_items_sold"] == 0


def test_sales_summary_invalid_from_date(auth_client):
    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "from_date": "invalid-date",
        },
    )

    assert response.status_code == 422


def test_sales_summary_invalid_to_date(auth_client):
    response = auth_client.get(
        "/reports/sales/summary",
        params={
            "to_date": "invalid-date",
        },
    )

    assert response.status_code == 422



def test_sales_report_empty(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-03",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == [
        {
            "date": "2026-09-01",
            "total_sales": 0,
            "total_orders": 0,
        },
        {
            "date": "2026-09-02",
            "total_sales": 0,
            "total_orders": 0,
        },
        {
            "date": "2026-09-03",
            "total_sales": 0,
            "total_orders": 0,
        },
    ]

    assert data["page"] == 1
    assert data["limit"] == 30
    assert data["total"] == 3
    assert data["pages"] == 1


def test_sales_report_single_confirmed_order(auth_client):
    customer_id = create_customer(auth_client, 1)
    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 30
    assert data["pages"] == 1

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1

    day = matching_days[0]

    assert day["total_orders"] == 1
    assert day["total_sales"] == 150


def test_sales_report_multiple_orders_same_day(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id_1 = create_product(
        auth_client,
        1,
        price=100,
        stock=100,
    )

    product_id_2 = create_product(
        auth_client,
        2,
        price=200,
        stock=100,
    )

    order_id_1 = create_order(
        auth_client,
        customer_id,
        product_id_1,
        quantity=1,
    )

    order_id_2 = create_order(
        auth_client,
        customer_id,
        product_id_2,
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id_1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id_2,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1

    day = matching_days[0]

    assert day["total_orders"] == 2
    assert day["total_sales"] == 300


def test_sales_report_multiple_sales_days(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=100,
        stock=100,
    )

    order_id_1 = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    order_id_2 = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id_1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id_2,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1

    day = matching_days[0]

    assert day["total_orders"] == 2
    assert day["total_sales"] == 300


def test_sales_report_ignores_pending_orders(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        item["total_orders"] == 0
        for item in data["items"]
    )

    assert all(
        item["total_sales"] == 0
        for item in data["items"]
    )


def test_sales_report_ignores_cancelled_orders(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        item["total_orders"] == 0
        for item in data["items"]
    )

    assert all(
        item["total_sales"] == 0
        for item in data["items"]
    )


def test_sales_report_includes_processing_orders(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "processing",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1
    assert matching_days[0]["total_orders"] == 1
    assert matching_days[0]["total_sales"] == 150


def test_sales_report_includes_shipped_orders(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
    )

    update_order_status(auth_client, order_id, "confirmed")
    update_order_status(auth_client, order_id, "processing")
    update_order_status(auth_client, order_id, "shipped")

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1
    assert matching_days[0]["total_orders"] == 1
    assert matching_days[0]["total_sales"] == 150


def test_sales_report_includes_delivered_orders(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
    )

    update_order_status(auth_client, order_id, "confirmed")
    update_order_status(auth_client, order_id, "processing")
    update_order_status(auth_client, order_id, "shipped")
    update_order_status(auth_client, order_id, "delivered")

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1
    assert matching_days[0]["total_orders"] == 1
    assert matching_days[0]["total_sales"] == 150


def test_sales_report_pagination(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-27",
            "page": 2,
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 10
    assert data["total"] == 27
    assert data["pages"] == 3

    assert len(data["items"]) == 10

    assert data["items"][0]["date"] == "2026-09-11"
    assert data["items"][-1]["date"] == "2026-09-20"


def test_sales_report_pagination_last_page(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-27",
            "page": 3,
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 3
    assert data["limit"] == 10
    assert data["total"] == 27
    assert data["pages"] == 3

    assert len(data["items"]) == 7

    assert data["items"][0]["date"] == "2026-09-21"
    assert data["items"][-1]["date"] == "2026-09-27"


def test_sales_report_page_beyond_last_page(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-27",
            "page": 4,
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 4
    assert data["limit"] == 10
    assert data["total"] == 27
    assert data["pages"] == 3
    assert data["items"] == []


def test_sales_report_limit_validation(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-10",
            "limit": 0,
        },
    )

    assert response.status_code == 422

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-10",
            "limit": 101,
        },
    )

    assert response.status_code == 422


def test_sales_report_page_validation(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-10",
            "page": 0,
        },
    )

    assert response.status_code == 422


def test_sales_report_invalid_from_date(auth_client):
    response = auth_client.get(
        "/reports/sales?from_date=invalid-date&to_date=2026-09-10"
    )

    assert response.status_code == 422


def test_sales_report_invalid_to_date(auth_client):
    response = auth_client.get(
        "/reports/sales?from_date=2026-09-01&to_date=invalid-date"
    )

    assert response.status_code == 422


def test_sales_report_from_date_filter(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
    )

    today = datetime.now(UTC).date()

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": today.isoformat(),
            "to_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"] == [
        {
            "date": today.isoformat(),
            "total_sales": 150,
            "total_orders": 1,
        }
    ]


def test_sales_report_to_date_filter(auth_client):
    customer_id = create_customer(auth_client, 1)

    product_id = create_product(
        auth_client,
        1,
        price=150,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id,
        product_id,
    )

    today = datetime.now(UTC).date()

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 28

    matching_days = [
        item
        for item in data["items"]
        if item["total_orders"] > 0
    ]

    assert len(matching_days) == 1
    assert matching_days[0]["date"] == today.isoformat()


def test_sales_report_date_range(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-10",
            "to_date": "2026-09-15",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 6
    assert data["pages"] == 1
    assert len(data["items"]) == 6

    assert data["items"][0]["date"] == "2026-09-10"
    assert data["items"][-1]["date"] == "2026-09-15"


def test_sales_report_from_date_greater_than_to_date(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-20",
            "to_date": "2026-09-10",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_sales_report_default_pagination(auth_client):
    response = auth_client.get(
        "/reports/sales",
        params={
            "from_date": "2026-09-01",
            "to_date": "2026-09-27",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 30
    assert data["total"] == 27
    assert data["pages"] == 1


# ============================================================
# Top Selling Products Report
# ============================================================


def test_top_selling_products_empty(auth_client):
    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_selling_products_single_product(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["pages"] == 1

    item = data["items"][0]

    assert item["product_id"] == product["id"]
    assert item["product_name"] == product["name"]
    assert item["quantity_sold"] == 3
    assert item["total_sales"] == 300000


def test_top_selling_products_multiple_products(auth_client):
    customer1 = create_customer(auth_client, index=1)
    customer2 = create_customer(auth_client, index=2)
    customer3 = create_customer(auth_client, index=3)

    product1 = create_product(
        auth_client,
        index=1,
        price=100000,
        stock=100,
    )

    product2 = create_product(
        auth_client,
        index=2,
        price=50000,
        stock=100,
    )

    product3 = create_product(
        auth_client,
        index=3,
        price=300000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product1["id"],
        quantity=5,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product2["id"],
        quantity=8,
    )

    order3 = create_order(
        auth_client,
        customer_id=customer3["id"],
        product_id=product3["id"],
        quantity=2,
    )

    update_order_status(auth_client, order1, "confirmed")
    update_order_status(auth_client, order2, "confirmed")
    update_order_status(auth_client, order3, "confirmed")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["pages"] == 1

    assert data["items"][0]["product_id"] == product2["id"]
    assert data["items"][0]["quantity_sold"] == 8

    assert data["items"][1]["product_id"] == product1["id"]
    assert data["items"][1]["quantity_sold"] == 5

    assert data["items"][2]["product_id"] == product3["id"]
    assert data["items"][2]["quantity_sold"] == 2


def test_top_selling_products_multiple_orders_same_product(auth_client):
    customer1 = create_customer(auth_client, index=1)
    customer2 = create_customer(auth_client, index=2)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product["id"],
        quantity=3,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product["id"],
        quantity=7,
    )

    update_order_status(auth_client, order1, "confirmed")
    update_order_status(auth_client, order2, "confirmed")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    item = data["items"][0]

    assert item["product_id"] == product["id"]
    assert item["quantity_sold"] == 10
    assert item["total_sales"] == 1000000


def test_top_selling_products_total_sales(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=275000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=4,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    item = response.json()["items"][0]

    assert item["quantity_sold"] == 4
    assert item["total_sales"] == 1100000


def test_top_selling_products_uses_snapshot_unit_price(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    # Change current product price after order creation.
    update_response = auth_client.put(
        f"/products/{product['id']}",
        json={
            "name": "Keyboard",
            "price": 200000,
            "stock": 100,
        },
    )

    assert update_response.status_code == 200

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    item = response.json()["items"][0]

    # Order was created at 100000, so the report
    # must use the snapshot price.
    assert item["quantity_sold"] == 2
    assert item["total_sales"] == 200000


def test_top_selling_products_ignores_pending_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=5,
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_top_selling_products_ignores_cancelled_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=5,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_top_selling_products_includes_confirmed_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    assert response.json()["items"][0]["quantity_sold"] == 3


def test_top_selling_products_includes_processing_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(auth_client, order_id, "confirmed")
    update_order_status(auth_client, order_id, "processing")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    assert response.json()["items"][0]["quantity_sold"] == 3


def test_top_selling_products_includes_shipped_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(auth_client, order_id, "confirmed")
    update_order_status(auth_client, order_id, "processing")
    update_order_status(auth_client, order_id, "shipped")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    assert response.json()["items"][0]["quantity_sold"] == 3


def test_top_selling_products_includes_delivered_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(auth_client, order_id, "confirmed")
    update_order_status(auth_client, order_id, "processing")
    update_order_status(auth_client, order_id, "shipped")
    update_order_status(auth_client, order_id, "delivered")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    assert response.json()["items"][0]["quantity_sold"] == 3


def test_top_selling_products_pagination(auth_client):
    customer = create_customer(auth_client)

    products = []

    for index in range(1, 6):
        product = create_product(
            auth_client,
            index=index,
            price=100000,
            stock=100,
        )

        products.append(product)

        order_id = create_order(
            auth_client,
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=index,
        )

        update_order_status(
            auth_client,
            order_id,
            "confirmed",
        )

    response = auth_client.get(
        "/reports/products/top-selling?page=1&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3
    assert len(data["items"]) == 2

    assert data["items"][0]["quantity_sold"] == 5
    assert data["items"][1]["quantity_sold"] == 4


def test_top_selling_products_pagination_last_page(auth_client):
    customer = create_customer(auth_client)

    for index in range(1, 6):
        product = create_product(
            auth_client,
            index=index,
            price=100000,
            stock=100,
        )

        order_id = create_order(
            auth_client,
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=index,
        )

        update_order_status(
            auth_client,
            order_id,
            "confirmed",
        )

    response = auth_client.get(
        "/reports/products/top-selling?page=3&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 3
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity_sold"] == 1


def test_top_selling_products_page_beyond_last_page(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/products/top-selling?page=2&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1
    assert data["items"] == []


def test_top_selling_products_limit_validation(auth_client):
    response = auth_client.get(
        "/reports/products/top-selling?limit=0"
    )

    assert response.status_code == 422

    response = auth_client.get(
        "/reports/products/top-selling?limit=101"
    )

    assert response.status_code == 422


def test_top_selling_products_page_validation(auth_client):
    response = auth_client.get(
        "/reports/products/top-selling?page=0"
    )

    assert response.status_code == 422


def test_top_selling_products_from_date_filter(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=4,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    today = datetime.now(UTC).date()

    response = auth_client.get(
        "/reports/products/top-selling",
        params={
            "from_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["quantity_sold"] == 4


def test_top_selling_products_to_date_filter(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=4,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    today = datetime.now(UTC).date()

    response = auth_client.get(
        "/reports/products/top-selling",
        params={
            "to_date": today.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["quantity_sold"] == 4


def test_top_selling_products_future_from_date_returns_empty(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=4,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    future_date = (
        datetime.now(UTC).date()
        + timedelta(days=1)
    )

    response = auth_client.get(
        "/reports/products/top-selling",
        params={
            "from_date": future_date.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_selling_products_past_to_date_returns_empty(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=4,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    past_date = (
        datetime.now(UTC).date()
        - timedelta(days=1)
    )

    response = auth_client.get(
        "/reports/products/top-selling",
        params={
            "to_date": past_date.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_selling_products_invalid_from_date(auth_client):
    response = auth_client.get(
        "/reports/products/top-selling"
        "?from_date=invalid-date"
    )

    assert response.status_code == 422


def test_top_selling_products_invalid_to_date(auth_client):
    response = auth_client.get(
        "/reports/products/top-selling"
        "?to_date=invalid-date"
    )

    assert response.status_code == 422


def test_top_selling_products_equal_quantity_uses_product_id_as_tiebreaker(
    auth_client,
):
    customer1 = create_customer(auth_client, index=1)
    customer2 = create_customer(auth_client, index=2)

    product1 = create_product(
        auth_client,
        index=1,
        price=100000,
        stock=100,
    )

    product2 = create_product(
        auth_client,
        index=2,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product1["id"],
        quantity=5,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product2["id"],
        quantity=5,
    )

    update_order_status(auth_client, order1, "confirmed")
    update_order_status(auth_client, order2, "confirmed")

    response = auth_client.get(
        "/reports/products/top-selling"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    assert data["items"][0]["quantity_sold"] == 5
    assert data["items"][1]["quantity_sold"] == 5

    assert (
        data["items"][0]["product_id"]
        < data["items"][1]["product_id"]
    )


def test_top_customers_empty(auth_client):
    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_customers_single_customer(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["pages"] == 1

    item = data["items"][0]

    assert item["customer_id"] == customer["id"]
    assert item["customer_name"] == customer["name"]
    assert item["total_orders"] == 1
    assert item["total_spent"] == 300000


def test_top_customers_multiple_customers(auth_client):
    customer1 = create_customer(
        auth_client,
        index=1,
    )

    customer2 = create_customer(
        auth_client,
        index=2,
    )

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product["id"],
        quantity=5,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order2,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 2

    assert items[0]["customer_id"] == customer1["id"]
    assert items[0]["total_spent"] == 500000

    assert items[1]["customer_id"] == customer2["id"]
    assert items[1]["total_spent"] == 200000


def test_top_customers_multiple_orders_same_customer(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order1,
        "confirmed",
    )

    update_order_status(
        auth_client,
        order2,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    item = data["items"][0]

    assert item["customer_id"] == customer["id"]
    assert item["total_orders"] == 2
    assert item["total_spent"] == 500000


def test_top_customers_ignores_pending_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_customers_ignores_cancelled_orders(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=3,
    )

    update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_top_customers_includes_all_sales_statuses(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    order3 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    order4 = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    update_order_status(auth_client, order1, "confirmed")

    update_order_status(auth_client, order2, "confirmed")
    update_order_status(auth_client, order2, "processing")

    update_order_status(auth_client, order3, "confirmed")
    update_order_status(auth_client, order3, "processing")
    update_order_status(auth_client, order3, "shipped")

    update_order_status(auth_client, order4, "confirmed")
    update_order_status(auth_client, order4, "processing")
    update_order_status(auth_client, order4, "shipped")
    update_order_status(auth_client, order4, "delivered")

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    item = response.json()["items"][0]

    assert item["total_orders"] == 4
    assert item["total_spent"] == 400000


def test_top_customers_pagination(auth_client):
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    for index in range(1, 6):
        customer = create_customer(
            auth_client,
            index=index,
        )

        order_id = create_order(
            auth_client,
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=index,
        )

        update_order_status(
            auth_client,
            order_id,
            "confirmed",
        )

    response = auth_client.get(
        "/reports/customers/top?page=1&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3

    assert len(data["items"]) == 2

    assert data["items"][0]["total_spent"] == 500000
    assert data["items"][1]["total_spent"] == 400000


def test_top_customers_pagination_last_page(auth_client):
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    for index in range(1, 6):
        customer = create_customer(
            auth_client,
            index=index,
        )

        order_id = create_order(
            auth_client,
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=index,
        )

        update_order_status(
            auth_client,
            order_id,
            "confirmed",
        )

    response = auth_client.get(
        "/reports/customers/top?page=3&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 3
    assert data["pages"] == 3
    assert len(data["items"]) == 1

    assert data["items"][0]["total_spent"] == 100000


def test_top_customers_page_beyond_last_page(auth_client):
    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    customer = create_customer(auth_client)

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top?page=2&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 1
    assert data["pages"] == 1


def test_top_customers_limit_validation(auth_client):
    response = auth_client.get(
        "/reports/customers/top?limit=0"
    )

    assert response.status_code == 422

    response = auth_client.get(
        "/reports/customers/top?limit=101"
    )

    assert response.status_code == 422


def test_top_customers_page_validation(auth_client):
    response = auth_client.get(
        "/reports/customers/top?page=0"
    )

    assert response.status_code == 422


def test_top_customers_from_date_filter(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top?from_date=2099-01-01"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_top_customers_to_date_filter(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top?to_date=2000-01-01"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_top_customers_future_from_date_returns_empty(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top?from_date=2099-01-01"
    )

    assert response.status_code == 200

    assert response.json()["items"] == []


def test_top_customers_past_to_date_returns_empty(auth_client):
    customer = create_customer(auth_client)

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order_id = create_order(
        auth_client,
        customer_id=customer["id"],
        product_id=product["id"],
        quantity=1,
    )

    update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    response = auth_client.get(
        "/reports/customers/top?to_date=2000-01-01"
    )

    assert response.status_code == 200

    assert response.json()["items"] == []


def test_top_customers_invalid_from_date(auth_client):
    response = auth_client.get(
        "/reports/customers/top?from_date=invalid-date"
    )

    assert response.status_code == 422


def test_top_customers_invalid_to_date(auth_client):
    response = auth_client.get(
        "/reports/customers/top?to_date=invalid-date"
    )

    assert response.status_code == 422


def test_top_customers_equal_spent_uses_customer_id_as_tiebreaker(auth_client):
    customer1 = create_customer(
        auth_client,
        index=1,
    )

    customer2 = create_customer(
        auth_client,
        index=2,
    )

    product = create_product(
        auth_client,
        price=100000,
        stock=100,
    )

    order1 = create_order(
        auth_client,
        customer_id=customer1["id"],
        product_id=product["id"],
        quantity=2,
    )

    order2 = create_order(
        auth_client,
        customer_id=customer2["id"],
        product_id=product["id"],
        quantity=2,
    )

    update_order_status(auth_client, order1, "confirmed")
    update_order_status(auth_client, order2, "confirmed")

    response = auth_client.get(
        "/reports/customers/top"
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 2

    assert items[0]["customer_id"] < items[1]["customer_id"]


def test_inventory_summary_empty(auth_client):
    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 0
    assert data["total_stock"] == 0
    assert data["total_inventory_value"] == 0
    assert data["out_of_stock_products"] == 0
    assert data["low_stock_products"] == 0


def test_inventory_summary_single_product(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=10,
    )

    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 1
    assert data["total_stock"] == 10
    assert data["total_inventory_value"] == 1000000
    assert data["out_of_stock_products"] == 0
    assert data["low_stock_products"] == 0


def test_inventory_summary_multiple_products(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=10,
    )

    create_product(
        auth_client,
        price=50000,
        stock=3,
    )

    create_product(
        auth_client,
        price=200000,
        stock=0,
    )

    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 3
    assert data["total_stock"] == 13
    assert data["total_inventory_value"] == 1150000
    assert data["out_of_stock_products"] == 1
    assert data["low_stock_products"] == 2


def test_inventory_summary_inventory_value(auth_client):
    create_product(
        auth_client,
        price=125000,
        stock=8,
    )

    create_product(
        auth_client,
        price=75000,
        stock=4,
    )

    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_inventory_value"] == (
        125000 * 8 + 75000 * 4
    )


def test_inventory_summary_out_of_stock_products(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=0,
    )

    create_product(
        auth_client,
        price=200000,
        stock=0,
    )

    create_product(
        auth_client,
        price=300000,
        stock=5,
    )

    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["out_of_stock_products"] == 2


def test_inventory_summary_low_stock_default_threshold(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=0,
    )

    create_product(
        auth_client,
        price=100000,
        stock=3,
    )

    create_product(
        auth_client,
        price=100000,
        stock=5,
    )

    create_product(
        auth_client,
        price=100000,
        stock=6,
    )

    response = auth_client.get(
        "/reports/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["low_stock_products"] == 3


def test_inventory_summary_custom_low_stock_threshold(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=2,
    )

    create_product(
        auth_client,
        price=100000,
        stock=5,
    )

    create_product(
        auth_client,
        price=100000,
        stock=8,
    )

    response = auth_client.get(
        "/reports/inventory/summary?low_stock_threshold=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["low_stock_products"] == 2


def test_inventory_summary_custom_lower_threshold(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=2,
    )

    create_product(
        auth_client,
        price=100000,
        stock=5,
    )

    create_product(
        auth_client,
        price=100000,
        stock=8,
    )

    response = auth_client.get(
        "/reports/inventory/summary?low_stock_threshold=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["low_stock_products"] == 1


def test_inventory_summary_zero_low_stock_threshold(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=0,
    )

    create_product(
        auth_client,
        price=100000,
        stock=1,
    )

    response = auth_client.get(
        "/reports/inventory/summary?low_stock_threshold=0"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["low_stock_products"] == 1
    assert data["out_of_stock_products"] == 1


def test_inventory_summary_negative_threshold_validation(auth_client):
    response = auth_client.get(
        "/reports/inventory/summary?low_stock_threshold=-1"
    )

    assert response.status_code == 422


def test_inventory_summary_large_threshold(auth_client):
    create_product(
        auth_client,
        price=100000,
        stock=10,
    )

    create_product(
        auth_client,
        price=100000,
        stock=20,
    )

    response = auth_client.get(
        "/reports/inventory/summary?low_stock_threshold=100"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["low_stock_products"] == 2

# ============================================================
# Reports Authorization Tests
# ============================================================


def test_reports_require_authentication(client):
    endpoints = [
        "/reports/sales/summary",
        "/reports/sales",
        "/reports/products/top-selling",
        "/reports/customers/top",
        "/reports/inventory/summary",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_reports_accept_authenticated_user(auth_client):
    endpoints = [
        "/reports/sales/summary",
        "/reports/sales",
        "/reports/products/top-selling",
        "/reports/customers/top",
        "/reports/inventory/summary",
    ]

    for endpoint in endpoints:
        response = auth_client.get(endpoint)
        assert response.status_code == 200


def test_reports_reject_invalid_token(client):
    client.headers.update(
        {
            "Authorization": "Bearer invalid-token"
        }
    )

    response = client.get(
        "/reports/sales/summary"
    )

    assert response.status_code == 401


def test_reports_reject_inactive_user(client, db, test_user):
    test_user.is_active = False
    db.commit()

    token = create_access_token(
        data={
            "sub": test_user.username,
            "user_id": test_user.id,
            "role": test_user.role,
        }
    )

    response = client.get(
        "/reports/sales/summary",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403
