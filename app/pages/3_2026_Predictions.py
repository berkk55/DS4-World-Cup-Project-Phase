"""2026 World Cup match predictions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components.ui import load_css, section_title
from data.prediction_2026 import (
    get_2026_matches_with_teams,
    get_available_models,
    get_unique_stages_2026,
    get_unique_teams_2026,
)
from data.predictor import predict_match


ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="2026 Predictions", page_icon="🔮", layout="wide")
load_css(str(ROOT / "styles" / "theme.css"))


def format_match_option(row: pd.Series) -> str:
    """Format match for dropdown display."""
    date_str = pd.Timestamp(row["date"]).strftime("%Y-%m-%d") if pd.notna(row.get("date")) else "?"
    return f"{date_str} | {row['home_team']} vs {row['away_team']} ({row['stage']})"


def render_match_info(row: pd.Series) -> None:
    """Display match date, location, stadium."""
    info = []
    if pd.notna(row.get("date")):
        info.append(("Date", pd.Timestamp(row["date"]).strftime("%A, %B %d, %Y")))
    if pd.notna(row.get("stadium")) and str(row["stadium"]).strip():
        info.append(("Stadium", str(row["stadium"])))
    if pd.notna(row.get("city")) and str(row["city"]).strip():
        info.append(("City", str(row["city"])))
    if pd.notna(row.get("host_country")) and str(row["host_country"]).strip():
        info.append(("Country", str(row["host_country"])))

    if info:
        st.markdown("**Match details**")
        for label, val in info:
            st.markdown(f"- **{label}:** {val}")
    else:
        st.markdown("*No venue details available for this match.*")


def main() -> None:
    st.markdown("<h1 class='display-font'>2026 Predictions</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='muted-text'>Select a match and model to predict the outcome.</p>",
        unsafe_allow_html=True,
    )

    matches_df = get_2026_matches_with_teams()
    models_with_display = get_available_models()

    if not models_with_display:
        st.warning("No models found in the models folder. Add a .joblib model to enable predictions.")
        return

    if matches_df.empty:
        st.warning("No 2026 schedule data found. Ensure data/2026_wc_data_v.csv exists.")
        return

    teams = get_unique_teams_2026()
    stages = get_unique_stages_2026()

    # Radio outside form so changing it triggers re-run and updates the form layout
    match_type = st.radio(
        "Match selection",
        ["From schedule", "Custom"],
        horizontal=True,
    )

    with st.form("prediction_form"):
        if match_type == "From schedule":
            options = [format_match_option(row) for _, row in matches_df.iterrows()]
            match_idx = st.selectbox("Select match", range(len(options)), format_func=lambda i: options[i])
            selected = matches_df.iloc[match_idx]
            home_team = str(selected["home_team"])
            away_team = str(selected["away_team"])
            stage = str(selected["stage"])
            match_row = selected
        else:
            home_team = st.selectbox("Home team", teams)
            away_team = st.selectbox("Away team", [t for t in teams if t != home_team] or teams)
            stage = st.selectbox("Stage", stages) if stages else "Group Stage"
            match_row = None

        display_names = [m[0] for m in models_with_display]
        model_idx = st.selectbox(
            "Model",
            range(len(display_names)),
            format_func=lambda i: display_names[i],
            index=0,
        )
        model_name = models_with_display[model_idx][1]

        submitted = st.form_submit_button("Predict")

    if match_type == "Custom" and home_team and away_team:
        st.markdown(f"**Stage:** {stage}")

    if match_row is not None:
        with st.expander("Match info", expanded=True):
            render_match_info(match_row)

    if submitted:
        if home_team == away_team:
            st.error("Home and away teams must be different.")
        else:
            with st.spinner("Running prediction..."):
                result = predict_match(home_team, away_team, stage, model_name)

            if result is None:
                st.error("Could not load model or run prediction.")
            else:
                section_title("Prediction")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Predicted winner", result["outcome_label"])
                with col2:
                    st.metric("Predicted score", f"{result['home_goals']} – {result['away_goals']}")
                with col3:
                    st.metric("Match", f"{home_team} vs {away_team}")


if __name__ == "__main__":
    main()
