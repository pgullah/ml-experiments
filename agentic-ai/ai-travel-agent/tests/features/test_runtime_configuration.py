import pytest
from pydantic import ValidationError

from app.common.config import AppSettings
from app.prompt.prompt_loader import load_prompts


class TestRuntimeConfiguration:
    def test_core_service_credentials_are_required(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("OPENWEATHERMAP_API_KEY", raising=False)
        with pytest.raises(ValidationError) as error:
            AppSettings(_env_file=None)

        missing_fields = {item["loc"][0] for item in error.value.errors()}
        assert missing_fields == {
            "openrouter_api_key",
            "openweathermap_api_key",
        }

    def test_environment_values_are_parsed_and_secrets_are_masked(self, monkeypatch):
        environment = {
            "OPENROUTER_API_KEY": "router-secret",
            "OPENWEATHERMAP_API_KEY": "weather-secret",
            "MAX_CONTEXT_MESSAGES": "7",
            "REQUEST_TIMEOUT_SECONDS": "2.5",
        }

        for name, value in environment.items():
            monkeypatch.setenv(name, value)
        settings = AppSettings(_env_file=None)

        assert settings.max_context_messages == 7
        assert settings.request_timeout_seconds == 2.5
        assert "router-secret" not in repr(settings)

    def test_invalid_operational_limits_are_rejected(self):
        with pytest.raises(ValidationError):
            AppSettings(
                _env_file=None,
                openrouter_api_key="router-secret",
                openweathermap_api_key="weather-secret",
                max_context_messages=0,
            )

    def test_plain_markdown_prompts_are_available(self):
        prompts = load_prompts()

        assert prompts
        assert all(prompt["prompt"] for prompt in prompts)
