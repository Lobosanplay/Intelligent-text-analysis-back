import os

from dotenv import load_dotenv

load_dotenv()

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "450"))


def chunk_text_simple(text: str, chunk_size: int = 500, overlap: int = 100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks


def chunk_text_tokenizer(text: str, tokenizer, max_tokens: int = 400):
    tokens = tokenizer.encode(text, truncation=False)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunk = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk)

    return chunks
