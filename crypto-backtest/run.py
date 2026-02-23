#!/usr/bin/env python3
"""
Main runner for crypto backtesting
Usage:
    python run.py fetch          # Fetch market data
    python run.py backtest      # Run backtest
    python run.py results       # Display results
    python run.py compare       # Compare strategies
"""

import sys
import os
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import CryptoDataFetcher
from backtest.engine import BacktestEngine
from strategies.base import get_strategy
from results.display import display_metrics, display_trade_list, load_results, compare_strategies


def fetch_data():
    """Fetch crypto market data"""
    fetcher = CryptoDataFetcher()
    
    # Get cheap coins
    print("Fetching cheap coins...")
    cheap = fetcher.get_cheap_coins(max_price=0.01, limit=10)
    
    coin_ids = [c["id"] for c in cheap[:5]]  # Top 5
    print(f"Fetching data for: {coin_ids}")
    
    df = fetcher.fetch_and_save(coin_ids, days=30)
    if df is not None:
        print(f"Fetched {len(df)} rows of data")
    else:
        print("No data fetched")

def run_backtest(strategy_name="momentum", **strategy_params):
    """Run backtest with given strategy"""
    from data.data_fetcher import CryptoDataFetcher
    
    # Load data
    data_dir = "data"
    files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    if not files:
        print("No data found. Run 'python run.py fetch' first.")
        return
    
    # Load latest data
    latest_file = sorted(files)[-1]
    df = pd.read_csv(os.path.join(data_dir, latest_file))
    
    print(f"Loaded {len(df)} rows from {latest_file}")
    
    # Get strategy
    strategy = get_strategy(strategy_name, **strategy_params)
    print(f"Running backtest with {strategy.name} strategy")
    
    # Run backtest
    engine = BacktestEngine(initial_balance=1000)
    
    def entry(row):
        idx = df[df["timestamp"] == row["timestamp"]].index[0]
        return strategy.entry_condition(df, idx)
    
    def exit(row, trade):
        idx = df[df["timestamp"] == row["timestamp"]].index[0]
        return strategy.exit_condition(df, idx, trade)
    
    metrics = engine.run(df, entry, exit)
    
    # Display results
    display_metrics(metrics)
    display_trade_list(metrics.get("trades", []))
    
    # Save results
    filename, _ = engine.save_results(strategy.name, {"data_file": latest_file})
    print(f"\nResults saved to {filename}")

def show_results():
    """Display latest results"""
    results = load_results()
    if results:
        latest = results[0]
        display_metrics(latest["metrics"])
        display_trade_list(latest["metrics"].get("trades", []))
    else:
        print("No results found. Run backtest first.")

def compare_results():
    """Compare all strategies"""
    results = load_results()
    compare_strategies(results)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "fetch":
        fetch_data()
    elif sys.argv[1] == "backtest":
        strategy = sys.argv[2] if len(sys.argv) > 2 else "momentum"
        run_backtest(strategy)
    elif sys.argv[1] == "results":
        show_results()
    elif sys.argv[1] == "compare":
        compare_results()
    else:
        print(__doc__)
