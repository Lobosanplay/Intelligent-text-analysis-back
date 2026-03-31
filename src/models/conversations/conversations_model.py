from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConversationsBase(BaseModel):
    user_id: str
    title: str


class ConversationCreate(ConversationsBase):
    title: str
    user_id: str


class Conversation(ConversationsBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        return cls(**data)
