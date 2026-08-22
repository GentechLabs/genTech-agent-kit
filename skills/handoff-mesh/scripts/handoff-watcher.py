#!/usr/bin/env python3
"""
HANDOFF watcher — STATEFUL. Reports only NEW handoffs and STATUS CHANGES.

Runs as a no_agent cron script. To stay silent when nothing changes, it keeps
a state file of what it has already reported and only prints:
  - NEW open handoffs (appeared since last run)
  - RESOLVED handoffs (were open, now marked resolved — "cleared")
  - NEW recent completions (agents reporting what they shipped)

If nothing changed since the last run, it prints NOTHING → cron stays silent.
When every open item is resolved/cleared and there are no new completions,
it prints nothing too (Jordan isn't working on anything).

State file lives next to the script: handoff-watcher.state.json

Usage:
    python3 handoff-watcher.py [vault_path] [--days N] [--vault-name NAME] [--state PATH]
"""
import os
import re
import sys
import json
import datetime

VAULT = "/root/vaults/gentech"
INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")
HANDOFFS = os.path.join(VAULT, "01-HANDOFFS")

VAULT_NAME = "gentech"
STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "handoff-watcher.state.json")

KNOWN_GROUPS = {"hq", "forge", "labs", "entertainment", "treasury", "gizmo"}

RESOLVED_MARKERS = (
    "status: [x]",
    "status: resolved",
    "status: done",
    "status: closed",
    "## resolved",
    "- [x]",
    "status:** resolved",   # bold form: **Status:** resolved
    "status:** done",       # bold form: **Status:** done
    "status:** [x]",
)

COMPLETION_FILES = {
    "gentech": "gentech-completions.md",
    "entertainment": "entertainment-completions.md",
    "treasury": "treasury-completions.md",
    "labs": "labs-completions.md",
    "gizmo": "gizmo-completions.md",
    "forge": "forge-completions.md",
    "hq": "hq-completions.md",
}


def is_resolved(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    low = text.lower()
    return any(m in low for m in RESOLVED_MARKERS)


def obsidian_link(rel_path):
    from urllib.parse import quote
    file_part = quote(rel_path, safe="")
    return f"obsidian://open?vault={VAULT_NAME}&file={file_part}"


def find_open():
    """Return dict {relative_path: (group, filename)} of still-open handoffs."""
    open_notes = {}
    if not os.path.isdir(INBOX):
        return open_notes
    for group in sorted(os.listdir(INBOX)):
        if group not in KNOWN_GROUPS:
            continue
        gdir = os.path.join(INBOX, group)
        if not os.path.isdir(gdir):
            continue
        for name in sorted(os.listdir(gdir)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(gdir, name)
            if is_resolved(path):
                continue
            rel = os.path.relpath(path, VAULT)
            open_notes[rel] = (group, name, path)
    return open_notes


def recent_completions(days=2):
    """Return {snippet: group} for completion lines dated within the window."""
    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    recent = {}
    for grp, fname in COMPLETION_FILES.items():
        fpath = os.path.join(HANDOFFS, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, encoding="utf-8") as f:
            text = f.read()
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            m = re.search(r"(20\d\d-\d\d-\d\d)", line)
            if m:
                try:
                    d = datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
                if d >= cutoff:
                    snippet = line.lstrip("- ").strip()
                    key = (grp, snippet[:120])
                    recent[key] = grp
    return recent


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except OSError:
        pass


def main():
    global VAULT, INBOX, HANDOFFS, VAULT_NAME, STATE_PATH
    argv = sys.argv[1:]
    days = 2
    while argv:
        a = argv.pop(0)
        if a == "--days" and argv:
            days = int(argv.pop(0))
        elif a == "--vault-name" and argv:
            VAULT_NAME = argv.pop(0)
        elif a == "--state" and argv:
            STATE_PATH = argv.pop(0)
        elif a.startswith("/") and os.path.isdir(a):
            VAULT = a
            INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")
    HANDOFFS = os.path.join(VAULT, "01-HANDOFFS")

    prev = load_state()
    prev_open = set(prev.get("open", []))
    # completions are stored as [grp, snippet] lists in JSON; convert to tuples
    prev_completions = set(tuple(c) if isinstance(c, list) else c
                           for c in prev.get("completions", []))

    cur_open = find_open()          # rel -> (group, name, path)
    cur_open_keys = set(cur_open.keys())
    cur_completions = recent_completions(days)
    cur_completion_keys = set(cur_completions.keys())

    lines = []

    # NEW open handoffs (not in previous state)
    new_open = cur_open_keys - prev_open
    if new_open:
        lines.append("🆕 NEW handoffs:")
        for rel in sorted(new_open):
            grp, name, path = cur_open[rel]
            lines.append(f"• [{grp}] {name}")
            lines.append(f"    {obsidian_link(rel)}")

    # RESOLVED handoffs (were in prev open, now gone -> cleared)
    resolved = prev_open - cur_open_keys
    if resolved:
        lines.append("")
        lines.append(f"✅ CLEARED ({len(resolved)}):")
        for rel in sorted(resolved):
            # show a friendly label from previous (we only stored rel)
            name = rel.split("/")[-1]
            lines.append(f"• {name}")

    # NEW completions
    new_completions = cur_completion_keys - prev_completions
    if new_completions:
        lines.append("")
        lines.append("🔧 NEW completions:")
        for (grp, snippet) in sorted(new_completions):
            if len(snippet) > 120:
                snippet = snippet[:120] + "…"
            lines.append(f"• [{grp}] {snippet}")

    # Update state
    save_state({"open": sorted(cur_open_keys), "completions": sorted(cur_completion_keys)})

    if not lines:
        # nothing changed — print nothing (silent)
        return 0

    print("\n".join(lines))
    return 0


import datetime

if __name__ == "__main__":
    sys.exit(main())
