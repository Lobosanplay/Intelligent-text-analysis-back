from sentence_transformers import SentenceTransformer

from services.document_chunks.document_chunks_services import document_chunks_service

model = SentenceTransformer("all-MiniLM-L6-v2")


class VectorService:
    async def store_chunks(self, document_id: str, chunks: list[str]):
        embeddings = model.encode(chunks).tolist()

        data = [
            {
                "document_id": document_id,
                "content": chunk,
                "embedding": emb,
            }
            for chunk, emb in zip(chunks, embeddings)
        ]

        await document_chunks_service.create_chunks(data)

    async def search(
        self,
        query: str,
        document_ids: list[str],
        top_k: int = 5,
    ):
        query_embedding = model.encode([query])[0].tolist()

        rows = await document_chunks_service.get_chunks(
            query_embedding, top_k, document_ids
        )

        return [row["content"] for row in rows]


vector_service = VectorService()
