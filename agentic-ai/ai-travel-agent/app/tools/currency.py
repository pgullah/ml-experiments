import requests

class CurrencyTool:
    
    def __init__(self):
        self.base_url = 'https://api.frankfurter.dev/v1/latest'
        
    def convert_currency(self,amount:float, from_currency: str, to_currency: str ) -> float:
        ''' Convert currency from one to another.'''
        try:
            url = f'{self.base_url}?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            return result['rates'][to_currency]
        except Exception as e:
            print(f'Error: {str(e)}')
            return None