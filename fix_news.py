import requests

apis = [
    "https://feeds.feedburner.com/CoinDesk",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://bitcoinist.com/feed/",
]

for api in apis:
    try:
        r = requests.get(api, timeout=5)
        print(f"Status {r.status_code}: {api[:50]}")
    except Exception as e:
        print(f"Error: {api[:50]} - {e}")
