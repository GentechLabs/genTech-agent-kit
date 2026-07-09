# GenTech Agent Kit

**One install. Full stack. Your agent, running.**

The GenTech Agent Kit packages the entire GenTech stack into a single installable MCP server. One command gives any AI agent real-time market data, DeFi intelligence, payment rails, and agent identity infrastructure.

```bash
uvx --from git+https://github.com/ProtoJay4789/genTech-agent-kit.git gentech-kit
```

## Why GenTech Agent Kit?

| Feature | Benefit |
|---------|---------|
| **Always updated** | Active development — new tools ship continuously. `uv tool install --reinstall` gets the latest. |
| **Adaptive stack** | Modular design. Tools are discovered dynamically — the kit grows without breaking existing integrations. |
| **x402 native** | Every API supports machine-to-machine micropayments. Pay per query, no subscription. |
| **Open source** | MIT license. Audit, fork, extend. No vendor lock-in. |
| **Premier distribution** | Listed on Atelier, PortalHQ, and Monad Agent Hub. Your agent finds us automatically. |

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

### More Coming
DeFi Intelligence, Agent Registration, Agent Search, and Agent Arena tools ship in upcoming releases.

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

## Development

```bash
git clone https://github.com/ProtoJay4789/genTech-agent-kit.git
cd genTech-agent-kit
uv sync
uv run gentech-kit
```

## License

MIT — GenTech Labs