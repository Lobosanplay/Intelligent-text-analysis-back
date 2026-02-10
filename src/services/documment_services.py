from typing import Any, Dict, List, Optional

from config.supabase import supabase
from models.documment_model import Document, DocumentCreate


class DocumentService:
    async def create(self, document: DocumentCreate) -> Document:
        response = (
            supabase.table("documents")
            .insert(document.model_dump(exclude_none=True, mode="json"))
            .execute()
        )

        if not response.data:
            raise Exception("Failed to create document")

        return Document(**response.data[0])

    async def get(self, document_id: str) -> Optional[Document]:
        response = (
            supabase.table("documents").select("*").eq("id", str(document_id)).execute()
        )
        return Document(**response.data[0]) if response.data else None

    async def get_by_user(self, user_id: str) -> List[Document]:
        response = (
            supabase.table("documents")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [Document(**doc) for doc in response.data]

    async def update(
        self, document_id: str, updates: Dict[str, Any]
    ) -> Optional[Document]:
        response = (
            supabase.table("documents")
            .update(updates)
            .eq("id", str(document_id))
            .execute()
        )
        return Document(**response.data[0]) if response.data else None

    async def delete(self, document_id: str) -> bool:
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


document_service = DocumentService()
