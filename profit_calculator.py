# Calculate profit from trading based on bullish and bearish candlestick patterns

import requests

def main():
    symbol = 'ENPH'
    days = 99
    params = {
        'symbol': symbol,
        'days': days,
    }
    response = requests.get("https://candleanalysis.vercel.app/analysis", params=params, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        print('Error getting request response')
        exit()
    candles = response.json().get('candlestick_data')
    candles.reverse()

    initial_cash = 1000
    shares = 0
    cash = initial_cash

    for candle in candles:
        close_price = candle.get('close')
        bullish_patterns = candle.get('bullish').split(', ')
        bearish_patterns = candle.get('bearish').split(', ')

        if bullish_patterns == ['']:
            bullish_patterns = []
        if bearish_patterns == ['']:
            bearish_patterns = []

        bullish_count = len(bullish_patterns)
        bearish_count = len(bearish_patterns)

        if bullish_count > bearish_count: # Buy as many shares as possible
            max_shares_to_buy = int(cash // close_price)
            shares += max_shares_to_buy
            cash -= max_shares_to_buy * close_price
            cash -= (0.005 * shares + 0.0003 * close_price)
        elif bullish_count < bearish_count and shares > 0: # Sell all shares
            cash += shares * close_price
            cash -= (0.005 * shares + 0.0003 * close_price)
            shares = 0


    final_investment = shares * candles[-1].get('close')
    profit = final_investment + cash - initial_cash
    profit_if_held = (initial_cash // candles[0].get('close')) * (candles[-1].get('close') - candles[0].get('close'))

    print(f"Symbol: {symbol}")
    print(f"Days: {days}")
    print(f"Initial cash: {initial_cash}")
    print(f"Final cash: {cash:.2f}")
    print(f"Final shares: {shares}")
    print(f"Final portfolio value: {final_investment:.2f}")
    print(f"Profit if just held through: {profit_if_held:.2f}")
    print(f"Profit: {profit:.2f}")


if __name__ == '__main__':
    main()