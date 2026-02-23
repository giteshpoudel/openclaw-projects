#!/usr/bin/env python3
"""
Enhanced Strategy Framework v3 - With filters, stop-loss, position sizing
"""

import pandas as pd

class Strategy:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or {}
        
    def entry_condition(self, df, idx) -> bool:
        raise NotImplementedError
        
    def exit_condition(self, df, idx, trade) -> bool:
        raise NotImplementedError
    
    def filters(self, df, idx) -> bool:
        if "volume" not in df.columns:
            return True
        # Volume filter - require minimum volume
        if self.params.get("min_volume") and idx >= 5:
            vol = df["volume"].iloc[idx] if idx < len(df) else 0
            vol_ma = df["volume"].iloc[max(0,idx-10):idx].mean()
            if vol_ma > 0 and vol < vol_ma * 0.5:  # Below 50% of recent avg
                return False
        return True
    
    def get_pnl_pct(self, df, idx, trade):
        entry = trade["entry_price"] if isinstance(trade, dict) else trade.entry_price
        current = df["close"].iloc[idx]
        return ((current - entry) / entry) * 100 if entry > 0 else 0
    
    def get_position_size(self):
        """Return position size as fraction of balance (0-1)"""
        return self.params.get("position_size", 1.0)  # Default full position


class ImprovedRSIV3(Strategy):
    """RSI with tuned thresholds and position sizing"""
    
    def __init__(self, period=14, oversold=40, overbought=60, stop_loss=0.03, position_size=0.2):
        super().__init__("RSIv3", {
            "period": period, 
            "oversold": oversold, 
            "overbought": overbought,
            "stop_loss": stop_loss,
            "position_size": position_size
        })
        
    def calculate_rsi(self, prices):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params["period"]).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params["period"]).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def entry_condition(self, df, idx):
        if idx < self.params["period"] + 5:
            return False
        if not self.filters(df, idx):
            return False
        rsi = self.calculate_rsi(df["close"])
        return rsi.iloc[idx] < self.params["oversold"]
        
    def exit_condition(self, df, idx, trade):
        pnl = self.get_pnl_pct(df, idx, trade)
        # Tight stop-loss
        if pnl < -self.params["stop_loss"] * 100:
            return True
        # Take profit at 2:1 ratio
        if pnl > self.params["stop_loss"] * 200:
            return True
        # RSI overbought
        if idx < self.params["period"]:
            return False
        rsi = self.calculate_rsi(df["close"])
        return rsi.iloc[idx] > self.params["overbought"]


class VolumeConfirmedMomentum(Strategy):
    """Momentum with volume confirmation and small positions"""
    
    def __init__(self, lookback=3, stop_loss=0.02, position_size=0.15):
        super().__init__("VolMomentumV3", {
            "lookback": lookback,
            "stop_loss": stop_loss,
            "position_size": position_size
        })
        
    def entry_condition(self, df, idx):
        if idx < self.params["lookback"] + 5:
            return False
        if not self.filters(df, idx):
            return False
        # Price momentum
        window = df.iloc[idx-self.params["lookback"]:idx]
        if len(window) < 2:
            return False
        price_up = window["close"].iloc[-1] > window["close"].iloc[0] * 1.015  # 1.5% gain
        # Volume confirmation
        vol_ma = df["volume"].iloc[max(0,idx-5):idx].mean() if "volume" in df.columns else 0
        volume_up = df["volume"].iloc[idx] > vol_ma * 1.2 if vol_ma > 0 else True
        return price_up and volume_up
        
    def exit_condition(self, df, idx, trade):
        pnl = self.get_pnl_pct(df, idx, trade)
        if pnl < -self.params["stop_loss"] * 100:
            return True
        if pnl > self.params["stop_loss"] * 200:
            return True
        # Price reversal
        if idx > 2:
            window = df.iloc[idx-2:idx]
            if window["close"].iloc[-1] < window["close"].iloc[0] * 0.98:
                return True
        return False


class TightBandStrategy(Strategy):
    """Mean reversion with tight bands and small positions"""
    
    def __init__(self, ma_period=10, band=0.01, stop_loss=0.02, position_size=0.15):
        super().__init__("TightBand", {
            "ma_period": ma_period,
            "band": band,
            "stop_loss": stop_loss,
            "position_size": position_size
        })
        
    def entry_condition(self, df, idx):
        if idx < self.params["ma_period"]:
            return False
        if not self.filters(df, idx):
            return False
        ma = df["close"].rolling(window=self.params["ma_period"]).mean()
        current = df["close"].iloc[idx]
        ma_val = ma.iloc[idx]
        # Tight band - 1% below MA
        return current < ma_val * (1 - self.params["band"])
        
    def exit_condition(self, df, idx, trade):
        pnl = self.get_pnl_pct(df, idx, trade)
        if pnl < -self.params["stop_loss"] * 100:
            return True
        # At band edge
        if idx >= self.params["ma_period"]:
            ma = df["close"].rolling(window=self.params["ma_period"]).mean()
            current = df["close"].iloc[idx]
            ma_val = ma.iloc[idx]
            if current > ma_val * (1 + self.params["band"] * 0.5):
                return True
        return False


class ScalperStrategy(Strategy):
    """Quick scalps - very short term, tight stops"""
    
    def __init__(self, gain_threshold=0.015, stop_loss=0.01, position_size=0.1):
        super().__init__("Scalper", {
            "gain_threshold": gain_threshold,
            "stop_loss": stop_loss,
            "position_size": position_size
        })
        
    def entry_condition(self, df, idx):
        if idx < 3:
            return False
        if not self.filters(df, idx):
            return False
        # 3 consecutive up candles
        window = df.iloc[idx-3:idx]
        if len(window) < 3:
            return False
        up = all(window["close"].iloc[i] > window["close"].iloc[i-1] for i in range(1, len(window)))
        return up
        
    def exit_condition(self, df, idx, trade):
        pnl = self.get_pnl_pct(df, idx, trade)
        # Quick profit
        if pnl > self.params["gain_threshold"] * 100:
            return True
        # Tight stop
        if pnl < -self.params["stop_loss"] * 100:
            return True
        # Max 1 hour
        entry_idx = df[df["timestamp"] == trade["entry_time"]].index[0] if isinstance(trade, dict) else df[df["timestamp"] == trade.entry_time].index[0]
        if idx - entry_idx >= 4:  # 4 hours max
            return True
        return False


# Registry
STRATEGIES = {
    "rsi_v3": ImprovedRSIV3,
    "vol_momentum_v3": VolumeConfirmedMomentum,
    "tight_band": TightBandStrategy,
    "scalper": ScalperStrategy,
}

def get_strategy(name, **kwargs) -> Strategy:
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}")
    return STRATEGIES[name](**kwargs)
