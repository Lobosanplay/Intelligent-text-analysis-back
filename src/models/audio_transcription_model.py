from datetime import datetime
from typing import Optional
from uuid import UUID

from documment_model import Document
from pydantic import BaseModel


class AudioTranscriptionBase(BaseModel):
    document_id: Optional[UUID] = None
    transcript: Optional[str] = None
    language: Optional[str] = None
    duration: Optional[int] = None


class AudioTranscriptionCreate(AudioTranscriptionBase):
    pass


class AudioTranscription(AudioTranscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AudioTranscriptionWithDocument(AudioTranscription):
    document: Optional[Document] = None
