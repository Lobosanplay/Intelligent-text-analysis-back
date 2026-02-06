import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.requests import TextRequest, TopicsRequest
from services.file_reader import read_file
from services.sentiment import analyze_sentiment
from services.speech import transcribe
from services.summarizer import summarize
from services.topics import extract_topics

router = APIRouter(prefix="/analyze", tags=["Analyze"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
async def transcribe_and_analyze(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file")

    try:
        audio_id = f"{uuid4()}_{file.filename}"
        audio_path = os.path.join(UPLOAD_DIR, audio_id)

        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = transcribe(audio_path)

        if not text or len(text.strip()) < 5:
            raise HTTPException(400, "Whisper returned empty text")

        summary = summarize(text)
        sentiment = analyze_sentiment(text)

        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]
        topics = extract_topics(sentences)

        return {
            "transcription": text,
            "summary": summary,
            "sentiment": sentiment,
            "topics": topics.tolist() if hasattr(topics, "tolist") else topics,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full/file")
async def full_analysis_file(file: UploadFile = File(...)):
    try:
        allowed = [
            "text/plain",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        file_id = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_id)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        text = read_file(file_path)

        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Empty or unreadable file")

        summary = summarize(text)
        sentiment = analyze_sentiment(text)
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]
        topics = extract_topics(sentences)
        return {
            "summary": summary,
            "sentiment": sentiment,
            "topics": topics.tolist() if hasattr(topics, "tolist") else topics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
