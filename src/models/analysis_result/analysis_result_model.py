from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AnalysisResultBase(BaseModel):
    document_id: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    topics: Optional[list[list[str]]] = None
    model_version: Optional[str] = None


class AnalysisResultCreate(AnalysisResultBase):
    pass


class AnalysisResult(AnalysisResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResultWithDocument(AnalysisResult):
    document: Optional["Document"] = None
