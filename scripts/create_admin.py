"""Interactive CLI script to create an administrator account."""

import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.security import hash_password
from app.database.mongodb import MongoDBManager
from app.database.repositories.users import UserRepository
from app.models.user import User


async def main():
    print("=== Routica Admin Account Creation ===")
    email = input("Admin Email: ").strip()
    if not email or "@" not in email:
        print("Error: Invalid email address.")
        sys.exit(1)

    password = getpass.getpass("Admin Password (min 8 chars): ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters long.")
        sys.exit(1)

    confirm_pass = getpass.getpass("Confirm Password: ")
    if password != confirm_pass:
        print("Error: Passwords do not match.")
        sys.exit(1)

    await MongoDBManager.connect()
    db = MongoDBManager.get_database()
    user_repo = UserRepository(db)

    existing = await user_repo.get_by_email(email)
    if existing:
        print(f"Error: User with email '{email}' already exists.")
        await MongoDBManager.close()
        sys.exit(1)

    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed, role="admin", is_active=True)
    created = await user_repo.create(user)

    print(f"\nAdministrator account created successfully! User ID: {created.id}")
    await MongoDBManager.close()


if __name__ == "__main__":
    asyncio.run(main())

