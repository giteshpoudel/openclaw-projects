# Crypto Backtest - Version History

## v3 (Current)
**Date:** 2026-02-23

### Changes Implemented:
- Position sizing (15-20% per trade instead of 100%)
- Tight stop-loss (2%)
- Tuned RSI thresholds (oversold=40, overbought=60)
- Volume filters
- New strategies: TightBand, RSIv3, VolMomentumV3, Scalper

### Results:
- **TightBand:** +24.2% return (WINNER)
- RSIv3: -1.7%
- Scalper: -2.6%
- VolMomentumV3: -6.7%

---

## v2
**Date:** 2026-02-23

### Changes Implemented:
- Added stop-loss
- Added volatility filters
- Improved RSI strategy

### Results:
- All strategies losing money
- RSI: -26%
- Momentum: -100%

---

## v1 (Initial)
**Date:** 2026-02-23

### Initial Setup:
- Basic backtest engine
- Strategies: Momentum, RSI, MeanReversion, Breakout
- No position sizing
- No stop-loss

### Results:
- Momentum: -99.99%
- RSI: -25.9%
- Win rates below 10%

---

## How to Revert

To use a previous version:

```bash
# View all versions
git log

# Checkout specific version
git checkout v1  # or v2, v3

# Or revert to specific commit
git revert <commit-hash>
```

## Strategy Parameters by Version

### v3 - TightBand (WINNER)
```python
ma_period=10
band=0.01  (1% below MA)
stop_loss=0.02
position_size=0.15
```

### v2 - ImprovedRSI
```python
period=14
oversold=35
overbought=65
stop_loss=0.05
```

### v1 - Original RSI
```python
period=14
oversold=30
overbought=70
```
