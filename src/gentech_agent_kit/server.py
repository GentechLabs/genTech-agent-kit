"""
GenTech Agent Kit — MCP Server
One install. Full stack. Your agent, running.

Integrates CoinMarketCap data, DeFi intelligence, agent identity,
and x402 payment rails into a single MCP server.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ── Version ─────────────────────────────────────────────────────────────────

VERSION = "0.3.0"

# ── Config (all from env, zero hardcoded secrets) ──────────────────────────

CMC_API_KEY = os.environ.get("CMC_API_KEY", "")
CMC_BASE = "https://pro-api.coinmarketcap.com"

# ── HTTP Client ─────────────────────────────────────────────────────────────

class _CMCClient:
    """Minimal CoinMarketCap API client. No external SDKs needed."""
    def __init__(self) -> None:
        self._http = httpx.Client(timeout=15.0)

    def _headers(self) -> dict[str, str]:
        return {"Accept": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self._http.get(f"{CMC_BASE}{path}", params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def quote(self, symbol: str) -> dict[str, Any]:
        return self._get("/v2/cryptocurrency/quotes/latest", {"symbol": symbol.upper()})

    def listings(self, start: int = 1, limit: int = 20) -> dict[str, Any]:
        return self._get("/v1/cryptocurrency/listings/latest", {
            "start": start, "limit": limit, "sort": "market_cap", "sort_dir": "desc",
        })

    def info(self, symbol: str) -> dict[str, Any]:
        return self._get("/v1/cryptocurrency/info", {"symbol": symbol.upper()})

    def trending(self, kind: str = "latest") -> dict[str, Any]:
        endpoints = {
            "gainers": "/v1/cryptocurrency/trending/gainers-losers",
            "losers": "/v1/cryptocurrency/trending/gainers-losers",
            "most_visited": "/v1/cryptocurrency/trending/most-visited",
            "latest": "/v1/cryptocurrency/trending/latest",
        }
        ep = endpoints.get(kind, endpoints["latest"])
        params: dict[str, Any] = {}
        if kind in ("gainers", "losers"):
            params = {"sort_dir": "asc" if kind == "gainers" else "desc", "limit": "20"}
        return self._get(ep, params)

    def dex_pairs(self, symbol: str) -> dict[str, Any]:
        return self._get("/v4/dex/pairs", {"symbol": symbol.upper()})

    def close(self) -> None:
        self._http.close()


def _extract_coin(info_list: Any) -> dict[str, Any]:
    """CMC v2 returns arrays per symbol; extract first element."""
    if isinstance(info_list, list) and info_list:
        return info_list[0]
    if isinstance(info_list, dict):
        return info_list
    return {}


# ── MCP Server ──────────────────────────────────────────────────────────────

mcp = FastMCP("GenTech Agent Kit")

# ──────────────────────────────────────────────────────────────────────────
#  TOOLS — CoinMarketCap Data
# ──────────────────────────────────────────────────────────────────────────


@mcp.tool()
def get_quote(symbol: str) -> str:
    """Get current price quote for crypto symbols. Cost: $0.001 USDC/query. Supports single or multiple comma-separated symbols (e.g. 'BTC' or 'BTC,ETH,SOL')."""
    try:
        c = _CMCClient()
        data = c.quote(symbol)
        c.close()
        result: dict[str, Any] = {
            "symbol": symbol,
            "timestamp": data.get("status", {}).get("timestamp"),
        }
        for sym, raw in data.get("data", {}).items():
            info = _extract_coin(raw)
            q = info.get("quote", {}).get("USD", {})
            result[sym] = {
                "price": q.get("price"),
                "24h_change_pct": q.get("percent_change_24h"),
                "market_cap": q.get("market_cap"),
                "volume_24h": q.get("volume_24h"),
            }
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


@mcp.tool()
def get_listings(start: int = 1, limit: int = 20) -> str:
    """Get top token listings by market cap. Returns up to 100 tokens ranked by market cap. Cost: $0.001 USDC/query."""
    try:
        c = _CMCClient()
        data = c.listings(start, min(limit, 100))
        c.close()
        tokens = []
        for item in data.get("data", []):
            q = item.get("quote", {}).get("USD", {})
            tokens.append({
                "rank": item.get("cmc_rank"),
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "price": q.get("price"),
                "24h_change_pct": q.get("percent_change_24h"),
                "market_cap": q.get("market_cap"),
            })
        return json.dumps({"count": len(tokens), "tokens": tokens}, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


@mcp.tool()
def search_token(symbol: str) -> str:
    """Search for crypto token information by symbol. Returns metadata, description, tags, logo URL. Cost: $0.001 USDC/query."""
    try:
        c = _CMCClient()
        data = c.info(symbol)
        c.close()
        result: dict[str, Any] = {}
        for sym, info in data.get("data", {}).items():
            result[sym] = {
                "name": info.get("name"),
                "symbol": info.get("symbol"),
                "category": info.get("category"),
                "description": info.get("description"),
                "logo": info.get("logo"),
                "date_added": info.get("date_added"),
                "platform": info.get("platform"),
                "tags": info.get("tags", []),
            }
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


@mcp.tool()
def get_trending(kind: str = "latest") -> str:
    """Get trending crypto data. Options: gainers, losers, most_visited, latest. Cost: $0.001 USDC/query."""
    try:
        c = _CMCClient()
        data = c.trending(kind)
        c.close()
        items = []
        for item in data.get("data", []):
            q = item.get("quote", {}).get("USD", {}) if "quote" in item else {}
            items.append({
                "symbol": item.get("symbol"),
                "name": item.get("name"),
                "price": q.get("price"),
                "change_24h_pct": q.get("percent_change_24h"),
            })
        return json.dumps({"kind": kind, "count": len(items), "results": items}, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


@mcp.tool()
def get_dex_pairs(symbol: str) -> str:
    """Get DEX pair data for a token across exchanges. Returns price, volume, liquidity. Cost: $0.001 USDC/query."""
    try:
        c = _CMCClient()
        data = c.dex_pairs(symbol)
        c.close()
        pairs = []
        for pair in data.get("data", {}).get("pairs", [])[:20]:
            pairs.append({
                "exchange": pair.get("exchange", {}).get("name"),
                "pair": f"{pair.get('base_currency', {}).get('symbol')}/{pair.get('quote_currency', {}).get('symbol')}",
                "price": pair.get("quote", {}).get("price"),
                "volume_24h_usd": pair.get("volume_24h_usd"),
                "liquidity_usd": pair.get("liquidity_usd"),
                "price_change_24h_pct": pair.get("price_change_24h"),
            })
        return json.dumps({"symbol": symbol.upper(), "count": len(pairs), "pairs": pairs}, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


# ──────────────────────────────────────────────────────────────────────────
#  TOOLS — Kit Meta
# ──────────────────────────────────────────────────────────────────────────


@mcp.tool()
def kit_info() -> str:
    """Get GenTech Agent Kit version, available tools, and update status."""
    tools_info = [
        "get_quote(symbol) — Real-time crypto prices",
        "get_listings(start, limit) — Top tokens by market cap",
        "search_token(symbol) — Token metadata and details",
        "get_trending(kind) — Gainers, losers, most visited",
        "get_dex_pairs(symbol) — DEX liquidity pair data",
    ]
    return json.dumps({
        "name": "GenTech Agent Kit",
        "version": VERSION,
        "description": "One install. Full stack. Your agent, running.",
        "tools": tools_info,
        "updates": "Always receiving updates — run `uv tool install --reinstall` to get the latest",
        "docs": "https://github.com/ProtoJay4789/genTech-agent-kit",
    }, indent=2)


# ── Entry Point ──────────────────────────────────────────────────────────────


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()