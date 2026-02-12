from models.analysis_result_model import AnalysisResultCreate
from services.analysis_service import analysis_service
from services.document_service import document_service
from services.sentiment_service import analyze_sentiment
from services.summarizer_service import summarize
from services.topics_service import extract_topics


class LLMPipelineService:
    async def run(self, document_id: str, text: str):
        try:
            summaries = [summarize(text)]

            combined_summary = " ".join(summaries)

            sentiment = analyze_sentiment(text)

            topics = extract_topics(
                [s.strip() for s in text.split(".") if len(s.strip()) > 10]
            )

            await analysis_service.create(
                AnalysisResultCreate(
                    document_id=document_id,
                    summary=combined_summary,
                    sentiment=sentiment,
                    topics=topics,
                )
            )

            await document_service.mark_completed(document_id)
        except Exception as e:
            await document_service.mark_failed(document_id)
            print(f"Error occurred during LLM pipeline execution: {e}")


llm_pipeline_service = LLMPipelineService()
