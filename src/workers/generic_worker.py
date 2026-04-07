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
from services.llm_pipeline.llm_pipeline_service import llm_pipeline_service
from services.messages.messages_service import message_service
from services.speech.speech_service import transcribe
from services.usage_stats.usage_stats_service import usage_stats_service
from utils.audio_utils import extract_audio, get_media_duration
from utils.file_reader import read_file
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

            audio_path = await run_blocking(extract_audio, tmp_path)

            text = await run_blocking(transcribe, audio_path)

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

            text = await run_blocking(transcribe, tmp_path)

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
            text = await run_blocking(read_file, tmp_path)

            if not text or len(text.strip()) < 20:
                raise ValueError("Unreadable document")

            await llm_pipeline_service.run(document_id, text)

        analysis = await analysis_service.get_by_document_id(document_id)
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
