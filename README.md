# Mantle AI Trading Agent

**Turing Test Hackathon 2026 - Track: AI Trading & Strategy**

An autonomous AI agent that monitors MNT price action and Mantle Network on-chain state in real time, generates trading signals using technical analysis, and is designed to permanently record every decision on-chain via the TradeLogger smart contract.

## How It Works

1. Live data ingestion
   - Fetches MNT/USD price + 24h change from CoinGecko
   - Reads the current Mantle Sepolia block height via JSON-RPC (eth_blockNumber)
   - Pulls 7-day price history for trend analysis

2. AI Strategy Engine (agent.py)
   - SMA Crossover: 6-period vs 24-period simple moving average to detect trend direction
   - RSI (14): identifies overbought (>70) / oversold (<30) conditions
   - 24h Momentum: scores sharp price moves
   - Each indicator contributes to a weighted score, producing a final signal:
     STRONG BUY / BUY / HOLD / SELL / STRONG SELL with a confidence level
     (HIGH / MEDIUM / LOW) and a human-readable reasoning trace for every decision

3. On-chain decision recording (contracts/TradeLogger.sol)
   - Every signal, score, price and reasoning string is designed to be written
     on-chain via logDecision(), emitting a DecisionLogged event
   - This satisfies the hackathon requirement that every agent decision
     and outcome is recorded permanently on Mantle
   - agentId (bytes32) is reserved for mapping to an ERC-8004 agent identity NFT,
     giving this agent a persistent on-chain reputation record

## Run the Agent

    pip install requests
    python3 agent.py

## Sample Output

    ==================================================
      Mantle AI Trading Agent v3.0
      Turing Test Hackathon 2026 - AI Trading & Strategy
    ==================================================

    Cycle 1 | Mantle Block #39987804
      Price: $0.574011 (2.6% 24h)
      SMA6: 0.5731 | SMA24: 0.5643 | RSI: 65.1
      >> Signal: HOLD (confidence: LOW, score: 0)
         - 24h gain of 2.6%
         - short-term SMA above long-term SMA - uptrend

Full structured output (including agent identity metadata) is saved to trades.json after each run.

## Architecture

    CoinGecko API (price+history)      Mantle Sepolia RPC (eth_blockNumber)
                |                                  |
                v                                  v
            agent.py AI Engine: SMA(6,24) + RSI(14) + 24h momentum
                              -> weighted score -> signal
                              |
                              v
              contracts/TradeLogger.sol (on-chain log)
                              |
                              v
                 ERC-8004 Agent Identity NFT (planned)

## Roadmap / On-chain Integration Plan

- [x] Real-time price + on-chain block monitoring
- [x] Multi-indicator AI signal engine with reasoning traces
- [x] On-chain TradeLogger contract design
- [ ] Deploy TradeLogger.sol to Mantle Sepolia (pending testnet funds)
- [ ] Wire agent.py to call logDecision() via web3.py after each cycle
- [ ] Mint ERC-8004 identity NFT for the agent and link agentId
- [ ] Integrate with RealClaw (Byreal) for live execution on Mantle DeFi

## Agent Identity

    agent_id: mantle-ai-trader-001
    name: Mantle AI Trading Agent
    version: 3.0
    wallet: 0x466ad8606625a3ce2923a7fea9b0eb5477433337
    track: AI Trading and Strategy
    hackathon: Turing Test Hackathon 2026

## Tech Stack

- Python 3 (requests, json, datetime)
- Mantle Sepolia Testnet (Chain ID 5003) via JSON-RPC
- Solidity ^0.8.20 (on-chain decision logging)
- CoinGecko API (price feed)
