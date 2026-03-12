from config.supabase import supabase
from models.document_model import DocumentCreate

from .document_service import document_service


def upload_file_to_supabase(
    file_path: str,
    filename: str,
    file_hash: str,
    content_type: str,
    user_id: str,
    status: str = "processing",
    bucket: str = "documents",
):
    storage_path = f"{user_id}/{filename}"

    with open(file_path, "rb") as f:
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=f,
            file_options={"content-type": content_type},
        )

    response = document_service.create(
        DocumentCreate(
            user_id=user_id,
            type=content_type,
            original_filename=filename,
            file_hash=file_hash,
            storage_path=storage_path,
            status=status,
        )
    )

    return response
