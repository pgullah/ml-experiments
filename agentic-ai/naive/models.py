from typing import Literal

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(
        min_length=3,
        description="The research question"
    )


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class Source(BaseModel):
    title: str
    url: str
    content: str


class AgentAction(BaseModel):
    action: Literal["search", "read", "finish"]

    query: str | None = None
    url: str | None = None
    reason: str


class AgentStep(BaseModel):
    step: int
    action: str
    reason: str


class ResearchResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    steps: list[AgentStep]