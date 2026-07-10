---
name: gentech-agent-kit
description: "GenTech Agent Kit — one install to deploy a full AI agent with payment rails, DeFi intelligence, market data, and identity. Always updated, adaptive stack, x402 micropayments."
---

# GenTech Agent Kit

One install. Full stack. Your agent, running.

## Quick Install

```bash
uvx --from git+https://github.com/ProtoJay4789/genTech-agent-kit.git gentech-kit
```

Requires: `CMC_API_KEY` env var (get one free at coinmarketcap.com/api)

## Tools

| Tool | Description |
|------|-------------|
| `get_quote` | Real-time price for BTC, ETH, SOL, etc. |
| `get_listings` | Top tokens by market cap (1-100) |
| `search_token` | Token metadata, description, tags, logo |
| `get_trending` | Gainers, losers, most visited, latest |
| `get_dex_pairs` | DEX pair data across exchanges |
| `kit_info` | Agent Kit version, tool list, update status |

## Why This Kit

- **Always updated** — Active development, new tools ship continuously
- **Adaptive stack** — Modular design, tools discovered dynamically
- **x402 native** — Machine-to-machine micropayments, pay per query
- **Open source** — MIT license, audit and extend freely
- **Premier distribution** — Listed on PortalHQ, Monad Agent Hub, Atelier

## Host

**GenTech Labs** — Payment infrastructure for AI agents

---

## Cost Optimization

Deploy with sensible defaults that balance capability and spend:

### Default Config (used by GenTech)

```yaml
# Conversation
model: "deepseek-v4-flash"
provider: "opencode-go"

# Subagents — cheaper model for delegated tasks
delegation:
  max_concurrent_children: 3
  model: "google/gemini-2.5-flash"
  provider: "openrouter"
```

### Quick Reference

| Task Type | Model | Cost Level |
|-----------|-------|------------|
| Main chat | deepseek-v4-flash | Free |
| Research / Draft | gemini-2.5-flash | $ |
| Code review / Audit | claude-sonnet-4 | $$ |
| Cron / Scripts | pin per job or no_agent | $0 |
| BlockRun queries | mode="free" or tier-1 | $0–0.005 |

### Pattern: Pin per-cron models

```python
cronjob(action='create',
  schedule='0 6 * * *',
  prompt='...',
  model={'provider': 'opencode-go', 'model': 'deepseek-v4-flash'})
```

### Pattern: Zero-cost script jobs

```python
cronjob(action='create',
  script='/path/to/script.py',
  no_agent=True)
```

For full Hermes cost-optimization patterns, load the `cost-optimization` skill:
```
skill_view(name='cost-optimization')
```