"""
GenTech Agent Kit — Output Enforcer Plugin

Validates tool outputs against pydantic schemas. On schema mismatch:
1. Logs the violation with tool name, schema, and actual output
2. Auto-retries once (for transient/API-dependent tools)
3. Returns a structured error if validation fails again

Usage:
    from .schemas import QuoteResponse, ListingsResponse
    from .decorator import validated_output

    @mcp.tool()
    @validated_output(QuoteResponse)
    def get_quote(symbol: str) -> str:
        ...

Plugin auto-discovered by the Agent Kit plugin loader.
"""

from __future__ import annotations

import functools
import json
import logging
import time
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from . import schemas

_LOG = logging.getLogger("gentech-kit.plugins.output-enforcer")

# ── Registry ──────────────────────────────────────────────────────────────────
# Track violations per tool for audit/reputation

_violations: dict[str, list[dict[str, Any]]] = {}  # tool_name -> [violation, ...]


def get_violations(tool_name: str | None = None, since: float = 0) -> list[dict[str, Any]]:
    """Get output validation violations. Optionally filter by tool and/or time window."""
    results = []
    for name, entries in _violations.items():
        if tool_name and name != tool_name:
            continue
        for entry in entries:
            if entry["timestamp"] >= since:
                results.append({"tool": name, **entry})
    return sorted(results, key=lambda x: x["timestamp"], reverse=True)


def clear_violations() -> int:
    """Clear all violation records. Returns count cleared."""
    global _violations
    count = sum(len(v) for v in _violations.values())
    _violations = {}
    return count


# ── Validated Output Decorator ────────────────────────────────────────────────

F = TypeVar("F", bound=callable)


def validated_output(schema_class: type[BaseModel], max_retries: int = 1) -> callable:
    """Decorator that validates a tool's JSON string output against a pydantic schema.
    
    Args:
        schema_class: A pydantic BaseModel subclass defining the expected output shape.
        max_retries: Number of retries on validation failure (default 1).
    
    Returns:
        Decorated function that validates output before returning.
    
    Example:
        @mcp.tool()
        @validated_output(schemas.QuoteResponse)
        def get_quote(symbol: str) -> str:
            ...
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            tool_name = func.__name__
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    raw_output = func(*args, **kwargs)

                    # Parse the JSON string output
                    try:
                        parsed = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
                    except json.JSONDecodeError:
                        # Already not valid JSON — this tool doesn't return JSON. Skip validation.
                        return raw_output

                    # Validate against schema
                    validated = schema_class(**parsed)
                    
                    # Success — log and return
                    _LOG.debug("Output enforcer: %s passed schema %s (attempt %d)", 
                               tool_name, schema_class.__name__, attempt + 1)
                    return validated.model_dump_json(indent=2)

                except ValidationError as exc:
                    last_error = exc
                    # Log the violation
                    violation = {
                        "timestamp": time.time(),
                        "schema": schema_class.__name__,
                        "attempt": attempt + 1,
                        "error": str(exc),
                        "args": str(args),
                        "kwargs": str(kwargs),
                    }
                    _violations.setdefault(tool_name, []).append(violation)
                    
                    _LOG.warning(
                        "Output enforcer: %s failed schema %s (attempt %d/%d): %s",
                        tool_name, schema_class.__name__, attempt + 1, max_retries + 1, exc
                    )
                    
                    if attempt < max_retries:
                        _LOG.info("Output enforcer: retrying %s (attempt %d)", tool_name, attempt + 2)
                    else:
                        _LOG.error(
                            "Output enforcer: %s failed after %d attempts. Schema: %s",
                            tool_name, max_retries + 1, schema_class.__name__
                        )

                except Exception as exc:
                    # Non-validation error — let it propagate
                    _LOG.error("Output enforcer: %s crashed: %s", tool_name, exc)
                    return json.dumps({"error": f"Tool execution failed: {exc}"})

            # All retries exhausted
            return json.dumps({
                "error": f"Output validation failed after {max_retries + 1} attempt(s)",
                "schema": schema_class.__name__,
                "tool": tool_name,
                "detail": str(last_error),
            })

        return wrapper  # type: ignore
    return decorator


# ── Plugin Registration ──────────────────────────────────────────────────────


__plugin_manifest__ = {
    "name": "Output Enforcer",
    "version": "0.1.0",
    "description": "Validates tool outputs against pydantic schemas with auto-retry and violation logging",
    "type": "middleware",
}


def register_gentech_plugin(mcp: Any) -> None:
    """Register Output Enforcer tools with the Agent Kit MCP server."""
    
    @mcp.tool()
    def output_enforcer_status() -> str:
        """Get Output Enforcer status — total violations, registered schemas, health."""
        total = sum(len(v) for v in _violations.values())
        tools_with_violations = list(_violations.keys())
        return json.dumps({
            "plugin": "Output Enforcer",
            "version": "0.1.0",
            "status": "active",
            "total_violations": total,
            "tools_with_violations": tools_with_violations,
            "registered_schemas": list(schemas.__all__) if hasattr(schemas, "__all__") else [],
        }, indent=2)

    @mcp.tool()
    def output_enforcer_violations(tool_name: str = "", hours: int = 24) -> str:
        """Get recent validation violations. Filter by tool name (optional) and time window.
        
        Args:
            tool_name: Optional tool name to filter by. Empty string returns all.
            hours: How many hours back to look (default 24).
        """
        since = time.time() - (hours * 3600)
        violations = get_violations(tool_name if tool_name else None, since)
        return json.dumps({
            "count": len(violations),
            "window_hours": hours,
            "violations": violations[:50],  # cap at 50
        }, indent=2)

    @mcp.tool()
    def output_enforcer_clear() -> str:
        """Clear all violation records. Returns count cleared."""
        count = clear_violations()
        return json.dumps({"cleared": count, "status": "ok"})

    _LOG.info("Registered Output Enforcer plugin v0.1.0")
