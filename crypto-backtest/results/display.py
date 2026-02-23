#!/usr/bin/env python3
"""
Results Display - Format and display backtest results
"""

import json
import os
from datetime import datetime

RESULTS_DIR = "results"

def format_currency(amount):
    """Format as USD"""
    return f"${amount:,.2f}"

def format_percent(pct):
    """Format as percentage"""
    return f"{pct:+.2f}%"

def display_metrics(metrics):
    """Display metrics in readable format"""
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    
    print(f"\n📊 SUMMARY")
    print(f"  Total Trades:    {metrics['total_trades']}")
    print(f"  Win Rate:        {metrics['win_rate']:.1f}%")
    
    print(f"\n💰 PROFIT/LOSS")
    print(f"  Total P&L:       {format_currency(metrics['total_pnl'])}")
    print(f"  Return:          {format_percent(metrics.get('return_pct', 0))}")
    print(f"  Final Balance:   {format_currency(metrics.get('final_balance', 0))}")
    
    print(f"\n✅ WINNING TRADES")
    print(f"  Count:           {metrics['profitable']}")
    print(f"  Avg Profit:      {format_currency(metrics.get('avg_profit', 0))}")
    print(f"  Max Profit:      {format_currency(metrics.get('max_profit', 0))}")
    
    print(f"\n❌ LOSING TRADES")
    print(f"  Count:           {metrics['losing']}")
    print(f"  Avg Loss:        {format_currency(metrics.get('avg_loss', 0))}")
    print(f"  Max Loss:        {format_currency(metrics.get('max_loss', 0))}")
    
    print("\n" + "="*50)

def display_trade_list(trades, limit=10):
    """Display individual trades"""
    if not trades:
        print("No trades executed.")
        return
        
    print(f"\n📋 LAST {min(limit, len(trades))} TRADES")
    print("-" * 60)
    print(f"{'Coin':<10} {'Entry':>10} {'Exit':>10} {'P&L':>12} {'%':>8}")
    print("-" * 60)
    
    for t in trades[-limit:]:
        print(f"{t['coin']:<10} ${t['entry']:>8.4f} ${t['exit']:>8.4f} {format_currency(t['pnl']):>12} {format_percent(t['pnl_pct']):>8}")


def load_results(strategy_name=None):
    """Load results from files"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
    if strategy_name:
        files = [f for f in files if strategy_name in f]
    
    files.sort(reverse=True)
    
    results = []
    for f in files:
        with open(os.path.join(RESULTS_DIR, f)) as fp:
            results.append(json.load(fp))
    
    return results

def compare_strategies(results):
    """Compare multiple strategy results"""
    if not results:
        print("No results to compare.")
        return
        
    print("\n" + "="*70)
    print("STRATEGY COMPARISON")
    print("="*70)
    print(f"{'Strategy':<20} {'Trades':>8} {'Win%':>8} {'P&L':>12} {'Return':>10}")
    print("-" * 70)
    
    for r in results:
        m = r["metrics"]
        print(f"{r['strategy']:<20} {m['total_trades']:>8} {m['win_rate']:>7.1f}% {format_currency(m['total_pnl']):>12} {format_percent(m.get('return_pct', 0)):>10}")
    
    print("="*70)


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Show latest results
        results = load_results()
        if results:
            latest = results[0]
            display_metrics(latest["metrics"])
            display_trade_list(latest["metrics"].get("trades", []))
        else:
            print("No results found.")
    elif sys.argv[1] == "list":
        results = load_results()
        compare_strategies(results)
    elif sys.argv[1] == "compare":
        results = load_results()
        compare_strategies(results)
    else:
        # Show specific strategy
        results = load_results(sys.argv[1])
        if results:
            latest = results[0]
            display_metrics(latest["metrics"])
        else:
            print(f"No results for {sys.argv[1]}")
