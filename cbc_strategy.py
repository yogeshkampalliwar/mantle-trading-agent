#!/usr/bin/env python3
"""
CBC Flip Strategy - Mantle Network AI Trading Agent
Turing Test Hackathon 2026 - AI Trading & Strategy Track
News Sentiment + Price Action + On-chain Data
"""

import requests
import time
import json
from datetime import datetime

RPC_URL = "https://rpc.sepolia.mantle.xyz"
COINGECKO = "https://api.coingecko.com/api/v3"
NEWS_API = "https://cryptopanic.com/api/v1/posts/?auth_token=free&currencies=MNT&kind=news"

def get_mnt_price():
    r = requests.get(f"{COINGECKO}/simple/price?ids=mantle&vs_currencies=usd&include_24hr_change=true", timeout=10)
    data = r.json().get("mantle", {})
    return data.get("usd", 0), data.get("usd_24h_change", 0)

def get_block():
    payload = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16)

def get_news_sentiment():
    """Free CryptoPanic news sentiment - no captcha"""
    try:
        r = requests.get(NEWS_API, timeout=10)
        data = r.json()
        results = data.get("results", [])
        bullish = 0
        bearish = 0
        headlines = []
        for news in results[:5]:
            title = news.get("title", "")
            headlines.append(title)
            votes = news.get("votes", {})
            bullish += votes.get("positive", 0)
            bearish += votes.get("negative", 0)
        if bullish > bearish:
            sentiment = "BULLISH"
            score = 1
        elif bearish > bullish:
            sentiment = "BEARISH"
            score = -1
        else:
            sentiment = "NEUTRAL"
            score = 0
        return sentiment, score, headlines[:3]
    except:
        return "NEUTRAL", 0, []

def get_gas_price():
    payload = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16) / 1e9

def cbc_signal(price, change_24h, prev_price, news_score):
    score = 0
    reasons = []

    # News sentiment
    if news_score > 0:
        score += 1
        reasons.append("Bullish news")
    elif news_score < 0:
        score -= 1
        reasons.append("Bearish news")

    # 24h change
    if change_24h < -5:
        score += 2
        reasons.append("Strong bearish 24h")
    elif change_24h < -2:
        score += 1
        reasons.append("Bearish 24h")
    elif change_24h > 5:
        score -= 2
        reasons.append("Strong bullish 24h")
    elif change_24h > 2:
        score -= 1
        reasons.append("Bullish 24h")

    # Flip detection
    if prev_price > 0:
        flip_pct = (price - prev_price) / prev_price * 100
        if flip_pct > 1.0:
            score -= 1
            reasons.append(f"Flip up {flip_pct:.2f}%")
        elif flip_pct < -1.0:
            score += 1
            reasons.append(f"Flip down {flip_pct:.2f}%")

    # Support/Resistance
    if price < 0.40:
        score += 2
        reasons.append("Near support $0.40")
    elif price > 0.80:
        score -= 2
        reasons.append("Near resistance $0.80")

    # Signal
    if score >= 3:
        signal, side = "STRONG BUY", "LONG"
    elif score >= 1:
        signal, side = "BUY", "LONG"
    elif score <= -3:
        signal, side = "STRONG SELL", "SHORT"
    elif score <= -1:
        signal, side = "SELL", "SHORT"
    else:
        signal, side = "HOLD", "NEUTRAL"

    sl_dist = price * 0.02
    if side == "LONG":
        sl = price - sl_dist
        tp1 = price + sl_dist * 1.0
        tp2 = price + sl_dist * 1.5
        tp3 = price + sl_dist * 2.0
    elif side == "SHORT":
        sl = price + sl_dist
        tp1 = price - sl_dist * 1.0
        tp2 = price - sl_dist * 1.5
        tp3 = price - sl_dist * 2.0
    else:
        sl = tp1 = tp2 = tp3 = price

    return {
        "signal": signal,
        "side": side,
        "score": score,
        "reasons": reasons,
        "sl": round(sl, 6),
        "tp1": round(tp1, 6),
        "tp2": round(tp2, 6),
        "tp3": round(tp3, 6),
        "rr": "1:2.0"
    }

def run_cbc_agent(cycles=5):
    print("="*55)
    print("  CBC Flip Strategy - Mantle AI Trading Agent v3")
    print("  News Sentiment + Price Action + On-chain Data")
    print("  Turing Test Hackathon 2026")
    print("="*55)

    prev_price = 0
    results = []

    for i in range(cycles):
        print(f"\n[Cycle {i+1}/{cycles}] {datetime.now().strftime('%H:%M:%S')}")
        price, change = get_mnt_price()
        block = get_block()
        gas = get_gas_price()
        sentiment, news_score, headlines = get_news_sentiment()
        signal_data = cbc_signal(price, change, prev_price, news_score)

        result = {
            "cycle": i+1,
            "timestamp": datetime.now().isoformat(),
            "price_usd": price,
            "change_24h": round(change, 2),
            "block": block,
            "gas_gwei": round(gas, 4),
            "news_sentiment": sentiment,
            "headlines": headlines,
            **signal_data
        }
        results.append(result)

        print(f"  Price     : ${price}")
        print(f"  24h Chg   : {change:.2f}%")
        print(f"  Block     : {block}")
        print(f"  Gas       : {gas:.4f} Gwei")
        print(f"  News      : {sentiment}")
        if headlines:
            print(f"  Headlines : {headlines[0][:60]}...")
        print(f"  Signal    : {signal_data['signal']} (score={signal_data['score']})")
        print(f"  Side      : {signal_data['side']}")
        print(f"  SL        : ${signal_data['sl']}")
        print(f"  TP1/2/3   : ${signal_data['tp1']} / ${signal_data['tp2']} / ${signal_data['tp3']}")
        print(f"  Reasons   : {', '.join(signal_data['reasons'])}")

        prev_price = price
        if i < cycles - 1:
            time.sleep(5)

    with open("cbc_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*55)
    print(f"  Completed {cycles} cycles")
    print(f"  Results saved to cbc_results.json")
    print("="*55)

if __name__ == "__main__":
    run_cbc_agent(5)
