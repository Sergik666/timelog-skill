---
name: timelog-summary
description: Build a Markdown table (date, time range, what was done) summarizing how the user spent their time in a given range, reconstructed from local Claude Code chat logs. Use when the user asks how much time they spent, or what they did yesterday/today/this week/some range — with no mention of a CSV file or Redmine.
---

# timelog-summary

1. Get the resolved range and raw activity: invoke the `timelog-data`
   skill with whatever range the user gave. If the raw activity for that
   exact range is already visible earlier in this conversation, reuse it
   instead of invoking `timelog-data` again.
2. Group the raw activity into contiguous work stretches by topic/task —
   consecutive log lines about the same thing become one row, not one row
   per message.
3. Output a Markdown table, one row per stretch:

   | Date | Time | What was done |
   |---|---|---|

   No project column — project isn't tracked in this mode.
4. Language: match whatever language the user is chatting in — default to
   Russian per the user's global preference, switch only if the user
   writes in another language or asks for one explicitly.
