#!/usr/bin/env python3
"""
Data Fetcher - Fetch crypto market data from CoinGecko API
"""

import requests
import pandas as pd
import time
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

class CryptoDataFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit = 10
        
    def get_coin_market_data(self, vs_currency="usd", per_page=100, page=1):
        url = f"{self.base_url}/coins/markets"
        params = {"vs_currency": vs_currency, "order": "market_cap_desc", "per_page": per_page, "page": page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_coin_market_chart(self, coin_id, days=7):
        """Get OHLC + volume data"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        
        if not prices:
            return None
            
        rows = []
        for i in range(len(prices)):
            rows.append({
                "timestamp": pd.to_datetime(prices[i][0], unit="ms"),
                "price": prices[i][1],
                "volume": volumes[i][1] if i < len(volumes) else 0
            })
        
        df = pd.DataFrame(rows)
        
        # Resample to hourly OHLCV
        df.set_index("timestamp", inplace=True)
        resampled = df.resample("1h").agg({
            "price": ["first", "high", "low", "last"],
            "volume": "sum"
        })
        resampled.columns = ["open", "high", "low", "close", "volume"]
        resampled.reset_index(inplace=True)
        resampled["coin"] = coin_id
        resampled.dropna(inplace=True)
        return resampled
    
    def get_cheap_coins(self, max_price=0.01, limit=20):
        markets = self.get_coin_market_data(per_page=250)
        cheap = [c for c in markets if c.get("current_price", 1) <= max_price]
        return cheap[:limit]
    
    def fetch_and_save(self, coin_ids, days=7):
        os.makedirs(DATA_DIR, exist_ok=True)
        
        all_data = []
        for coin_id in coin_ids:
            print(f"Fetching {coin_id}...")
            try:
                df = self.get_coin_market_chart(coin_id, days=days)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                time.sleep(60 / self.rate_limit)
            except Exception as e:
                print(f"Error fetching {coin_id}: {e}")
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            output_file = f"{DATA_DIR}/ohlcv_{datetime.now().strftime('%Y%m%d')}.csv"
            combined.to_csv(output_file, index=False)
            print(f"Saved {len(combined)} rows to {output_file}")
            return combined
        return None

if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    cheap = fetcher.get_cheap_coins(max_price=0.01, limit=10)
    print(f"Found {len(cheap)} coins under $0.01")
    for coin in cheap[:5]:
        print(f"  - {coin['symbol']}: ${coin['current_price']}")
