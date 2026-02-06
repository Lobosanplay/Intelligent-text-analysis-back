from transformers import AutoTokenizer, pipeline

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

sentiment_pipeline = pipeline(
    "sentiment-analysis", model=MODEL_NAME, tokenizer=tokenizer
)

MAX_TOKENS = 450


def chunk_text(text: str):
    tokens = tokenizer.encode(text, add_special_tokens=False)

    for i in range(0, len(tokens), MAX_TOKENS):
        chunk = tokens[i : i + MAX_TOKENS]
        yield tokenizer.decode(chunk, skip_special_tokens=True)


def analyze_sentiment(text: str):
    text = text.strip()

    if len(text.split()) < 20:
        return sentiment_pipeline(text)

    results = []

    for chunk in chunk_text(text):
        result = sentiment_pipeline(chunk, truncation=True)[0]
        results.append(result)

    # 🔢 promedio simple
    positive = sum(1 for r in results if r["label"] == "POSITIVE")
    negative = sum(1 for r in results if r["label"] == "NEGATIVE")

    total = len(results)

    return {
        "positive_chunks": positive,
        "negative_chunks": negative,
        "total_chunks": total,
        "overall": "POSITIVE" if positive >= negative else "NEGATIVE",
    }
