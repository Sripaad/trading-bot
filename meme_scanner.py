#!/usr/bin/env python3
"""
Meme Coin Scanner CLI

Scans meme coins on various chains and shows opportunities.

Usage:
    python3 meme_scanner.py                     # Scan trending
    python3 meme_scanner.py --search PEPE       # Search specific token
    python3 meme_scanner.py --chain ethereum    # Scan different chain
    python3 meme_scanner.py --watch BONK WIF    # Watch specific tokens
"""

import argparse
import time
from datetime import datetime
from data_sources.dexscreener import DexScreener


def print_pair_table(pairs, title=""):
    """Print pairs in a nice table format."""
    if title:
        print(f"\n{title}")
        print("=" * 80)
    
    print(f"{'Token':<15} {'Price':<14} {'1h':<8} {'24h':<8} {'Volume':<12} {'Signal':<10}")
    print("-" * 80)
    
    for pair in pairs:
        # Determine signal emoji
        if pair.price_change_1h > 5 and pair.buy_sell_ratio > 1.2:
            signal = "🟢 BULLISH"
        elif pair.price_change_1h < -5 or pair.buy_sell_ratio < 0.7:
            signal = "🔴 BEARISH"
        else:
            signal = "⚪ NEUTRAL"
        
        # Format price
        if pair.price_usd < 0.00001:
            price_str = f"${pair.price_usd:.8f}"
        elif pair.price_usd < 1:
            price_str = f"${pair.price_usd:.6f}"
        else:
            price_str = f"${pair.price_usd:,.2f}"
        
        # Format volume
        if pair.volume_24h >= 1_000_000:
            vol_str = f"${pair.volume_24h/1_000_000:.1f}M"
        elif pair.volume_24h >= 1_000:
            vol_str = f"${pair.volume_24h/1_000:.0f}K"
        else:
            vol_str = f"${pair.volume_24h:.0f}"
        
        symbol = pair.base_token.get('symbol', '???')[:12]
        
        print(f"{symbol:<15} {price_str:<14} {pair.price_change_1h:+6.1f}% {pair.price_change_24h:+6.1f}% {vol_str:<12} {signal}")
    
    print()


def scan_trending(dex: DexScreener, chain: str = 'solana'):
    """Scan trending meme coins."""
    print(f"🔍 Scanning trending meme coins on {chain.upper()}...")
    
    pairs = dex.get_trending(chain)
    
    if not pairs:
        print("No pairs found!")
        return
    
    print_pair_table(pairs, f"🔥 Top Meme Coins by Volume ({chain.upper()})")
    
    # Highlight opportunities
    bullish = [p for p in pairs if p.is_bullish()]
    if bullish:
        print("🎯 POTENTIAL OPPORTUNITIES:")
        for p in bullish[:3]:
            print(f"  • {p.base_token['symbol']}: {p.price_change_1h:+.1f}% 1h, {p.buy_sell_ratio:.1f}x buy pressure")
    else:
        print("😴 No strong bullish signals right now")


def search_token(dex: DexScreener, query: str):
    """Search and analyze a specific token."""
    print(f"🔍 Searching for {query}...")
    
    analysis = dex.analyze_token(query)
    
    if not analysis:
        print(f"❌ No results found for '{query}'")
        return
    
    print(f"\n📊 {analysis['symbol']} on {analysis['chain'].upper()}")
    print("=" * 50)
    print(f"Price:       ${analysis['price']:.8f}")
    print(f"1h Change:   {analysis['price_change_1h']:+.1f}%")
    print(f"24h Change:  {analysis['price_change_24h']:+.1f}%")
    print(f"24h Volume:  ${analysis['volume_24h']:,.0f}")
    print(f"Liquidity:   ${analysis['liquidity']:,.0f}")
    print(f"Buy/Sell:    {analysis['buy_sell_ratio']:.2f}x")
    print()
    
    # Signal
    signal_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}
    print(f"Signal: {signal_emoji.get(analysis['signal'], '❓')} {analysis['signal']}")
    
    if analysis['reasons']:
        print("Reasons:")
        for reason in analysis['reasons']:
            print(f"  • {reason}")
    
    print(f"\nChart: {analysis['url']}")


def watch_tokens(dex: DexScreener, tokens: list, interval: int = 30):
    """Watch specific tokens with live updates."""
    print(f"👀 Watching: {', '.join(tokens)}")
    print(f"   Refreshing every {interval}s (Ctrl+C to stop)\n")
    
    try:
        while True:
            print(f"\n--- {datetime.now().strftime('%H:%M:%S')} ---")
            
            for token in tokens:
                analysis = dex.analyze_token(token)
                if analysis:
                    signal_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}
                    print(f"{token}: ${analysis['price']:.6f} | {analysis['price_change_1h']:+.1f}% 1h | {signal_emoji.get(analysis['signal'], '❓')} {analysis['signal']}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n👋 Stopped watching")


def main():
    parser = argparse.ArgumentParser(description='Meme Coin Scanner')
    parser.add_argument('--search', '-s', type=str, help='Search for specific token')
    parser.add_argument('--chain', '-c', type=str, default='solana', help='Chain to scan (solana/ethereum/bsc)')
    parser.add_argument('--watch', '-w', nargs='+', help='Watch specific tokens')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Watch interval in seconds')
    
    args = parser.parse_args()
    
    dex = DexScreener()
    
    if args.search:
        search_token(dex, args.search)
    elif args.watch:
        watch_tokens(dex, args.watch, args.interval)
    else:
        scan_trending(dex, args.chain)


if __name__ == '__main__':
    main()
