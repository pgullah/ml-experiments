import logging

from langchain_openrouter import ChatOpenRouter

from app.common.config import AppSettings

logger = logging.getLogger(__name__)


def load_llm(settings: AppSettings):
    model = settings.openrouter_model
    logger.info("Initializing LLM provider (provider=OpenRouter, model=%s)", model)
    try:
        return ChatOpenRouter(
            model=model,
            api_key=settings.openrouter_api_key,
        )
    except Exception as e:
        raise SystemError("Failed to load LLM provider") from e
