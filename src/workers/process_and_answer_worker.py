import math

from models.messages.messages_model import MessageCreate
from services.analysis.analysis_service import analysis_service
from services.conversations.conversations_service import conversations_service
from services.llm_pipeline.llm_pipeline_service import llm_pipeline_service
from services.messages.messages_service import message_service
from services.qa.qa_service import qa_service
from services.usage_stats.usage_stats_service import usage_stats_service
from services.vector.vector_service import vector_service
from utils.chunk_text import chunk_text_simple
from utils.extract_text import extract_text_from_file


async def process_and_answer_worker(
    document_id: str,
    storage_path: str,
    question: str,
    file_type: str,
    user_id: str,
    size_mb: float,
    conversation_id: str,
    message_id: str,
):
    try:
        result = await extract_text_from_file(storage_path, file_type)
        text = result["text"]

        if not text or len(text.strip()) < 20:
            raise ValueError("Unreadable document")

        chunks = chunk_text_simple(text)
        await vector_service.store_chunks(document_id, chunks)

        top_chunks = await vector_service.search(question, [document_id])

        if not top_chunks:
            context = "No relevant context found in the document."
        else:
            context = "\n".join(top_chunks)
            answer = qa_service.generate_answer(question, context)

        await llm_pipeline_service.run(document_id, text)
        analysis = await analysis_service.get_by_document_id(document_id)

        if analysis.summary:
            title = await qa_service.generate_title(analysis.summary)

            await conversations_service.update_conversation_title(
                conversation_id,
                title,
            )

        minutes = 0

        if file_type.startswith("audio/") or file_type.startswith("video/"):
            minutes = math.ceil(result["duration"] / 60) if result["duration"] else 0

        await usage_stats_service.increment_user_stats_by_id(user_id, size_mb, minutes)

        await message_service.update_message_by_id(
            MessageCreate(
                role="assistant",
                content=answer,
                conversation_id=conversation_id,
                document_id=document_id,
            ),
            message_id=message_id,
        )

    except Exception as e:
        await message_service.update_message_by_id(
            MessageCreate(
                role="assistant",
                content="Error processing and answering",
                conversation_id=conversation_id,
                document_id=document_id,
            ),
            message_id=message_id,
        )
        print("Error", e)
