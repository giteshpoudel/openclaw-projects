#!/usr/bin/env python3
"""
Main runner for crypto backtesting
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import CryptoDataFetcher
from backtest.engine import BacktestEngine
from strategies.base import get_strategy
from results.display import display_metrics, display_trade_list, load_results, compare_strategies


def fetch_data():
    fetcher = CryptoDataFetcher()
    print("Fetching cheap coins...")
    cheap = fetcher.get_cheap_coins(max_price=0.01, limit=10)
    coin_ids = [c["id"] for c in cheap[:5]]
    print(f"Fetching data for: {coin_ids}")
    df = fetcher.fetch_and_save(coin_ids, days=30)
    if df is not None:
        print(f"Fetched {len(df)} rows of data")
    else:
        print("No data fetched")


def run_backtest(strategy_name="rsi_v3", **strategy_params):
    data_dir = "data"
    files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    ohlcv_files = [f for f in files if "ohlcv" in f]
    if ohlcv_files:
        files = ohlcv_files
    
    if not files:
        print("No data found. Run 'python run.py fetch' first.")
        return
    
    latest_file = sorted(files)[-1]
    df = pd.read_csv(os.path.join(data_dir, latest_file))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    print(f"Loaded {len(df)} rows from {latest_file}")
    print(f"Coins: {df['coin'].unique()}")
    
    strategy = get_strategy(strategy_name, **strategy_params)
    position_size = strategy.get_position_size()
    print(f"Running {strategy.name} with position_size={position_size}")
    
    engine = BacktestEngine(initial_balance=1000)
    
    metrics = engine.run(
        df, 
        lambda row: strategy.entry_condition(df, df[df["timestamp"] == row["timestamp"]].index[0]),
        lambda row, trade: strategy.exit_condition(df, df[df["timestamp"] == row["timestamp"]].index[0], trade),
        position_size
    )
    
    display_metrics(metrics)
    display_trade_list(metrics.get("trades", []))
    
    filename, _ = engine.save_results(strategy.name, {"data_file": latest_file, "position_size": position_size})
    print(f"\nResults saved to {filename}")


def show_results():
    results = load_results()
    if results:
        latest = results[0]
        display_metrics(latest["metrics"])
        display_trade_list(latest["metrics"].get("trades", []))
    else:
        print("No results found.")


def compare_results():
    results = load_results()
    compare_strategies(results)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "fetch":
        fetch_data()
    elif sys.argv[1] == "backtest":
        strategy = sys.argv[2] if len(sys.argv) > 2 else "rsi_v3"
        run_backtest(strategy)
    elif sys.argv[1] == "results":
        show_results()
    elif sys.argv[1] == "compare":
        compare_results()
    else:
        print(__doc__)
