import logging
from typing import Any

import requests

from app.common.config import AppSettings

logger = logging.getLogger(__name__)


class WeatherTool:
    def __init__(self, settings: AppSettings):
        self.api_key = settings.openweathermap_api_key.get_secret_value()
        self.base_url = str(settings.openweathermap_api_url).rstrip("/")
        self.request_timeout = settings.request_timeout_seconds

    def get_weather(self, city: str) -> dict[str, Any]:
        """Get the current weather for a given city."""
        try:
            self.url = f"{self.base_url}/weather"
            response = requests.get(
                self.url,
                params={"q": city, "units": "metric", "appid": self.api_key},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.exception(f"Failed to get weather for {city}")
            return {"Error": str(e)}

    def get_forecast(self, city: str, days: int) -> dict[str, Any]:
        """Get the weather forecast for a given city."""
        try:
            days = max(1, min(days, 5))
            num_intervals = days * 8  # OpenWeatherMap API returns 8 forecasts per day
            self.url = f"{self.base_url}/forecast"

            response = requests.get(
                self.url,
                params={
                    "q": city,
                    "cnt": num_intervals,
                    "units": "metric",
                    "appid": self.api_key,
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.exception(f"Failed to get forecast for {city}")
            return {"Error": str(e)}
