from typing import Optional

from pydantic import BaseModel


class MessagesBase(BaseModel):
    role: str = "user" or "assistant" or "system"
    content: Optional[str]
    document_id: Optional[str]
    conversation_id: str


class MessageCreate(MessagesBase):
    role: str = "user" or "assistant" or "system"
    content: Optional[str]
    document_id: Optional[str]
    conversation_id: str


class Message(MessagesBase):
    id: str

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(**data)
