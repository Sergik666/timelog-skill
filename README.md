# timelog — a Claude Code skill family

Version 1.1.0 — see [CHANGELOG.md](CHANGELOG.md).

Reconstructs what you were working on from your local Claude Code chat
history (`~/.claude/projects/**/*.jsonl`) — no separate time-tracking
input needed, you just ask.

```
"/timelog", or anything time-related with no clear format -> timelog (router)
"what did I do yesterday"              -> timelog-summary
"how much time did I spend this week"  -> timelog-summary
"fill time-entries.csv, project TT"    -> timelog-csv
"fill TT slots in the tracker"         -> timelog-api
"write a Redmine summary for this week" -> timelog-redmine
```

## Why six skills instead of one

Split so that only the skill you actually need gets loaded into context,
and so the raw log data is fetched once per range and reused, instead of
being re-read every time a different output format is requested.

- **timelog** — the entry point. Doesn't do any timelog work itself: it
  reads the request and routes to whichever of the skills below fits, so
  you can just say `/timelog` (or ask in plain language) without knowing
  the family exists. Claude Code will often match the specific skill
  directly from what you typed anyway — this is the fallback/umbrella for
  when you don't.
- **timelog-data** — the shared building block. Resolves a date/time range
  and returns the raw chat activity in it. Not meant to be invoked
  directly by the user in normal use; the others invoke it, and skip
  invoking it again if the same range's raw activity is already visible
  earlier in the conversation.
- **timelog-summary** — a Markdown table (date, time range, what was
  done) for any range.
- **timelog-csv** — fills blank `description` cells in a
  `date,start,end,project,description` CSV, for the project and rows you
  specify, with confirmation before writing and a warning for untracked
  gaps.
- **timelog-api** — the same as timelog-csv, but for entries in the
  Time Tracker, read and written through its API (`/api/v1/entries`).
  Before every write it saves a full backup (`/api/v1/backup`) to
  `~/.config/timelog/backups/` and refuses to write if that fails; the
  server keeps its own snapshots too (`/api/v1/backups`).
- **timelog-redmine** — one English line per day (≤20 words) summarizing
  everything done that day, for pasting into Redmine time tracking.

All reasoning about what a stretch of time was *about* is done by Claude
reading the raw log lines — `collect_logs.py` only extracts and filters,
it never summarizes.

## Layout

```
skills/timelog/SKILL.md                       entry point, routes to one of the three below
skills/timelog-data/SKILL.md                 range resolution + log fetching, shared by the other three
skills/timelog-data/scripts/collect_logs.py   extracts chat lines in a UTC time window
skills/timelog-data/scripts/test_collect_logs.py  self-check (stdlib only)
skills/timelog-summary/SKILL.md               chat-summary table
skills/timelog-csv/SKILL.md                   CSV filling
skills/timelog-redmine/SKILL.md               Redmine daily summary
skills/timelog-api/SKILL.md                   time-tracker filling via API
skills/timelog-api/scripts/tt_api.py          API client: slots, backup + patch
skills/timelog-api/scripts/test_tt_api.py     self-check (stdlib only)
tt.env.example                                credentials template for timelog-api
```

## Tests

```bash
cd /workspace/project1/timelog
python3 skills/timelog-data/scripts/test_collect_logs.py
python3 skills/timelog-api/scripts/test_tt_api.py
```

## Install

Personal (all projects):

```bash
cp -r skills/timelog skills/timelog-data skills/timelog-summary skills/timelog-csv skills/timelog-redmine skills/timelog-api ~/.claude/skills/
```

Project-local (committed with the repo):

```bash
cp -r skills/timelog skills/timelog-data skills/timelog-summary skills/timelog-csv skills/timelog-redmine skills/timelog-api <project>/.claude/skills/
```

For `timelog-api`, put the tracker URL and a **Read & write** key (Settings
→ API keys) into `~/.config/timelog/tt.env` — keep it out of the chat:

```bash
mkdir -p ~/.config/timelog && cp tt.env.example ~/.config/timelog/tt.env
chmod 600 ~/.config/timelog/tt.env   # then fill it in an editor
```

Restart the session, then invoke `/timelog`, `/timelog-summary`,
`/timelog-csv`, `/timelog-api`, `/timelog-redmine`, or just ask in plain language.

## collect_logs.py

Usable on its own:

```bash
python3 skills/timelog-data/scripts/collect_logs.py --since 2026-08-17T00:00:00Z --until 2026-08-18T00:00:00Z
```

Prints every user message and assistant text/tool-use across all local
projects in that UTC window, tab-separated (`timestamp cwd session role
text`), sorted by time.
