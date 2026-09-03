from dataclasses import dataclass

@dataclass
class BaseApiConfig:
    api_key: str

@dataclass
class LLMResponse:
    pass

@dataclass
class WeatherApiConfig(BaseApiConfig):
    api_url: str

@dataclass
class DuckDuckGoApiConfig(BaseApiConfig):
    pass

@dataclass
class OpenRouteApiConfig(BaseApiConfig):
    model: str

@dataclass
class SerperApiConfig(BaseApiConfig):
    pass

@dataclass
class TavilyApiConfig(BaseApiConfig):
    pass
