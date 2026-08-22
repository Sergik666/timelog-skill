---
name: timelog-redmine
description: Build a short English per-day summary table for Redmine time tracking, reconstructed from local Claude Code chat logs. Use when the user asks for a Redmine summary/write-up for a date range.
---

# timelog-redmine

1. Get the resolved range and raw activity: invoke the `timelog-data`
   skill with whatever range the user gave. If the raw activity for that
   exact range is already visible earlier in this conversation, reuse it
   instead of invoking `timelog-data` again.
2. Output a chat table:

   | Date | Description |
   |---|---|

   One row per day by default — merge everything done that day into one
   summary. Only split into per-interval rows if the user explicitly asks
   for that.
3. Description is in **English**, max 20 words, regardless of what
   language the request was made in — unless the user explicitly asks for
   another language.
