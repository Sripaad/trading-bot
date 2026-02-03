# Trading Bot 🥤

Crypto trading bot built with [Jesse.trade](https://jesse.trade) framework, integrated with Kraken exchange.

## Status
🚧 **Active Development** - Paper trading phase

## Project Structure

```
trading-bot/
├── README.md
├── venv/                     # Python virtual environment
├── kraken-bot/               # Main trading project
│   ├── strategies/           # Trading strategies
│   │   ├── __init__.py
│   │   ├── golden_cross.py   # EMA 8/21 trend following
│   │   ├── rsi_mean_reversion.py  # RSI + Bollinger Bands
│   │   └── momentum_roc.py   # Rate of Change momentum
│   ├── config.py             # Configuration
│   ├── backtest_runner.py    # Backtest execution
│   ├── .env.example          # Environment template
│   └── .env                  # Your API keys (git-ignored)
├── signal_engine.py          # Legacy: Basic signal generator
├── soda_paper_trader.py      # Legacy: Simple paper trader
└── alerts/                   # Discord alerting
```

## Strategies

### 1. Golden Cross (EMA 8/21)
**Type:** Trend Following

Entry signals based on exponential moving average crossovers:
- **Long:** EMA8 crosses above EMA21
- **Short:** EMA8 crosses below EMA21
- **Exit:** Reverse crossover or stop loss

### 2. RSI Mean Reversion
**Type:** Mean Reversion

Buys oversold / sells overbought with Bollinger Band confirmation:
- **Long:** RSI < 30 + price at lower Bollinger Band
- **Short:** RSI > 70 + price at upper Bollinger Band
- **Exit:** RSI normalizes to 50 or take profit at middle band

### 3. Momentum ROC
**Type:** Momentum

Trades strong momentum confirmed by volume:
- **Long:** ROC > 5% + volume spike + uptrend
- **Short:** ROC < -5% + volume spike + downtrend
- **Exit:** Momentum fades (ROC crosses zero)

## Quick Start

```bash
# Navigate to project
cd trading-bot

# Activate virtual environment
source venv/bin/activate

# Verify Jesse installation
jesse --version  # Should show 1.12.2

# Set up config (copy and edit .env)
cd kraken-bot
cp .env.example .env
# Edit .env with your Kraken API keys

# Run a backtest
python backtest_runner.py --strategy GoldenCross --start 2024-01-01 --end 2024-06-01
```

## Kraken API Setup

1. Go to [Kraken API Settings](https://www.kraken.com/u/settings/api)
2. Create a new API key with permissions:
   - ✅ **Query Funds** - Check balances
   - ✅ **Query Open Orders & Trades** - Monitor positions
   - ✅ **Query Closed Orders & Trades** - Trade history
   - ✅ **Create & Modify Orders** - Place trades
   - ❌ **Withdraw Funds** - Keep disabled for safety!
3. Copy keys to your `.env` file

## Backtesting

```bash
# Single strategy
python backtest_runner.py --strategy GoldenCross --symbol BTC-USDT --timeframe 1h

# All strategies
python backtest_runner.py --all --start 2024-01-01 --end 2024-12-01

# Custom balance
python backtest_runner.py --strategy RSIMeanReversion --balance 5000
```

## Risk Management

Built-in safeguards:
- **Position sizing:** Max 2-5% of capital per trade
- **Stop losses:** ATR-based or percentage-based
- **Take profits:** Risk-reward ratios of 1.5-2x
- **Max drawdown:** Configurable daily loss limits

## Roadmap

- [x] Jesse framework integration
- [x] Three core strategies (Golden Cross, RSI Mean Reversion, Momentum ROC)
- [x] Strategy hyperparameter optimization support
- [ ] Backtest on historical data
- [ ] Paper trading with live prices
- [ ] Discord notifications for signals
- [ ] Performance dashboard
- [ ] Live trading (after extensive paper testing)

## Dependencies

- Python 3.11+
- Jesse 1.12.2
- python-dotenv
- numpy

## Disclaimer

⚠️ **This is not financial advice.** Trading involves risk. Start with paper trading. Never trade with money you can't afford to lose.

## Contributors

- **SodaPoppy** - AI agent (strategy implementation)
- **Sripaad** - Human overseer
