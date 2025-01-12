# Bullish
def is_hammer(candle):
    c = candle
    real_body = abs(c['open'] - c['close'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])
    total_range = c['high'] - c['low']

    is_small_body = real_body <= total_range * 0.25
    is_long_lower_wick = lower_wick >= real_body * 2 
    is_small_upper_wick = upper_wick <= real_body * 0.3 # Needs work

    return is_small_body and is_long_lower_wick and is_small_upper_wick


def is_inverted_hammer(candle):
    c = candle
    real_body = abs(c['open'] - c['close'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])
    total_range = c['high'] - c['low']

    is_small_body = real_body <= total_range * 0.25
    is_long_upper_wick = upper_wick >= real_body * 2 
    is_small_lower_wick = lower_wick <= real_body * 0.3

    return is_small_body and is_long_upper_wick and is_small_lower_wick


def is_white_marubozu(candle):
    c = candle
    real_body = abs(c['close'] - c['open'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])
    total_range = c['high'] - c['low']
    is_bullish = c['close'] > c['open']
    is_large_body = real_body >= total_range * 0.75
    is_small_upper_wick = upper_wick <= real_body * 0.2
    is_small_lower_wick = lower_wick <= real_body * 0.2

    return is_bullish and is_large_body and is_small_upper_wick and is_small_lower_wick


def is_dragonfly_doji(candle):
    c = candle
    real_body = abs(c['open'] - c['close'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])

    no_body = real_body == 0
    is_long_lower_wick = lower_wick >= real_body * 2 
    is_small_upper_wick = upper_wick <= real_body * 0.3 # Needs work

    return no_body and is_long_lower_wick and is_small_upper_wick


def is_bullish_engulfing(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c2_engulfs_c1 = c2['close'] > c1['open'] and c2['open'] < c1['close']

    return c1_bearish and c2_bullish and c2_engulfs_c1


def is_piercing(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c2_open_below_c1_close = c2['open'] < c1['close']
    c2_close_above_c1_midway = c2['close'] > (c1['open'] + c1['close'])/2 and c2['close'] <= c1['open']

    return c1_bearish and c2_bullish and c2_open_below_c1_close and c2_close_above_c1_midway


def is_bullish_harami(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c2_inside_c1 = c2['close'] < c1['open'] and c2['open'] > c1['close']

    return c1_bearish and c2_bullish and c2_inside_c1


def is_tweezer_bottom(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    similar_bottoms = abs(c1['low'] - c2['low']) < 0.1 * min((c1['open'] - c1['close']), (c2['close'] - c2['open']))

    return c1_bearish and c2_bullish and similar_bottoms


def is_bullish_counterattack_line(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c1_big_to_c2 = abs(c1['open'] - c1['close']) > 3 * abs(c2['close'] - c2['open'])
    gap_exists = c2['open'] < c1['close']
    similar_close = abs(c1['close'] - c2['close']) < 0.1 * min((c1['high'] - c1['low']), (c2['high'] - c2['low']))

    return c1_bearish and c2_bullish and c1_big_to_c2 and gap_exists and similar_close


def is_morning_star(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c3_bullish = c3['close'] > c3['open']
    non_overlapping = max(c2['close'], c2['open']) < min(c1['close'], c3['open'])
    small_second = abs(c2['open'] - c2['close']) < min(abs(c1['open'] - c1['close']), abs(c3['close'] - c3['open'])) * 0.3

    return c1_bearish and c3_bullish and non_overlapping and small_second


def is_three_white_soldiers(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    all_bullish = c1['close'] > c1['open'] and c2['close'] > c2['open'] and c3['close'] > c3['open']
    c2_open_in_c1_body = c2['open'] > c1['open'] and c2['open'] < c1['close']
    c3_open_in_c2_body = c3['open'] > c2['open'] and c3['open'] < c2['close']
    progressive_higher_closes = c3['close'] > c2['close'] > c1['close']
    # Check all small wicks
    for c in candles:
        real_body = abs(c['open'] - c['close'])
        lower_wick = min(c['open'], c['close']) - c['low']
        upper_wick = c['high'] - max(c['open'], c['close'])
        if lower_wick > real_body * 0.3 or upper_wick > real_body * 0.3:
            return False
    
    return all_bullish and c2_open_in_c1_body and c3_open_in_c2_body and progressive_higher_closes


def is_three_inside_up(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c2_close_above_c1_50 = c2['close'] > ((c1['close'] + c1['open']) / 2)
    c3_close_above_c1 = c3['close'] > c1['open']

    return c1_bearish and c2_bullish and c2_close_above_c1_50 and c3_close_above_c1


def is_three_outside_up(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bearish = c1['close'] < c1['open']
    c2_bullish = c2['close'] > c2['open']
    c2_engulfs_c1 = c2['close'] > c1['open'] and c2['open'] < c1['close']
    c3_bullish = c3['close'] > c3['open']
    c3_closes_above = c3['close'] > c2['close'] and c3['close'] > c1['open']

    return c1_bearish and c2_bullish and c2_engulfs_c1 and c3_bullish and c3_closes_above


# Bearish
def is_hanging_man(candles):
    return False


def is_shooting_star(candles):
    return False


def is_black_marubozu(candle):
    c = candle
    real_body = abs(c['open'] - c['close'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])
    total_range = c['high'] - c['low']
    is_bearish = c['close'] < c['open']
    is_large_body = real_body >= total_range * 0.75
    is_small_upper_wick = upper_wick <= real_body * 0.2
    is_small_lower_wick = lower_wick <= real_body * 0.2

    return is_bearish and is_large_body and is_small_upper_wick and is_small_lower_wick


def is_gravestone_doji(candle):
    c = candle
    real_body = abs(c['open'] - c['close'])
    lower_wick = min(c['open'], c['close']) - c['low']
    upper_wick = c['high'] - max(c['open'], c['close'])

    no_body = real_body == 0
    is_long_upper_wick = upper_wick >= real_body * 2 
    is_small_lower_wick = lower_wick <= real_body * 0.3

    return no_body and is_long_upper_wick and is_small_lower_wick


def is_bearish_engulfing(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c2_engulfs_c1 = c2['open'] > c1['close'] and c2['close'] < c1['open']

    return c1_bullish and c2_bearish and c2_engulfs_c1


def is_dark_cloud_cover(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles


    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c2_open_above_c1_close = c2['open'] > c1['close']
    c2_close_below_c1_midway = c2['close'] < (c1['open'] + c1['close'])/2 and c2['close'] >= c1['open']

    return c1_bullish and c2_bearish and c2_open_above_c1_close and c2_close_below_c1_midway


def is_bearish_harami(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c2_inside_c1 = c2['close'] > c1['open'] and c2['open'] < c1['close']

    return c1_bullish and c2_bearish and c2_inside_c1


def is_tweezer_top(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    similar_tops = abs(c1['high'] - c2['high']) < 0.1 * min((c1['open'] - c1['close']), (c2['close'] - c2['open']))

    return c1_bullish and c2_bearish and similar_tops


def is_evening_star(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c3_bearish = c3['close'] < c3['open']
    non_overlapping = min(c2['close'], c2['open']) > max(c1['close'], c3['open'])
    small_second = abs(c2['open'] - c2['close']) < min(abs(c1['close'] - c1['open']), abs(c3['open'] - c3['close'])) * 0.3
    return c1_bullish and c3_bearish and non_overlapping and small_second


def is_three_black_crows(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    all_bearish = c1['close'] < c1['open'] and c2['close'] < c2['open'] and c3['close'] < c3['open']
    c2_open_in_c1_body = c2['open'] < c1['open'] and c2['open'] > c1['close']
    c3_open_in_c2_body = c3['open'] < c2['open'] and c3['open'] > c2['close']
    progressive_lower_closes = c3['close'] < c2['close'] < c1['close']
    # Check all small wicks
    for c in candles:
        real_body = abs(c['open'] - c['close'])
        lower_wick = min(c['open'], c['close']) - c['low']
        upper_wick = c['high'] - max(c['open'], c['close'])
        if lower_wick > real_body * 0.3 or upper_wick > real_body * 0.3:
            return False

    return all_bearish and c2_open_in_c1_body and c3_open_in_c2_body and progressive_lower_closes


def is_three_inside_down(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c2_close_below_c1_50 = c2['close'] < ((c1['close'] + c1['open']) / 2)
    c3_close_below_c1 = c3['close'] < c1['open']

    return c1_bullish and c2_bearish and c2_close_below_c1_50 and c3_close_below_c1


def is_three_outside_down(candles):
    if len(candles) != 3:
        return False
    c3, c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c2_engulfs_c1 = c2['open'] > c1['close'] and c2['close'] < c1['open']
    c3_bearish = c3['close'] < c3['open']
    c3_closes_below = c3['close'] < c2['close'] and c3['close'] < c1['open']

    return c1_bullish and c2_bearish and c2_engulfs_c1 and c3_bearish and c3_closes_below


def is_bearish_counterattack_line(candles):
    if len(candles) != 2:
        return False
    c2, c1 = candles

    c1_bullish = c1['close'] > c1['open']
    c2_bearish = c2['close'] < c2['open']
    c1_big_to_c2 = abs(c1['close'] - c1['open']) > 3 * abs(c2['open'] - c2['close'])
    gap_exists = c2['open'] > c1['close']
    similar_close = abs(c1['close'] - c2['close']) < 0.1 * min((c1['high'] - c1['low']), (c2['high'] - c2['low']))

    return c1_bullish and c2_bearish and c1_big_to_c2 and gap_exists and similar_close