#!/usr/bin/env python3
"""
Strategy Framework - Define and run trading strategies
"""

from typing import Dict, List
import pandas as pd

class Strategy:
    """Base class for trading strategies"""
    
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or {}
        
    def entry_condition(self, df, idx) -> bool:
        """Return True to enter a trade"""
        raise NotImplementedError
        
    def exit_condition(self, df, idx, trade) -> bool:
        """Return True to exit a trade"""
        raise NotImplementedError


class MomentumStrategy(Strategy):
    """Buy when price momentum is positive"""
    
    def __init__(self, lookback=3):
        super().__init__("Momentum", {"lookback": lookback})
        
    def entry_condition(self, df, idx):
        if idx < self.params["lookback"]:
            return False
        window = df.iloc[idx-self.params["lookback"]:idx]
        return window["close"].iloc[-1] > window["close"].iloc[0] * 1.01  # 1% gain
        
    def exit_condition(self, df, idx, trade):
        if idx < 2:
            return False
        window = df.iloc[idx-2:idx]
        return window["close"].iloc[-1] < window["close"].iloc[0] * 0.99  # 1% loss


class RSIStrategy(Strategy):
    """Buy when RSI is oversold, sell when overbought"""
    
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__("RSI", {"period": period, "oversold": oversold, "overbought": overbought})
        
    def calculate_rsi(self, prices):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params["period"]).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params["period"]).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def entry_condition(self, df, idx):
        if idx < self.params["period"]:
            return False
        rsi = self.calculate_rsi(df["close"])
        return rsi.iloc[idx] < self.params["oversold"]
        
    def exit_condition(self, df, idx, trade):
        if idx < self.params["period"]:
            return False
        rsi = self.calculate_rsi(df["close"])
        return rsi.iloc[idx] > self.params["overbought"]


class MeanReversionStrategy(Strategy):
    """Buy when price is below moving average"""
    
    def __init__(self, ma_period=20, threshold=0.02):
        super().__init__("MeanReversion", {"ma_period": ma_period, "threshold": threshold})
        
    def entry_condition(self, df, idx):
        if idx < self.params["ma_period"]:
            return False
        ma = df["close"].rolling(window=self.params["ma_period"]).mean()
        current = df["close"].iloc[idx]
        ma_val = ma.iloc[idx]
        return current < ma_val * (1 - self.params["threshold"])
        
    def exit_condition(self, df, idx, trade):
        if idx < self.params["ma_period"]:
            return False
        ma = df["close"].rolling(window=self.params["ma_period"]).mean()
        current = df["close"].iloc[idx]
        ma_val = ma.iloc[idx]
        return current > ma_val * (1 + self.params["threshold"] / 2)


class BreakoutStrategy(Strategy):
    """Buy when price breaks resistance"""
    
    def __init__(self, lookback=10):
        super().__init__("Breakout", {"lookback": lookback})
        
    def entry_condition(self, df, idx):
        if idx < self.params["lookback"]:
            return False
        window = df.iloc[idx-self.params["lookback"]:idx]
        resistance = window["high"].max()
        current = df["close"].iloc[idx]
        return current > resistance * 1.02  # 2% breakout
        
    def exit_condition(self, df, idx, trade):
        # Exit after fixed time or profit target
        entry_idx = df[df["timestamp"] == trade.entry_time].index[0]
        bars_held = idx - entry_idx
        return bars_held >= 10 or trade.pnl_percent >= 5


# Registry of available strategies
STRATEGIES = {
    "momentum": MomentumStrategy,
    "rsi": RSIStrategy,
    "mean_reversion": MeanReversionStrategy,
    "breakout": BreakoutStrategy,
}

def get_strategy(name, **kwargs) -> Strategy:
    """Factory function to get strategy by name"""
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}")
    return STRATEGIES[name](**kwargs)
