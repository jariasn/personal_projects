import pandas as pd
from ta import add_all_ta_features
from ta.volatility import BollingerBands
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volume import OnBalanceVolumeIndicator
import asyncio
import json
import websockets

class KrakenWebSocketClient:
    def __init__(self, pairs, subscription_types, interval=1, data_handler=None):
        self.ws_url = "wss://ws.kraken.com/"
        self.pairs = pairs
        self.subscription_types = subscription_types
        self.interval = interval
        self.data_handler = data_handler

    async def subscribe(self, websocket):
        for pair in self.pairs:
            for sub_type in self.subscription_types:
                if sub_type == "ohlc":
                    subscribe_message = {
                        "event": "subscribe",
                        "pair": [pair],
                        "subscription": {"name": sub_type, "interval": self.interval}
                    }
                else:
                    subscribe_message = {
                        "event": "subscribe",
                        "pair": [pair],
                        "subscription": {"name": sub_type}
                    }
                await websocket.send(json.dumps(subscribe_message))
                print(f"Subscribed to {sub_type} data for {pair}")

    async def handle_message(self, message):
        data = json.loads(message)

        if 'event' in data and data['event'] == 'heartbeat':
            return

        if 'event' in data and data['event'] == 'subscriptionStatus':
            print(f"Subscription status: {data}")
            return

        if isinstance(data, list) and len(data) > 2 and data[2] == "ohlc":
            ohlc_data = data[1]
            if self.data_handler:
                self.data_handler('ohlc', ohlc_data)
            else:
                print(f"OHLC Data: {ohlc_data}")

        elif isinstance(data, list) and len(data) > 2 and data[2] == "ticker":
            ticker_data = data[1]
            if self.data_handler:
                self.data_handler('ticker', ticker_data)
            else:
                print(f"Ticker Data: {ticker_data}")
        
        elif isinstance(data, list) and len(data) > 2 and data[2] == "trade":
            trade_data = data[1]
            if self.data_handler:
                self.data_handler('trade', trade_data)
            else:
                print(f"Trade Data: {trade_data}")
        
        else:
            print(f"Received message: {data}")

    async def connect(self):
        async with websockets.connect(self.ws_url) as websocket:
            await self.subscribe(websocket)
            while True:
                try:
                    message = await websocket.recv()
                    await self.handle_message(message)
                except websockets.ConnectionClosed:
                    print("WebSocket connection closed")
                    break

    def run(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(self.connect())
            try:
                loop.run_until_complete(task)
            except KeyboardInterrupt:
                print("KeyboardInterrupt: Stopping WebSocket client.")
                task.cancel()
                loop.run_until_complete(task)
        else:
            loop.run_until_complete(self.connect())

