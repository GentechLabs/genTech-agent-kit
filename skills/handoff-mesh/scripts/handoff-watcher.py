#!/usr/bin/env python3
"""
HANDOFF watcher — enhanced: surfaces OPEN handoffs AND recent completions,
with tappable Obsidian deep-links so Jordan can open the note in his phone app.

Two halves of the loop:
  OPEN    — handoffs still sitting in INBOX/<group>/ that need picking up.
  DONE    — recent completion notes (agents reporting what they shipped).

Output is STABLE (no timestamps) so it stays safe as a no_agent monitor script.
Completions are matched by date; pass --days N (default 2) to widen the window.

Usage:
    python3 handoff-watcher.py [vault_path] [--days N] [--vault-name NAME]
"""
import os
import re
import sys
import datetime

VAULT = "/root/vaults/gentech"
INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")
HANDOFFS = os.path.join(VAULT, "01-HANDOFFS")

# The name of the vault as it appears in Jordan's Obsidian app. This is what
# makes the obsidian:// links resolve on his phone. Default "gentech".
VAULT_NAME = "gentech"

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

# Completion files per group. <group>-completions.md at 01-HANDOFFS/ root.
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
    """Return an Obsidian deep-link that opens the note in Jordan's app.
    rel_path is vault-relative, e.g. 01-HANDOFFS/INBOX/hq/x.md"""
    from urllib.parse import quote
    file_part = quote(rel_path, safe="")
    return f"obsidian://open?vault={VAULT_NAME}&file={file_part}"


def find_open():
    open_notes = []
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
            open_notes.append((group, name, path))
    return open_notes


def recent_completions(days=2):
    """Pull shipped lines from each group's completions file, tagged recent."""
    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    recent = []
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
            # look for a date in the line
            m = re.search(r"(20\d\d-\d\d-\d\d)", line)
            if m:
                try:
                    d = datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
                if d >= cutoff:
                    recent.append((grp, line))
    return recent


def main():
    global VAULT, VAULT_NAME
    argv = sys.argv[1:]
    days = 2
    while argv:
        a = argv.pop(0)
        if a == "--days" and argv:
            days = int(argv.pop(0))
        elif a == "--vault-name" and argv:
            VAULT_NAME = argv.pop(0)
        elif a.startswith("/") and os.path.isdir(a):
            VAULT = a
            INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")
    HANDOFFS = os.path.join(VAULT, "01-HANDOFFS")

    lines = []

    open_notes = find_open()
    if open_notes:
        lines.append("📥 OPEN handoffs — pick these up:")
        for grp, name, path in open_notes:
            rel = os.path.relpath(path, VAULT)
            lines.append(f"• [{grp}] {name}")
            lines.append(f"    {obsidian_link(rel)}")

    done = recent_completions(days)
    if done:
        lines.append("")
        lines.append(f"✅ HANDLED (last {days}d):")
        for grp, line in done:
            snippet = line.lstrip("- ").strip()
            if len(snippet) > 100:
                snippet = snippet[:100] + "…"
            lines.append(f"• [{grp}] {snippet}")

    if not lines:
        return 0

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
