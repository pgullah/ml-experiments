import logging

import requests

from app.common.config import AppSettings
from app.common.errors import ClientError, ServiceError

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self, settings: AppSettings):
        self.base_url = str(settings.currency_api_url)
        self.request_timeout = settings.request_timeout_seconds

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> float:
        """Convert currency from one to another."""
        if amount < 0:
            raise ClientError("Currency amount must not be negative")
        source = from_currency.strip().upper()
        target = to_currency.strip().upper()
        if len(source) != 3 or len(target) != 3:
            raise ClientError("Currency codes must be three-letter ISO codes")

        try:
            logger.info("Converting currency (from=%s, to=%s)", source, target)
            response = requests.get(
                self.base_url,
                params={
                    "amount": amount,
                    "from": source,
                    "to": target,
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            result = response.json()
            return float(result["rates"][target])
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            status = (
                error.response.status_code
                if isinstance(error, requests.RequestException)
                and error.response is not None
                else None
            )
            logger.error(
                "Currency conversion failed (from=%s, to=%s, status=%s)",
                source,
                target,
                status,
            )
            raise ServiceError(
                "Currency conversion is currently unavailable"
            ) from error
