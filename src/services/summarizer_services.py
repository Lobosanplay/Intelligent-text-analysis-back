import os

from dotenv import load_dotenv
from transformers import AutoTokenizer, pipeline

from utils.chunk_text import chunk_text

load_dotenv()

MODEL_NAME = os.getenv("SUMMARIZER_MODEL_NAME")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

summarizer = pipeline("summarization", model=MODEL_NAME, tokenizer=tokenizer)


def summarize(text: str) -> str:
    text = text.strip()

    if len(text.split()) < 50:
        return text

    summaries = []

    for chunk in chunk_text(text, tokenizer):
        output = summarizer(chunk, max_length=150, min_length=40)

        summaries.append(output[0]["summary_text"])

    return " ".join(summaries)
