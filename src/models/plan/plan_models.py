from typing import Dict

from pydantic import BaseModel


class PlanBase(BaseModel):
    id: str
    name: str
    price_monthly: int = 0
    max_documents: int = 15
    max_minutes_audio: int = 45
    max_storage_mb: int = 300
    features: Dict[str, bool]
