from datetime import datetime
from typing import List, Optional
from uuid import UUID

from analysis_result_model import AnalysisResult
from audio_transcription_model import AudioTranscription
from pydantic import BaseModel


class DocumentBase(BaseModel):
    type: Optional[str] = None
    original_filename: Optional[str] = None
    storage_path: Optional[str] = None


class DocumentCreate(DocumentBase):
    user_id: Optional[UUID] = None


class Document(DocumentBase):
    id: UUID
    user_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithRelations(Document):
    analysis_results: List[AnalysisResult] = []
    audio_transcriptions: List[AudioTranscription] = []
