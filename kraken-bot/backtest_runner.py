#!/usr/bin/env python3
"""
Backtest Runner for Kraken Trading Bot

Usage:
    python backtest_runner.py --strategy GoldenCross --symbol BTC-USDT --start 2024-01-01 --end 2024-06-01
    python backtest_runner.py --all  # Run all strategies on default config
"""
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

# Jesse imports
from jesse.research import backtest, get_candles, import_candles

# Local imports
from config import BACKTEST_CONFIG, DEFAULT_ROUTES, DEFAULT_DATA_ROUTES, STRATEGY_MAP
from strategies import GoldenCross, RSIMeanReversion, MomentumROC


def fetch_candles(
    exchange: str,
    symbol: str,
    start_date: str,
    end_date: str,
    timeframe: str = '1h'
) -> np.ndarray:
    """
    Fetch historical candles for backtesting.
    
    Args:
        exchange: Exchange name (e.g., 'Kraken Futures')
        symbol: Trading pair (e.g., 'BTC-USDT')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timeframe: Candle timeframe (e.g., '1h', '4h', '1D')
    
    Returns:
        NumPy array of candles
    """
    print(f"📊 Fetching candles: {exchange} {symbol} {timeframe}")
    print(f"   Period: {start_date} to {end_date}")
    
    try:
        candles = get_candles(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            start_date_str=start_date,
            finish_date_str=end_date,
        )
        print(f"   ✅ Fetched {len(candles)} candles")
        return candles
    except Exception as e:
        print(f"   ❌ Error fetching candles: {e}")
        raise


def run_backtest(
    strategy_class,
    config: Dict,
    routes: List[Dict],
    data_routes: List[Dict],
    candles: Dict,
    warmup_candles: Optional[Dict] = None,
) -> Dict:
    """
    Run a single backtest.
    
    Args:
        strategy_class: Strategy class to test
        config: Backtest configuration
        routes: Trading routes
        data_routes: Additional data routes
        candles: Candle data dictionary
        warmup_candles: Optional warmup candles
    
    Returns:
        Backtest results dictionary
    """
    strategy_name = strategy_class.__name__
    print(f"\n🚀 Running backtest: {strategy_name}")
    print(f"   Config: ${config['starting_balance']:,.0f} | Fee: {config['fee']*100:.2f}%")
    
    results = backtest(
        config=config,
        routes=routes,
        data_routes=data_routes,
        candles=candles,
        warmup_candles=warmup_candles,
        generate_equity_curve=True,
        generate_csv=True,
        generate_logs=True,
    )
    
    return results


def print_results(results: Dict, strategy_name: str):
    """
    Print formatted backtest results.
    """
    print(f"\n{'='*60}")
    print(f"📈 BACKTEST RESULTS: {strategy_name}")
    print(f"{'='*60}")
    
    if 'metrics' in results:
        m = results['metrics']
        print(f"\n💰 Performance:")
        print(f"   Starting Balance: ${m.get('starting_balance', 0):,.2f}")
        print(f"   Final Balance:    ${m.get('final_balance', 0):,.2f}")
        print(f"   Total Return:     {m.get('total_return_percentage', 0):.2f}%")
        print(f"   Annual Return:    {m.get('annual_return_percentage', 0):.2f}%")
        
        print(f"\n📊 Trade Statistics:")
        print(f"   Total Trades:     {m.get('total_trades', 0)}")
        print(f"   Win Rate:         {m.get('win_rate', 0):.1f}%")
        print(f"   Profit Factor:    {m.get('profit_factor', 0):.2f}")
        print(f"   Avg Win:          ${m.get('average_win', 0):,.2f}")
        print(f"   Avg Loss:         ${m.get('average_loss', 0):,.2f}")
        
        print(f"\n⚠️  Risk Metrics:")
        print(f"   Max Drawdown:     {m.get('max_drawdown_percentage', 0):.2f}%")
        print(f"   Sharpe Ratio:     {m.get('sharpe_ratio', 0):.2f}")
        print(f"   Sortino Ratio:    {m.get('sortino_ratio', 0):.2f}")
    else:
        print("   ⚠️ No metrics available in results")
    
    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Backtest trading strategies')
    parser.add_argument('--strategy', type=str, choices=['GoldenCross', 'RSIMeanReversion', 'MomentumROC'],
                        help='Strategy to backtest')
    parser.add_argument('--all', action='store_true', help='Run all strategies')
    parser.add_argument('--symbol', type=str, default='BTC-USDT', help='Trading pair')
    parser.add_argument('--timeframe', type=str, default='1h', help='Candle timeframe')
    parser.add_argument('--start', type=str, default='2024-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2024-12-01', help='End date (YYYY-MM-DD)')
    parser.add_argument('--balance', type=float, default=10000, help='Starting balance')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.strategy and not args.all:
        parser.error("Please specify --strategy or --all")
    
    # Build strategy list
    strategies = []
    if args.all:
        strategies = [GoldenCross, RSIMeanReversion, MomentumROC]
    else:
        strategy_map = {
            'GoldenCross': GoldenCross,
            'RSIMeanReversion': RSIMeanReversion,
            'MomentumROC': MomentumROC,
        }
        strategies = [strategy_map[args.strategy]]
    
    # Update config
    config = BACKTEST_CONFIG.copy()
    config['starting_balance'] = args.balance
    
    # Fetch candles
    exchange = 'Kraken Futures'
    candle_key = f"{exchange}-{args.symbol}"
    
    try:
        candle_data = fetch_candles(
            exchange=exchange,
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end,
            timeframe=args.timeframe,
        )
    except Exception as e:
        print(f"\n❌ Failed to fetch candles: {e}")
        print("\n💡 Tip: You may need to import candles first using Jesse's import_candles function")
        print("   Or use a different data source / exchange that has historical data available")
        sys.exit(1)
    
    candles = {
        candle_key: {
            'exchange': exchange,
            'symbol': args.symbol,
            'candles': candle_data,
        }
    }
    
    # Run backtests
    for strategy_class in strategies:
        routes = [
            {'exchange': exchange, 'strategy': strategy_class.__name__, 
             'symbol': args.symbol, 'timeframe': args.timeframe}
        ]
        
        results = run_backtest(
            strategy_class=strategy_class,
            config=config,
            routes=routes,
            data_routes=[],
            candles=candles,
        )
        
        print_results(results, strategy_class.__name__)
    
    print("✅ Backtesting complete!")


if __name__ == '__main__':
    main()
