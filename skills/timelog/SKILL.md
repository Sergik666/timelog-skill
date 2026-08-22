---
name: timelog
description: Summarize how the user spent their time in a given date/time range, fill blank description cells in a time-entries CSV, or produce a short English per-day summary for Redmine — all reconstructed from local Claude Code chat logs, never asked from the user directly. Use when the user asks "сколько времени я потратил", "что я делал вчера/сегодня/на этой неделе", "заполни csv", "заполни таблицу времени", "сделай сводку для редмайна", or types /timelog.
---

# timelog

Reconstructs what the user was working on during a time range from their
local Claude Code chat history (`~/.claude/projects/**/*.jsonl`), and
presents it in one of three shapes. All three share the same data source
and the same range-parsing step below — only the output differs.

## 1. Resolve the date/time range

Parse whatever the user said (in Russian or English) into a start and end
moment in the local timezone **Europe/Kyiv**:

- "сегодня" / "today" → 00:00 today .. now
- "вчера" / "yesterday" → 00:00 .. 24:00 of yesterday
- "на этой неделе" / "this week" → Monday 00:00 .. now
- "с понедельника после обеда" → Monday 13:00 .. now ("после обеда" = 13:00 unless the user gives another hour)
- an explicit range ("17-23 августа", "с 10 по 15") → that range, 00:00..24:00 on each end unless times are given
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

Output a Markdown table in Russian, one row per contiguous work stretch:

| Дата | Время | Что делал |
|---|---|---|

No project column — project isn't tracked in this mode (see note below).

### B. Fill a CSV

Fields: `date,start,end,project,description`. The user gives you the file
path directly — don't search for it.

1. Ask which project (e.g. `TT`, `MAX`) this run is for, if not already said. It's needed only to know which rows to touch: fill a row **only if its `project` column matches** and its `description` is empty. Never touch a row that already has a description.
2. For each such row, use the CWD/text of activity falling inside its `start`–`end` interval to draft a description in Russian.
3. Show the drafts to the user for confirmation/edits before writing anything.
4. Write the file only after confirmation (edit the CSV in place, keep other rows untouched).
5. Separately: if the collected activity in step 2 shows time **outside every row's interval** within the requested range, warn about that untracked gap (date + approximate time span).

### C. Redmine summary

One row per day by default (only split into per-interval rows if the user
explicitly asks for that), in a chat table:

| Date | Description |
|---|---|

Description is in **English**, max 20 words, summarizing everything done
that day.

## Language

Chat-summary and CSV descriptions: Russian. Redmine descriptions: English.
Everything else you say around this: Russian, per the user's global
preference.
