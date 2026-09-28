import pytest


@pytest.fixture
def auth_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


# =========================
# Authentication / Authorization
# =========================


def test_create_customer_requires_authentication(client):
    response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert response.status_code == 401


def test_get_customers_requires_authentication(client):
    response = client.get("/customers")

    assert response.status_code == 401


def test_get_customer_requires_authentication(client):
    response = client.get("/customers/1")

    assert response.status_code == 401


def test_update_customer_requires_authentication(client):
    response = client.put(
        "/customers/1",
        json={
            "name": "Ali Updated",
            "email": "ali.updated@example.com",
            "phone": "09876543210",
        },
    )

    assert response.status_code == 401


def test_delete_customer_requires_authentication(client):
    response = client.delete("/customers/1")

    assert response.status_code == 401


def test_delete_customer_requires_admin(client, auth_headers):
    client.headers.update(auth_headers)

    response = client.delete("/customers/1")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Admin access required"
    }


# =========================
# Create
# =========================


def test_create_customer(auth_client):
    response = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert data["name"] == "Ali Ahmadi"
    assert data["email"] == "ali@example.com"
    assert data["phone"] == "09123456789"


def test_create_customer_duplicate_email(auth_client):
    customer = {
        "name": "Ali Ahmadi",
        "email": "ali@example.com",
        "phone": "09123456789",
    }

    first_response = auth_client.post(
        "/customers",
        json=customer,
    )

    assert first_response.status_code == 200

    second_response = auth_client.post(
        "/customers",
        json={
            "name": "Reza Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456788",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "A customer with this email already exists"
    }


# =========================
# Get
# =========================


def test_get_customers(auth_client):
    create_response = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    response = auth_client.get("/customers")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1

    assert len(data["items"]) == 1

    customer = data["items"][0]

    assert customer["name"] == "Ali Ahmadi"
    assert customer["email"] == "ali@example.com"
    assert customer["phone"] == "09123456789"


def test_get_customer(auth_client):
    create_response = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = auth_client.get(f"/customers/{customer_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Ali Ahmadi"
    assert data["email"] == "ali@example.com"
    assert data["phone"] == "09123456789"


def test_get_customer_not_found(auth_client):
    response = auth_client.get("/customers/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }


# =========================
# Update
# =========================


def test_update_customer(auth_client):
    create_response = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = auth_client.put(
        f"/customers/{customer_id}",
        json={
            "name": "Ali Updated",
            "email": "ali.updated@example.com",
            "phone": "09876543210",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Ali Updated"
    assert data["email"] == "ali.updated@example.com"
    assert data["phone"] == "09876543210"


def test_update_customer_not_found(auth_client):
    response = auth_client.put(
        "/customers/9999",
        json={
            "name": "Ali Updated",
            "email": "ali.updated@example.com",
            "phone": "09876543210",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }


def test_update_customer_duplicate_email(auth_client):
    first_customer = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    second_customer = auth_client.post(
        "/customers",
        json={
            "name": "Reza Ahmadi",
            "email": "reza@example.com",
            "phone": "09876543210",
        },
    )

    assert first_customer.status_code == 200
    assert second_customer.status_code == 200

    second_customer_id = second_customer.json()["id"]

    response = auth_client.put(
        f"/customers/{second_customer_id}",
        json={
            "name": "Reza Updated",
            "email": "ali@example.com",
            "phone": "09111111111",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "A customer with this email already exists"
    }


# =========================
# Delete
# =========================


def test_delete_customer(auth_client, admin_headers):
    create_response = auth_client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = auth_client.delete(
        f"/customers/{customer_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Customer deleted successfully"
    }

    get_response = auth_client.get(f"/customers/{customer_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Customer not found"
    }


def test_delete_customer_not_found(auth_client, admin_headers):
    response = auth_client.delete(
        "/customers/9999",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }


# =========================
# Pagination
# =========================


def test_list_customers_pagination(auth_client):
    for i in range(15):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get("/customers/?page=1&limit=10")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 15
    assert data["pages"] == 2
    assert len(data["items"]) == 10


def test_list_customers_second_page(auth_client):
    for i in range(15):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get("/customers/?page=2&limit=10")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 10
    assert data["total"] == 15
    assert data["pages"] == 2
    assert len(data["items"]) == 5


def test_list_customers_page_beyond_last_page(auth_client):
    for i in range(5):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get("/customers/?page=3&limit=10")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 3
    assert data["limit"] == 10
    assert data["total"] == 5
    assert data["pages"] == 1
    assert data["items"] == []


# =========================
# Search
# =========================


def test_list_customers_search_by_name(auth_client):
    customers = [
        {
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09121111111",
        },
        {
            "name": "Reza Karimi",
            "email": "reza@example.com",
            "phone": "09122222222",
        },
    ]

    for customer in customers:
        response = auth_client.post("/customers/", json=customer)
        assert response.status_code == 200

    response = auth_client.get("/customers/?search=Ali")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Ali Ahmadi"


def test_list_customers_search_by_email(auth_client):
    customers = [
        {
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09121111111",
        },
        {
            "name": "Reza Karimi",
            "email": "reza@example.com",
            "phone": "09122222222",
        },
    ]

    for customer in customers:
        response = auth_client.post("/customers/", json=customer)
        assert response.status_code == 200

    response = auth_client.get("/customers/?search=reza@example.com")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "reza@example.com"


def test_list_customers_search_by_phone(auth_client):
    customers = [
        {
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09121111111",
        },
        {
            "name": "Reza Karimi",
            "email": "reza@example.com",
            "phone": "09122222222",
        },
    ]

    for customer in customers:
        response = auth_client.post("/customers/", json=customer)
        assert response.status_code == 200

    response = auth_client.get("/customers/?search=09122222222")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["phone"] == "09122222222"


def test_list_customers_search_case_insensitive(auth_client):
    response = auth_client.post(
        "/customers/",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09121111111",
        },
    )

    assert response.status_code == 200

    response = auth_client.get("/customers/?search=ALI")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Ali Ahmadi"


def test_list_customers_search_no_results(auth_client):
    response = auth_client.post(
        "/customers/",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09121111111",
        },
    )

    assert response.status_code == 200

    response = auth_client.get("/customers/?search=NotFound")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 0


def test_list_customers_combined_search_and_pagination(auth_client):
    for i in range(15):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Ali Customer {i}",
                "email": f"ali{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?search=Ali&page=2&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 10
    assert data["total"] == 15
    assert data["pages"] == 2
    assert len(data["items"]) == 5


# =========================
# Sorting
# =========================


def test_list_customers_sort_by_id_asc(auth_client):
    for i in range(3):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?sort_by=id&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    ids = [customer["id"] for customer in data["items"]]

    assert ids == sorted(ids)


def test_list_customers_sort_by_name_asc(auth_client):
    names = ["Zahra", "Ali", "Reza"]

    for i, name in enumerate(names):
        response = auth_client.post(
            "/customers/",
            json={
                "name": name,
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?sort_by=name&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    names = [customer["name"] for customer in data["items"]]

    assert names == ["Ali", "Reza", "Zahra"]


def test_list_customers_sort_by_name_desc(auth_client):
    names = ["Zahra", "Ali", "Reza"]

    for i, name in enumerate(names):
        response = auth_client.post(
            "/customers/",
            json={
                "name": name,
                "email": f"customer{i}@example.com",
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?sort_by=name&sort_order=desc"
    )

    assert response.status_code == 200

    data = response.json()

    names = [customer["name"] for customer in data["items"]]

    assert names == ["Zahra", "Reza", "Ali"]


def test_list_customers_sort_by_email(auth_client):
    emails = [
        "z@example.com",
        "a@example.com",
        "m@example.com",
    ]

    for i, email in enumerate(emails):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": email,
                "phone": f"091200000{i:02d}",
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?sort_by=email&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    emails = [customer["email"] for customer in data["items"]]

    assert emails == [
        "a@example.com",
        "m@example.com",
        "z@example.com",
    ]


def test_list_customers_sort_by_phone(auth_client):
    phones = [
        "09123333333",
        "09121111111",
        "09122222222",
    ]

    for i, phone in enumerate(phones):
        response = auth_client.post(
            "/customers/",
            json={
                "name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "phone": phone,
            },
        )
        assert response.status_code == 200

    response = auth_client.get(
        "/customers/?sort_by=phone&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    phones = [customer["phone"] for customer in data["items"]]

    assert phones == [
        "09121111111",
        "09122222222",
        "09123333333",
    ]


# =========================
# Validation
# =========================


def test_list_customers_invalid_page(auth_client):
    response = auth_client.get("/customers/?page=0")

    assert response.status_code == 422


def test_list_customers_invalid_limit_zero(auth_client):
    response = auth_client.get("/customers/?limit=0")

    assert response.status_code == 422


def test_list_customers_invalid_limit_too_large(auth_client):
    response = auth_client.get("/customers/?limit=101")

    assert response.status_code == 422


def test_list_customers_invalid_sort_by(auth_client):
    response = auth_client.get(
        "/customers/?sort_by=invalid"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_by. Allowed values: id, name, email, phone"
    )


def test_list_customers_invalid_sort_order(auth_client):
    response = auth_client.get(
        "/customers/?sort_order=invalid"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid sort_order. Allowed values: asc, desc"
    )