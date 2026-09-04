from pathlib import Path

from pydantic import AnyHttpUrl, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILES = (
    PROJECT_ROOT.parent / ".env",
    PROJECT_ROOT / ".env",
)


class AppSettings(BaseSettings):
    """Validated, immutable snapshot of application configuration."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    openrouter_api_key: SecretStr
    openrouter_model: str = "openrouter/free"

    openweathermap_api_key: SecretStr
    openweathermap_api_url: AnyHttpUrl = AnyHttpUrl(
        "https://api.openweathermap.org/data/2.5/"
    )

    serper_api_key: SecretStr | None = None
    serper_api_url: AnyHttpUrl = AnyHttpUrl("https://google.serper.dev/search")
    tavily_api_key: SecretStr | None = None
    tavily_api_url: AnyHttpUrl = AnyHttpUrl("https://api.tavily.com/search")
    search_max_results: int = Field(default=5, ge=1, le=20)

    prompt_dir: Path | None = None
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.6"

    max_context_messages: PositiveInt = 5
    max_context_characters: PositiveInt = 4_000
    max_request_characters: PositiveInt = 4_000

    currency_api_url: AnyHttpUrl = AnyHttpUrl(
        "https://api.frankfurter.dev/v1/latest"
    )
    request_timeout_seconds: float = Field(default=10.0, gt=0, le=120)
