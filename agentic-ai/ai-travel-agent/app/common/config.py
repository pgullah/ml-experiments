import os
from dotenv import load_dotenv
from app.common.models import ApiKeys, WeatherApiConfig

## Config Class

class ConfigProvider:
    
    def __init__(self):
        load_dotenv()
        
    
    def weather_api(self) -> WeatherApiConfig:
        return WeatherApiConfig(api_key= self.get_api_keys().weather_api_key, api_url= os.getenv("OPENWEATHERMAP_API_URL", 'https://api.openweathermap.org/data/2.5/'))
        
    
    def get_api_keys(self) -> ApiKeys:
        '''
        Returns a dictionary of all configured API Key
        '''
        return ApiKeys(
            weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY'),
            serper_api_key = os.getenv('SERPER_API_KEY'),
            tavily_api_key = os.getenv('TAVILY_API_KEY'),
            openai_api_key = os.getenv('OPENAI_API_KEY'),
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY'),
        )