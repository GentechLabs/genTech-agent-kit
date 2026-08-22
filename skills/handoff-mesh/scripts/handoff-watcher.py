#!/usr/bin/env python3
"""
HANDOFF watcher — surfaces unread handoffs sitting in any group's INBOX.

Scans 01-HANDOFFS/INBOX/<group>/ for handoff notes that are still OPEN
(not resolved, not archived) and reports them so the receiving agent picks
them up. This is the "nobody drops a handoff" half of the V4 mesh protocol.

Behavior:
- Lists every <group>/ subfolder under INBOX.
- For each, finds *.md notes that are NOT in _archive/ and NOT marked
  resolved (Status: [x] / resolved / done in the frontmatter/body).
- Emits a short, stable report of OPEN handoffs (or nothing if all clear).
- Stable output (no timestamps) so it can be used as a monitor_script.

Usage:
    python3 handoff-watcher.py [vault_path]
"""
import os
import re
import sys

VAULT = sys.argv[1] if len(sys.argv) > 1 else "/root/vaults/gentech"
INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")

# Groups we watch. Auto-discovered from the INBOX dir, but keep an explicit
# allowlist so a stray folder never gets scanned.
KNOWN_GROUPS = {"hq", "forge", "labs", "entertainment", "treasury", "gizmo"}

RESOLVED_MARKERS = (
    "status: [x]",
    "status: resolved",
    "status: done",
    "status: closed",
    "## resolved",
    "- [x]",
)


def is_resolved(path):
    """A note is resolved if its body carries a resolved marker."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    low = text.lower()
    return any(m in low for m in RESOLVED_MARKERS)


def main():
    if not os.path.isdir(INBOX):
        print(f"⚠️ INBOX missing at {INBOX} — nothing to watch.")
        return 1

    open_notes = []
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
            open_notes.append((group, name))

    if not open_notes:
        # Stable, silent output — nothing to report.
        return 0

    print("📥 Open handoffs in INBOX — pick these up:")
    for group, name in open_notes:
        print(f"- [{group}] {name}")
    print("\nRead the note, act on it, then mark it resolved and move to _archive/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
