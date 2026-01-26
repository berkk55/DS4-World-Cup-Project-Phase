# World Cup Project Data Dictionary

This folder contains the **production datasets** used for modeling and analysis.

## Files

- `project_dataset.csv` – Match-level dataset (1930–2026). One row per match.
- `players.csv` – Player-level dataset. Multiple rows per match.
- `rankings.csv` – FIFA ranking snapshot (2022-10-06). One row per team.

## Keys and Relationships

- `project_dataset.csv` ↔ `players.csv`:
  - Join on `match_key` (string key composed of year, date, home team, away team).
- `players.csv` ↔ `rankings.csv`:
  - Join on `team_initials` (FIFA/ISO 3-letter team codes where available).

## project_dataset.csv (match-level columns)

Base columns:
- `match_id`: Match identifier from source (when available).
- `year`: Tournament year (1930–2026).
- `date`: Match date/time (UTC).
- `stage`: Tournament stage.
- `group_name`: Group label (when available).
- `home_team`: Home team name (source text).
- `away_team`: Away team name (source text).
- `home_team_norm`: Normalized home team name for matching.
- `away_team_norm`: Normalized away team name for matching.
- `home_goals`: Home team goals.
- `away_goals`: Away team goals.
- `home_xg`: Home team expected goals (xG) (when available).
- `away_xg`: Away team expected goals (xG) (when available).
- `attendance`: Attendance (when available).
- `stadium`: Stadium name (when available).
- `city`: City name (when available).
- `host_country`: Host country (when available).
- `referee`: Referee name (when available).
- `win_conditions`: Extra time / penalties (when available).
- `host_team`: Boolean flag (host playing) (when available).
- `extra_time`: Indicator from detailed dataset (when available).
- `penalty_shootout`: Indicator from detailed dataset (when available).
- `score_penalties`: Penalty score string (when available).
- `home_penalties`: Home penalties scored (when available).
- `away_penalties`: Away penalties scored (when available).
- `result`: Result label (when available).
- `notes`: Match notes (when available).
- `dup_key`: Internal deduplication key.
- `tournament_id`: Tournament identifier.
- `tournament_name`: Tournament name.
- `d7_match_id`: Match identifier in d7.
- `match_name`: Match name (e.g., "France v Mexico").
- `group_stage`: Group stage flag.
- `knockout_stage`: Knockout stage flag.
- `replayed`: Replayed match flag.
- `replay`: Replay flag.
- `match_time`: Match time string.
- `stadium_id`: Stadium ID.
- `stadium_name_d7`: Stadium name from d7 (raw).
- `city_name_d7`: City name from d7 (raw).
- `host_country_d7`: Host country from d7 (raw).
- `home_team_id_d7`: Home team ID from d7.
- `home_team_code`: Home team code (3 letters).
- `away_team_id_d7`: Away team ID from d7.
- `away_team_code`: Away team code (3 letters).
- `score`: Score string.
- `home_score_margin`: Home score margin.
- `away_score_margin`: Away score margin.
- `home_team_win`: Home team win flag.
- `away_team_win`: Away team win flag.
- `draw`: Draw flag.

## players.csv (player-level columns)

- `match_id`: Match identifier from source.
- `match_key`: Key to join to `project_dataset.csv`.
- `team_initials`: Team 3-letter code.
- `side`: `home` / `away` / `unknown`.
- `coach_name`: Coach name (from lineup record).
- `player_name`: Player name.
- `position`: Position (GK, DF, MF, FW, etc.).
- `shirt_number`: Shirt number (numeric when available).
- `lineup`: Line-up indicator (S = starter, etc.).
- `event`: Player event string (goals/cards/etc. when present).

## rankings.csv (ranking snapshot columns)

- `team_initials`: Team 3-letter code.
- `team_name`: Team name.
- `confederation`: Confederation name.
- `rank`: Current rank (as of 2022-10-06).
- `previous_rank`: Previous rank.
- `points`: Current ranking points.
- `previous_points`: Previous ranking points.

## Notes

- Rankings are a **single snapshot** (2022-10-06). Add more snapshots as needed.
- Team and name normalization is applied to improve matching across sources.
