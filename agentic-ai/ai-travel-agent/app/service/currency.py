import logging

import requests

from app.common.config import AppSettings

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self, settings: AppSettings):
        self.base_url = str(settings.currency_api_url)
        self.request_timeout = settings.request_timeout_seconds

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> float | None:
        """Convert currency from one to another."""
        try:
            logger.info(f"Converting {amount} from {from_currency} to {to_currency}")
            response = requests.get(
                self.base_url,
                params={
                    "amount": amount,
                    "from": from_currency.upper(),
                    "to": to_currency.upper(),
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            result = response.json()
            return result["rates"][to_currency.upper()]
        except requests.HTTPError:
            logger.exception(
                f"Failed to convert currency from {from_currency} to {to_currency}"
            )
            return None
