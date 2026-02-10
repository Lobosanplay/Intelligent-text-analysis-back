from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentBase(BaseModel):
    type: Optional[str] = None
    original_filename: Optional[str] = None
    storage_path: Optional[str] = None
    file_hash: Optional[str] = None


class DocumentCreate(DocumentBase):
    user_id: Optional[str] = None


class Document(DocumentBase):
    id: str
    user_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithRelations(Document):
    analysis_results: List["AnalysisResult"] = []
    audio_transcriptions: List["AudioTranscription"] = []
