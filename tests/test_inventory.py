import pytest


@pytest.fixture
def auth_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def test_add_inventory(auth_client):
    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Keyboard",
            "price": 50,
            "stock": 10,
        },
    )

    assert product_response.status_code == 200

    product_id = product_response.json()["id"]

    response = auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": 5,
            "transaction_type": "purchase",
            "reason": "New stock",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["quantity"] == 5
    assert data["transaction_type"] == "purchase"
    assert data["reason"] == "New stock"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 15


def test_remove_inventory(auth_client):
    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Mouse",
            "price": 20,
            "stock": 10,
        },
    )

    assert product_response.status_code == 200

    product_id = product_response.json()["id"]

    response = auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": -3,
            "transaction_type": "adjustment",
            "reason": "Damaged item",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity"] == -3
    assert data["transaction_type"] == "adjustment"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 7


def test_inventory_cannot_exceed_stock(auth_client):
    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Monitor",
            "price": 200,
            "stock": 5,
        },
    )

    assert product_response.status_code == 200

    product_id = product_response.json()["id"]

    response = auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": -6,
            "transaction_type": "adjustment",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 5


def test_inventory_product_not_found(auth_client):
    response = auth_client.post(
        "/products/9999/inventory",
        json={
            "quantity": 5,
            "transaction_type": "purchase",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_inventory_quantity_cannot_be_zero(auth_client):
    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Headset",
            "price": 30,
            "stock": 10,
        },
    )

    assert product_response.status_code == 200

    product_id = product_response.json()["id"]

    response = auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": 0,
            "transaction_type": "adjustment",
        },
    )

    assert response.status_code == 422


def test_get_inventory_history(auth_client):
    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Webcam",
            "price": 80,
            "stock": 10,
        },
    )

    assert product_response.status_code == 200

    product_id = product_response.json()["id"]

    auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": 5,
            "transaction_type": "purchase",
            "reason": "First purchase",
        },
    )

    auth_client.post(
        f"/products/{product_id}/inventory",
        json={
            "quantity": -2,
            "transaction_type": "adjustment",
            "reason": "Damaged item",
        },
    )

    response = auth_client.get(
        f"/products/{product_id}/inventory"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["quantity"] == -2
    assert data[0]["transaction_type"] == "adjustment"
    assert data[1]["quantity"] == 5
    assert data[1]["transaction_type"] == "purchase"