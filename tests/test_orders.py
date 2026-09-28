import pytest
from models import Product


@pytest.fixture
def auth_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


def update_order_status(client, order_id, status):
    return client.patch(
        f"/orders/{order_id}/status",
        params={
            "new_status": status,
        },
    )


def create_customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert response.status_code == 200

    return response.json()["id"]


def create_product(
    client,
    name="Laptop",
    price=1500,
    stock=10,
):
    response = client.post(
        "/products",
        json={
            "name": name,
            "price": price,
            "stock": stock,
        },
    )

    assert response.status_code == 200

    return response.json()["id"]


def create_order(
    client,
    customer_id,
    product_id,
    quantity=2,
):
    response = client.post(
        "/orders",
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

    return response.json()


def test_create_order(auth_client):
    customer_id = create_customer(auth_client)
    product_id = create_product(
        auth_client,
        price=1500,
        stock=10,
    )

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["order_id"], int)
    assert data["order_id"] > 0
    assert data["customer_id"] == customer_id
    assert data["total_price"] == 3000
    assert data["status"] == "pending"
    assert data["message"] == "Order created successfully"


def test_create_order_multiple_items(auth_client):
    customer_id = create_customer(auth_client)

    product_1 = create_product(
        auth_client,
        name="Laptop",
        price=1500,
        stock=10,
    )

    product_2 = create_product(
        auth_client,
        name="Mouse",
        price=50,
        stock=20,
    )

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_1,
                    "quantity": 2,
                },
                {
                    "product_id": product_2,
                    "quantity": 3,
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == customer_id
    assert data["total_price"] == 3150
    assert data["status"] == "pending"


def test_create_order_customer_not_found(auth_client):
    product_id = create_product(auth_client)

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": 9999,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }


def test_create_order_product_not_found(auth_client):
    customer_id = create_customer(auth_client)

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": 9999,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product 9999 not found"
    }


def test_create_order_without_items(auth_client):
    customer_id = create_customer(auth_client)

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Order must contain at least one item"
    }


def test_create_order_invalid_quantity(auth_client):
    customer_id = create_customer(auth_client)
    product_id = create_product(auth_client)

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 0,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_create_order_negative_quantity(auth_client):
    customer_id = create_customer(auth_client)
    product_id = create_product(auth_client)

    response = auth_client.post(
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": -1,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_create_order_does_not_reduce_stock(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=3,
    )

    response = auth_client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["stock"] == 10


def test_get_order(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=1500,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["customer_id"] == customer_id
    assert data["total_price"] == 3000
    assert data["status"] == "pending"

    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["product_id"] == product_id
    assert item["quantity"] == 2
    assert item["unit_price"] == 1500
    assert item["item_total"] == 3000


def test_get_order_not_found(auth_client):
    response = auth_client.get("/orders/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order not found"
    }


def test_order_item_price_is_snapshot(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    update_response = auth_client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Product",
            "price": 200,
            "stock": 10,
        },
    )

    assert update_response.status_code == 200

    response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_price"] == 200

    item = data["items"][0]

    assert item["unit_price"] == 100
    assert item["item_total"] == 200


def test_add_order_item(auth_client):
    customer_id = create_customer(auth_client)

    product_1 = create_product(
        auth_client,
        name="Laptop",
        price=1500,
        stock=10,
    )

    product_2 = create_product(
        auth_client,
        name="Mouse",
        price=50,
        stock=20,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_1,
        quantity=1,
    )

    order_id = order["order_id"]

    response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": product_2,
            "quantity": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["product_id"] == product_2
    assert data["quantity"] == 3
    assert data["unit_price"] == 50
    assert data["item_total"] == 150
    assert data["total_price"] == 1650


def test_add_existing_order_item_increases_quantity(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": product_id,
            "quantity": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["quantity"] == 5
    assert data["unit_price"] == 100
    assert data["item_total"] == 500
    assert data["total_price"] == 500


def test_add_existing_order_item_keeps_original_price(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    update_response = auth_client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Product",
            "price": 200,
            "stock": 10,
        },
    )

    assert update_response.status_code == 200

    response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": product_id,
            "quantity": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity"] == 5
    assert data["unit_price"] == 100
    assert data["item_total"] == 500
    assert data["total_price"] == 500


def test_add_order_item_order_not_found(auth_client):
    product_id = create_product(auth_client)

    response = auth_client.post(
        "/orders/9999/items",
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order not found"
    }


def test_add_order_item_product_not_found(auth_client):
    customer_id = create_customer(auth_client)

    order = create_order(
        auth_client,
        customer_id,
        create_product(auth_client),
        quantity=1,
    )

    order_id = order["order_id"]

    response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": 9999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product 9999 not found"
    }


def test_update_order_item(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/items/{product_id}",
        json={
            "quantity": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["quantity"] == 5
    assert data["unit_price"] == 100
    assert data["item_total"] == 500
    assert data["total_price"] == 500


def test_update_order_item_not_found(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(auth_client)

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    order_id = order["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/items/9999",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order item not found"
    }


def test_update_order_item_order_not_found(auth_client):
    response = auth_client.patch(
        "/orders/9999/items/1",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order not found"
    }


def test_update_order_item_invalid_quantity(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(auth_client)

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    order_id = order["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/items/{product_id}",
        json={
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_delete_order_item(auth_client):
    customer_id = create_customer(auth_client)

    product_1 = create_product(
        auth_client,
        name="Laptop",
        price=1500,
        stock=10,
    )

    product_2 = create_product(
        auth_client,
        name="Mouse",
        price=50,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_1,
        quantity=2,
    )

    order_id = order["order_id"]

    add_response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": product_2,
            "quantity": 2,
        },
    )

    assert add_response.status_code == 200

    response = auth_client.delete(
        f"/orders/{order_id}/items/{product_2}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["total_price"] == 3000
    assert data["status"] == "pending"
    assert data["message"] == "Order item deleted successfully"

    order_response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert order_response.status_code == 200

    order_data = order_response.json()

    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["product_id"] == product_1


def test_delete_order_item_not_found(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(auth_client)

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    order_id = order["order_id"]

    response = auth_client.delete(
        f"/orders/{order_id}/items/9999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order item not found"
    }


def test_delete_order_item_order_not_found(auth_client):
    response = auth_client.delete(
        "/orders/9999/items/1"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order not found"
    }


def test_confirm_order_reduces_stock(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=3,
    )

    order_id = order["order_id"]

    response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "confirmed"
    assert data["order_id"] == order_id

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.status_code == 200

    product_data = product_response.json()

    assert product_data["stock"] == 7


def test_confirm_order_insufficient_stock(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=2,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=5,
    )

    order_id = order["order_id"]

    response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            f"Not enough stock for product {product_id}. "
            "Available: 2, requested: 5"
        )
    }

    order_response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert order_response.status_code == 200
    assert order_response.json()["status"] == "pending"

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.status_code == 200
    assert product_response.json()["stock"] == 2


def test_confirm_order_product_not_found(auth_client, db):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    assert product is not None

    db.delete(product)
    db.commit()

    response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Product {product_id} not found"
    }

    order_response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert order_response.status_code == 200
    assert order_response.json()["status"] == "pending"


def test_cancel_confirmed_order_product_not_found(auth_client, db):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    confirm_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert confirm_response.status_code == 200

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    assert product is not None

    db.delete(product)
    db.commit()

    response = update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Product {product_id} not found"
    }

    order_response = auth_client.get(
        f"/orders/{order_id}"
    )

    assert order_response.status_code == 200
    assert order_response.json()["status"] == "confirmed"


def test_confirm_order_does_not_reduce_stock_twice(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=3,
    )

    order_id = order["order_id"]

    first_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert first_response.status_code == 200

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 7

    second_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert second_response.status_code == 400

    assert second_response.json() == {
        "detail": "Order is already confirmed"
    }

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 7


def test_cancel_pending_order_does_not_change_stock(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=3,
    )

    order_id = order["order_id"]

    response = update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 10


def test_cancel_confirmed_order_restores_stock(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=3,
    )

    order_id = order["order_id"]

    confirm_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert confirm_response.status_code == 200

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 7

    cancel_response = update_order_status(
        auth_client,
        order_id,
        "cancelled",
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 10


def test_invalid_order_status_transition(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(auth_client)

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    order_id = order["order_id"]

    response = update_order_status(
        auth_client,
        order_id,
        "shipped",
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": (
            "Cannot change order status "
            "from pending to shipped"
        )
    }


def test_order_status_not_found(auth_client):
    response = update_order_status(
        auth_client,
        9999,
        "confirmed",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_order_status_full_valid_transition(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    statuses = [
        "confirmed",
        "processing",
        "shipped",
        "delivered",
    ]

    for status in statuses:
        response = update_order_status(
            auth_client,
            order_id,
            status,
        )

        assert response.status_code == 200
        assert response.json()["status"] == status

    product_response = auth_client.get(
        f"/products/{product_id}"
    )

    assert product_response.json()["stock"] == 8


def test_order_items_cannot_be_added_after_confirmation(auth_client):
    customer_id = create_customer(auth_client)

    product_1 = create_product(
        auth_client,
        name="Laptop",
        price=1500,
        stock=10,
    )

    product_2 = create_product(
        auth_client,
        name="Mouse",
        price=50,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_1,
        quantity=1,
    )

    order_id = order["order_id"]

    confirm_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert confirm_response.status_code == 200

    response = auth_client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": product_2,
            "quantity": 1,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Items can only be added to pending orders"
    }


def test_order_items_cannot_be_updated_after_confirmation(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    confirm_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert confirm_response.status_code == 200

    response = auth_client.patch(
        f"/orders/{order_id}/items/{product_id}",
        json={
            "quantity": 5,
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Items can only be updated in pending orders"
    }


def test_order_items_cannot_be_deleted_after_confirmation(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        price=100,
        stock=10,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    order_id = order["order_id"]

    confirm_response = update_order_status(
        auth_client,
        order_id,
        "confirmed",
    )

    assert confirm_response.status_code == 200

    response = auth_client.delete(
        f"/orders/{order_id}/items/{product_id}"
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Items can only be deleted from pending orders"
    }


def test_confirm_order_creates_sale_inventory_transaction(auth_client):
    customer_response = auth_client.post(
        "/customers/",
        json={
            "name": "Ali",
            "email": "ali@example.com",
            "phone": "09120000000",
        },
    )

    customer_id = customer_response.json()["id"]

    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Keyboard",
            "price": 50,
            "stock": 10,
        },
    )

    product_id = product_response.json()["id"]

    order_response = auth_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                }
            ],
        },
    )

    assert order_response.status_code == 200

    order_id = order_response.json()["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={"new_status": "confirmed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 7

    inventory_response = auth_client.get(
        f"/products/{product_id}/inventory"
    )

    assert inventory_response.status_code == 200

    transactions = inventory_response.json()

    assert len(transactions) == 1
    assert transactions[0]["quantity"] == -3
    assert transactions[0]["transaction_type"] == "sale"
    assert transactions[0]["reason"] == f"Order {order_id} confirmed"


def test_cancel_confirmed_order_creates_cancel_transaction(auth_client):
    customer_response = auth_client.post(
        "/customers/",
        json={
            "name": "Reza",
            "email": "reza@example.com",
            "phone": "09121111111",
        },
    )

    customer_id = customer_response.json()["id"]

    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Mouse",
            "price": 20,
            "stock": 10,
        },
    )

    product_id = product_response.json()["id"]

    order_response = auth_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 4,
                }
            ],
        },
    )

    order_id = order_response.json()["order_id"]

    confirm_response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={"new_status": "confirmed"},
    )

    assert confirm_response.status_code == 200

    cancel_response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={"new_status": "cancelled"},
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 10

    inventory_response = auth_client.get(
        f"/products/{product_id}/inventory"
    )

    transactions = inventory_response.json()

    assert len(transactions) == 2

    assert transactions[0]["quantity"] == 4
    assert transactions[0]["transaction_type"] == "order_cancelled"

    assert transactions[1]["quantity"] == -4
    assert transactions[1]["transaction_type"] == "sale"


def test_confirm_order_with_insufficient_stock_creates_no_inventory_transaction(
    auth_client,
):
    customer_response = auth_client.post(
        "/customers/",
        json={
            "name": "Hassan",
            "email": "hassan@example.com",
            "phone": "09122222222",
        },
    )

    customer_id = customer_response.json()["id"]

    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Monitor",
            "price": 200,
            "stock": 2,
        },
    )

    product_id = product_response.json()["id"]

    order_response = auth_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 5,
                }
            ],
        },
    )

    order_id = order_response.json()["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={"new_status": "confirmed"},
    )

    assert response.status_code == 400
    assert "Not enough stock" in response.json()["detail"]

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 2

    inventory_response = auth_client.get(
        f"/products/{product_id}/inventory"
    )

    assert inventory_response.status_code == 200
    assert inventory_response.json() == []


def test_pending_order_cancellation_creates_no_inventory_transaction(
    auth_client,
):
    customer_response = auth_client.post(
        "/customers/",
        json={
            "name": "Mehdi",
            "email": "mehdi@example.com",
            "phone": "09123333333",
        },
    )

    customer_id = customer_response.json()["id"]

    product_response = auth_client.post(
        "/products/",
        json={
            "name": "Headset",
            "price": 30,
            "stock": 8,
        },
    )

    product_id = product_response.json()["id"]

    order_response = auth_client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                }
            ],
        },
    )

    order_id = order_response.json()["order_id"]

    response = auth_client.patch(
        f"/orders/{order_id}/status",
        params={"new_status": "cancelled"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    product = auth_client.get(
        f"/products/{product_id}"
    ).json()

    assert product["stock"] == 8

    inventory_response = auth_client.get(
        f"/products/{product_id}/inventory"
    )

    assert inventory_response.status_code == 200
    assert inventory_response.json() == []


def test_list_orders(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=1500,
        stock=10,
    )

    create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    response = auth_client.get("/orders/")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "pages" in data

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1

    assert len(data["items"]) == 1

    order = data["items"][0]

    assert order["order_id"] > 0
    assert order["customer_id"] == customer_id
    assert order["total_price"] == 3000
    assert order["status"] == "pending"


def test_list_orders_pagination(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=100,
        stock=100,
    )

    for _ in range(5):
        create_order(
            auth_client,
            customer_id,
            product_id,
            quantity=1,
        )

    response = auth_client.get(
        "/orders/",
        params={
            "page": 1,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3
    assert len(data["items"]) == 2


def test_list_orders_second_page(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=100,
        stock=100,
    )

    for _ in range(5):
        create_order(
            auth_client,
            customer_id,
            product_id,
            quantity=1,
        )

    response = auth_client.get(
        "/orders/",
        params={
            "page": 2,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["pages"] == 3
    assert len(data["items"]) == 2


def test_list_orders_page_beyond_last_page(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=100,
        stock=100,
    )

    for _ in range(3):
        create_order(
            auth_client,
            customer_id,
            product_id,
            quantity=1,
        )

    response = auth_client.get(
        "/orders/",
        params={
            "page": 10,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 10
    assert data["limit"] == 2
    assert data["total"] == 3
    assert data["pages"] == 2
    assert data["items"] == []


def test_list_orders_filter_by_customer_id(auth_client):
    customer_1 = create_customer(auth_client)

    customer_2_response = auth_client.post(
        "/customers/",
        json={
            "name": "Reza Ahmadi",
            "email": "reza@example.com",
            "phone": "09121111111",
        },
    )

    assert customer_2_response.status_code == 200

    customer_2 = customer_2_response.json()["id"]

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=100,
        stock=100,
    )

    create_order(
        auth_client,
        customer_1,
        product_id,
        quantity=1,
    )

    create_order(
        auth_client,
        customer_2,
        product_id,
        quantity=2,
    )

    response = auth_client.get(
        "/orders/",
        params={
            "customer_id": customer_2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["customer_id"] == customer_2
    assert data["items"][0]["total_price"] == 200


def test_list_orders_filter_by_status(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Laptop",
        price=100,
        stock=100,
    )

    pending_order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    confirmed_order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=2,
    )

    confirm_response = update_order_status(
        auth_client,
        confirmed_order["order_id"],
        "confirmed",
    )

    assert confirm_response.status_code == 200

    response = auth_client.get(
        "/orders/",
        params={
            "status": "confirmed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    order = data["items"][0]

    assert order["order_id"] == confirmed_order["order_id"]
    assert order["status"] == "confirmed"

    assert order["order_id"] != pending_order["order_id"]


def test_list_orders_filter_by_product_name(auth_client):
    customer_id = create_customer(auth_client)

    laptop_id = create_product(
        auth_client,
        name="Gaming Laptop",
        price=1500,
        stock=20,
    )

    mouse_id = create_product(
        auth_client,
        name="Wireless Mouse",
        price=50,
        stock=20,
    )

    laptop_order = create_order(
        auth_client,
        customer_id,
        laptop_id,
        quantity=1,
    )

    create_order(
        auth_client,
        customer_id,
        mouse_id,
        quantity=2,
    )

    response = auth_client.get(
        "/orders/",
        params={
            "product_name": "Laptop",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    order = data["items"][0]

    assert order["order_id"] == laptop_order["order_id"]
    assert order["total_price"] == 1500


def test_list_orders_product_name_case_insensitive(auth_client):
    customer_id = create_customer(auth_client)

    product_id = create_product(
        auth_client,
        name="Gaming Laptop",
        price=1500,
        stock=20,
    )

    order = create_order(
        auth_client,
        customer_id,
        product_id,
        quantity=1,
    )

    response = auth_client.get(
        "/orders/",
        params={
            "product_name": "lApToP",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["order_id"] == order["order_id"]


def test_list_orders_combined_filters(auth_client):
    customer_1 = create_customer(auth_client)

    customer_2_response = auth_client.post(
        "/customers/",
        json={
            "name": "Reza Ahmadi",
            "email": "reza@example.com",
            "phone": "09121111111",
        },
    )

    assert customer_2_response.status_code == 200

    customer_2 = customer_2_response.json()["id"]

    laptop_id = create_product(
        auth_client,
        name="Gaming Laptop",
        price=1500,
        stock=20,
    )

    mouse_id = create_product(
        auth_client,
        name="Wireless Mouse",
        price=50,
        stock=20,
    )

    create_order(
        auth_client,
        customer_1,
        laptop_id,
        quantity=1,
    )

    target_order = create_order(
        auth_client,
        customer_2,
        laptop_id,
        quantity=2,
    )

    create_order(
        auth_client,
        customer_2,
        mouse_id,
        quantity=1,
    )

    response = auth_client.get(
        "/orders/",
        params={
            "customer_id": customer_2,
            "status": "pending",
            "product_name": "Laptop",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    order = data["items"][0]

    assert order["order_id"] == target_order["order_id"]
    assert order["customer_id"] == customer_2
    assert order["status"] == "pending"
    assert order["total_price"] == 3000


def test_list_orders_invalid_page(auth_client):
    response = auth_client.get(
        "/orders/",
        params={
            "page": 0,
        },
    )

    assert response.status_code == 422


def test_list_orders_invalid_limit_zero(auth_client):
    response = auth_client.get(
        "/orders/",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_list_orders_invalid_limit_too_large(auth_client):
    response = auth_client.get(
        "/orders/",
        params={
            "limit": 101,
        },
    )

    assert response.status_code == 422


def test_list_orders_no_results(auth_client):
    response = auth_client.get(
        "/orders/",
        params={
            "product_name": "NonExistingProduct",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10


# ---------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------


def test_create_order_requires_authentication(client):
    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 401


def test_list_orders_requires_authentication(client):
    response = client.get("/orders/")

    assert response.status_code == 401


def test_get_order_requires_authentication(client):
    response = client.get("/orders/1")

    assert response.status_code == 401


def test_update_order_status_requires_authentication(client):
    response = client.patch(
        "/orders/1/status",
        params={
            "new_status": "confirmed",
        },
    )

    assert response.status_code == 401


def test_add_order_item_requires_authentication(client):
    response = client.post(
        "/orders/1/items",
        json={
            "product_id": 1,
            "quantity": 1,
        },
    )

    assert response.status_code == 401


def test_update_order_item_requires_authentication(client):
    response = client.patch(
        "/orders/1/items/1",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 401


def test_delete_order_item_requires_authentication(client):
    response = client.delete(
        "/orders/1/items/1"
    )

    assert response.status_code == 401