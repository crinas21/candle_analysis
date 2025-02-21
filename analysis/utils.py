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
        f"<b>Bullish:</b> {bullish_}<br>"
        f"<b>Bearish:</b> {bearish_}<br>"
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
                marker=dict(symbol='triangle-up', color='green', size=5),
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
            )
        ]
    )

    fig.update_layout(
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            color='white',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            color='white',
        ),
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent outer area
        font=dict(
            color="white"  # White text for labels
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color="white")  # White legend text
        ),
        height=800
    )
    chart_html = fig.to_html(full_html=False) # Only return chart content
    return chart_html



def identify_patterns(data):
    bullish_single_candlestick_patterns = {
        'Hammer': is_hammer,
        'Inverted Hammer': is_inverted_hammer,
        'White Marubozu': is_white_marubozu,
        'Dragonfly Foji': is_dragonfly_doji,
    }

    bullish_two_candlestick_patterns = {
        'Bullish Engulfing (2)': is_bullish_engulfing,
        'Piercing (2)': is_piercing,
        'Bullish Harami (2)': is_bullish_harami,
        'Tweezer Bottom (2)': is_tweezer_bottom,
        'Bullish Counterattack Line (2)': is_bullish_counterattack_line,
        'Rising Window (2)': is_rising_window,
        'On Neck Bullish (2)': is_on_neck_bullish,
        'In Neck Bullish (2)': is_in_neck_bullish,
    }

    bullish_three_candlestick_patterns = {
        'Morning Star (3)': is_morning_star,
        'Three White Soldiers (3)': is_three_white_soldiers,
        'Three Inside Up (3)': is_three_inside_up,
        'Three Outside Up (3)': is_three_outside_up,
        'Upside Tasuki Gap (3)': is_upside_tasuki_gap,
    }

    bullish_five_candlestick_patterns = {
        'Rising Three Methods (5)': is_rising_three_methods,
        'Mat Hold Bullish (5)': is_mat_hold_bullish,
    }

    bearish_single_candlestick_patterns = {
        'Hanging Man': is_hanging_man,
        'Shooting Star': is_shooting_star,
        'Black Marubozu': is_black_marubozu,
        'Gravestone Doji': is_gravestone_doji,
    }

    bearish_two_candlestick_patterns = {
        'Bearish Engulfing (2)': is_bearish_engulfing,
        'Dark Cloud Cover (2)': is_dark_cloud_cover,
        'Bearish Harami (2)': is_bearish_harami,
        'Tweezer Top (2)': is_tweezer_top,
        'Bearish Counterattack Line (2)': is_bearish_counterattack_line,
        'Falling Window (2)': is_falling_window,
        'On Neck Bearish (2)': is_on_neck_bearish,
        'In Neck Bearish (2)': is_in_neck_bearish,
    }

    bearish_three_candlestick_patterns = {
        'Evening Star (3)': is_evening_star,
        'Three Black Crows (3)': is_three_black_crows,
        'Three Inside Down (3)': is_three_inside_down,
        'Three Outside Down (3)': is_three_outside_down,
    }

    bearish_five_candlestick_patterns = {
        'Falling Three Methods (5)': is_falling_three_methods,
        'Mat Hold Bearish (5)': is_mat_hold_bearish,
    }

    n = len(data)
    for i in range(n):
        # Check single-candlestick patterns
        for pattern_name, pattern_fn in bullish_single_candlestick_patterns.items():
            if pattern_fn(data[i]):
                data[i]['bullish'].add(pattern_name)
        
        for pattern_name, pattern_fn in bearish_single_candlestick_patterns.items():
            if pattern_fn(data[i]):
                data[i]['bearish'].add(pattern_name)

        # Check two-candlestick patterns
        if i < n - 1:
            for pattern_name, pattern_fn in bullish_two_candlestick_patterns.items():
                if pattern_fn(data[i:i+2]):
                    data[i]['bullish'].add(pattern_name)
                    # data[i+1]['bullish'].add(pattern_name)
            
            for pattern_name, pattern_fn in bearish_two_candlestick_patterns.items():
                if pattern_fn(data[i:i+2]):
                    data[i]['bearish'].add(pattern_name)
                    # data[i+1]['bearish'].add(pattern_name)

        # Check three-candlestick patterns
        if i < n - 2:
            for pattern_name, pattern_fn in bullish_three_candlestick_patterns.items():
                if pattern_fn(data[i:i+3]):
                    data[i]['bullish'].add(pattern_name)
                    # data[i+1]['bullish'].add(pattern_name)
                    # data[i+2]['bullish'].add(pattern_name)

            for pattern_name, pattern_fn in bearish_three_candlestick_patterns.items():
                if pattern_fn(data[i:i+3]):
                    data[i]['bearish'].add(pattern_name)
                    # data[i+1]['bearish'].add(pattern_name)
                    # data[i+2]['bearish'].add(pattern_name)

        # Check five-candlestick patterns
        if i < n - 4:
            for pattern_name, pattern_fn in bullish_five_candlestick_patterns.items():
                if pattern_fn(data[i:i+5]):
                    data[i]['bullish'].add(pattern_name)
                    # data[i+1]['bullish'].add(pattern_name)
                    # data[i+2]['bullish'].add(pattern_name)
                    # data[i+3]['bullish'].add(pattern_name)
                    # data[i+4]['bullish'].add(pattern_name)

            for pattern_name, pattern_fn in bearish_five_candlestick_patterns.items():
                if pattern_fn(data[i:i+5]):
                    data[i]['bearish'].add(pattern_name)
                    # data[i+1]['bearish'].add(pattern_name)
                    # data[i+2]['bearish'].add(pattern_name)
                    # data[i+3]['bearish'].add(pattern_name)
                    # data[i+4]['bearish'].add(pattern_name)

        data[i]['bullish'] = ', '.join(data[i]['bullish'])
        data[i]['bearish'] = ', '.join(data[i]['bearish'])

    return data