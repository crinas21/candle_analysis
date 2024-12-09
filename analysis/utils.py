import requests
from django.conf import settings
import pandas as pd
import plotly.graph_objects as go


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


def get_alpha_data(symbol, days):
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
    return data


def get_table_data(alpha_data):
    results = [
        {
            'date': date,
            'open': alpha_data.get(date).get('1. open'),
            'high': alpha_data.get(date).get('2. high'),
            'low': alpha_data.get(date).get('3. low'),
            'close': alpha_data.get(date).get('4. close'),
            'volume': alpha_data.get(date).get('5. volume')
        }
        for date in alpha_data
    ]
    return results


def get_chart_data(alpha_data):
    df = pd.DataFrame.from_dict(alpha_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.astype({
        'open': 'float',
        'high': 'float',
        'low': 'float',
        'close': 'float',
        'volume': 'int'
    })
    df = df.sort_index(ascending=False)
    df = df.reset_index()  # Reset the index and add it as a column
    df.rename(columns={'index': 'date'}, inplace=True)

    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
    chart_html = fig.to_html(full_html=False)  # Only return chart content
    return chart_html



def three_black_crows(points):
    pass