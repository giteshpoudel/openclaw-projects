# Crypto Backtest

Python system for backtesting intraday crypto trading strategies on cheap/meme coins.

## Setup

```bash
cd crypto-backtest
pip install -r requirements.txt
```

## Usage

### 1. Fetch Market Data
```bash
python run.py fetch
```
Fetches OHLC data from CoinGecko for cheap coins (<$0.01).

### 2. Run Backtest
```bash
python run.py backtest momentum      # Momentum strategy
python run.py backtest rsi          # RSI strategy
python run.py backtest breakout     # Breakout strategy
python run.py backtest mean_reversion  # Mean reversion
```

### 3. View Results
```bash
python run.py results   # Latest results
python run.py compare   # Compare all strategies
```

## Strategies

| Strategy | Description | Parameters |
|----------|-------------|------------|
| Momentum | Buy on positive price momentum | lookback (default: 3) |
| RSI | Buy oversold, sell overbought | period (14), oversold (30), overbought (70) |
| MeanReversion | Buy below moving average | ma_period (20), threshold (0.02) |
| Breakout | Buy on resistance break | lookback (10) |

## Results

Results are saved to `results/` folder.

### View Dashboard
Open `results/dashboard.html` in a browser, or view on GitHub Pages.

### Metrics Tracked

- Total trades
- Win rate %
- Total P&L ($)
- Profitable trades (count + $)
- Losing trades (count + $)
- Average profit/loss per trade

## Project Structure

```
crypto-backtest/
├── data/           # Market data (CSV)
├── strategies/     # Trading strategies
├── backtest/       # Backtest engine
├── results/        # Results JSON
└── run.py          # Main runner
```

## Goal

Win on short-term (intraday) trades with cheap/meme coins.
