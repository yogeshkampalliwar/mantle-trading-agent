import requests
import time
import json
from datetime import datetime

RPC_URL = "https://rpc.sepolia.mantle.xyz"

def get_mnt_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=mantle&vs_currencies=usd&include_24hr_change=true"
    r = requests.get(url, timeout=10)
    data = r.json().get("mantle", {})
    return data.get("usd", 0), data.get("usd_24h_change", 0)

def get_block():
    payload = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16)

def ai_signal(price, change_24h):
    score = 0
    if price < 0.4: score += 2
    elif price < 0.6: score += 1
    if change_24h < -5: score += 2
    elif change_24h < -2: score += 1
    elif change_24h > 5: score -= 2
    elif change_24h > 2: score -= 1
    if score >= 2: return "STRONG BUY", "HIGH"
    elif score == 1: return "BUY", "MEDIUM"
    elif score == -1: return "SELL", "MEDIUM"
    elif score <= -2: return "STRONG SELL", "HIGH"
    else: return "HOLD", "LOW"

def run_agent(cycles=3):
    print("Mantle AI Trading Agent v2.0")
    print("="*40)
    trades = []
    for i in range(cycles):
        price, change = get_mnt_price()
        block = get_block()
        signal, confidence = ai_signal(price, change)
        trade = {
            "cycle": i+1,
            "time": datetime.now().strftime("%H:%M:%S"),
            "price": price,
            "change_24h": round(change, 2),
            "block": block,
            "signal": signal,
            "confidence": confidence
        }
        trades.append(trade)
        print(f"Cycle {i+1}: Price=${price} | 24h={change:.2f}% | Signal={signal} | Confidence={confidence}")
        if i < cycles-1:
            time.sleep(5)
    with open("trades.json", "w") as f:
        json.dump(trades, f, indent=2)
    print("="*40)
    print(f"Agent completed {cycles} cycles. Results saved to trades.json")
    return trades

if __name__ == "__main__":
    run_agent(3)
