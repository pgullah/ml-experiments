"""HTTP interface for trusted bot clients."""

import logging
from contextlib import asynccontextmanager
import os
from secrets import compare_digest
from threading import Lock
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from app.agent import Agent
from app.common.config import AppSettings
from app.planner import TravelPlanner

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    message: str = Field(min_length=1)
    thread_id: str = Field(min_length=1, max_length=256)


class ChatResponse(BaseModel):
    content: str
    thread_id: str


def authorize(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> None:
    expected = request.app.state.settings.travel_agent_api_key.get_secret_value()
    if credentials is None or not compare_digest(
        credentials.credentials.encode(), expected.encode()
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_app(
    settings: AppSettings | None = None, agent: Agent | None = None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        runtime_settings = settings or AppSettings()  # pyright: ignore[reportCallIssue]
        token = runtime_settings.travel_agent_api_key
        if token is None or not token.get_secret_value().strip():
            raise RuntimeError("TRAVEL_AGENT_API_KEY is required to start the REST API")
        application.state.settings = runtime_settings
        application.state.agent = agent or Agent(TravelPlanner(runtime_settings))
        # The graph and domain guard share mutable in-memory state. Admit one
        # invocation at a time rather than allowing overlapping writes.
        application.state.chat_lock = Lock()
        yield
        del application.state.agent

    application = FastAPI(
        title="AI Travel Agent API", version="0.1.0", lifespan=lifespan,
    )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post(
        "/chat", response_model=ChatResponse, dependencies=[Depends(authorize)]
    )
    def chat(body: ChatRequest, request: Request) -> ChatResponse:
        limit = request.app.state.settings.max_request_characters
        if len(body.message) > limit:
            raise HTTPException(422, f"message must not exceed {limit} characters")
        lock = request.app.state.chat_lock
        if not lock.acquire(blocking=False):
            raise HTTPException(
                503, "Agent is busy; retry later", headers={"Retry-After": "1"}
            )
        try:
            result = request.app.state.agent.chat(
                body.message, thread_id=body.thread_id
            )
            # The domain guard returns plain text for refusals.
            content = result if isinstance(result, str) else result.content
            return ChatResponse(content=content, thread_id=body.thread_id)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        except Exception as error:
            logger.exception("Travel agent request failed")
            raise HTTPException(500, "Travel agent request failed") from error
        finally:
            lock.release()

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8000)))
