from config.supabase import supabase
from models.documment_model import DocumentCreate

from .documment_services import document_service


async def upload_file_to_supabase(
    file_bytes: bytes,
    filename: str,
    file_hash: str,
    content_type: str,
    user_id: str,
    bucket: str = "documents",
):
    storage_path = f"{user_id}/{filename}"

    supabase.storage.from_(bucket).upload(
        path=storage_path,
        file=file_bytes,
    )

    response = await document_service.create(
        DocumentCreate(
            user_id=user_id,
            type=content_type,
            original_filename=filename,
            file_hash=file_hash,
            storage_path=storage_path,
        )
    )

    return response
