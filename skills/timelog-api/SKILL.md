---
name: timelog-api
description: Fill blank descriptions of time-tracker entries (slots) for one project directly through the Time Tracker API, reconstructing what was done from local Claude Code chat logs, with a backup before every write. Use when the user asks to fill slots / entries in the time tracker (not a CSV file), e.g. "fill TT slots for this week".
---

# timelog-api

Like `timelog-csv`, but the rows live in the Time Tracker and are read and
written through its API by `scripts/tt_api.py` (stdlib only). Run it as
`python3 <this skill dir>/scripts/tt_api.py …`.

The script reads `TT_API_URL` and `TT_API_KEY` from
`~/.claude/timelog/tt.env`. **Never print, cat or echo that file or the
key.** If the script says they are missing, tell the user to fill that
file themselves in an editor (not through the chat) with a **Read & write**
key from Settings → API keys, then `chmod 600 ~/.claude/timelog/tt.env`.

1. Ask which project (e.g. `TT`) if not already said. Range defaults to the
   current week (Mon–Sun); otherwise resolve it to `--from`/`--to` dates
   (`YYYY-MM-DD`, inclusive).
2. Get the slots to fill:
   ```bash
   python3 scripts/tt_api.py slots --project TT [--from 2026-10-19 --to 2026-10-25]
   ```
   It returns only finished entries of that project with an empty
   description — never touch any other entry. If the project name isn't in
   `projects`, show the list and ask. No slots → say so and stop.
3. Get the raw activity: invoke `timelog-data` with the range from the
   earliest slot start to the latest slot end (slot times carry their
   offset; `timelog-data` works in Europe/Kyiv). Reuse activity already in
   context for that range instead of re-fetching.
4. For each slot, draft a description from the activity inside its
   `start`–`end`. Language: the user's chat language, default Russian.
   A slot with no matching activity → leave it out and list it as
   "no activity found".
5. Show a table (date, start–end, draft) and wait for confirmation/edits.
   Don't write anything before that.
6. After confirmation, write the approved drafts to a JSON file in the
   scratchpad (`[{"id": "…", "description": "…"}]`) and run:
   ```bash
   python3 scripts/tt_api.py patch <file.json>
   ```
   It first saves a full backup to `~/.claude/timelog/backups/` and stops
   without writing if that fails; the server also keeps its own snapshot
   (`GET /api/v1/backups`). Report the backup path and `updated` count.
   A `409` means the data kept changing — rerun step 2 and retry once.
7. Separately: if the activity shows work in the range **outside every
   entry** (`allEntries` from step 2, any project), warn about that
   untracked gap (date + approximate time span).
