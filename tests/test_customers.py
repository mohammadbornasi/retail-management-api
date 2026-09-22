def test_create_customer(client):
    response = client.post(
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


def test_get_customers(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    response = client.get("/customers")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Ali Ahmadi"
    assert data[0]["email"] == "ali@example.com"
    assert data[0]["phone"] == "09123456789"


def test_create_customer_duplicate_email(client):
    customer = {
        "name": "Ali Ahmadi",
        "email": "ali@example.com",
        "phone": "09123456789",
    }

    first_response = client.post(
        "/customers",
        json=customer,
    )

    assert first_response.status_code == 200

    second_response = client.post(
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


def test_get_customer(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = client.get(f"/customers/{customer_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Ali Ahmadi"
    assert data["email"] == "ali@example.com"
    assert data["phone"] == "09123456789"


def test_get_customer_not_found(client):
    response = client.get("/customers/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }


def test_update_customer(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = client.put(
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


def test_update_customer_not_found(client):
    response = client.put(
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


def test_update_customer_duplicate_email(client):
    first_customer = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    second_customer = client.post(
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

    response = client.put(
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


def test_delete_customer(client):
    create_response = client.post(
        "/customers",
        json={
            "name": "Ali Ahmadi",
            "email": "ali@example.com",
            "phone": "09123456789",
        },
    )

    assert create_response.status_code == 200

    customer_id = create_response.json()["id"]

    response = client.delete(f"/customers/{customer_id}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Customer deleted successfully"
    }

    get_response = client.get(f"/customers/{customer_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Customer not found"
    }


def test_delete_customer_not_found(client):
    response = client.delete("/customers/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Customer not found"
    }
