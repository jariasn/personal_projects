from kraken import KrakenWebSocketClient

def print_close_price(data_type, data):
    if data_type == 'ohlc':
        # Assuming the close price is the last item in the OHLC data list
        close_price = data[-2]  # OHLC data structure: [time, open, high, low, close, ...]
        print(f"Close Price: {close_price}")

pairs = ["BTC/USD"]
subscription_types = ["ohlc"]

client = KrakenWebSocketClient(pairs, subscription_types, interval=1, data_handler=print_close_price)
client.run()
