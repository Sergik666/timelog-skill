---
name: timelog-data
description: Internal building block that loads raw Claude Code chat activity for a date/time range into context, reconstructed from local session logs. Used by timelog-summary, timelog-csv and timelog-redmine — they invoke this first and hand it the range they need, instead of each re-implementing range parsing or re-reading logs. Also usable directly if the user explicitly wants the raw activity dump for a range.
---

# timelog-data

Resolves a date/time range and returns the raw chat activity in it, so the
three consuming skills (timelog-summary, timelog-csv, timelog-redmine)
never have to parse ranges or read logs themselves.

## 1. Resolve the date/time range

Parse whatever range you were given (from the user directly, or passed
along by the skill that invoked you) into a start and end moment in the
local timezone **Europe/Kyiv**:

- "today" → 00:00 today .. now
- "yesterday" → 00:00 .. 24:00 of yesterday
- "this week" → Monday 00:00 .. now
- "since Monday afternoon" → Monday 13:00 .. now ("afternoon" defaults to 13:00 unless another hour is given)
- an explicit range ("Aug 17-23", "from the 10th to the 15th") → that range, 00:00..24:00 on each end unless times are given
- If genuinely ambiguous, ask. Otherwise resolve it yourself — don't stall on a range you can infer.

Convert the resolved local start/end to UTC ISO strings (`...Z`) — that's
what the log files use. Get the current time and timezone offset with:

```bash
TZ=Europe/Kyiv date +"%Y-%m-%d %H:%M %z"
```

## 2. Reuse what's already in context

Before running anything: check whether the raw activity for this exact
UTC range already appears earlier in this conversation — e.g. output from
a previous `collect_logs.py` call this session that fully covers the
requested window. If it does, reuse it as-is and stop here — do not
re-run the script. Only re-fetch when the needed range isn't already
covered, or the user explicitly asks for a re-check/refresh.

## 3. Pull the raw activity

```bash
python3 scripts/collect_logs.py --since <UTC_START> --until <UTC_END>
```

(`scripts/collect_logs.py` sits next to this SKILL.md — use its path
relative to wherever this file was loaded from.) This prints every user
message and assistant text/tool-use in that window, tab-separated as
`TIMESTAMP  CWD  SESSION_ID  ROLE  TEXT`, sorted by time, across every
project on the machine.

Ignore meta noise you find in there (slash-command echoes, empty
assistant acks, tool-search chatter) and focus on what task/topic each
stretch of time was actually about — that reasoning is yours, the script
only extracts and filters, it does not summarize.

## 4. Hand it back

If you were invoked by another skill (timelog-summary, timelog-csv,
timelog-redmine), continue directly into that skill's own steps using
this raw activity — don't print the raw dump to the user, it's a working
artifact for the report the calling skill is building. If invoked
directly by the user with no follow-up format requested, just show the
resolved range and the raw activity as-is.
