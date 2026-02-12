import os

from dotenv import load_dotenv

load_dotenv()

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "450"))


def chunk_text(text: str, tokenizer, max_tokens: int = 400):
    tokens = tokenizer.encode(text, truncation=False)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)

    return chunks
