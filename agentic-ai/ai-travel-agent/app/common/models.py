

from dataclasses import dataclass


@dataclass
class ApiKeys:
    weather_api_key: str
    serper_api_key: str
    tavily_api_key: str
    openai_api_key: str
    openrouter_api_key: str
    
@dataclass
class LLMResponse:
    pass

@dataclass
class WeatherApiConfig:
    api_key: str
    api_url: str
    
@dataclass
class DuckDuckGoApiConfig:
    api_key: str

@dataclass
class OpenRouteApiConfig:
    api_key: str
    model: str