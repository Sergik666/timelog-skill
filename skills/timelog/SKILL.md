---
name: timelog
description: Summarize how the user spent their time in a given date/time range, fill blank description cells in a time-entries CSV, or produce a short English per-day summary for Redmine — all reconstructed from local Claude Code chat logs, never asked from the user directly. Use when the user asks how much time they spent, what they did yesterday/today/this week, to fill in a CSV or time table, or to build a Redmine summary — in Russian or English — or types /timelog.
---

# timelog

Reconstructs what the user was working on during a time range from their
local Claude Code chat history (`~/.claude/projects/**/*.jsonl`), and
presents it in one of three shapes. All three share the same data source
and the same range-parsing step below — only the output differs.

## 1. Resolve the date/time range

Parse whatever the user said (in Russian or English) into a start and end
moment in the local timezone **Europe/Kyiv**:

- "today" → 00:00 today .. now
- "yesterday" → 00:00 .. 24:00 of yesterday
- "this week" → Monday 00:00 .. now
- "since Monday afternoon" → Monday 13:00 .. now ("afternoon" defaults to 13:00 unless the user gives another hour)
- an explicit range ("Aug 17-23", "from the 10th to the 15th") → that range, 00:00..24:00 on each end unless times are given
- If genuinely ambiguous, ask. Otherwise resolve it yourself — don't stall on a range you can infer.

Convert the resolved local start/end to UTC ISO strings (`...Z`) — that's
what the log files use. Get the current time and timezone offset with:

```bash
TZ=Europe/Kyiv date +"%Y-%m-%d %H:%M %z"
```

## 2. Pull the raw activity

```bash
python3 scripts/collect_logs.py --since <UTC_START> --until <UTC_END>
```

(`scripts/collect_logs.py` sits next to this SKILL.md — use its path
relative to wherever this file was loaded from.) This
prints every user message and assistant text/tool-use in that window,
tab-separated as `TIMESTAMP  CWD  SESSION_ID  ROLE  TEXT`, sorted by time,
across every project on the machine. Read through it yourself and group
consecutive activity into work sessions/topics — that reasoning is yours,
the script only extracts and filters, it does not summarize.

Ignore meta noise you find in there anyway (slash-command echoes, empty
assistant acks, tool-search chatter) and focus on what task/topic each
stretch of time was actually about.

## 3. Pick the output mode

### A. Chat summary (default when the user just asks what they did / how much time they spent)

Output a Markdown table, one row per contiguous work stretch, with columns
date / time range / what was done. Language: match whatever language the
user is chatting in (see "Language" below).

| Date | Time | What was done |
|---|---|---|

No project column — project isn't tracked in this mode (see note below).

### B. Fill a CSV

Fields: `date,start,end,project,description`. The user gives you the file
path directly — don't search for it.

1. Ask which project (e.g. `TT`, `MAX`) this run is for, if not already said. It's needed only to know which rows to touch: fill a row **only if its `project` column matches** and its `description` is empty. Never touch a row that already has a description.
2. For each such row, use the CWD/text of activity falling inside its `start`–`end` interval to draft a description (see "Language" below for which language to write it in).
3. Show the drafts to the user for confirmation/edits before writing anything.
4. Write the file only after confirmation (edit the CSV in place, keep other rows untouched).
5. Separately: if the collected activity in step 2 shows time **outside every row's interval** within the requested range, warn about that untracked gap (date + approximate time span).

### C. Redmine summary

One row per day by default (only split into per-interval rows if the user
explicitly asks for that), in a chat table:

| Date | Description |
|---|---|

Description is in **English**, max 20 words, summarizing everything done
that day — regardless of what language the request was made in, unless
the user explicitly asks for another language.

## Language

- Chat summary (mode A) and CSV descriptions (mode B): match the language
  the user is chatting in — default to Russian per the user's global
  preference, switch only if the user writes in another language or asks
  for one explicitly.
- Redmine summary (mode C): always English, regardless of the chat
  language, unless the user explicitly asks for a different language.
- Everything else you say around this (questions, confirmations,
  warnings): same rule as mode A/B — match the user's language, default
  Russian.
