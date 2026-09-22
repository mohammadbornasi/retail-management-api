def test_create_product(client):
    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert data["name"] == "Laptop"
    assert data["price"] == 1500
    assert data["stock"] == 10


def test_get_products(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Laptop"
    assert data[0]["price"] == 1500
    assert data[0]["stock"] == 10


def test_get_product(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Laptop"
    assert data["price"] == 1500
    assert data["stock"] == 10


def test_get_product_not_found(client):
    response = client.get("/products/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_update_product(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={
            "name": "Updated Laptop",
            "price": 1800,
            "stock": 15,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Updated Laptop"
    assert data["price"] == 1800
    assert data["stock"] == 15


def test_update_product_not_found(client):
    response = client.put(
        "/products/9999",
        json={
            "name": "Updated Laptop",
            "price": 1800,
            "stock": 15,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_delete_product(client):
    create_response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Product deleted successfully"
    }

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Product not found"
    }


def test_delete_product_not_found(client):
    response = client.delete("/products/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_search_products(client):
    client.post(
        "/products",
        json={
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Office Chair",
            "price": 300,
            "stock": 10,
        },
    )

    response = client.get("/products?search=laptop")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Gaming Laptop"


def test_low_stock_products(client):
    client.post(
        "/products",
        json={
            "name": "Low Stock Product",
            "price": 100,
            "stock": 3,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Normal Stock Product",
            "price": 200,
            "stock": 10,
        },
    )

    response = client.get("/products/low-stock?threshold=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Low Stock Product"
    assert data[0]["stock"] == 3


def test_create_product_invalid_price(client):
    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": -100,
            "stock": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_invalid_stock(client):
    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": -1,
        },
    )

    assert response.status_code == 422


def test_create_product_empty_name(client):
    response = client.post(
        "/products",
        json={
            "name": "",
            "price": 1500,
            "stock": 10,
        },
    )

    assert response.status_code == 422