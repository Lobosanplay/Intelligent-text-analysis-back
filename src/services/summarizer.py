from transformers import AutoTokenizer, pipeline

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

summarizer = pipeline("summarization", model=MODEL_NAME, tokenizer=tokenizer)


MAX_INPUT_TOKENS = 450


def chunk_text(text: str):
    tokens = tokenizer.encode(text, add_special_tokens=False)

    for i in range(0, len(tokens), MAX_INPUT_TOKENS):
        chunk_tokens = tokens[i : i + MAX_INPUT_TOKENS]
        yield tokenizer.decode(chunk_tokens, skip_special_tokens=True)


def summarize(text: str) -> str:
    text = text.strip()

    if len(text.split()) < 50:
        return text

    summaries = []

    for chunk in chunk_text(text):
        output = summarizer(chunk, max_length=150, min_length=40, truncation=True)

        summaries.append(output[0]["summary_text"])

    return " ".join(summaries)
