# timelog — a Claude Code skill

Reconstructs what you were working on from your local Claude Code chat
history (`~/.claude/projects/**/*.jsonl`) — no separate time-tracking input
needed, you just ask.

```
"что я делал вчера"            -> chat summary table (date, time, what)
"сколько времени потратил на этой неделе" -> same, for a range
"заполни time-entries.csv, проект TT"     -> fills blank description cells
"сделай сводку для редмайна за эту неделю" -> one English line per day
```

## Modes

- **Chat summary** — a Markdown table (date, time range, what you did) for
  any range you name: today, yesterday, this week, "since Monday
  afternoon", an explicit date range.
- **Fill a CSV** — `date,start,end,project,description`. You give the file
  path and the project directly; only rows matching that project with an
  empty `description` get filled, from chat activity in that row's
  `start`–`end` window. Drafts are shown for confirmation before writing.
  Untracked time (chat activity outside every row's interval) is flagged.
- **Redmine summary** — one English line per day (≤20 words), or per
  interval if you ask for that split.

All reasoning about what a stretch of time was *about* is done by Claude
reading the raw log lines — the script only extracts and filters, it
never summarizes.

## Layout

```
skills/timelog/SKILL.md                 the skill itself
skills/timelog/scripts/collect_logs.py  extracts chat lines in a UTC time window
skills/timelog/scripts/test_collect_logs.py  self-check (stdlib only)
```

## Tests

```bash
cd /workspace/project1/timelog
python3 skills/timelog/scripts/test_collect_logs.py
```

## Install

Personal (all projects):

```bash
cp -r skills/timelog ~/.claude/skills/
```

Project-local (committed with the repo):

```bash
cp -r skills/timelog <project>/.claude/skills/
```

Restart the session, then invoke `/timelog` or just ask in plain language.

## collect_logs.py

Usable on its own:

```bash
python3 skills/timelog/scripts/collect_logs.py --since 2026-08-17T00:00:00Z --until 2026-08-18T00:00:00Z
```

Prints every user message and assistant text/tool-use across all local
projects in that UTC window, tab-separated (`timestamp cwd session role
text`), sorted by time.
