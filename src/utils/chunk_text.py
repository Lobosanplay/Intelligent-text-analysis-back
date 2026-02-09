import os

from dotenv import load_dotenv

load_dotenv()

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "450"))


def chunk_text(text: str, tokenizer):
    tokens = tokenizer.encode(text, add_special_tokens=False)

    for i in range(0, len(tokens), int(MAX_TOKENS)):
        chunk = tokens[i : i + int(MAX_TOKENS)]
        yield tokenizer.decode(chunk, skip_special_tokens=True)
