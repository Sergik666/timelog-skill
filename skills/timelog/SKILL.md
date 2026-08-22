---
name: timelog
description: Entry point for everything time-tracking related, reconstructed from local Claude Code chat logs — routes to whichever specific timelog skill fits the request (a summary table, filling a CSV, a Redmine write-up) so the user doesn't have to know the family exists. Use whenever the user asks about time spent, what they did in some period, filling a time-entries CSV, or a Redmine summary, or types /timelog with no further detail.
---

# timelog

Single entry point for the timelog skill family. Figure out which
specific skill the request needs, then invoke it with the Skill tool —
don't reimplement its logic here, and don't make the user pick.

## Routing

- Mentions a CSV file, a time table to fill in, or gives a file path with
  a project → invoke **timelog-csv**.
- Mentions Redmine, or asks for a short write-up/summary to paste
  somewhere → invoke **timelog-redmine**.
- Anything else — "what did I do", "how much time did I spend", a plain
  date/range with no format specified → invoke **timelog-summary**
  (the default).
- Genuinely can't tell which format is wanted (e.g. "tell me about last
  week" with no hint of a table vs. CSV vs. Redmine) → ask, don't guess a
  format that's expensive to redo (a written CSV in particular).

Pass along whatever range/file/project details the user already gave —
the invoked skill handles range parsing and data fetching itself (via
timelog-data), including reusing raw activity already visible earlier in
this conversation instead of re-fetching it.

If the user's request could plausibly need more than one output (e.g.
"summarize this week and also fill the CSV") → invoke each needed skill
in turn.
