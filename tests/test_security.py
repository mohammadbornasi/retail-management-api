
from security import hash_password, verify_password


def test_hash_password():
    password = "MyPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password


def test_verify_password_with_correct_password():
    password = "MyPassword123"

    hashed_password = hash_password(password)

    assert verify_password(
        password,
        hashed_password,
    ) is True


def test_verify_password_with_wrong_password():
    password = "MyPassword123"

    hashed_password = hash_password(password)

    assert verify_password(
        "WrongPassword123",
        hashed_password,
    ) is False


def test_same_password_produces_different_hashes():
    password = "MyPassword123"

    hashed_password_1 = hash_password(password)
    hashed_password_2 = hash_password(password)

    assert hashed_password_1 != hashed_password_2