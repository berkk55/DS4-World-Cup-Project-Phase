"""Match outcome and score prediction using trained models."""

from __future__ import annotations

import hashlib
import math
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
    PROJECT_ROOT,
    get_ranking_score,
    get_team_code,
    load_rankings,
    normalize_stage,
    _team_for_features,
)

DEFAULT_POINTS = 1500.0


def _poisson_score_probability(lam: float, k: int) -> float:
    """P(X=k) for Poisson with mean lam."""
    if k < 0:
        return 0.0
    return float(np.exp(-lam) * (lam**k) / math.factorial(k))


def _lambda_to_score(
    lambda_home: float,
    lambda_away: float,
    max_goals: int = 8,
    seed: int | None = None,
) -> tuple[int, int]:
    """
    Convert predicted λ (expected goals) to integer score.

    Uses weighted sampling from top likely scores, constrained to outcomes
    that match the expected direction (home favored when λ_home > λ_away).
    Produces varied scores (1-0, 2-1, 2-0, 1-1, etc.) instead of collapsing
    to a single mode like 1-0 or 2-1 for all matches.
    """
    lam_h = max(0.01, float(lambda_home))
    lam_a = max(0.01, float(lambda_away))

    # Build scores and probabilities
    candidates: list[tuple[int, int, float]] = []
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = _poisson_score_probability(lam_h, h) * _poisson_score_probability(lam_a, a)
            # Constrain to direction implied by λ (avoids home-favorite → 1-2)
            if lam_h > lam_a + 0.1 and h < a:
                continue  # home favored, skip away-win scores
            if lam_a > lam_h + 0.1 and h > a:
                continue  # away favored, skip home-win scores
            candidates.append((h, a, prob))

    if not candidates:
        return (int(round(lam_h)), int(round(lam_a)))

    candidates.sort(key=lambda x: x[2], reverse=True)
    top = candidates[:10]
    total = sum(p for _, _, p in top)
    if total <= 0:
        return (int(round(lam_h)), int(round(lam_a)))

    weights = np.array([p / total for _, _, p in top])
    rng = np.random.default_rng(seed)
    idx = int(rng.choice(len(top), p=weights))
    return (top[idx][0], top[idx][1])


def load_artifact(model_name: str) -> dict | None:
    """Load model artifact by name (without .joblib)."""
    _ensure_unpickle_compat()
    # v3 model was saved from analysis/ and references analysis.ml_utils; add project root to path
    project_root = str(PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
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
    model_name: str = "",
) -> pd.DataFrame:
    """Build a feature row for prediction using a template from ml_df/ml_df_v2 + our rankings."""
    home_points = get_ranking_score(home_team, rankings)
    away_points = get_ranking_score(away_team, rankings)
    ranking_diff = home_points - away_points
    elo_diff = home_points - away_points
    stage_norm = normalize_stage(stage)

    # Use team names in ml_df format for correct OneHotEncoder encoding
    home_team_feat = _team_for_features(home_team)
    away_team_feat = _team_for_features(away_team)

    # Start from a template row so categoricals match training data format
    template = _get_ml_template_row(feature_cols, model_name)
    row = template.copy() if template else {c: np.nan for c in feature_cols}

    # Override with our match-specific values
    overrides = {
        "home_team": home_team_feat,
        "away_team": away_team_feat,
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
    # v3/v4 use ml_df_v2/v4 features: no prior 2026 tournament goals
    if model_name in ("worldcup_model_v3", "worldcup_model_v4"):
        overrides.update({
            "home_wc_goals_before": 0,
            "away_wc_goals_before": 0,
            "wc_goals_diff_before": 0,
            "home_wc_unique_scorers_before": 0,
            "away_wc_unique_scorers_before": 0,
            "home_wc_penalty_goals_before": 0,
            "away_wc_penalty_goals_before": 0,
        })
    # v4: neutral venue and home advantage (2026 joint hosts = USA, Mexico, Canada)
    if model_name == "worldcup_model_v4":
        HOSTS_2026 = {"United States", "USA", "Mexico", "Canada"}
        home_feat = _team_for_features(home_team)
        away_feat = _team_for_features(away_team)
        home_is_host = home_feat in HOSTS_2026
        away_is_host = away_feat in HOSTS_2026
        overrides["is_neutral_venue"] = 1 if (not home_is_host and not away_is_host) else 0
        overrides["home_advantage_strength"] = 1 if home_is_host else (-1 if away_is_host else 0)
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


def get_ml_medians(model_name: str = "") -> dict | None:
    """Get median values for numeric features. Use ml_df_v4 for v4, ml_df_v2 for v3."""
    path = (
        DATA_DIR / "ml_df_v4.csv" if model_name == "worldcup_model_v4"
        else DATA_DIR / "ml_df_v2.csv" if model_name == "worldcup_model_v3"
        else DATA_DIR / "ml_df.csv"
    )
    if not path.exists():
        return None
    df = pd.read_csv(path, nrows=1000)
    numeric = df.select_dtypes(include=[np.number])
    return numeric.median().to_dict()


def _get_ml_template_row(feature_cols: list[str], model_name: str = "") -> dict | None:
    """Get a template row from ml_df/ml_df_v2/ml_df_v4 to use as base for 2026 predictions."""
    path = (
        DATA_DIR / "ml_df_v4.csv" if model_name == "worldcup_model_v4"
        else DATA_DIR / "ml_df_v2.csv" if model_name == "worldcup_model_v3"
        else DATA_DIR / "ml_df.csv"
    )
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
    primary_prediction = artifact.get("primary_prediction", "outcome")

    rankings = load_rankings()
    ml_medians = get_ml_medians(model_name)

    X = build_feature_row(
        home_team, away_team, stage, feature_cols, rankings, ml_medians, model_name
    )

    # Ensure all feature cols present
    X = X.reindex(columns=feature_cols, fill_value=0)

    proba = model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    outcome = class_order[pred_idx]

    home_goals = away_goals = 0
    if score_models:
        home_model = score_models.get("home_goals")
        away_model = score_models.get("away_goals")
        if home_model and away_model:
            raw_home = float(np.clip(home_model.predict(X)[0], 0, 10))
            raw_away = float(np.clip(away_model.predict(X)[0], 0, 10))
            # Deterministic seed: same match always gets same score
            seed = int(hashlib.md5(f"{home_team}|{away_team}".encode()).hexdigest()[:8], 16)
            # Weighted sample from direction-constrained scores for variety
            home_goals, away_goals = _lambda_to_score(raw_home, raw_away, seed=seed)
            # Derive outcome from Poisson score
            if primary_prediction == "score":
                outcome = (
                    "HomeWin" if home_goals > away_goals
                    else "AwayWin" if away_goals > home_goals
                    else "Draw"
                )

    outcome_labels = {
        "HomeWin": f"{home_team} wins",
        "Draw": "Draw",
        "AwayWin": f"{away_team} wins",
    }
    outcome_label = outcome_labels.get(outcome, outcome)

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
