from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components.charts import (
    attendance_area,
    avg_goals_line,
    goals_bar,
    radar_countries,
    scatter_goals_matches,
    titles_pie,
)
from components.ui import kpi_grid, load_css, section_title
from data.world_cup_data import scorers_df, total_kpis, winners_df


ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="World Cup Dashboard", page_icon="📊", layout="wide")
load_css(str(ROOT / "styles" / "theme.css"))


def filter_data(df: pd.DataFrame, year_range: tuple[int, int], country: str) -> pd.DataFrame:
    filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    if country != "All":
        filtered = filtered[filtered["winner"] == country]
    return filtered


def dashboard() -> None:
    st.markdown("<h1 class='display-font'>Interactive Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Filter results by era and winning country.</p>", unsafe_allow_html=True)

    df = winners_df()

    ranges = {
        "All": (1930, 2022),
        "1930–1970": (1930, 1970),
        "1974–1998": (1974, 1998),
        "2002–2022": (2002, 2022),
    }

    with st.sidebar:
        st.header("Filters")
        range_label = st.radio("Year range", list(ranges.keys()), horizontal=False)
        countries = ["All"] + sorted(df["winner"].unique().tolist())
        country = st.selectbox("Winning country", countries)

    filtered = filter_data(df, ranges[range_label], country)
    kpis = total_kpis(filtered if not filtered.empty else df)

    kpi_grid(
        [
            {"label": "Tournaments", "value": f"{kpis['tournaments']}"},
            {"label": "Total Goals", "value": f"{kpis['total_goals']:,}"},
            {"label": "Avg Goals/Match", "value": f"{kpis['avg_goals_per_match']}"},
            {"label": "Attendance", "value": f"{kpis['total_attendance']:,}"},
        ]
    )

    if filtered.empty:
        st.warning("No tournaments match the selected filters.")
        return

    filtered_chart = filtered.copy()
    filtered_chart["year"] = filtered_chart["year"].astype(str)

    titles = (
        filtered.groupby("winner")
        .size()
        .reset_index(name="titles")
        .rename(columns={"winner": "country"})
        .sort_values("titles", ascending=False)
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.plotly_chart(goals_bar(filtered_chart[["year", "goals"]]), use_container_width=True)
    with col2:
        st.plotly_chart(titles_pie(titles), use_container_width=True)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        avg_df = filtered_chart[["year", "goals", "matches"]].copy()
        avg_df["avg_goals"] = (avg_df["goals"] / avg_df["matches"]).round(2)
        st.plotly_chart(avg_goals_line(avg_df[["year", "avg_goals"]]), use_container_width=True)
    with col4:
        attendance = filtered_chart[["year", "attendance"]]
        st.plotly_chart(attendance_area(attendance), use_container_width=True)

    col5, col6 = st.columns(2, gap="large")
    with col5:
        st.plotly_chart(scatter_goals_matches(filtered), use_container_width=True)
    with col6:
        agg = filtered.groupby("winner")[["goals", "matches"]].sum().reset_index().rename(columns={"winner": "country"})
        radar_data = titles.head(5).merge(agg, on="country", how="left")[["country", "titles", "goals", "matches"]]
        st.plotly_chart(radar_countries(radar_data), use_container_width=True)

    section_title("Top Scorers")
    scorers = scorers_df().copy()
    st.dataframe(
        scorers,
        use_container_width=True,
        column_config={
            "goals": st.column_config.ProgressColumn(
                "Goals",
                min_value=0,
                max_value=int(scorers["goals"].max()),
                format="%d",
            )
        },
        hide_index=True,
    )


if __name__ == "__main__":
    dashboard()
