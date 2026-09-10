import logging
from typing import Any

import requests

from app.common.config import AppSettings
from app.common.errors import ServiceError

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self, settings: AppSettings):
        self.api_key = settings.openweathermap_api_key.get_secret_value()
        self.base_url = str(settings.openweathermap_api_url).rstrip("/")
        self.request_timeout = settings.request_timeout_seconds

    def get_weather(self, city: str) -> dict[str, Any]:
        """Get the current weather for a given city."""
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={"q": city, "units": "metric", "appid": self.api_key},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Weather response must be an object")
            return payload
        except (requests.RequestException, ValueError, TypeError) as error:
            status = (
                error.response.status_code
                if isinstance(error, requests.RequestException)
                and error.response is not None
                else None
            )
            logger.error(
                "Weather request failed (city=%s, status=%s)",
                city,
                status,
            )
            raise ServiceError(
                "Weather information is currently unavailable"
            ) from error

    def get_forecast(self, city: str, days: int) -> dict[str, Any]:
        """Get the weather forecast for a given city."""
        try:
            days = max(1, min(days, 5))
            num_intervals = days * 8  # OpenWeatherMap API returns 8 forecasts per day
            response = requests.get(
                f"{self.base_url}/forecast",
                params={
                    "q": city,
                    "cnt": num_intervals,
                    "units": "metric",
                    "appid": self.api_key,
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Weather forecast response must be an object")
            return payload
        except (requests.RequestException, ValueError, TypeError) as error:
            status = (
                error.response.status_code
                if isinstance(error, requests.RequestException)
                and error.response is not None
                else None
            )
            logger.error(
                "Weather forecast request failed (city=%s, status=%s)",
                city,
                status,
            )
            raise ServiceError("Weather forecast is currently unavailable") from error


# Backwards-compatible import for callers that have not migrated yet.
WeatherTool = WeatherService
