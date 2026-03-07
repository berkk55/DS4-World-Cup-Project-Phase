"""Data and helpers for 2026 World Cup predictions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Project root (parent of app/)
APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

# Map 2026 team names to rankings.csv team_name
TEAM_NAME_MAP = {
    "South Korea": "Korea Republic",
    "Korea Republic": "Korea Republic",
    "IR Iran": "IR Iran",
    "Iran": "IR Iran",
    "USA": "USA",
    "United States": "USA",
    "Côte d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Cabo Verde": "Cabo Verde",
    "Cape Verde": "Cabo Verde",
    "UAE": "United Arab Emirates",
    "DR Congo": "Congo DR",
    "North Korea": "Korea DPR",
    "Korea DPR": "Korea DPR",
    "Republic of Ireland": "Republic of Ireland",
    "Ireland": "Republic of Ireland",
    "Türkiye": "Türkiye",
    "Turkey": "Türkiye",
    "China": "China PR",
    "China PR": "China PR",
    "Chinese Taipei": "Chinese Taipei",
    "Taiwan": "Chinese Taipei",
    "St Vincent and the Grenadines": "St Vincent and the Grenadines",
    "Venezuela": "Venezuela",
}


def load_2026_schedule() -> pd.DataFrame:
    """Load 2026 World Cup schedule."""
    path = DATA_DIR / "2026_wc_data_v.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def load_rankings() -> pd.DataFrame:
    """Load FIFA rankings with points as ranking score."""
    path = DATA_DIR / "rankings.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def get_2026_matches_with_teams() -> pd.DataFrame:
    """Return 2026 matches that have both home and away teams (no placeholder)."""
    df = load_2026_schedule()
    if df.empty:
        return df
    placeholder = df["home_team"].str.contains("Winner|Playoff", case=False, na=False) | df[
        "away_team"
    ].str.contains("Winner|Playoff", case=False, na=False)
    return df[~placeholder].dropna(subset=["home_team", "away_team"]).copy()


def get_unique_teams_2026() -> list[str]:
    """Unique team names from 2026 schedule (excluding placeholders)."""
    df = get_2026_matches_with_teams()
    if df.empty:
        return []
    home = set(df["home_team"].dropna().astype(str))
    away = set(df["away_team"].dropna().astype(str))
    return sorted(home | away)


def get_unique_stages_2026() -> list[str]:
    """Unique stage names from 2026 schedule."""
    df = load_2026_schedule()
    if df.empty:
        return []
    stages = df["stage"].dropna().unique().tolist()
    return sorted(stages)


def get_2026_matches_for_stage(stage: str) -> pd.DataFrame:
    """Matches for a given stage."""
    df = get_2026_matches_with_teams()
    if df.empty:
        return df
    return df[df["stage"].str.lower() == stage.lower()].copy()


def get_ranking_score(team: str, rankings: pd.DataFrame) -> float:
    """Get ranking points for a team."""
    if rankings.empty:
        return 1500.0
    name = TEAM_NAME_MAP.get(team, team)
    row = rankings[rankings["team_name"] == name]
    if row.empty:
        return 1500.0
    return float(row.iloc[0]["points"])


def get_team_code(team: str, rankings: pd.DataFrame) -> str:
    """Get FIFA team code (initials) for a team."""
    if rankings.empty:
        return "XXX"
    name = TEAM_NAME_MAP.get(team, team)
    row = rankings[rankings["team_name"] == name]
    if row.empty:
        return "XXX"
    return str(row.iloc[0]["team_initials"])


# Map 2026 stage names to ml_df stage format
STAGE_MAP = {
    "group stage": "Group stage",
    "round of 32": "round of 32",
    "round of 16": "round of 16",
    "quarterfinals": "quarter-finals",
    "quarter-finals": "quarter-finals",
    "semifinals": "semi-finals",
    "semi-finals": "semi-finals",
    "third place playoff": "Third Place Playoff",
    "final": "final",
}


def normalize_stage(stage: str) -> str:
    """Normalize stage name to match training data format."""
    key = stage.lower().strip()
    return STAGE_MAP.get(key, stage)


def get_available_models() -> list[str]:
    """List .joblib model files in models folder."""
    if not MODELS_DIR.exists():
        return []
    return sorted(
        f.stem for f in MODELS_DIR.glob("*.joblib") if f.stat().st_size > 0
    )
