from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from app.common.errors import ServiceError
from app.prompt.prompt_router import route
from tests.support.fakes import TEST_SETTINGS


def _openai_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class TestPromptRouting:
    def test_router_validates_and_returns_a_known_prompt(self, monkeypatch):
        create = Mock(
            return_value=_openai_response(
                '{"primary_prompt":"system-prompt",'
                '"secondary_prompts":[],"reason":"default"}'
            )
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        openai = Mock(return_value=client)
        monkeypatch.setattr("app.prompt.prompt_router.OpenAI", openai)
        settings = TEST_SETTINGS.model_copy(
            update={"openai_api_key": SecretStr("router-key")}
        )

        result = route("Plan a trip", settings)

        assert result.primary_prompt == "system-prompt"
        openai.assert_called_once_with(api_key="router-key", timeout=10)

    def test_router_rejects_unknown_prompt_ids(self, monkeypatch):
        create = Mock(
            return_value=_openai_response(
                '{"primary_prompt":"invented","secondary_prompts":[],"reason":"bad"}'
            )
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        monkeypatch.setattr(
            "app.prompt.prompt_router.OpenAI", Mock(return_value=client)
        )
        settings = TEST_SETTINGS.model_copy(
            update={"openai_api_key": SecretStr("router-key")}
        )

        with pytest.raises(ServiceError, match="unknown prompt"):
            route("Plan a trip", settings)

    def test_router_requires_a_configured_key(self):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            route("Plan a trip", TEST_SETTINGS)

    def test_router_rejects_empty_requests(self):
        with pytest.raises(ValueError, match="must not be empty"):
            route("   ", TEST_SETTINGS)
