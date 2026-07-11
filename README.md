# GenTech Agent Kit

**One install. Full stack. Your agent, running.**

[![Release](https://img.shields.io/github/v/release/ProtoJay4789/genTech-agent-kit?style=flat&label=release)](https://github.com/ProtoJay4789/genTech-agent-kit/releases)
[![License](https://img.shields.io/github/license/ProtoJay4789/genTech-agent-kit?style=flat)](LICENSE)
[![Language](https://img.shields.io/github/languages/top/ProtoJay4789/genTech-agent-kit?style=flat)](https://github.com/ProtoJay4789/genTech-agent-kit)
[![Skills](https://img.shields.io/badge/skills-npx%20install-blue?style=flat)](https://github.com/ProtoJay4789/genTech-agent-kit/tree/main/skills)
[![x402](https://img.shields.io/badge/payments-x402-8A2BE2?style=flat)](https://www.x402.org)
[![Atelier](https://img.shields.io/badge/marketplace-Atelier-000?style=flat)](https://useatelier.ai)

The GenTech Agent Kit packages the entire GenTech stack into a single installable MCP server. One command gives any AI agent real-time market data, DeFi intelligence, payment rails, and agent identity infrastructure.

```bash
uvx --from git+https://github.com/ProtoJay4789/genTech-agent-kit.git gentech-kit
```

## Install as Agent Skills

```bash
# Install the main skill
npx skills add ProtoJay4789/genTech-agent-kit

# Install specific skills
npx skills add ProtoJay4789/genTech-agent-kit --skill x402-payments
npx skills add ProtoJay4789/genTech-agent-kit --skill robinhood-chain
npx skills add ProtoJay4789/genTech-agent-kit --skill output-enforcer
```

## Quick Start

```bash
# Install and run
uvx --from git+https://github.com/ProtoJay4789/genTech-agent-kit.git gentech-kit
```

Requires: `CMC_API_KEY` env var (get one free at coinmarketcap.com/api)

```bash
export CMC_API_KEY="your-key-here"
```

## Tools

### Market Data
| Tool | Description |
|------|-------------|
| `get_quote(symbol)` | Real-time price for BTC, ETH, SOL, etc. |
| `get_listings(start, limit)` | Top tokens by market cap |
| `search_token(symbol)` | Token metadata, description, tags, logo |
| `get_trending(kind)` | Gainers, losers, most visited, latest |
| `get_dex_pairs(symbol)` | DEX pair data across exchanges |

### Platform
| Tool | Description |
|------|-------------|
| `kit_info()` | Agent Kit version, tool list, update status |

### Plugins (auto-discovered)
| Plugin | Tools | Settlement |
|--------|-------|------------|
| Algorand x402 Gateway | `algorand_x402_info`, `algorand_verify_payment`, `algorand_get_quote` | ALGO via GoPlausible |
| Robinhood Chain x402 | `rh_info`, `rh_list_stocks`, `rh_get_stock`, `rh_crypto_quote`, `rh_verify_payment` | USDG via Naven Network |
| Output Enforcer | `output_enforcer_status`, `output_enforcer_violations`, `output_enforcer_clear`, `output_enforcer_breakers` | — |
| Pika Creative Suite | `pika_skills`, `pika_generate`, `pika_build_brand`, `pika_app_sizzle`, `pika_explainer` | — |

### Demo: x402 Payment Flow

```bash
# Hit a paid endpoint without payment
curl -i https://api.naven.network/x402-test/ping
# → HTTP 402 Payment Required with x402 v2 challenge
# → Network: Robinhood Chain (eip155:4663)
# → Token: USDG ($0.0001 per query)
```

## Why GenTech Agent Kit?

| Feature | Benefit |
|---------|---------|
| **Always updated** | Active development — new tools ship continuously. `uv tool install --reinstall` gets the latest. |
| **Adaptive stack** | Modular design. Tools discovered dynamically — the kit grows without breaking existing integrations. |
| **x402 native** | Every API supports machine-to-machine micropayments. Pay per query, no subscription. |
| **Open source** | MIT license. Audit, fork, extend. No vendor lock-in. |
| **Premier distribution** | Listed on Atelier, PortalHQ, Monad Agent Hub. Your agent finds us automatically. |

## MCP Client Setup

### Claude Code
```bash
claude mcp add gentech-agent-kit \
  --env CMC_API_KEY=your-key-here \
  -- uvx --from git+https://github.com/ProtoJay4789/genTech-agent-kit.git gentech-kit
```

### Claude Desktop
```json
{
  "mcpServers": {
    "gentech-agent-kit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/ProtoJay4789/genTech-agent-kit.git", "gentech-kit"],
      "env": { "CMC_API_KEY": "your-key-here" }
    }
  }
}
```

## License

MIT — GenTech Labs

## About

**GenTech Labs** builds payment infrastructure for AI agents. We make it possible for agents to pay each other, subscribe to services, and earn revenue — all on-chain, all autonomously.
