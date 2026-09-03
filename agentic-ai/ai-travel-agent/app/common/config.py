import os
from dotenv import load_dotenv
from app.common.models import OpenRouteApiConfig, SerperApiConfig, TavilyApiConfig, WeatherApiConfig

## Config Class

class ConfigProvider:
    def __init__(self):
        load_dotenv()

    def weather_api(self) -> WeatherApiConfig:
        return WeatherApiConfig(api_key= os.getenv('OPENWEATHERMAP_API_KEY'), api_url= os.getenv("OPENWEATHERMAP_API_URL", 'https://api.openweathermap.org/data/2.5/'))

    def openrouter_api(self) -> OpenRouteApiConfig:
        return OpenRouteApiConfig(api_key=os.getenv('OPENROUTER_API_KEY'), model=os.getenv('OPENROUTER_MODEL', 'openrouter/free'))

    def serper_api(self) -> SerperApiConfig:
        return SerperApiConfig(api_key=os.getenv('SERPER_API_KEY'))

    def tavily_api(self) -> TavilyApiConfig:
        return TavilyApiConfig(api_key=os.getenv('TAVILY_API_KEY'))
