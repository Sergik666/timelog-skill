---
name: timelog-csv
description: Fill blank description cells in a time-entries CSV (date,start,end,project,description), reconstructing what was done from local Claude Code chat logs. Use when the user asks to fill in a CSV file or time table.
---

# timelog-csv

Fields: `date,start,end,project,description`. The user gives you the file
path directly — don't search for it.

1. Ask which project (e.g. `TT`, `MAX`) this run is for, if not already
   said. It's needed only to know which rows to touch: fill a row **only
   if its `project` column matches** and its `description` is empty.
   Never touch a row that already has a description.
2. Work out the overall date range the file (or the relevant rows) covers,
   then get the raw activity: invoke the `timelog-data` skill with that
   range. If the raw activity for that exact range is already visible
   earlier in this conversation, reuse it instead of invoking
   `timelog-data` again.
3. For each row to fill, use the activity falling inside its `start`–`end`
   interval to draft a description. Language: match whatever language the
   user is chatting in — default to Russian per the user's global
   preference, switch only if the user writes in another language or asks
   for one explicitly.
4. Show the drafts to the user for confirmation/edits before writing
   anything.
5. Write the file only after confirmation (edit the CSV in place, keep
   other rows untouched).
6. Separately: if the collected activity shows time **outside every row's
   interval** within the requested range, warn about that untracked gap
   (date + approximate time span).
