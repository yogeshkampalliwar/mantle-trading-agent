import requests
import json

RPC_URL = "https://rpc.sepolia.mantle.xyz"

def get_mnt_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=mantle&vs_currencies=usd"
    r = requests.get(url, timeout=10)
    return r.json().get("mantle", {}).get("usd", 0)

def get_block_number():
    payload = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    return int(r.json()["result"], 16)

def trading_signal(price):
    if price < 0.5:
        return "BUY"
    elif price > 1.0:
        return "SELL"
    else:
        return "HOLD"

if __name__ == "__main__":
    print("Mantle AI Trading Agent Starting...")
    price = get_mnt_price()
    print(f"MNT Price: ${price}")
    block = get_block_number()
    print(f"Latest Block: {block}")
    signal = trading_signal(price)
    print(f"Trading Signal: {signal}")
    print("Agent Running Successfully!")
