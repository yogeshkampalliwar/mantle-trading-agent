import requests
import time
import json
from datetime import datetime

RPC_URL = "https://rpc.sepolia.mantle.xyz"
COINGECKO = "https://api.coingecko.com/api/v3"

AGENT_IDENTITY = {
    "agent_id": "mantle-ai-trader-001",
    "name": "Mantle AI Trading Agent",
    "version": "3.0",
    "wallet": "0x466ad8606625a3ce2923a7fea9b0eb5477433337",
    "track": "AI Trading & Strategy",
    "hackathon": "Turing Test Hackathon 2026",
    "capabilities": ["price_monitoring", "technical_analysis", "signal_generation", "on_chain_block_tracking", "decision_logging"]
}

def get_price_history(days=7):
    url = COINGECKO + "/coins/mantle/market_chart?vs_currency=usd&days=" + str(days)
    r = requests.get(url, timeout=15)
    prices = r.json().get("prices", [])
    return [p[1] for p in prices]

def get_current_price_and_change():
    url = COINGECKO + "/simple/price?ids=mantle&vs_currencies=usd&include_24hr_change=true"
    r = requests.get(url, timeout=10)
    data = r.json().get("mantle", {})
    return data.get("usd", 0), data.get("usd_24h_change", 0)

def get_block():
    payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16)

def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period

def rsi(values, period=14):
    if len(values) < period + 1:
        return 50.0
    deltas = [values[i] - values[i-1] for i in range(1, len(values))]
    recent = deltas[-period:]
    gains = [d for d in recent if d > 0]
    losses = [-d for d in recent if d < 0]
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ai_signal(price, change_24h, sma_short, sma_long, rsi_val):
    score = 0
    reasons = []

    if change_24h < -5:
        score += 2
        reasons.append("24h drop of " + str(round(change_24h, 2)) + "% (oversold momentum)")
    elif change_24h < -2:
        score += 1
        reasons.append("24h decline of " + str(round(change_24h, 2)) + "%")
    elif change_24h > 5:
        score -= 2
        reasons.append("24h surge of " + str(round(change_24h, 2)) + "% (overbought momentum)")
    elif change_24h > 2:
        score -= 1
        reasons.append("24h gain of " + str(round(change_24h, 2)) + "%")

    if sma_short and sma_long:
        if sma_short > sma_long:
            score += 1
            reasons.append("short-term SMA above long-term SMA - uptrend")
        else:
            score -= 1
            reasons.append("short-term SMA below long-term SMA - downtrend")

    if rsi_val < 30:
        score += 2
        reasons.append("RSI=" + str(round(rsi_val, 1)) + " indicates oversold")
    elif rsi_val > 70:
        score -= 2
        reasons.append("RSI=" + str(round(rsi_val, 1)) + " indicates overbought")

    if score >= 3:
        return "STRONG BUY", "HIGH", score, reasons
    elif score >= 1:
        return "BUY", "MEDIUM", score, reasons
    elif score <= -3:
        return "STRONG SELL", "HIGH", score, reasons
    elif score <= -1:
        return "SELL", "MEDIUM", score, reasons
    else:
        return "HOLD", "LOW", score, reasons

def run_agent(cycles=3):
    print("=" * 50)
    print("  " + AGENT_IDENTITY["name"] + " v" + AGENT_IDENTITY["version"])
    print("  " + AGENT_IDENTITY["hackathon"] + " - " + AGENT_IDENTITY["track"])
    print("=" * 50)

    history = get_price_history(days=7)
    trades = []

    for i in range(cycles):
        price, change = get_current_price_and_change()
        block = get_block()
        prices_now = history + [price]
        sma_short = sma(prices_now, 6)
        sma_long = sma(prices_now, 24)
        rsi_val = rsi(prices_now, 14)
        signal, confidence, score, reasons = ai_signal(price, change, sma_short, sma_long, rsi_val)

        trade = {
            "cycle": i + 1,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "mantle_block": block,
            "price_usd": price,
            "change_24h_pct": round(change, 2),
            "sma_short_6period": round(sma_short, 6) if sma_short else None,
            "sma_long_24period": round(sma_long, 6) if sma_long else None,
            "rsi_14": round(rsi_val, 2),
            "signal": signal,
            "confidence": confidence,
            "score": score,
            "reasoning": reasons
        }
        trades.append(trade)

        print("")
        print("Cycle " + str(i+1) + " | Mantle Block #" + str(block))
        print("  Price: $" + str(price) + " (" + str(round(change,2)) + "% 24h)")
        print("  SMA6: " + str(sma_short) + " | SMA24: " + str(sma_long) + " | RSI: " + str(round(rsi_val,1)))
        print("  >> Signal: " + signal + " (confidence: " + confidence + ", score: " + str(score) + ")")
        for r in reasons:
            print("     - " + r)

        if i < cycles - 1:
            time.sleep(5)

    with open("trades.json", "w") as f:
        json.dump({"agent": AGENT_IDENTITY, "trades": trades}, f, indent=2)

    print("")
    print("=" * 50)
    print("Completed " + str(cycles) + " cycles. Decisions logged to trades.json")
    print("On-chain recording design: contracts/TradeLogger.sol")
    return trades

if __name__ == "__main__":
    run_agent(3)
