import os
import tempfile

from config.supabase import supabase
from services.speech.speech_service import transcribe
from utils.audio_utils import extract_audio, get_media_duration
from utils.file_reader import read_file
from utils.run_blocking import run_blocking


async def extract_text_from_file(storage_path: str, file_type: str):
    tmp_path = None
    audio_path = None
    duration = 0

    try:
        file_bytes = await run_blocking(
            supabase.storage.from_("documents").download, storage_path
        )

        suffix = os.path.splitext(storage_path)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        if file_type.startswith("video/"):
            audio_path = await run_blocking(extract_audio, tmp_path)
            text = await run_blocking(transcribe, audio_path)
            duration = await run_blocking(get_media_duration, tmp_path)
        elif file_type.startswith("audio/"):
            text = await run_blocking(transcribe, tmp_path)
            duration = await run_blocking(get_media_duration, tmp_path)

        else:
            text = await run_blocking(read_file, tmp_path)

        return {"text": text, "duration": duration or 0}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
