import os
import tempfile

from config.supabase import supabase
from utils.run_blocking import run_blocking


async def download_to_temp(storage_path: str) -> str:
    file_bytes = await run_blocking(
        supabase.storage.from_("documents").download,
        storage_path,
    )

    suffix = os.path.splitext(storage_path)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        return tmp.name
