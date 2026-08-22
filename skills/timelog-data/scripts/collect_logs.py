#!/usr/bin/env python3
"""Dump Claude Code chat activity across all local projects within a UTC time window.

Timestamps in Claude Code session logs are ISO-8601 UTC strings like
"2026-08-01T06:00:23.399Z" - always the same format, so plain string
comparison against --since/--until (pass them in the same format) is
enough to order and filter, no date parsing needed.

Usage:
    collect_logs.py --since 2026-08-17T05:00:00Z --until 2026-08-18T05:00:00Z

Prints one line per relevant message, sorted by time:
    TIMESTAMP<TAB>CWD<TAB>SESSION_ID<TAB>ROLE<TAB>TEXT
"""
import argparse
import glob
import json
import os
import sys

TOOL_ARG_KEYS = ("file_path", "command", "description", "path", "pattern")


def tool_use_summary(block):
    name = block.get("name", "?")
    inp = block.get("input") or {}
    for key in TOOL_ARG_KEYS:
        if key in inp:
            val = str(inp[key])[:120]
            return f"[{name}: {val}]"
    return f"[{name}]"


def extract_texts(message):
    """Yield short text snippets worth showing for this message."""
    content = message.get("content")
    if isinstance(content, str):
        if not content.startswith("<"):  # skip caveat/system wrapper strings
            yield content[:2000]
        return
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text = block.get("text", "").strip()
                if text:
                    yield text[:2000]
            elif btype == "tool_use":
                yield tool_use_summary(block)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="UTC ISO timestamp, inclusive")
    ap.add_argument("--until", required=True, help="UTC ISO timestamp, inclusive")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    args = ap.parse_args()

    rows = []
    for path in glob.glob(os.path.join(args.root, "**", "*.jsonl"), recursive=True):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = obj.get("timestamp")
                if not ts or not (args.since <= ts <= args.until):
                    continue
                if obj.get("isMeta") or obj.get("isSidechain"):
                    continue
                message = obj.get("message")
                if not isinstance(message, dict):
                    continue
                role = message.get("role")
                if role not in ("user", "assistant"):
                    continue
                cwd = obj.get("cwd", "?")
                session = obj.get("sessionId", "?")
                for text in extract_texts(message):
                    rows.append((ts, cwd, session, role, text))

    rows.sort(key=lambda r: r[0])
    for ts, cwd, session, role, text in rows:
        text = text.replace("\t", " ").replace("\n", " \\n ")
        print(f"{ts}\t{cwd}\t{session}\t{role}\t{text}")


if __name__ == "__main__":
    sys.exit(main())
