#!/usr/bin/env python3
"""
Data Fetcher - Fetch crypto market data from CoinGecko API
"""

import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

class CryptoDataFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit = 10  # requests per minute (free tier)
        
    def get_coins_list(self, per_page=250):
        """Get list of all available coins"""
        url = f"{self.base_url}/coins/list"
        params = {"per_page": per_page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_coin_market_data(self, vs_currency="usd", per_page=100, page=1, 
                             price_change_percentage="1h,24h,7d", sparkline=False):
        """Get market data for coins"""
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "price_change_percentage": price_change_percentage,
            "sparkline": sparkline
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_coin_ohlc(self, coin_id, days=7):
        """Get OHLC data for a coin"""
        url = f"{self.base_url}/coins/{coin_id}/ohlc"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["coin"] = coin_id
        return df
    
    def get_coin_history(self, coin_id, days=30):
        """Get historical market data including volume"""
        url = f"{self.coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract prices and volumes
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["volume"] = [v[1] for v in volumes]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["coin"] = coin_id
        return df
    
    def get_cheap_coins(self, max_price=0.01, limit=50):
        """Get list of cheap coins (meme coins, low cap)"""
        markets = self.get_coin_market_data(per_page=250)
        cheap = [c for c in markets if c.get("current_price", 1) <= max_price]
        return cheap[:limit]
    
    def fetch_and_save(self, coin_ids, days=7):
        """Fetch OHLC data for multiple coins and save to CSV"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        all_data = []
        for coin_id in coin_ids:
            print(f"Fetching {coin_id}...")
            try:
                df = self.get_coin_ohlc(coin_id, days=days)
                all_data.append(df)
                time.sleep(60 / self.rate_limit)  # Rate limiting
            except Exception as e:
                print(f"Error fetching {coin_id}: {e}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            output_file = f"{DATA_DIR}/ohlc_{datetime.now().strftime('%Y%m%d')}.csv"
            combined.to_csv(output_file, index=False)
            print(f"Saved to {output_file}")
            return combined
        return None

if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    
    # Example: Get cheap coins
    cheap_coins = fetcher.get_cheap_coins(max_price=0.01, limit=20)
    print(f"Found {len(cheap_coins)} coins under $0.01")
    for coin in cheap_coins[:5]:
        print(f"  - {coin['symbol']}: ${coin['current_price']}")
