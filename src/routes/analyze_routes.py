import hashlib
import os
import shutil
import tempfile

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from errors.domain_errors import DuplicateDocumentError, FileTooLargeError
from schemas.requests import TextRequest, TopicsRequest
from services.document_service import document_service
from services.sentiment_service import analyze_sentiment
from services.summarizer_service import summarize
from services.topics_service import extract_topics
from services.upload_files_service import upload_file_to_supabase
from workers.generic_worker import process_document_generic

load_dotenv()

router = APIRouter(prefix="/analyze", tags=["Analyze"])

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 200))


@router.post("/summarize")
def summarize_text(payload: TextRequest):
    try:
        result = summarize(payload.text)
        return {"summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment")
def sentiment_text(payload: TextRequest):
    try:
        result = analyze_sentiment(payload.text)
        return {"sentiment": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topics")
def topics_text(payload: TopicsRequest):
    try:
        result = extract_topics(payload.sentences, payload.n_topics)
        return {"topics": result.tolist() if hasattr(result, "tolist") else result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", status_code=202)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = None,
    background_tasks: BackgroundTasks = None,
):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    size_mb = os.path.getsize(temp_path) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        os.remove(temp_path)
        raise FileTooLargeError(
            message="File too large",
            details={"filename": file.filename, "size": size_mb},
        )

    hasher = hashlib.sha256()
    with open(temp_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    exists = await document_service.exists_by_hash(user_id, file_hash)

    if exists:
        os.remove(temp_path)
        raise DuplicateDocumentError(
            message="You already uploaded this file",
            details={"filename": file.filename},
        )

    document = await run_in_threadpool(
        upload_file_to_supabase,
        temp_path,
        file.filename,
        file_hash,
        file.content_type,
        user_id,
        "processing",
    )

    os.remove(temp_path)

    background_tasks.add_task(
        process_document_generic,
        document.id,
        document.storage_path,
        document.type,
    )

    return {
        "document_id": document.id,
        "status": "processing",
        "message": "File uploaded. Processing started.",
    }
