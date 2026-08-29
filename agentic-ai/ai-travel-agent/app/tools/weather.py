import requests
from typing import  Any, Dict
from app.common.config import ConfigProvider


class WeatherTool:
    def __init__(self, conf: ConfigProvider):
        self.api_key = conf.weather_api().api_key
        self.base_url = conf.weather_api().api_url
        
    def get_weather(self, city: str) -> Dict[str, Any]:
        ''' Get the current weather for a given city.'''
        try:
            self.url = f'{self.base_url}weather?q={city}&units=metric&appid={self.api_key}'
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f'Error: {str(e)}')
            return {'Error': str(e)}
        
    def get_forecast(self, city: str, days:int) -> Dict[str, Any]:
        ''' Get the weather forecast for a given city.'''
        try:
            num_intervals = days * 8  # OpenWeatherMap API returns 8 forecasts per day
            self.url = f'{self.base_url}/forecast?q={city}&cnt={num_intervals}&units=metric&appid={self.api_key}'
            
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f'Error: {str(e)}')
            return {'Error': str(e)}
