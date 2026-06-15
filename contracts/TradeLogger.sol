// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title TradeLogger
/// @notice On-chain decision log for the Mantle AI Trading Agent
/// @dev Built for the Turing Test Hackathon 2026 - AI Trading & Strategy track.
///      Every AI trading decision (signal, score, reasoning) is recorded
///      permanently on Mantle, satisfying the hackathon's on-chain
///      benchmarking requirement.
///
///      agentId is designed to map to an ERC-8004 agent identity NFT,
///      giving this agent a permanent on-chain reputation record.
contract TradeLogger {
    struct Decision {
        uint256 timestamp;
        string signal;
        int256 score;
        uint256 priceUsdE6;
        string reasoning;
    }

    address public owner;
    bytes32 public agentId;
    Decision[] public decisions;

    event DecisionLogged(
        uint256 indexed index,
        string signal,
        int256 score,
        uint256 priceUsdE6,
        uint256 timestamp
    );

    constructor(bytes32 _agentId) {
        owner = msg.sender;
        agentId = _agentId;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    function logDecision(
        string calldata signal,
        int256 score,
        uint256 priceUsdE6,
        string calldata reasoning
    ) external onlyOwner {
        decisions.push(Decision(block.timestamp, signal, score, priceUsdE6, reasoning));
        emit DecisionLogged(decisions.length - 1, signal, score, priceUsdE6, block.timestamp);
    }

    function totalDecisions() external view returns (uint256) {
        return decisions.length;
    }

    function getDecision(uint256 index) external view returns (Decision memory) {
        return decisions[index];
    }
}
