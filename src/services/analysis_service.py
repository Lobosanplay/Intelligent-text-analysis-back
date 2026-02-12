from typing import List, Optional

from config.supabase import supabase
from models.analysis_result_model import (
    AnalysisResult,
    AnalysisResultCreate,
    AnalysisResultWithDocument,
)
from models.document_model import Document


class AnalysisService:
    async def create(self, analysis: AnalysisResultCreate) -> AnalysisResult:
        response = (
            supabase.table("analysis_results")
            .insert(analysis.model_dump(exclude_none=True))
            .execute()
        )
        return AnalysisResult(**response.data[0])

    async def get(self, result_id: int) -> Optional[AnalysisResultWithDocument]:
        response = (
            supabase.table("analysis_results")
            .select("*, document:documents(*)")
            .eq("id", result_id)
            .execute()
        )

        if not response.data:
            return None

        data = response.data[0]
        document = Document(**data.pop("document")) if data.get("document") else None
        return AnalysisResultWithDocument(**data, document=document)

    async def get_by_document(self, document_id: str) -> List[AnalysisResult]:
        response = (
            supabase.table("analysis_results")
            .select("*")
            .eq("document_id", str(document_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [AnalysisResult(**r) for r in response.data]

    async def delete_by_document(self, document_id: str) -> bool:
        response = (
            supabase.table("analysis_results")
            .delete()
            .eq("document_id", str(document_id))
            .execute()
        )
        return bool(response.data)


analysis_service = AnalysisService()
