from langchain_openrouter import ChatOpenRouter
from app.common.config import ConfigProvider
import traceback


def load_llm(conf: ConfigProvider):
    apiKeys = conf.get_api_keys()
    # ChatOpenAI(model = 'o3-mini', openai_api_key = self.config.get('openai_api_key'))
    model = 'openrouter/free'
    print(f"Intializing LLM Provider: OpenRouter with model={model}")
    try:
        return ChatOpenRouter(model = model, api_key = apiKeys.openrouter_api_key)
    except Exception as e:
        raise SystemError("Failed to load LLM provider") from e