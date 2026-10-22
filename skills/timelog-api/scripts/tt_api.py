#!/usr/bin/env python3
"""Time Tracker API client for the timelog-api skill (stdlib only).

Reads TT_API_URL and TT_API_KEY from ~/.claude/timelog/tt.env (or the
environment) so the key never shows up in the chat.

  tt_api.py slots --project TT [--from 2026-10-19 --to 2026-10-25]
  tt_api.py patch drafts.json      # [{"id": "...", "description": "..."}]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".claude" / "timelog"  # ~/.claude survives container rebuilds
ENV_FILE = CONFIG_DIR / "tt.env"
BACKUP_DIR = CONFIG_DIR / "backups"


def load_config():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("'\"")
    url = os.environ.get("TT_API_URL") or env.get("TT_API_URL")
    key = os.environ.get("TT_API_KEY") or env.get("TT_API_KEY")
    if not url or not key:
        sys.exit(f"Set TT_API_URL and TT_API_KEY in {ENV_FILE} (chmod 600)")
    return url.rstrip("/"), key


def call(method, path, body=None):
    url, key = load_config()
    req = urllib.request.Request(
        url + path,
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "timelog-skill",  # some proxies block the default urllib agent
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code} {e.read().decode(errors='replace')}")


def empty_slots(report, project):
    """Finished entries of `project` (name, case-insensitive) with no description."""
    p = project.lower()
    return [
        {k: e[k] for k in ("id", "date", "start", "end", "durationSeconds")}
        for e in report["entries"]
        if (e["project"] or "").lower() == p and not e["description"].strip() and not e["running"]
    ]


def backup():
    data = call("GET", "/api/v1/backup")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKUP_DIR / f"tt-{datetime.now():%Y-%m-%dT%H-%M-%S}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    if not data.get("state", {}).get("entries"):
        sys.exit(f"Backup at {path} has no entries, refusing to patch")
    return path


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("slots")
    s.add_argument("--project", required=True)
    s.add_argument("--from", dest="date_from")
    s.add_argument("--to", dest="date_to")
    p = sub.add_parser("patch")
    p.add_argument("file")
    a = ap.parse_args()

    if a.cmd == "slots":
        q = {k: v for k, v in (("from", a.date_from), ("to", a.date_to)) if v}
        report = call("GET", "/api/v1/entries" + ("?" + urllib.parse.urlencode(q) if q else ""))
        out = {k: report[k] for k in ("from", "to", "timezone")}
        out["projects"] = [x["name"] for x in report["projects"]]
        out["slots"] = empty_slots(report, a.project)
        out["allEntries"] = [{k: e[k] for k in ("start", "end", "project")} for e in report["entries"]]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        patches = json.loads(Path(a.file).read_text())
        path = backup()  # exits on failure, so nothing is patched without a local backup
        print(f"backup: {path}")
        print(json.dumps(call("PATCH", "/api/v1/entries", patches)))


if __name__ == "__main__":
    main()
