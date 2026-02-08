from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from documment_model import Document
from pydantic import BaseModel


class AnalysisResultBase(BaseModel):
    document_id: Optional[UUID] = None
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    topics: Optional[List[str]] = None
    model_version: Optional[str] = None


class AnalysisResultCreate(AnalysisResultBase):
    pass


class AnalysisResult(AnalysisResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResultWithDocument(AnalysisResult):
    document: Optional[Document] = None
