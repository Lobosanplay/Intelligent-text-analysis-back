from pydantic import BaseModel


class UsageStatsBase(BaseModel):
    user_id: str
    documents_uploaded: int = 0
    minutes_audio_processed: int = 0
    monthly_storage_used_mb: float = 0
    total_storage_mb: float = 0
