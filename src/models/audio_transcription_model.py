from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AudioTranscriptionBase(BaseModel):
    document_id: Optional[str] = None
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
    document: Optional["Document"] = None
