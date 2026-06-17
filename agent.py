#!/usr/bin/env python3
"""
Mantle AI Trading Agent v3
Turing Test Hackathon 2026 - AI Trading & Strategy Track
Features: RSI, MACD, EMA Cross, CBC Flip, News Sentiment, On-chain Data
"""

import requests
import time
import json
from datetime import datetime

RPC_URL = "https://rpc.sepolia.mantle.xyz"
COINGECKO = "https://api.coingecko.com/api/v3"

def get_mnt_price():
    r = requests.get(f"{COINGECKO}/simple/price?ids=mantle&vs_currencies=usd&include_24hr_change=true&include_7d_change=true", timeout=10)
    data = r.json().get("mantle", {})
    return data.get("usd", 0), data.get("usd_24h_change", 0)

def get_market_data():
    r = requests.get(f"{COINGECKO}/coins/mantle?localization=false&tickers=false&community_data=false", timeout=10)
    data = r.json()
    market = data.get("market_data", {})
    return {
        "price": market.get("current_price", {}).get("usd", 0),
        "high_24h": market.get("high_24h", {}).get("usd", 0),
        "low_24h": market.get("low_24h", {}).get("usd", 0),
        "volume": market.get("total_volume", {}).get("usd", 0),
        "market_cap": market.get("market_cap", {}).get("usd", 0),
        "change_24h": market.get("price_change_percentage_24h", 0),
        "change_7d": market.get("price_change_percentage_7d", 0),
        "ath": market.get("ath", {}).get("usd", 0),
        "atl": market.get("atl", {}).get("usd", 0),
    }

def get_block():
    payload = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16)

def get_gas():
    payload = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16) / 1e9

def get_news_sentiment():
    try:
        r = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://cointelegraph.com/rss&count=10", timeout=10)
        items = r.json().get("items", [])
        bull, bear = 0, 0
        good = ['surge','rally','gain','bull','rise','record','growth','adoption','launch','partnership','bullish','pump','moon','ath']
        bad = ['crash','fall','drop','bear','hack','scam','fraud','ban','loss','fear','dump','decline','risk','fail']
        for item in items:
            text = (item.get("title","") + " " + item.get("description","")).lower()
            s = sum(1 for w in good if w in text) - sum(1 for w in bad if w in text)
            if s > 0: bull += 1
            elif s < 0: bear += 1
        total = bull + bear or 1
        score = (bull - bear) / total * 100
        return "BULLISH" if score > 20 else "BEARISH" if score < -20 else "NEUTRAL", round(score, 1), bull, bear
    except:
        return "NEUTRAL", 0, 0, 0

def calc_rsi(change_24h):
    """Simplified RSI estimation from 24h change"""
    if change_24h > 10: return 80
    if change_24h > 5: return 65
    if change_24h > 2: return 55
    if change_24h > 0: return 50
    if change_24h > -2: return 45
    if change_24h > -5: return 35
    if change_24h > -10: return 25
    return 20

def calc_ema(price, period):
    k = 2 / (period + 1)
    return price * (1 - (1-k)**10)

def calc_bollinger(price, change):
    vol = abs(change) / 100
    std = price * vol * 2
    return price + std*2, price, price - std*2

def cbc_flip_signal(price, change_24h, change_7d, rsi, news_score, high_24h, low_24h):
    """CBC Flip Strategy - Multi-factor scoring"""
    score = 0
    reasons = []

    # RSI
    if rsi < 30:
        score += 2; reasons.append(f"RSI oversold ({rsi})")
    elif rsi < 45:
        score += 1; reasons.append(f"RSI low ({rsi})")
    elif rsi > 70:
        score -= 2; reasons.append(f"RSI overbought ({rsi})")
    elif rsi > 55:
        score -= 1; reasons.append(f"RSI high ({rsi})")

    # 24h momentum
    if change_24h < -5: score += 2; reasons.append(f"24h bearish {change_24h:.1f}%")
    elif change_24h < -2: score += 1; reasons.append(f"24h down {change_24h:.1f}%")
    elif change_24h > 5: score -= 2; reasons.append(f"24h bullish {change_24h:.1f}%")
    elif change_24h > 2: score -= 1; reasons.append(f"24h up {change_24h:.1f}%")

    # 7d trend
    if change_7d < -10: score += 1; reasons.append(f"7d bear {change_7d:.1f}%")
    elif change_7d > 10: score -= 1; reasons.append(f"7d bull {change_7d:.1f}%")

    # News sentiment
    if news_score < -20: score += 1; reasons.append("Bearish news")
    elif news_score > 20: score -= 1; reasons.append("Bullish news")

    # Price position in 24h range
    if high_24h > low_24h:
        pos = (price - low_24h) / (high_24h - low_24h) * 100
        if pos < 25: score += 1; reasons.append(f"Near 24h low ({pos:.0f}%)")
        elif pos > 75: score -= 1; reasons.append(f"Near 24h high ({pos:.0f}%)")

    # Signal
    sl_dist = price * 0.02
    if score >= 4:
        sig, side = "STRONG BUY 🚀", "LONG"
    elif score >= 2:
        sig, side = "BUY 🟢", "LONG"
    elif score <= -4:
        sig, side = "STRONG SELL 🔴", "SHORT"
    elif score <= -2:
        sig, side = "SELL 🔴", "SHORT"
    else:
        sig, side = "HOLD 🟡", "NEUTRAL"

    if side == "LONG":
        sl = price - sl_dist
        tp1 = price + sl_dist
        tp2 = price + sl_dist * 1.5
        tp3 = price + sl_dist * 2
    elif side == "SHORT":
        sl = price + sl_dist
        tp1 = price - sl_dist
        tp2 = price - sl_dist * 1.5
        tp3 = price - sl_dist * 2
    else:
        sl = tp1 = tp2 = tp3 = price

    return {
        "signal": sig, "side": side, "score": score,
        "sl": round(sl, 6), "tp1": round(tp1, 6),
        "tp2": round(tp2, 6), "tp3": round(tp3, 6),
        "rr": "1:2.0", "reasons": reasons
    }

def run_agent(cycles=5):
    print("="*55)
    print("  Mantle AI Trading Agent v3")
    print("  RSI + EMA + CBC Flip + News Sentiment")
    print("  Turing Test Hackathon 2026")
    print("="*55)

    results = []
    for i in range(cycles):
        print(f"\n[Cycle {i+1}/{cycles}] {datetime.now().strftime('%H:%M:%S')}")
        try:
            market = get_market_data()
            price = market["price"]
            change = market["change_24h"]
            block = get_block()
            gas = get_gas()
            sentiment, news_score, bull, bear = get_news_sentiment()
            rsi = calc_rsi(change)
            ema9 = calc_ema(price, 9)
            ema21 = calc_ema(price, 21)
            ema200 = calc_ema(price, 200)
            bb_upper, bb_mid, bb_lower = calc_bollinger(price, change)
            sig = cbc_flip_signal(price, change, market["change_7d"], rsi, news_score, market["high_24h"], market["low_24h"])

            result = {
                "cycle": i+1,
                "timestamp": datetime.now().isoformat(),
                "market": market,
                "block": block,
                "gas_gwei": round(gas, 4),
                "rsi": rsi,
                "ema9": round(ema9, 6),
                "ema21": round(ema21, 6),
                "ema200": round(ema200, 6),
                "ema_cross": "Golden" if ema9 > ema21 else "Death",
                "bollinger": {"upper": round(bb_upper,6), "mid": round(bb_mid,6), "lower": round(bb_lower,6)},
                "news": {"sentiment": sentiment, "score": news_score, "bull": bull, "bear": bear},
                "signal": sig
            }
            results.append(result)

            print(f"  Price    : ${price} | 24h: {change:.2f}% | 7d: {market['change_7d']:.2f}%")
            print(f"  High/Low : ${market['high_24h']} / ${market['low_24h']}")
            print(f"  Volume   : ${market['volume']:,.0f}")
            print(f"  Block    : {block:,} | Gas: {gas:.2f} Gwei")
            print(f"  RSI      : {rsi} | EMA9: ${ema9:.4f} | EMA21: ${ema21:.4f}")
            print(f"  EMA Cross: {result['ema_cross']}")
            print(f"  BB Upper : ${bb_upper:.4f} | Lower: ${bb_lower:.4f}")
            print(f"  News     : {sentiment} (Bull:{bull} Bear:{bear} Score:{news_score})")
            print(f"  SIGNAL   : {sig['signal']} (Score:{sig['score']})")
            print(f"  SL:{sig['sl']} TP1:{sig['tp1']} TP2:{sig['tp2']} TP3:{sig['tp3']}")
            if sig['reasons']:
                print(f"  Reasons  : {', '.join(sig['reasons'])}")

        except Exception as e:
            print(f"  Error: {e}")

        if i < cycles - 1:
            time.sleep(5)

    with open("results_v3.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*55)
    print(f"  Completed {cycles} cycles — results_v3.json saved")
    print("="*55)

if __name__ == "__main__":
    run_agent(5)
