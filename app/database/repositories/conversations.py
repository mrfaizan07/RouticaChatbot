"""Repository for conversations and messages."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.conversation import Conversation, Message


class ConversationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.conv_col = db["conversations"]
        self.msg_col = db["messages"]

    async def create_conversation(self, session_id: str, title: str = "New Conversation") -> Conversation:
        conv = Conversation(session_id=session_id, title=title)
        conv_dict = conv.model_dump(by_alias=True, exclude={"id"})
        result = await self.conv_col.insert_one(conv_dict)
        conv.id = str(result.inserted_id)
        return conv

    async def get_conversation(self, conv_id: str, session_id: str | None = None) -> Conversation | None:
        try:
            query = {"_id": ObjectId(conv_id), "is_active": True}
            if session_id:
                query["session_id"] = session_id
            doc = await self.conv_col.find_one(query)
            if doc:
                doc["_id"] = str(doc["_id"])
                return Conversation(**doc)
        except Exception:
            return None
        return None

    async def list_by_session(self, session_id: str, limit: int = 20) -> list[Conversation]:
        cursor = self.conv_col.find({"session_id": session_id, "is_active": True}).sort("updated_at", -1).limit(limit)
        convs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            convs.append(Conversation(**doc))
        return convs

    async def delete_conversation(self, conv_id: str, session_id: str | None = None) -> bool:
        try:
            query = {"_id": ObjectId(conv_id)}
            if session_id:
                query["session_id"] = session_id
            result = await self.conv_col.update_one(query, {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}})
            return result.modified_count > 0
        except Exception:
            return False

    async def add_message(self, message: Message) -> Message:
        msg_dict = message.model_dump(by_alias=True, exclude={"id"})
        result = await self.msg_col.insert_one(msg_dict)
        message.id = str(result.inserted_id)

        # Update conversation's updated_at timestamp
        try:
            await self.conv_col.update_one(
                {"_id": ObjectId(message.conversation_id)},
                {"$set": {"updated_at": datetime.now(timezone.utc)}},
            )
        except Exception:
            pass
        return message

    async def get_messages(self, conv_id: str, limit: int = 50) -> list[Message]:
        cursor = self.msg_col.find({"conversation_id": conv_id}).sort("created_at", 1).limit(limit)
        messages = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            messages.append(Message(**doc))
        return messages

    async def get_recent_history(self, conv_id: str, max_messages: int = 6) -> list[dict[str, str]]:
        """Returns recent messages formatted as role-content pairs for LLM context."""
        cursor = self.msg_col.find({"conversation_id": conv_id}).sort("created_at", -1).limit(max_messages)
        msgs = []
        async for doc in cursor:
            msgs.append({"role": doc["role"], "content": doc["content"]})
        # Reverse to chronological order
        msgs.reverse()
        return msgs
