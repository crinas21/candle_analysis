import requests
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
            'bullish': '',
            'bearish': ''
        }
        for date in alpha_data
    ]
    pattern_data = all_patterns(pattern_data)
    for candlestick in pattern_data:
        candlestick['bullish'] = candlestick['bullish'].rstrip(', ')
        candlestick['bearish'] = candlestick['bearish'].rstrip(', ')
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

    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=opens,
        high=highs,
        low=lows,
        close=closes,
        hovertext=hover_text,
        hoverinfo="text",
        increasing=dict(line=dict(width=1)),  # Decrease border weight
        decreasing=dict(line=dict(width=1))
    )])

    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        height=800
    )
    chart_html = fig.to_html(full_html=False) # Only return chart content
    return chart_html



def all_patterns(data):
    pattern_data = data
    pattern_data = hammer(pattern_data)
    pattern_data = three_black_crows(pattern_data)
    return pattern_data


def hammer(data):
    for candlestick in data:
        open = candlestick['open']
        close = candlestick['close']
        high = candlestick['high']
        low = candlestick['low']

        real_body = abs(open - close)
        lower_wick = min(open, close) - low
        upper_wick = high - max(open, close)
        total_range = high - low

        is_small_body = real_body <= total_range * 0.25
        is_long_lower_wick = lower_wick >= real_body * 2 
        is_small_upper_wick = upper_wick <= real_body * 0.3 # Needs work

        if is_small_body and is_long_lower_wick and is_small_upper_wick:
            candlestick['bullish'] += 'Hammer, '

    return data



def three_black_crows(data):
    return data