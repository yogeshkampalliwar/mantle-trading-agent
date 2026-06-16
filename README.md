# Mantle AI Trading Agent

Turing Test Hackathon 2026 - AI Trading and Strategy Track

Live Dashboard: https://yogeshkampalliwar.github.io/mantle-trading-agent/dashboard.html

## Overview
Autonomous AI trading agent for Mantle Network. Monitors price action, on-chain data, and news sentiment to generate real-time BUY/SELL/HOLD signals using CBC Flip Strategy.

## Features
- Real-time MNT/BTC/ETH price tracking via CoinGecko
- On-chain block and gas monitoring via Mantle Sepolia RPC
- AI news sentiment analysis BULLISH/BEARISH/NEUTRAL
- CBC Flip Strategy with multi-factor scoring
- TP1/TP2/TP3 and SL calculation
- Live colorful dashboard with auto-refresh every 30 seconds

## How It Works
1. Fetches MNT price and 24h change from CoinGecko
2. Reads block height and gas price from Mantle RPC
3. Analyzes crypto news sentiment using AI keyword scoring
4. Generates trading signal with confidence score
5. Calculates SL TP1 TP2 TP3 levels automatically

## Files
- agent.py - Basic trading agent with multi-cycle analysis
- cbc_strategy.py - CBC Flip Strategy with news sentiment
- dashboard.html - Live colorful trading dashboard

## Run
python agent.py
python cbc_strategy.py

## Tech Stack
Python 3, Mantle Sepolia RPC, CoinGecko API, CryptoPanic API, HTML CSS JS, GitHub Pages

## Contract
TradeLogger on Mantle Sepolia Testnet

## Links
Dashboard: https://yogeshkampalliwar.github.io/mantle-trading-agent/dashboard.html
GitHub: https://github.com/yogeshkampalliwar/mantle-trading-agent
