def auth_post(client, auth_headers, url, **kwargs):
    return client.post(
        url,
        headers=auth_headers,
        **kwargs,
    )


def auth_get(client, auth_headers, url, **kwargs):
    return client.get(
        url,
        headers=auth_headers,
        **kwargs,
    )


def auth_put(client, auth_headers, url, **kwargs):
    return client.put(
        url,
        headers=auth_headers,
        **kwargs,
    )


def admin_delete(client, admin_headers, url, **kwargs):
    return client.delete(
        url,
        headers=admin_headers,
        **kwargs,
    )


def test_create_product(client, auth_headers):
    response = auth_post(
        client,
        auth_headers,
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


def test_get_products(client, auth_headers):
    create_response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    response = auth_get(
        client,
        auth_headers,
        "/products",
    )

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


def test_get_product(client, auth_headers):
    create_response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = auth_get(
        client,
        auth_headers,
        f"/products/{product_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Laptop"
    assert data["price"] == 1500
    assert data["stock"] == 10


def test_get_product_not_found(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/9999",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_update_product(client, auth_headers):
    create_response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = auth_put(
        client,
        auth_headers,
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


def test_update_product_not_found(client, auth_headers):
    response = auth_put(
        client,
        auth_headers,
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


def test_delete_product(client, auth_headers, admin_headers):
    create_response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = admin_delete(
        client,
        admin_headers,
        f"/products/{product_id}",
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Product deleted successfully"
    }

    get_response = auth_get(
        client,
        auth_headers,
        f"/products/{product_id}",
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Product not found"
    }


def test_delete_product_not_found(client, admin_headers):
    response = admin_delete(
        client,
        admin_headers,
        "/products/9999",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Product not found"
    }


def test_delete_product_requires_admin(client, auth_headers):
    create_response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert create_response.status_code == 200

    product_id = create_response.json()["id"]

    response = client.delete(
        f"/products/{product_id}",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin access required"
    }


def test_create_product_requires_authentication(client):
    response = client.post(
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    assert response.status_code == 401


def test_get_products_requires_authentication(client):
    response = client.get("/products")

    assert response.status_code == 401


def test_delete_product_requires_authentication(client):
    response = client.delete("/products/9999")

    assert response.status_code == 401


def test_search_products(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
    )

    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Office Chair",
            "price": 300,
            "stock": 10,
        },
    )

    response = auth_get(
        client,
        auth_headers,
        "/products?search=laptop",
    )

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


def test_low_stock_products(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Low Stock Product",
            "price": 100,
            "stock": 3,
        },
    )

    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Normal Stock Product",
            "price": 200,
            "stock": 10,
        },
    )

    response = auth_get(
        client,
        auth_headers,
        "/products/low-stock?threshold=5",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Low Stock Product"
    assert data[0]["stock"] == 3


def test_create_product_invalid_price(client, auth_headers):
    response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": -100,
            "stock": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_invalid_stock(client, auth_headers):
    response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": -1,
        },
    )

    assert response.status_code == 422


def test_create_product_empty_name(client, auth_headers):
    response = auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "",
            "price": 1500,
            "stock": 10,
        },
    )

    assert response.status_code == 422


def test_list_products(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
    )

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


def test_list_products_pagination(client, auth_headers):
    for i in range(5):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_second_page(client, auth_headers):
    for i in range(5):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_page_beyond_last_page(client, auth_headers):
    for i in range(3):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100 + i,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_filter_by_search(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
    )

    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Office Chair",
            "price": 300,
            "stock": 10,
        },
    )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"search": "Laptop"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Gaming Laptop"


def test_list_products_search_case_insensitive(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Gaming Laptop",
            "price": 2000,
            "stock": 5,
        },
    )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"search": "lApToP"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Gaming Laptop"


def test_list_products_filter_by_min_price(client, auth_headers):
    prices = [100, 500, 1000]

    for i, price in enumerate(prices):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"min_price": 500},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["price"] >= 500


def test_list_products_filter_by_max_price(client, auth_headers):
    prices = [100, 500, 1000]

    for i, price in enumerate(prices):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"max_price": 500},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["price"] <= 500


def test_list_products_filter_by_price_range(client, auth_headers):
    prices = [100, 500, 1000, 1500]

    for i, price in enumerate(prices):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_invalid_price_range(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_filter_by_min_stock(client, auth_headers):
    stocks = [0, 5, 10]

    for i, stock in enumerate(stocks):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"min_stock": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["stock"] >= 5


def test_list_products_filter_by_max_stock(client, auth_headers):
    stocks = [0, 5, 10]

    for i, stock in enumerate(stocks):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"max_stock": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for product in data["items"]:
        assert product["stock"] <= 5


def test_list_products_filter_by_stock_range(client, auth_headers):
    stocks = [0, 5, 10, 15]

    for i, stock in enumerate(stocks):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_invalid_stock_range(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_combined_filters(client, auth_headers):
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
        auth_post(
            client,
            auth_headers,
            "/products",
            json=product,
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_no_results(client, auth_headers):
    auth_post(
        client,
        auth_headers,
        "/products",
        json={
            "name": "Laptop",
            "price": 1500,
            "stock": 10,
        },
    )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_invalid_page(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"page": 0},
    )

    assert response.status_code == 422


def test_list_products_invalid_limit_zero(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_list_products_invalid_limit_too_large(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_list_products_sort_by_price_asc(client, auth_headers):
    prices = [1000, 100, 500]

    for i, price in enumerate(prices):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_sort_by_price_desc(client, auth_headers):
    prices = [1000, 100, 500]

    for i, price in enumerate(prices):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": price,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_sort_by_stock(client, auth_headers):
    stocks = [20, 5, 10]

    for i, stock in enumerate(stocks):
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": f"Product {i}",
                "price": 100,
                "stock": stock,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_sort_by_name(client, auth_headers):
    names = ["Mouse", "Laptop", "Keyboard"]

    for name in names:
        auth_post(
            client,
            auth_headers,
            "/products",
            json={
                "name": name,
                "price": 100,
                "stock": 10,
            },
        )

    response = auth_get(
        client,
        auth_headers,
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


def test_list_products_invalid_sort_by(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"sort_by": "invalid"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_by. Allowed values: id, name, price, stock"
    )


def test_list_products_invalid_sort_order(client, auth_headers):
    response = auth_get(
        client,
        auth_headers,
        "/products/",
        params={"sort_order": "invalid"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_order. Allowed values: asc, desc"
    )