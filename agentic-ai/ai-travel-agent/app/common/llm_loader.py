from langchain_openrouter import ChatOpenRouter
from app.common.config import AppSettings


def load_llm(settings: AppSettings):
    model = settings.openrouter_model
    print(f"Intializing LLM Provider: OpenRouter with model={model}")
    try:
        return ChatOpenRouter(
            model=model,
            api_key=settings.openrouter_api_key.get_secret_value(),
        )
    except Exception as e:
        raise SystemError("Failed to load LLM provider") from e
