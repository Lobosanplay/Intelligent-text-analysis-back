import os
import tempfile

from dotenv import load_dotenv

from config.supabase import supabase
from models.audio_transcription_model import AudioTranscriptionCreate
from services.audio_service import audio_service
from services.document_service import document_service
from services.llm_pipeline_service import llm_pipeline_service
from services.speech_service import transcribe
from utils.audio_utils import extract_audio, get_media_duration
from utils.file_reader import read_file
from utils.run_blocking import run_blocking

load_dotenv()

MAX_VIDEO_DURATION_SECONDS = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", 3600))
MAX_AUDIO_DURATION_SECONDS = int(os.getenv("MAX_AUDIO_DURATION_SECONDS", 3600))


async def process_document_generic(document_id: str, storage_path: str, file_type: str):
    tmp_path = None
    audio_path = None

    try:
        file_bytes = supabase.storage.from_("documents").download(storage_path)

        suffix = os.path.splitext(storage_path)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        if file_type.startswith("video/"):
            duration = await run_blocking(get_media_duration, tmp_path)

            if duration > MAX_VIDEO_DURATION_SECONDS:
                raise ValueError("Video exceeds max duration")

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

            if duration > MAX_AUDIO_DURATION_SECONDS:
                raise ValueError("Audio exceeds max duration")

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
            text = await run_blocking(read_file, tmp_path)

            if not text or len(text.strip()) < 20:
                raise ValueError("Unreadable document")

            await llm_pipeline_service.run(document_id, text)

        await document_service.mark_completed(document_id)

    except Exception as e:
        await document_service.mark_failed(document_id, str(e))

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
