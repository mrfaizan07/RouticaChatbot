"""User repository for administrator persistence."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return User(**doc)
        except Exception:
            return None
        return None

    async def get_by_email(self, email: str) -> User | None:
        doc = await self.collection.find_one({"email": email.lower().strip()})
        if doc:
            doc["_id"] = str(doc["_id"])
            return User(**doc)
        return None

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        user_dict["email"] = user_dict["email"].lower().strip()
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def update_last_login(self, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}},
        )

    async def update_password(self, user_id: str, new_password_hash: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_password_hash, "updated_at": datetime.now(timezone.utc)}},
        )

    async def count_admins(self) -> int:
        return await self.collection.count_documents({"role": "admin"})
