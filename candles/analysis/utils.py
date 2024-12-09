import requests
from django.conf import settings

def get_matches(query):
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': query,
        'apikey': settings.ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get('https://www.alphavantage.co/query', params=params)
    if response.status_code == 200:
        data = response.json().get('bestMatches', [])
    else:
        data = []

    matches = [
        {
            'symbol': match.get('1. symbol'),
            'name': match.get('2. name'),
            'type': match.get('3. type'),
            'region': match.get('4. region'),
            'currency': match.get('8. currency')
        }
        for match in data if match.get('3. type') in ['Equity', 'ETF']
    ]
    return matches


def get_symbol_data(symbol, days):
    if days <= 100:
        outputsize = 'compact'
    else:
        outputsize = 'full'

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': outputsize,
        'apikey': settings.ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get('https://www.alphavantage.co/query', params=params)
    if response.status_code == 200:
        data = response.json().get("Time Series (Daily)", {})
    else:
        data = {}

    results = [
        {
            'date': date,
            'open': data.get(date).get('1. open'),
            'high': data.get(date).get('2. high'),
            'low': data.get(date).get('3. low'),
            'close': data.get(date).get('4. close'),
            'volume': data.get(date).get('5. volume')
        }
        for date in data
    ]
    return results