#!/usr/bin/env python3
"""
Backtest Engine - Execute trading strategies on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Callable

RESULTS_DIR = "results"

class Trade:
    def __init__(self, entry_price, entry_time, quantity, coin):
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.quantity = quantity
        self.coin = coin
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0
        self.pnl_percent = 0
        
    def close(self, exit_price, exit_time):
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.pnl = (exit_price - self.entry_price) * self.quantity
        self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100

class BacktestEngine:
    def __init__(self, initial_balance=1000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: List[Trade] = []
        self.open_positions: Dict[str, Trade] = {}  # coin -> Trade
        self.current_strategy = None
        
    def reset(self):
        """Reset for new backtest"""
        self.balance = self.initial_balance
        self.trades = []
        self.open_positions = {}
        
    def buy(self, coin, price, time, quantity=None):
        """Open a long position"""
        if quantity is None:
            quantity = self.balance / price  # Use all balance
            
        cost = quantity * price
        if cost > self.balance:
            return False  # Not enough balance
            
        self.balance -= cost
        trade = Trade(price, time, quantity, coin)
        self.open_positions[coin] = trade
        return True
    
    def sell(self, coin, price, time, quantity=None):
        """Close a position (short or long)"""
        if coin not in self.open_positions:
            return False
            
        trade = self.open_positions[coin]
        if quantity and quantity < trade.quantity:
            # Partial close - not implemented for simplicity
            return False
            
        trade.close(price, time)
        self.balance += trade.quantity * price
        self.trades.append(trade)
        del self.open_positions[coin]
        return True
    
    def run(self, data, entry_signal: Callable, exit_signal: Callable):
        """Run backtest with given entry/exit signals"""
        self.reset()
        
        for i, row in data.iterrows():
            coin = row.get("coin", "UNKNOWN")
            
            # Check exit signals first
            if coin in self.open_positions:
                if exit_signal(row, self.open_positions[coin]):
                    self.sell(coin, row["close"], row["timestamp"])
            
            # Check entry signals
            if coin not in self.open_positions:
                if entry_signal(row):
                    self.buy(coin, row["close"], row["timestamp"])
        
        # Close remaining positions at last price
        last_price = data.iloc[-1]["close"]
        last_time = data.iloc[-1]["timestamp"]
        for coin in list(self.open_positions.keys()):
            self.sell(coin, last_price, last_time)
            
        return self.get_metrics()
    
    def get_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                "total_trades": 0,
                "profitable": 0,
                "losing": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "max_profit": 0,
                "max_loss": 0,
            }
        
        pnls = [t.pnl for t in self.trades]
        profits = [t for t in pnls if t > 0]
        losses = [t for t in pnls if t < 0]
        
        return {
            "total_trades": len(self.trades),
            "profitable": len(profits),
            "losing": len(losses),
            "win_rate": (len(profits) / len(self.trades)) * 100 if self.trades else 0,
            "total_pnl": sum(pnls),
            "avg_profit": np.mean(profits) if profits else 0,
            "avg_loss": np.mean(losses) if losses else 0,
            "max_profit": max(profits) if profits else 0,
            "max_loss": min(losses) if losses else 0,
            "final_balance": self.balance,
            "return_pct": ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            "trades": [
                {
                    "coin": t.coin,
                    "entry": t.entry_price,
                    "exit": t.exit_price,
                    "pnl": t.pnl,
                    "pnl_pct": t.pnl_percent
                }
                for t in self.trades
            ]
        }
    
    def save_results(self, strategy_name, data_params):
        """Save results to JSON"""
        import json
        import os
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        metrics = self.get_metrics()
        result = {
            "strategy": strategy_name,
            "params": data_params,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        filename = f"{RESULTS_DIR}/{strategy_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        
        return filename, metrics


# Example usage
if __name__ == "__main__":
    # Simple test with dummy data
    engine = BacktestEngine(initial_balance=1000)
    
    # Create dummy OHLC data
    data = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=100, freq="1H"),
        "open": np.random.uniform(0.001, 0.01, 100),
        "high": np.random.uniform(0.001, 0.01, 100),
        "low": np.random.uniform(0.001, 0.01, 100),
        "close": np.random.uniform(0.001, 0.01, 100),
        "coin": ["DOGE"] * 100
    })
    
    # Simple entry: price up for 3 consecutive hours
    def entry(row, idx, df):
        if idx < 3: return False
        return df.iloc[idx-3:idx]["close"].is_monotonic_increasing
    
    # Simple exit: price down for 2 consecutive hours
    def exit(row, idx, df, trade):
        if idx < 2: return False
        return df.iloc[idx-2:idx]["close"].is_monotonic_decreasing
    
    # Run
    metrics = engine.run(data, lambda r: entry(r, 0, data), lambda r, t: exit(r, 0, data, t))
    print("Test Results:", metrics)
