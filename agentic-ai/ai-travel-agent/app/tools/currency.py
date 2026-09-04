import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

class CurrencyTool:
    
    def __init__(self):
        self.base_url = 'https://api.frankfurter.dev/v1/latest'
        
    def convert_currency(self,amount:float, from_currency: str, to_currency: str ) -> Optional[float]:
        ''' Convert currency from one to another.'''
        try:
            logger.info(f"Converting {amount} from {from_currency} to {to_currency}")
            response = requests.get(
                self.base_url,
                params={"amount": amount, "from": from_currency.upper(), "to": to_currency.upper()},
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            return result['rates'][to_currency.upper()]
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return None
