from typing import Optional

import requests

class CurrencyTool:
    
    def __init__(self):
        self.base_url = 'https://api.frankfurter.dev/v1/latest'
        
    def convert_currency(self,amount:float, from_currency: str, to_currency: str ) -> Optional[float]:
        ''' Convert currency from one to another.'''
        try:
            response = requests.get(
                self.base_url,
                params={"amount": amount, "from": from_currency.upper(), "to": to_currency.upper()},
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            return result['rates'][to_currency.upper()]
        except Exception as e:
            print(f'Error: {str(e)}')
            return None
