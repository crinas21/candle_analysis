import requests
from .patterns import *
from django.conf import settings
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


def get_alpha_data(symbol, compact):
    print(f"API Called for Symbol: {symbol}, Compact: {compact}")
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'compact' if compact else 'full',
        'apikey': settings.ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get('https://www.alphavantage.co/query', params=params)
    if response.status_code == 200:
        data = response.json().get("Time Series (Daily)", {})
    else:
        data = {}
    return data


def get_pattern_data(alpha_data):
    pattern_data = [
        {
            'date': date,
            'open': round(float(alpha_data.get(date).get('1. open')), 2),
            'high': round(float(alpha_data.get(date).get('2. high')), 2),
            'low': round(float(alpha_data.get(date).get('3. low')), 2),
            'close': round(float(alpha_data.get(date).get('4. close')), 2),
            'volume': int(alpha_data.get(date).get('5. volume')),
            'bullish': set(),
            'bearish': set()
        }
        for date in alpha_data
    ]
    pattern_data = identify_patterns(pattern_data)
    return pattern_data


def get_chart_html(pattern_data):
    sorted_data = sorted(pattern_data, key=lambda x: x['date'], reverse=True)

    dates = [item['date'] for item in sorted_data]
    opens = [float(item['open']) for item in sorted_data]
    highs = [float(item['high']) for item in sorted_data]
    lows = [float(item['low']) for item in sorted_data]
    closes = [float(item['close']) for item in sorted_data]
    volumes = [int(item['volume']) for item in sorted_data]
    bullish = [item['bullish'] for item in sorted_data]
    bearish = [item['bearish'] for item in sorted_data]

    hover_text = [
        f"<b>Date:</b> {date}<br>"
        f"<b>Open:</b> {open_}<br>"
        f"<b>High:</b> {high}<br>"
        f"<b>Low:</b> {low}<br>"
        f"<b>Close:</b> {close}<br>"
        f"<b>Volume:</b> {volume}<br>"
        f"<b><span style='color:green'>Bullish:</span></b> {bullish_}<br>"
        f"<b><span style='color:red'>Bearish:</span></b> {bearish_}<br>"
        for date, open_, high, low, close, volume, bullish_, bearish_ in zip(
            dates, opens, highs, lows, closes, volumes, bullish, bearish
        )
    ]

    fig = go.Figure(data=[
            go.Candlestick(
                x=dates,
                open=opens,
                high=highs,
                low=lows,
                close=closes,
                hovertext=hover_text,
                hoverinfo="text",
                increasing=dict(line=dict(width=1)),  # Decrease border weight
                decreasing=dict(line=dict(width=1)),
                name="Candlestick"
            ),
            go.Scatter(     # Triangle indicator for bullish pattern
                x=[item['date'] for item in sorted_data if item['bullish']], # Bullish dates
                y=[item['high'] for item in sorted_data if item['bullish']], # Bullish highs
                mode='markers',
                marker=dict(symbol='triangle-up', color='lime', size=5),
                hoverinfo='skip',
                name='Bullish Pattern'
            ),
            go.Scatter(     # Triangle indicator for bearish pattern
                x=[item['date'] for item in sorted_data if item['bearish']], # Bearish dates
                y=[item['low'] for item in sorted_data if item['bearish']], # Bearish lows
                mode='markers',
                marker=dict(symbol='triangle-down', color='red', size=5),
                hoverinfo='skip',
                name='Bearish Pattern'
            )]
        )
    

    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5),
        height=800
    )
    chart_html = fig.to_html(full_html=False) # Only return chart content
    return chart_html


def identify_patterns(data):
    n = len(data)
    for i in range(n):
        # Check single-candlestick patterns
        candle = data[i]
        if is_hammer(candle):
            data[i]['bullish'].add('Hammer')
        if is_inverted_hammer(candle):
            data[i]['bullish'].add('Inverted Hammer')

        # Check two-candlestick patterns
        if i < n - 1:
            candles = data[i:i+2]
            if is_bullish_engulfing(candles):
                data[i]['bullish'].add('Bullish Engulfing')
                data[i+1]['bullish'].add('Bullish Engulfing')
            if is_piercing(candles):
                data[i]['bullish'].add('Piercing')
                data[i+1]['bullish'].add('Piercing')
        
        # Check three-candlestick patterns
        if i < n - 2:
            candles = data[i:i+3]
            if is_morning_star(candles):
                data[i]['bullish'].add('Morning Star')
                data[i+1]['bullish'].add('Morning Star')
                data[i+2]['bullish'].add('Morning Star')
            if is_three_white_soldiers(candles):
                data[i]['bullish'].add('Three White Soldiers')
                data[i+1]['bullish'].add('Three White Soldiers')
                data[i+2]['bullish'].add('Three White Soldiers')
            if is_three_black_crows(candles):  # Pass the next 3 candlesticks
                data[i]['bearish'].add('Three Black Crows')
                data[i+1]['bearish'].add('Three Black Crows')
                data[i+2]['bearish'].add('Three Black Crows')

        # Check four-candlestick patterns
        if i < n - 3:
            pass

        data[i]['bullish'] = ', '.join(list(data[i]['bullish']))
        data[i]['bearish'] = ', '.join(list(data[i]['bearish']))
    
    return data