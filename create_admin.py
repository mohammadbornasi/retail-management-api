from getpass import getpass

from database import SessionLocal
from models import User
from security import hash_password


def create_admin():
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip()

    if not 3 <= len(username) <= 50:
        print("Error: Username must be 3-50 characters.")
        return

    if not 5 <= len(email) <= 150:
        print("Error: Email must be 5-150 characters.")
        return

    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    if not 8 <= len(password) <= 100:
        print("Error: Password must be 8-100 characters.")
        return

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(
                (User.username == username)
                | (User.email == email)
            )
            .first()
        )

        if existing_user:
            print(
                "Error: Username or email already exists. "
                "No changes were made."
            )
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")
        print(f"Username: {admin.username}")
        print(f"Role: {admin.role}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()