import math

from models.messages.messages_model import MessageCreate
from models.plan.plan_models import PlanBase
from services.analysis.analysis_service import analysis_service
from services.conversations.conversations_service import conversations_service
from services.document.document_service import document_service
from services.llm_pipeline.llm_pipeline_service import llm_pipeline_service
from services.messages.messages_service import message_service
from services.qa.qa_service import qa_service
from services.usage_stats.usage_stats_service import usage_stats_service
from services.vector.vector_service import vector_service
from utils.chunk_text import chunk_text_simple
from utils.download_to_temp import download_to_temp
from utils.extract_text import extract_text_from_file


async def process_and_answer_worker(
    document_id: str,
    storage_path: str,
    question: str,
    file_type: str,
    plan: PlanBase,
    user_id: str,
    size_mb: float,
    conversation_id: str,
    message_id: str,
    generate_title: bool = True,
):
    try:
        tmp_path = await download_to_temp(storage_path)

        result = await extract_text_from_file(tmp_path, file_type)
        text = result["text"]

        if not text or len(text.strip()) < 20:
            raise ValueError("Unreadable document")

        chunks = chunk_text_simple(text)
        await vector_service.store_chunks(document_id, chunks)

        top_chunks = await vector_service.search(question, document_id)

        if not top_chunks:
            answer = "No relevant information found in the document."

        elif top_chunks[0]["similarity"] < 0.45:
            answer = "No relevant information found in the document."

        else:
            context = "\n".join(c["content"] for c in top_chunks)

            answer = qa_service.generate_answer(question, context)

        await llm_pipeline_service.run(document_id, text)
        analysis = await analysis_service.get_by_document_id(document_id)

        if generate_title and analysis.summary and conversation_id:
            title = await qa_service.generate_title(analysis.summary)
            await conversations_service.update_conversation_title(
                title,
                conversation_id,
            )

        minutes = 0
        usage = await usage_stats_service.get_usage_by_user_id(user_id)

        if file_type.startswith("audio/") or file_type.startswith("video/"):
            minutes = math.ceil(result["duration"] / 60) if result["duration"] else 0
            if minutes + usage.minutes_audio_processed > plan.max_minutes_audio:
                raise ValueError("Audio limit exceeded")

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
        await document_service.mark_failed_by_document_id(document_id)
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
