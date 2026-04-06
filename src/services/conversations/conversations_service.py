from typing import List

from config.supabase import supabase
from models.conversations.conversations_model import (
    Conversation,
    ConversationCreate,
)


class ConversationsServices:
    async def create_conversation(
        self, conversation: ConversationCreate
    ) -> Conversation:
        response = (
            supabase.table("conversations")
            .insert(conversation.model_dump(exclude_none=True, mode="json"))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create conversation")

        return Conversation.model_validate(response.data[0])

    async def update_conversation_by_id(
        self, conversation: ConversationCreate, conversation_id: str
    ) -> Conversation:
        response = (
            supabase.table("conversations")
            .update(conversation.model_dump(exclude_none=True, mode="json"))
            .eq("id", conversation_id)
            .execute()
        )

        if not response.data:
            raise Exception("failed to update conversation")

        return Conversation.model_validate(response.data[0])

    async def get_conversation_by_id(self, conversation_id: str) -> Conversation:
        response = (
            supabase.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed getting conversation")

        return Conversation.model_validate(response.data[0])

    async def get_conversation_by_user_id(self, user_id: str) -> List[Conversation]:
        response = (
            supabase.table("conversations").select("*").eq("user_id", user_id).execute()
        )

        if not response.data:
            return []

        return [Conversation.from_dict(item) for item in response.data]

    async def delete_conversation_by_id(self, conversation_id: str) -> Conversation:
        response = (
            supabase.table("conversations").delete().eq("id", conversation_id).execute()
        )

        if not response.data:
            raise Exception("Failed to deleted conversation")

        return Conversation.model_validate(response.data[0])

    async def validate_conversation_exists_by_conversation_id(
        self, conversation_id: str, user_id: str
    ) -> bool:
        response = await self.get_conversation_by_id(conversation_id)

        if response and response.user_id == user_id:
            return True

        return False


conversations_service = ConversationsServices()
