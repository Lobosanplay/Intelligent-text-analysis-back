from typing import Any, Dict, List

from config.supabase import supabase
from models.document.document_model import Document, DocumentCreate


class DocumentService:
    def create_document(self, document: DocumentCreate) -> Document:
        response = (
            supabase.table("documents")
            .insert(document.model_dump(exclude_none=True, mode="json"))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create document")

        return Document.model_validate(response.data[0])

    async def get_by_document_id(self, document_id: str) -> Document:
        response = (
            supabase.table("documents").select("*").eq("id", str(document_id)).execute()
        )

        if not response.data:
            raise Exception("Failed get document")

        return Document.model_validate(response.data[0])

    async def get_by_user(self, user_id: str) -> List[Document]:
        response = (
            supabase.table("documents")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [Document(doc) for doc in response.data]

    async def update_by_document_id(
        self, document_id: str, updates: Dict[str, Any]
    ) -> Document:
        response = (
            supabase.table("documents")
            .update(updates)
            .eq("id", str(document_id))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to update document")

        return Document.model_validate(response.data[0])

    async def delete_by_document_id(self, document_id: str) -> bool:
        response = (
            supabase.table("documents").delete().eq("id", str(document_id)).execute()
        )
        return bool(response.data)

    async def exists_by_hash(self, user_id: str, file_hash: str):
        response = (
            supabase.table("documents")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("file_hash", file_hash)
            .execute()
        )
        return bool(response.data)

    async def mark_completed_by_document_id(self, document_id: str):
        (
            supabase.table("documents")
            .update({"status": "completed"})
            .eq("id", document_id)
            .execute()
        )

    async def mark_failed_by_document_id(self, document_id: str):
        (
            supabase.table("documents")
            .update({"status": "failed"})
            .eq("id", document_id)
            .execute()
        )


document_service = DocumentService()
