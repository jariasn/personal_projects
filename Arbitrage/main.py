import os
import requests
import time
from itertools import permutations
import logging
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import urllib.parse
import json

class KrakenTriangularArbitrage:
    def __init__(self, api_key=None, api_secret=None, base_currencies=['USD', 'EUR', 'BTC', 'ETH']):
        self.base_url = "https://api.kraken.com/0/public"
        self.private_url = "https://api.kraken.com/0/private"
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_currencies = base_currencies
        self.pairs_data = {}
        self.logger = self._setup_logger()
        self.fee_tiers = self._get_fee_tiers()
        self.cached_volume = None
        self.volume_last_updated = None
        self.trading_fees = None
        self.available_pairs_cache = None
        self.asset_mapping_cache = None
        
    def _setup_logger(self):
        logger = logging.getLogger('triangular_arbitrage')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _get_kraken_signature(self, urlpath, data):
        """Generate Kraken API signature."""
        if not self.api_secret:
            return None
            
        post_data = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + post_data).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        try:
            mac = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
            sig_digest = base64.b64encode(mac.digest())
            return sig_digest.decode()
        except Exception as e:
            self.logger.error(f"Error generating API signature: {str(e)}")
            return None

    def _get_nonce(self):
        """Generate a valid nonce for Kraken API."""
        return str(int(time.time() * 1000))

    def _get_fee_tiers(self):
        """Get Kraken's fee tiers structure."""
        # Return default fee tiers (may need periodic updates if Kraken’s structure changes)
        return {
            '0': {'maker': 0.0026, 'taker': 0.0026},    # $0 - $50,000
            '50000': {'maker': 0.0024, 'taker': 0.0026},
            '100000': {'maker': 0.0022, 'taker': 0.0024},
            '250000': {'maker': 0.0020, 'taker': 0.0022},
            '500000': {'maker': 0.0018, 'taker': 0.0020},
            '1000000': {'maker': 0.0016, 'taker': 0.0018},
            '2500000': {'maker': 0.0014, 'taker': 0.0016},
            '5000000': {'maker': 0.0012, 'taker': 0.0014},
            '10000000': {'maker': 0.0010, 'taker': 0.0012},
        }

    def _get_trading_volume(self):
        """Get 30-day trading volume for fee calculation with caching for efficiency."""
        if not self.api_key or not self.api_secret:
            self.logger.warning("No API credentials provided. Using default highest fees.")
            return 0

        # Cache volume for 1 hour
        if (self.cached_volume is not None and self.volume_last_updated is not None and 
            datetime.now() - self.volume_last_updated < timedelta(hours=1)):
            return self.cached_volume

        try:
            data = {
                'nonce': self._get_nonce(),
                'pair': 'XXBTZUSD'  # Example pair for volume calculation
            }
            
            signature = self._get_kraken_signature('/0/private/TradeVolume', data)
            if not signature:
                return 0
                
            headers = {
                'API-Key': self.api_key,
                'API-Sign': signature
            }
            
            response = requests.post(
                f"{self.private_url}/TradeVolume",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'error' in result and result['error']:
                    raise Exception(f"Kraken API error: {result['error']}")
                if 'result' in result and 'volume' in result['result']:
                    self.cached_volume = float(result['result']['volume'])
                    self.volume_last_updated = datetime.now()
                    return self.cached_volume
                else:
                    raise Exception("Volume data not found in response")
            else:
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error fetching trading volume: {str(e)}")
            return 0

    def _get_asset_mapping(self):
        """Fetch Kraken asset names and cache them for efficiency."""
        if self.asset_mapping_cache and (datetime.now() - self.asset_mapping_cache['timestamp']).total_seconds() < 3600:
            return self.asset_mapping_cache['data']

        try:
            response = requests.get(f"{self.base_url}/Assets")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch assets: {response.text}")
                
            result = response.json()
            if 'error' in result and result['error']:
                raise Exception(f"Kraken API error: {result['error']}")
            
            asset_mapping = {details['altname']: kraken_symbol for kraken_symbol, details in result['result'].items()}
            self.asset_mapping_cache = {'data': asset_mapping, 'timestamp': datetime.now()}
            return asset_mapping
        except Exception as e:
            self.logger.error(f"Error fetching asset mapping: {str(e)}")
            return {}

    def calculate_triangle(self, base_currency, inter_currency1, inter_currency2, prices):
        """Calculate profit percentage for a triangular arbitrage path."""
        try:
            asset_mapping = self._get_asset_mapping()
            
            pair1 = f"{asset_mapping.get(base_currency, base_currency)}{asset_mapping.get(inter_currency1, inter_currency1)}"
            pair2 = f"{asset_mapping.get(inter_currency1, inter_currency1)}{asset_mapping.get(inter_currency2, inter_currency2)}"
            pair3 = f"{asset_mapping.get(inter_currency2, inter_currency2)}{asset_mapping.get(base_currency, base_currency)}"
            
            if pair1 not in prices or pair2 not in prices or pair3 not in prices:
                self.logger.warning(f"Missing price data for one or more pairs in triangle: {base_currency} -> {inter_currency1} -> {inter_currency2} -> {base_currency}")
                return None

            initial_amount = 1  # Starting amount

            price1 = float(prices[pair1]['a'][0])
            price2 = float(prices[pair2]['a'][0])
            price3 = float(prices[pair3]['b'][0])

            inter_amount1 = initial_amount / price1
            inter_amount2 = inter_amount1 / price2
            final_amount = inter_amount2 * price3

            profit_percentage = ((final_amount - initial_amount) / initial_amount) * 100
            fees_used = self.trading_fees['maker'] * 3  # Assuming maker fees for simplicity

            net_profit_percentage = profit_percentage - (fees_used * 100)
            
            return {
                'path': [pair1, pair2, pair3],
                'initial_amount': initial_amount,
                'final_amount': final_amount,
                'profit_percentage': net_profit_percentage,
                'fees_used': fees_used
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating triangle: {str(e)}")
            return None

    def get_trading_pairs(self):
        """Fetch and cache trading pairs from Kraken."""
        if self.available_pairs_cache and (datetime.now() - self.available_pairs_cache['timestamp']).total_seconds() < 3600:
            return self.available_pairs_cache['data']
        
        try:
            response = requests.get(f"{self.base_url}/AssetPairs")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch trading pairs: {response.text}")
                
            result = response.json()
            if 'error' in result and result['error']:
                raise Exception(f"Kraken API error: {result['error']}")
                
            pairs = result['result']
            self.available_pairs_cache = {'data': pairs, 'timestamp': datetime.now()}
            return pairs
        except Exception as e:
            self.logger.error(f"Error fetching trading pairs: {str(e)}")
            return {}

    def get_current_fees(self):
        """Calculate and cache current trading fees based on 30-day volume."""
        if self.trading_fees is None or (self.volume_last_updated and datetime.now() - self.volume_last_updated >= timedelta(hours=1)):
            volume = self._get_trading_volume()
            current_tier = '0'
            for tier in sorted(self.fee_tiers.keys(), key=float):
                if volume >= float(tier):
                    current_tier = tier
                else:
                    break
            self.trading_fees = self.fee_tiers[current_tier]
            self.logger.info(f"Current fee tier - Maker: {self.trading_fees['maker']}, Taker: {self.trading_fees['taker']}")
        return self.trading_fees

    def get_ticker_prices(self, pairs):
        """Fetch current prices for validated trading pairs."""
        available_pairs = self.get_trading_pairs()
        valid_pairs = [pair for pair in pairs if pair in available_pairs]
        
        if not valid_pairs:
            self.logger.warning("No valid trading pairs found")
            return {}

        pairs_str = ','.join(valid_pairs)
        try:
            response = requests.get(f"{self.base_url}/Ticker?pair={pairs_str}")
            if response.status_code != 200:
                raise Exception(f"Failed to fetch ticker prices: {response.text}")
                
            result = response.json()
            if 'error' in result and result['error']:
                raise Exception(f"Kraken API error: {result['error']}")
                
            return result['result']
        except Exception as e:
            self.logger.error(f"Error fetching ticker prices: {str(e)}")
            return {}

    def find_opportunities(self, min_profit_percentage=0):
        """Monitor specific arbitrage paths with manually defined pairs."""
        try:
            # Define specific triangular arbitrage paths with exact pairs
            triangular_paths = [
                {"pairs": ["ZEURZUSD", "XXBTZEUR", "XXBTZUSD"], "currencies": ["EUR", "USD", "BTC"]},
                {"pairs": ["XETHZUSD", "XETHXXBT", "XXBTZUSD"], "currencies": ["ETH", "USD", "BTC"]},
                {"pairs": ["XLTCZUSD", "XLTCXXBT", "XXBTZUSD"], "currencies": ["LTC", "USD", "BTC"]},
                {"pairs": ["XETHZEUR", "XETHXXBT", "XXBTZEUR"], "currencies": ["ETH", "EUR", "BTC"]},
                {"pairs": ["ADAEUR", "ADAXBT", "XXBTZEUR"], "currencies": ["ADA", "EUR", "BTC"]}
                # Add more paths as needed, each with exact Kraken pair names and their respective currencies
            ]

            while True:
                try:
                    self.get_current_fees()
                    pairs_needed = []
                    
                    # Collect all unique pairs needed for price lookup
                    for path in triangular_paths:
                        pairs_needed.extend(path["pairs"])
                    
                    # Fetch current prices for all required pairs
                    prices = self.get_ticker_prices(list(set(pairs_needed)))
                    if not prices:
                        self.logger.warning("No price data received, skipping iteration")
                        continue

                    # Check each defined path for arbitrage opportunities
                    for path in triangular_paths:
                        pair1, pair2, pair3 = path["pairs"]
                        base_currency, inter_currency, final_currency = path["currencies"]
                        
                        # Calculate arbitrage for the specified path
                        result = self.calculate_triangle(base_currency, inter_currency, final_currency, prices)
                        
                        if result and result['profit_percentage'] > min_profit_percentage:
                            self.logger.info(f"Opportunity found!")
                            self.logger.info(f"Path: {result['path']}")
                            self.logger.info(f"Profit: {result['profit_percentage']:.2f}%")
                            self.logger.info(f"Initial: {result['initial_amount']} {base_currency}")
                            self.logger.info(f"Final: {result['final_amount']:.2f} {base_currency}")
                            self.logger.info(f"Current fee rate: {result['fees_used']*100:.3f}%")
                            self.logger.info("-" * 50)

                    time.sleep(1)  # Adjust to prevent hitting rate limits

                except Exception as e:
                    self.logger.error(f"Error in iteration: {str(e)}")
                    time.sleep(5)  # Wait longer on error

        except KeyboardInterrupt:
            self.logger.info("Stopping arbitrage monitor...")
        except Exception as e:
            self.logger.error(f"Critical error in main loop: {str(e)}")

if __name__ == "__main__":
    arbitrage_monitor = KrakenTriangularArbitrage(
        api_key=os.environ["KRAKEN_API_KEY"],
        api_secret=os.environ["KRAKEN_API_SECRET"],
    )
    
    arbitrage_monitor.find_opportunities(min_profit_percentage=0.1)