"""Match outcome and score prediction using trained models."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import joblib


def _to_dense_fn(x):
    """Compat for pickled FunctionTransformer from notebooks."""
    return x.toarray() if hasattr(x, "toarray") else x


class PrefitPipeline:
    """Compat for pickled PrefitPipeline from n4.1_training notebook."""

    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        Xp = self.preprocessor.transform(X)
        return self.model.predict(Xp)

    def predict_proba(self, X):
        Xp = self.preprocessor.transform(X)
        return self.model.predict_proba(Xp)


def _ensure_unpickle_compat() -> None:
    """Patch __main__ so joblib can load models with custom classes from notebooks."""
    main = sys.modules.get("__main__")
    needs_compat = main is None or not hasattr(main, "to_dense_fn") or not hasattr(main, "PrefitPipeline")
    if needs_compat:
        compat = types.ModuleType("__main__")
        compat.to_dense_fn = _to_dense_fn
        compat.PrefitPipeline = PrefitPipeline
        sys.modules["__main__"] = compat


import numpy as np
import pandas as pd

from data.prediction_2026 import (
    DATA_DIR,
    MODELS_DIR,
    get_ranking_score,
    get_team_code,
    load_rankings,
    normalize_stage,
)

DEFAULT_POINTS = 1500.0


def _round_goal(x: float) -> int:
    """Round predicted goals to non-negative integer."""
    return max(0, int(round(x)))


def load_artifact(model_name: str) -> dict | None:
    """Load model artifact by name (without .joblib)."""
    _ensure_unpickle_compat()
    path = MODELS_DIR / f"{model_name}.joblib"
    if not path.exists() or path.stat().st_size == 0:
        return None
    return joblib.load(path)


def build_feature_row(
    home_team: str,
    away_team: str,
    stage: str,
    feature_cols: list[str],
    rankings: pd.DataFrame,
    ml_medians: dict | None = None,
) -> pd.DataFrame:
    """Build a feature row for prediction using a template from ml_df + our rankings."""
    home_points = get_ranking_score(home_team, rankings)
    away_points = get_ranking_score(away_team, rankings)
    ranking_diff = home_points - away_points
    elo_diff = home_points - away_points
    stage_norm = normalize_stage(stage)

    # Start from a template row so categoricals match training data format
    template = _get_ml_template_row(feature_cols)
    row = template.copy() if template else {c: np.nan for c in feature_cols}

    # Override with our match-specific values
    overrides = {
        "home_team": home_team,
        "away_team": away_team,
        "stage": stage_norm,
        "tournament_name": "2026 FIFA World Cup",
        "host_country": "USA",
        "home_team_code": get_team_code(home_team, rankings),
        "away_team_code": get_team_code(away_team, rankings),
        "ranking_diff": ranking_diff,
        "elo_diff": elo_diff,
        "home_ranking_score": home_points,
        "away_ranking_score": away_points,
        "home_elo_before": home_points,
        "away_elo_before": away_points,
        "year": 2026,
        "year_normalized": 0.96,
        "tournament_size_category": "large",
        "total_teams": 48,
        "matches_played": 0,
        "goals_scored_tournament": 0,
        "avg_goals_per_game": 2.7,
    }
    for col, val in overrides.items():
        if col in feature_cols:
            row[col] = val

    # Fill remaining NaN with median (numeric) or 0
    numeric_cols = set(ml_medians.keys()) if ml_medians else set()
    for col in feature_cols:
        val = row.get(col)
        if pd.isna(val) or (isinstance(val, float) and val != val):
            row[col] = ml_medians.get(col, 0.0) if col in numeric_cols else 0.0

    return pd.DataFrame([row]).reindex(columns=feature_cols)


def get_ml_medians() -> dict | None:
    """Get median values for numeric features from ml_df."""
    path = DATA_DIR / "ml_df.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, nrows=1000)
    numeric = df.select_dtypes(include=[np.number])
    return numeric.median().to_dict()


def _get_ml_template_row(feature_cols: list[str]) -> dict | None:
    """Get a template row from ml_df to use as base for 2026 predictions."""
    path = DATA_DIR / "ml_df.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, nrows=500)
    if not all(c in df.columns for c in feature_cols):
        return None
    return df.iloc[-1].reindex(feature_cols).to_dict()


def predict_match(
    home_team: str,
    away_team: str,
    stage: str,
    model_name: str,
) -> dict | None:
    """
    Predict match outcome and score.
    Returns dict with: outcome, outcome_label, home_goals, away_goals, proba_home, proba_draw, proba_away
    or None if model load fails.
    """
    artifact = load_artifact(model_name)
    if not artifact:
        return None

    model = artifact["model"]
    feature_cols = artifact.get("feature_cols", [])
    class_order = artifact.get("class_order", ["HomeWin", "Draw", "AwayWin"])
    score_models = artifact.get("score_models", {})

    rankings = load_rankings()
    ml_medians = get_ml_medians()

    X = build_feature_row(
        home_team, away_team, stage, feature_cols, rankings, ml_medians
    )

    # Ensure all feature cols present
    X = X.reindex(columns=feature_cols, fill_value=0)

    proba = model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    outcome = class_order[pred_idx]

    outcome_labels = {
        "HomeWin": f"{home_team} wins",
        "Draw": "Draw",
        "AwayWin": f"{away_team} wins",
    }
    outcome_label = outcome_labels.get(outcome, outcome)

    home_goals = away_goals = 0
    if score_models:
        home_model = score_models.get("home_goals")
        away_model = score_models.get("away_goals")
        if home_model and away_model:
            home_goals = _round_goal(float(home_model.predict(X)[0]))
            away_goals = _round_goal(float(away_model.predict(X)[0]))

    idx_home = class_order.index("HomeWin") if "HomeWin" in class_order else 0
    idx_draw = class_order.index("Draw") if "Draw" in class_order else 1
    idx_away = class_order.index("AwayWin") if "AwayWin" in class_order else 2

    return {
        "outcome": outcome,
        "outcome_label": outcome_label,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "proba_home": float(proba[idx_home]) if idx_home < len(proba) else 0,
        "proba_draw": float(proba[idx_draw]) if idx_draw < len(proba) else 0,
        "proba_away": float(proba[idx_away]) if idx_away < len(proba) else 0,
    }
