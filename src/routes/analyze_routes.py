from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from errors.domain_errors import DuplicateDocumentError
from schemas.requests import TextRequest, TopicsRequest
from services.documment_services import document_service
from services.sentiment_services import analyze_sentiment
from services.summarizer_services import summarize
from services.topics_services import extract_topics
from services.upload_files_services import upload_file_to_supabase
from utils.calculate_hash import hash_file
from workers.audio_worker import process_audio_file
from workers.document_worker import process_document_file

router = APIRouter(prefix="/analyze", tags=["Analyze"])


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


@router.post("/transcribe")
async def transcribe_and_analyze(
    file: UploadFile = File(...),
    user_id: str = None,
    background_tasks: BackgroundTasks = None,
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, "Invalid audio file")

    file_bytes = await file.read()

    file_hash = hash_file(file_bytes)

    exists = await document_service.exists_by_hash(user_id, file_hash)

    if exists:
        raise DuplicateDocumentError(
            message="You already uploaded this file",
            details={"filename": file.filename},
        )

    document = await upload_file_to_supabase(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type,
        file_hash=file_hash,
        user_id=user_id,
    )

    background_tasks.add_task(
        process_audio_file,
        document_id=document.id,
        storage_path=document.storage_path,
        user_id=user_id,
    )

    return {
        "status": "processing",
        "message": "File uploaded successfully. Analysis started.",
    }


@router.post("/full/file")
async def full_analysis_file(
    file: UploadFile = File(...),
    user_id: str = None,
    background_tasks: BackgroundTasks = None,
):
    file_bytes = await file.read()

    file_hash = hash_file(file_bytes)

    exists = await document_service.exists_by_hash(user_id, file_hash)

    if exists:
        raise DuplicateDocumentError(
            message="You already uploaded this file",
            details={"filename": file.filename},
        )

    document = await upload_file_to_supabase(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type,
        file_hash=file_hash,
        user_id=user_id,
    )

    background_tasks.add_task(
        process_document_file,
        document.id,
        document.storage_path,
        user_id,
    )

    return {
        "status": "processing",
        "message": "File uploaded successfully. Analysis started.",
    }
