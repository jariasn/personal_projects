import pandas as pd
from ta import add_all_ta_features
from ta.volatility import BollingerBands
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volume import OnBalanceVolumeIndicator
import kraken


ohlc_data = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

def handle_data(data_type, data):
    global ohlc_data

    if data_type == 'ohlc':
        row = {
            "timestamp": pd.to_datetime(float(data[0]), unit='s'),
            "open": float(data[2]),
            "high": float(data[3]),
            "low": float(data[4]),
            "close": float(data[5]),
            "volume": float(data[7])
        }
        ohlc_data = ohlc_data.append(row, ignore_index=True)
        print("OHLC Data added to DataFrame")

        ohlc_data = ohlc_data.tail(1000)

        calculate_indicators()

def calculate_indicators():
    global ohlc_data

    ohlc_data = ohlc_data.sort_values(by='timestamp')

    ohlc_data['sma'] = SMAIndicator(close=ohlc_data['close'], window=14).sma_indicator()
    ohlc_data['ema'] = EMAIndicator(close=ohlc_data['close'], window=14).ema_indicator()
    ohlc_data['rsi'] = RSIIndicator(close=ohlc_data['close'], window=14).rsi()
    macd = MACD(close=ohlc_data['close'])
    ohlc_data['macd'] = macd.macd()
    ohlc_data['macd_signal'] = macd.macd_signal()
    ohlc_data['macd_diff'] = macd.macd_diff()
    bollinger = BollingerBands(close=ohlc_data['close'])
    ohlc_data['bollinger_mavg'] = bollinger.bollinger_mavg()
    ohlc_data['bollinger_hband'] = bollinger.bollinger_hband()
    ohlc_data['bollinger_lband'] = bollinger.bollinger_lband()
    stoch = StochasticOscillator(high=ohlc_data['high'], low=ohlc_data['low'], close=ohlc_data['close'])
    ohlc_data['stoch'] = stoch.stoch()
    ohlc_data['obv'] = OnBalanceVolumeIndicator(close=ohlc_data['close'], volume=ohlc_data['volume']).on_balance_volume()
    ohlc_data['adx'] = ADXIndicator(high=ohlc_data['high'], low=ohlc_data['low'], close=ohlc_data['close']).adx()

    print(ohlc_data.tail(1))

if __name__ == "__main__":
    pairs = ["XBT/USD"]
    subscription_types = ["ohlc"]
    interval = 1

    client = kraken.KrakenWebSocketClient(pairs, subscription_types, interval, data_handler=handle_data)
    client.run()
