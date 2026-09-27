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

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1

    assert len(data["items"]) == 1

    product = data["items"][0]

    assert product["name"] == "Laptop"
    assert product["price"] == 1500
    assert product["stock"] == 10


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

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1

    assert len(data["items"]) == 1

    product = data["items"][0]

    assert product["name"] == "Gaming Laptop"
    assert product["price"] == 2000
    assert product["stock"] == 5


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

def test_list_products(client):
    client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1

    assert len(data["items"]) == 1

    product = data["items"][0]

    assert product["name"] == "Laptop"
    assert product["price"] == 1500
    assert product["stock"] == 10


def test_list_products_pagination(client):
    for i in range(5):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
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


def test_list_products_second_page(client):
    for i in range(5):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
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


def test_list_products_page_beyond_last_page(client):
    for i in range(3):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
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


def test_list_products_filter_by_search(client):
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

    response = client.get(
        "/products/",
        params={"search": "Laptop"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Gaming Laptop"


def test_list_products_search_case_insensitive(client):
    client.post(
        "/products",
        json={
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
    )

    response = client.get(
        "/products/",
        params={"search": "lApToP"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Gaming Laptop"


def test_list_products_filter_by_min_price(client):
    prices = [100, 500, 1000]

    for i, price in enumerate(prices):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={"min_price": 500},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["price"] >= 500


def test_list_products_filter_by_max_price(client):
    prices = [100, 500, 1000]

    for i, price in enumerate(prices):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={"max_price": 500},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["price"] <= 500


def test_list_products_filter_by_price_range(client):
    prices = [100, 500, 1000, 1500]

    for i, price in enumerate(prices):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={
            "min_price": 500,
            "max_price": 1000,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert 500 <= product["price"] <= 1000


def test_list_products_invalid_price_range(client):
    response = client.get(
        "/products/",
        params={
            "min_price": 1000,
            "max_price": 500,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "min_price cannot be greater than max_price"
    )


def test_list_products_filter_by_min_stock(client):
    stocks = [0, 5, 10]

    for i, stock in enumerate(stocks):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = client.get(
        "/products/",
        params={"min_stock": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["stock"] >= 5


def test_list_products_filter_by_max_stock(client):
    stocks = [0, 5, 10]

    for i, stock in enumerate(stocks):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = client.get(
        "/products/",
        params={"max_stock": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["stock"] <= 5


def test_list_products_filter_by_stock_range(client):
    stocks = [0, 5, 10, 15]

    for i, stock in enumerate(stocks):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = client.get(
        "/products/",
        params={
            "min_stock": 5,
            "max_stock": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert 5 <= product["stock"] <= 10


def test_list_products_invalid_stock_range(client):
    response = client.get(
        "/products/",
        params={
            "min_stock": 10,
            "max_stock": 5,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "min_stock cannot be greater than max_stock"
    )


def test_list_products_combined_filters(client):
    products = [
        {
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
        {
            "name": "Office Laptop",
            "price": 1000,
            "stock": 20,
        },
        {
            "name": "Gaming Mouse",
            "price": 500,
            "stock": 5,
        },
        {
            "name": "Office Chair",
            "price": 800,
            "stock": 10,
        },
    ]

    for product in products:
        client.post("/products", json=product)

    response = client.get(
        "/products/",
        params={
            "search": "Laptop",
            "min_price": 1500,
            "max_price": 2500,
            "min_stock": 1,
            "max_stock": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    product = data["items"][0]

    assert product["name"] == "Gaming Laptop"
    assert product["price"] == 2000
    assert product["stock"] == 5


def test_list_products_no_results(client):
    client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    response = client.get(
        "/products/",
        params={"search": "NonExistingProduct"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10


def test_list_products_invalid_page(client):
    response = client.get(
        "/products/",
        params={"page": 0},
    )

    assert response.status_code == 422


def test_list_products_invalid_limit_zero(client):
    response = client.get(
        "/products/",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_list_products_invalid_limit_too_large(client):
    response = client.get(
        "/products/",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_list_products_sort_by_price_asc(client):
    prices = [1000, 100, 500]

    for i, price in enumerate(prices):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={
            "sort_by": "price",
            "sort_order": "asc",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert [product["price"] for product in data["items"]] == [
        100,
        500,
        1000,
    ]


def test_list_products_sort_by_price_desc(client):
    prices = [1000, 100, 500]

    for i, price in enumerate(prices):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={
            "sort_by": "price",
            "sort_order": "desc",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert [product["price"] for product in data["items"]] == [
        1000,
        500,
        100,
    ]


def test_list_products_sort_by_stock(client):
    stocks = [20, 5, 10]

    for i, stock in enumerate(stocks):
        client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = client.get(
        "/products/",
        params={
            "sort_by": "stock",
            "sort_order": "asc",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert [product["stock"] for product in data["items"]] == [
        5,
        10,
        20,
    ]


def test_list_products_sort_by_name(client):
    names = ["Mouse", "Laptop", "Keyboard"]

    for name in names:
        client.post(
            "/products",
            json={
                "name": name,
                "price": 100,
                "stock": 10,
            },
        )

    response = client.get(
        "/products/",
        params={
            "sort_by": "name",
            "sort_order": "asc",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert [product["name"] for product in data["items"]] == [
        "Keyboard",
        "Laptop",
        "Mouse",
    ]


def test_list_products_invalid_sort_by(client):
    response = client.get(
        "/products/",
        params={"sort_by": "invalid"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_by. Allowed values: id, name, price, stock"
    )


def test_list_products_invalid_sort_order(client):
    response = client.get(
        "/products/",
        params={"sort_order": "invalid"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_order. Allowed values: asc, desc"
    )