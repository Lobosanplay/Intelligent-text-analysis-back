from docx import Document
from PyPDF2 import PdfReader


def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text


def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def read_file(file_path: str) -> str:
    if file_path.endswith(".txt"):
        return read_txt(file_path)

    if file_path.endswith(".pdf"):
        return read_pdf(file_path)

    if file_path.endswith(".docx"):
        return read_docx(file_path)

    raise ValueError("Unsupported file format")
