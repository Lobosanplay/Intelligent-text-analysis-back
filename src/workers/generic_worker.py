import math
import os
import tempfile

from dotenv import load_dotenv

from config.supabase import supabase
from models.audio_trancription.audio_transcription_model import AudioTranscriptionCreate
from models.messages.messages_model import MessageCreate
from models.plan.plan_models import PlanBase
from services.analysis.analysis_service import analysis_service
from services.audio_service.audio_service import audio_service
from services.conversations.conversations_service import conversations_service
from services.llm_pipeline.llm_pipeline_service import llm_pipeline_service
from services.messages.messages_service import message_service
from services.qa.qa_service import qa_service
from services.usage_stats.usage_stats_service import usage_stats_service
from services.vector.vector_service import vector_service
from utils.audio_utils import get_media_duration
from utils.chunk_text import chunk_text_simple
from utils.extract_text import extract_text_from_file
from utils.run_blocking import run_blocking

load_dotenv()


async def process_document_generic(
    document_id: str,
    plan: PlanBase,
    storage_path: str,
    file_type: str,
    user_id: str,
    size_mb: float,
    conversation_id: str | None = None,
    message_id: str | None = None,
):
    tmp_path = None
    audio_path = None

    try:
        usage = await usage_stats_service.get_usage_by_user_id(user_id)

        file_bytes = await run_blocking(
            supabase.storage.from_("documents").download, storage_path
        )

        suffix = os.path.splitext(storage_path)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        if file_type.startswith("video/"):
            duration = await run_blocking(get_media_duration, tmp_path)
            minutes = math.ceil(duration / 60)

            if minutes + usage.minutes_audio_processed > plan.max_minutes_audio:
                raise ValueError("Audio limit exceeded")

            text = await extract_text_from_file(storage_path, file_type)

            await audio_service.create(
                AudioTranscriptionCreate(
                    document_id=document_id,
                    transcript=text,
                    duration=int(duration),
                )
            )

            await llm_pipeline_service.run(document_id, text)

        elif file_type.startswith("audio/"):
            duration = await run_blocking(get_media_duration, tmp_path)
            minutes = math.ceil(duration / 60)

            if minutes + usage.minutes_audio_processed > plan.max_minutes_audio:
                raise ValueError("Audio limit exceeded")

            text = await extract_text_from_file(storage_path, file_type)

            await audio_service.create(
                AudioTranscriptionCreate(
                    document_id=document_id,
                    transcript=text,
                    duration=int(duration),
                )
            )

            await llm_pipeline_service.run(document_id, text)

        else:
            minutes = 0
            text = await extract_text_from_file(storage_path, file_type)

            chunks = chunk_text_simple(text)
            await vector_service.store_chunks(document_id, chunks)

            if not text or len(text.strip()) < 20:
                raise ValueError("Unreadable document")

            await llm_pipeline_service.run(document_id, text)

        analysis = await analysis_service.get_by_document_id(document_id)

        if analysis.summary and conversation_id:
            title = await qa_service.generate_title(analysis.summary)

            await conversations_service.update_conversation_title(
                conversation_id,
                title,
            )

        await usage_stats_service.increment_user_stats_by_id(user_id, size_mb, minutes)

        if message_id and conversation_id:
            await message_service.update_message_by_id(
                MessageCreate(
                    role="assistant",
                    content=analysis.summary,
                    conversation_id=conversation_id,
                    document_id=document_id,
                ),
                message_id=message_id,
            )

    except Exception as e:
        if message_id and conversation_id:
            await message_service.update_message_by_id(
                MessageCreate(
                    role="assistant",
                    content="Error en el procesamiento de el archivo",
                    conversation_id=conversation_id,
                    document_id=document_id,
                ),
                message_id=message_id,
            )
        raise Exception(e)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
