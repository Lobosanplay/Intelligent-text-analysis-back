import os
import tempfile

from config.supabase import supabase
from models.analysis_result_model import AnalysisResultCreate
from services.analysis_service import analysis_service
from services.file_reader_services import read_file
from services.sentiment_services import analyze_sentiment
from services.summarizer_services import summarize
from services.topics_services import extract_topics


async def process_document_file(document_id: str, storage_path: str, user_id):
    file_bytes = supabase.storage.from_("documents").download(storage_path)

    suffix = os.path.splitext(storage_path)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        text = read_file(tmp_path)

        if not text or len(text.strip()) < 20:
            raise Exception("Unreadable file")

        summary = summarize(text)
        sentiment = analyze_sentiment(text)
        topics = extract_topics([s for s in text.split(".") if len(s.strip()) > 10])

        await analysis_service.create(
            AnalysisResultCreate(
                document_id=document_id,
                summary=summary,
                sentiment=sentiment,
                topics=topics,
            )
        )

    finally:
        os.remove(tmp_path)
