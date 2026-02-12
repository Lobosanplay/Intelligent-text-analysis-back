import os

from dotenv import load_dotenv
from transformers import AutoTokenizer, pipeline

from utils.chunk_text import chunk_text

load_dotenv()

MODEL_NAME = os.getenv("SENTIMENT_MODEL_NAME")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

sentiment_pipeline = pipeline(
    "sentiment-analysis", model=MODEL_NAME, tokenizer=tokenizer
)

raw_max = tokenizer.model_max_length

if raw_max > 4096:
    raw_max = 1024

safe_tokens = int(raw_max * 0.8)


def analyze_sentiment(text: str):
    text = text.strip()

    if len(text.split()) < 20:
        return sentiment_pipeline(text)

    results = []

    for chunk in chunk_text(text, tokenizer, safe_tokens):
        result = sentiment_pipeline(chunk, truncation=True)[0]
        results.append(result)

    positive = sum(1 for r in results if r["label"] == "POSITIVE")
    negative = sum(1 for r in results if r["label"] == "NEGATIVE")

    total = len(results)

    return {
        "positive_chunks": positive,
        "negative_chunks": negative,
        "total_chunks": total,
        "overall": "POSITIVE" if positive >= negative else "NEGATIVE",
    }
