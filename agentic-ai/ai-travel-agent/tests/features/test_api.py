from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from api import create_app
from app.agent import Agent
from app.guard_rails.policy import TRAVEL_REFUSAL
from tests.support.fakes import TEST_SETTINGS, FakePlanner

AUTH = {"Authorization": "Bearer test-service-token"}
BODY = {"message": "Plan a trip to Rome", "thread_id": "telegram:123"}


@pytest.fixture
def api():
    planner = FakePlanner()
    agent = Agent(planner)
    settings = TEST_SETTINGS.model_copy(
        update={"travel_agent_api_key": SecretStr("test-service-token")}
    )
    with TestClient(create_app(settings, agent)) as client:
        yield client, agent, planner


def test_health_and_openapi(api):
    client, _, _ = api
    assert client.get("/health").json() == {"status": "ok"}
    assert "/chat" in client.get("/openapi.json").json()["paths"]


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}])
def test_chat_requires_authentication(api, headers):
    client, _, planner = api
    assert client.post("/chat", json=BODY, headers=headers).status_code == 401
    assert planner.llm_with_tools.invocations == 0


def test_chat_preserves_history_and_isolates_threads(api):
    client, _, planner = api
    for thread in ["telegram:123", "telegram:123", "telegram:456"]:
        response = client.post(
            "/chat", json={**BODY, "thread_id": thread}, headers=AUTH
        )
        assert response.status_code == 200
        assert response.json() == {"content": "ok", "thread_id": thread}
    assert [len(messages) for messages in planner.llm_with_tools.received_messages] == [
        2,
        4,
        2,
    ]


@pytest.mark.parametrize(
    "body",
    [
        {},
        {**BODY, "message": "  "},
        {**BODY, "message": "x" * (TEST_SETTINGS.max_request_characters + 1)},
        {**BODY, "thread_id": " "},
        {**BODY, "thread_id": "x" * 257},
        {**BODY, "unexpected": True},
    ],
)
def test_invalid_requests_do_not_invoke_agent(api, body):
    client, _, planner = api
    assert client.post("/chat", json=body, headers=AUTH).status_code == 422
    assert planner.llm_with_tools.invocations == 0


def test_guard_refusal_has_same_response_schema(api):
    client, _, planner = api
    planner.llm.classification = planner.llm.classification.model_copy(
        update={"confidence": 0.0}
    )
    response = client.post("/chat", json=BODY, headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {
        "content": TRAVEL_REFUSAL,
        "thread_id": BODY["thread_id"],
    }


def test_busy_agent_is_retryable(api):
    client, _, planner = api
    with client.app.state.chat_lock:
        response = client.post("/chat", json=BODY, headers=AUTH)
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "1"
    assert planner.llm_with_tools.invocations == 0


def test_unexpected_errors_are_hidden_and_lock_is_released(api):
    client, agent, _ = api
    with patch.object(
        agent, "chat", side_effect=RuntimeError("private provider details")
    ):
        response = client.post("/chat", json=BODY, headers=AUTH)
    assert response.status_code == 500
    assert response.json() == {"detail": "Travel agent request failed"}
    assert client.post("/chat", json=BODY, headers=AUTH).status_code == 200


def test_startup_requires_service_token():
    with (
        pytest.raises(RuntimeError, match="TRAVEL_AGENT_API_KEY"),
        TestClient(create_app(TEST_SETTINGS, Agent(FakePlanner()))),
    ):
        pass
