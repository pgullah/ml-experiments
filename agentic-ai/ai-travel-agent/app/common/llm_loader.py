from langchain_openrouter import ChatOpenRouter
from app.common.config import ConfigProvider
import traceback


def load_llm(conf: ConfigProvider):
    # ChatOpenAI(model = 'o3-mini', openai_api_key = self.config.get('openai_api_key'))
    model = conf.openrouter_api().model
    print(f"Intializing LLM Provider: OpenRouter with model={model}")
    api_conf = conf.openrouter_api()
    try:
        return ChatOpenRouter(model = model, api_key = api_conf.api_key)
    except Exception as e:
        raise SystemError("Failed to load LLM provider") from e