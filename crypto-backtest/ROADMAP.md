# Crypto Backtest Project

## Goal
Build a Python system to fetch crypto market data and backtest intraday trading strategies for cheap/meme coins. Target: short-term profitable transactions.

## Project Structure
```
crypto-backtest/
├── data/           # Market data storage (CSV, JSON)
├── strategies/     # Trading strategy definitions
├── backtest/       # Backtesting engine
├── results/        # Results and metrics
└── logs/           # Execution logs
```

## Key Metrics
1. Total gain/loss ($)
2. Number of transactions
3. Profitable transactions (count + $)
4. Loss transactions (count + $)
5. Win rate %
6. Average profit/loss per trade

## Phases

### Phase 1: Data Fetching
- Connect to CoinGecko API
- Fetch historical data (OHLCV)
- Store in data/ folder
- Support for cheap coins (<$0.01)

### Phase 2: Basic Backtest Engine
- Load historical data
- Execute buy/sell signals
- Track positions
- Calculate P&L

### Phase 3: Strategy Framework
- Entry signals (buy conditions)
- Exit signals (sell conditions)  
- Position sizing
- Stop loss

### Phase 4: Results Dashboard
- Summary metrics
- Per-strategy breakdown
- Export to JSON/CSV

### Phase 5: BA Review
- Analyze results
- Recommend new variables
- Iterate strategies

## Tech Stack
- Python 3.10+
- pandas, numpy
- CoinGecko API (free)
- Optional: Binance API

## Success Criteria
- Win rate > 50% on short-term trades
- Profitable overall
- Replicable results
