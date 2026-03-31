from typing import List

from config.supabase import supabase
from models.messages.messages_model import Message, MessageCreate


class MessageServices:
    async def create_message(self, message: MessageCreate) -> Message:
        response = (
            supabase.table("messages")
            .insert(message.model_dump(exclude_none=True, mode="json"))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create Message")

        return Message.model_validate(response.data[0])

    async def update_message_by_id(
        self, message: MessageCreate, message_id: str
    ) -> Message:
        response = (
            supabase.table("messages")
            .update(message.model_dump(exclude_none=True, mode="json"))
            .eq("id", message_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update Message by Message Id")

        return Message.model_validate(response.data[0])

    async def update_message_by_conversation_id(
        self, message: MessageCreate, conversation_id: str
    ) -> Message:
        response = (
            supabase.table("messages")
            .update(message.model_dump(exclude_none=True, mode="json"))
            .eq("conversation_id", conversation_id)
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update Message by Convesation ID")

        return Message.model_validate(response.data[0])

    async def get_message_by_id(self, message_id: str) -> List[Message]:
        response = supabase.table("messages").select("*").eq("id", message_id).execute()

        if not response.data or response.data == []:
            raise Exception("Failed to get Message")

        return [Message.from_dict(item) for item in response.data]

    async def get_message_by_conversation_id(
        self, conversation_id: str
    ) -> List[Message]:
        response = (
            supabase.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .execute()
        )

        if not response.data or response.data == []:
            raise Exception("Failed to get Message")

        return [Message.from_dict(item) for item in response.data]

    def deleted_message_by_id(self, message_id: str) -> Message:
        response = supabase.table("messages").delete().eq("id", message_id).execute()

        if not response.data:
            raise Exception("Failed to delete Message")

        return Message.model_validate(response.data[0])


message_service = MessageServices()
