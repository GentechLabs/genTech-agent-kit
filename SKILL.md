---
name: gentech-agent-kit
description: "Full GenTech stack — payments, DeFi, self-evolution, MCP server"
version: 0.4.0
author: GenTech Labs
tags: [mcp, payments, defi, self-evolution, hermes, x402, q402]
dependencies: [hermes-v0.19+]
---

# GenTech Agent Kit

Full-stack agent infrastructure: payment rails (x402 + Q402), DeFi intelligence, self-evolution harness, and MCP server.

## Included Skills
- **x402-payments** — Solana micropayment gateway
- **robinhood-chain** — Robinhood Chain (USDG, stocks)
- **output-enforcer** — Structured output with circuit breaker
- **wakeup-protocol** — Session wakeup + env loading

## Self-Evolution
Four cron jobs (Evolution, Critic, Verifier, Gardener) make the agent measurably better over time. Witness log auto-fed from context-weight nightly.

## Requires
- Hermes v0.19.0+
- CMC_API_KEY

## Payment Rails
- x402 Solana micropayments (Pay wallet: pX1FTLyXAskfD4y8pRwx7Go58GpM9t2PtGZGj6Lq2hR)
- Q402 gasless stablecoin (USDC/USDT on 12 chains, BNB trial)
