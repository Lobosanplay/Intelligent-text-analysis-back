from typing import List

from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str


class TopicsRequest(BaseModel):
    sentences: List[str]
    n_topics: int = 5


class FullAnalysisRequest(BaseModel):
    text: str
