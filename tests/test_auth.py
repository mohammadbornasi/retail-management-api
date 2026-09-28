from models import User
from security import ALGORITHM, SECRET_KEY, verify_password, create_access_token
from datetime import timedelta
import jwt


def test_register_user(client, db):
    response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "mohammad"
    assert data["email"] == "mohammad@example.com"
    assert data["role"] == "staff"
    assert data["is_active"] is True

    assert "password" not in data
    assert "hashed_password" not in data

    user = db.query(User).filter(
        User.username == "mohammad"
    ).first()

    assert user is not None
    assert user.email == "mohammad@example.com"
    assert user.hashed_password != "secret123"
    assert verify_password(
        "secret123",
        user.hashed_password,
    )


def test_register_duplicate_username(client):
    first_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "first@example.com",
            "password": "secret123",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "second@example.com",
            "password": "secret456",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Username already registered"
    )


def test_register_duplicate_email(client):
    first_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad1",
            "email": "same@example.com",
            "password": "secret123",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad2",
            "email": "same@example.com",
            "password": "secret456",
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Email already registered"
    )


def test_register_password_too_short(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "1234567",
        },
    )

    assert response.status_code == 422


def test_register_username_too_short(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "ab",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 422


def test_register_missing_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
        },
    )

    assert response.status_code == 422


def test_login_success(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "secret123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password"
    )


def test_login_unknown_username(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "unknown",
            "password": "secret123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password"
    )


def test_login_inactive_user(client, db):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    user = (
        db.query(User)
        .filter(User.username == "mohammad")
        .first()
    )

    assert user is not None

    user.is_active = False
    db.commit()

    response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "secret123",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "User account is inactive"
    )


def test_get_me_with_valid_token(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "secret123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "mohammad"
    assert data["email"] == "mohammad@example.com"
    assert data["role"] == "staff"
    assert data["is_active"] is True

    assert "password" not in data
    assert "hashed_password" not in data


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Could not validate credentials"
    )


def test_get_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_with_tampered_token(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "secret123",
        },
    )

    token = login_response.json()["access_token"]

    tampered_token = token[:-1] + "x"

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {tampered_token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Could not validate credentials"
    )


def test_login_token_claims(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "username": "mohammad",
            "password": "secret123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "mohammad"
    assert payload["user_id"] == user_id
    assert payload["role"] == "staff"
    assert "exp" in payload


def test_expired_token_rejected(client, db):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "mohammad",
            "email": "mohammad@example.com",
            "password": "secret123",
        },
    )

    assert register_response.status_code == 200

    user_id = register_response.json()["id"]

    expired_token = create_access_token(
        data={
            "sub": "mohammad",
            "user_id": user_id,
            "role": "staff",
        },
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Could not validate credentials"
    )