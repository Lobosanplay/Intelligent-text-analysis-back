from config.supabase import supabase


class DocumentChunksService:
    async def create_chunks(self, data):
        response = supabase.table("document_chunks").insert(data).execute()

        if not response.data:
            raise Exception("Failed to create chunks")

        return response.data[0]

    async def get_chunks(
        self,
        query_embedding: str,
        document_id: str,
        top_k: int = 5,
    ):
        response = supabase.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "match_count": top_k,
                "document_id": document_id,
            },
        ).execute()

        data = getattr(response, "data", None)

        if not data:
            print("No chunks returned from RPC")
            return []

        return data


document_chunks_service = DocumentChunksService()
