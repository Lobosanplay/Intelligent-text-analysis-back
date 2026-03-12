from typing import List, Optional

from config.supabase import supabase
from models.audio_transcription_model import (
    AudioTranscription,
    AudioTranscriptionCreate,
    AudioTranscriptionWithDocument,
)
from models.document_model import Document


class AudioService:
    async def create(
        self, transcription: AudioTranscriptionCreate
    ) -> AudioTranscription:
        response = (
            supabase.table("audio_transcriptions")
            .insert(transcription.model_dump(exclude_none=True))
            .execute()
        )
        return AudioTranscription(**response.data[0])

    async def get(
        self, transcription_id: int
    ) -> Optional[AudioTranscriptionWithDocument]:
        response = (
            supabase.table("audio_transcriptions")
            .select("*, document:documents(*)")
            .eq("id", transcription_id)
            .execute()
        )

        if not response.data:
            return None

        data = response.data[0]
        document = Document(**data.pop("document")) if data.get("document") else None
        return AudioTranscriptionWithDocument(**data, document=document)

    async def get_by_document(self, document_id: str) -> List[AudioTranscription]:
        response = (
            supabase.table("audio_transcriptions")
            .select("*")
            .eq("document_id", str(document_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [AudioTranscription(**t) for t in response.data]

    async def delete_by_document(self, document_id: str) -> bool:
        response = (
            supabase.table("audio_transcriptions")
            .delete()
            .eq("document_id", str(document_id))
            .execute()
        )
        return bool(response.data)


audio_service = AudioService()
