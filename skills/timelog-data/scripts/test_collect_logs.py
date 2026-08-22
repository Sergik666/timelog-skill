#!/usr/bin/env python3
"""Minimal self-check for collect_logs.py filtering/extraction logic. No framework."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "collect_logs.py")

LINES = [
    {"timestamp": "2026-08-17T05:00:00.000Z", "cwd": "/w", "sessionId": "s1",
     "message": {"role": "user", "content": "<local-command-caveat>skip me</local-command-caveat>"}},
    {"timestamp": "2026-08-17T06:00:00.000Z", "cwd": "/w", "sessionId": "s1", "isMeta": True,
     "message": {"role": "user", "content": "meta, should be skipped"}},
    {"timestamp": "2026-08-17T07:00:00.000Z", "cwd": "/w", "sessionId": "s1",
     "message": {"role": "user", "content": "fix the widget bug"}},
    {"timestamp": "2026-08-17T08:00:00.000Z", "cwd": "/w", "sessionId": "s1",
     "message": {"role": "assistant", "content": [
         {"type": "text", "text": "looking into it"},
         {"type": "tool_use", "name": "Edit", "input": {"file_path": "/w/widget.py"}},
     ]}},
    {"timestamp": "2026-08-17T09:00:00.000Z", "cwd": "/w", "sessionId": "s1",
     "message": {"role": "user", "content": "outside the requested window"}},
]

with tempfile.TemporaryDirectory() as root:
    proj = os.path.join(root, "proj")
    os.makedirs(proj)
    with open(os.path.join(proj, "a.jsonl"), "w") as f:
        for obj in LINES:
            f.write(json.dumps(obj) + "\n")

    out = subprocess.run(
        [sys.executable, SCRIPT,
         "--since", "2026-08-17T06:30:00Z", "--until", "2026-08-17T08:30:00Z",
         "--root", root],
        capture_output=True, text=True, check=True,
    ).stdout

    assert "skip me" not in out
    assert "meta, should be skipped" not in out
    assert "outside the requested window" not in out
    assert "fix the widget bug" in out
    assert "looking into it" in out
    assert "[Edit: /w/widget.py]" in out
    # sorted by timestamp: the user line must precede the assistant line
    assert out.index("fix the widget bug") < out.index("looking into it")

print("ok")
