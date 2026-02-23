#!/usr/bin/env python3
"""
Backtest Engine v3 - With position sizing
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
        self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100 if self.entry_price > 0 else 0

class BacktestEngine:
    def __init__(self, initial_balance=1000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades: List[Trade] = []
        self.open_positions: Dict[str, Trade] = {}
        
    def reset(self):
        self.balance = self.initial_balance
        self.trades = []
        self.open_positions = {}
        
    def run_on_coin(self, df, entry_signal, exit_signal, coin, position_size=1.0):
        """Run backtest for a single coin"""
        coin_data = df[df["coin"] == coin].reset_index(drop=True)
        if len(coin_data) < 10:
            return []
        
        coin_balance = self.initial_balance * position_size
        coin_trades = []
        position = None
        
        for idx in range(len(coin_data)):
            row = coin_data.iloc[idx]
            current_price = row["close"]
            
            if position is not None:
                if exit_signal(row, position):
                    pnl = (current_price - position["entry_price"]) * position["quantity"]
                    coin_balance += pnl
                    coin_trades.append({
                        "coin": coin,
                        "entry": position["entry_price"],
                        "exit": current_price,
                        "pnl": pnl,
                        "pnl_pct": ((current_price - position["entry_price"]) / position["entry_price"]) * 100 if position["entry_price"] > 0 else 0
                    })
                    position = None
            
            if position is None:
                if entry_signal(row):
                    if current_price > 0:
                        position = {
                            "entry_price": current_price,
                            "entry_time": row["timestamp"],
                            "quantity": coin_balance / current_price
                        }
        
        if position is not None:
            last_row = coin_data.iloc[-1]
            pnl = (last_row["close"] - position["entry_price"]) * position["quantity"]
            coin_trades.append({
                "coin": coin,
                "entry": position["entry_price"],
                "exit": last_row["close"],
                "pnl": pnl,
                "pnl_pct": ((last_row["close"] - position["entry_price"]) / position["entry_price"]) * 100 if position["entry_price"] > 0 else 0
            })
        
        return coin_trades
    
    def run(self, data, entry_signal: Callable, exit_signal: Callable, position_size=1.0):
        self.reset()
        
        all_trades = []
        coins = data["coin"].unique()
        
        for coin in coins:
            coin_trades = self.run_on_coin(data, entry_signal, exit_signal, coin, position_size)
            all_trades.extend(coin_trades)
        
        self.trades = all_trades
        return self.get_metrics()
    
    def get_metrics(self) -> Dict:
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
        
        pnls = [t["pnl"] for t in self.trades]
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
            "final_balance": self.initial_balance + sum(pnls),
            "return_pct": (sum(pnls) / self.initial_balance) * 100,
            "trades": self.trades
        }
    
    def save_results(self, strategy_name, data_params):
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
