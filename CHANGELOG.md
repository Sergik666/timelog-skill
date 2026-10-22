# Changelog

## 1.1.1 — 2026-10-22

- `timelog-api` keeps credentials and backups in `~/.claude/timelog/`
  (was `~/.config/timelog/`), which survives container rebuilds.

## 1.1.0 — 2026-10-22

- New `timelog-api` skill: fills blank descriptions of one project's entries
  in the Time Tracker through its API (needs Time Tracker 0.7.0+), with
  confirmation before writing and a local full backup before every write.
- `timelog` router sends "fill slots in the tracker" requests to `timelog-api`.
- `tt.env.example` credentials template.

## 1.0.0 — 2026-08-22

- Router `timelog` plus `timelog-data`, `timelog-summary`, `timelog-csv`,
  `timelog-redmine`.
