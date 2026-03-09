from pydantic import BaseModel


class UsageStatsBase(BaseModel):
    user_id: str
    documents_uploaded: int = 0
    minutes_audio_processed: int = 0
    storage_used_mb: int = 0
