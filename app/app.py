from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.charts import (
    attendance_area,
    avg_goals_line,
    goals_bar,
    titles_pie,
    top_scorers_bar,
)
from components.ui import champion_grid, hero_section, kpi_grid, load_css, section_title
from data.world_cup_data import attendance_data, goals_per_tournament, scorers_df, titles_df, total_kpis, winners_df


ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="World Cup Analytics", page_icon="⚽", layout="wide")
load_css(str(ROOT / "styles" / "theme.css"))


def main() -> None:
    hero_section(
        "FIFA World Cup Analytics",
        "Historical performance, tournament insights, and iconic winners",
        str(ROOT / "assets" / "stadium-hero.jpg"),
    )

    df_winners = winners_df()
    kpis = total_kpis(df_winners)
    kpi_grid(
        [
            {"label": "Tournaments", "value": f"{kpis['tournaments']}", "caption": "1930–2022"},
            {"label": "Total Goals", "value": f"{kpis['total_goals']:,}", "caption": "All-time"},
            {"label": "Champions", "value": "8", "caption": "Winning nations"},
            {"label": "Attendance", "value": f"{kpis['total_attendance']:,}", "caption": "Total spectators"},
        ]
    )

    section_title("Recent Champions")
    recent = df_winners.tail(8).copy()
    champion_grid(
        [
            {
                "year": str(row.year),
                "winner": row.winner,
                "host": row.host,
                "runner_up": row.runner_up,
            }
            for row in recent.itertuples()
        ]
    )

    section_title("Tournament Trends")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.plotly_chart(goals_bar(goals_per_tournament()), use_container_width=True)
    with col2:
        st.plotly_chart(titles_pie(titles_df()), use_container_width=True)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.plotly_chart(avg_goals_line(goals_per_tournament()), use_container_width=True)
    with col4:
        st.plotly_chart(attendance_area(attendance_data()), use_container_width=True)

    section_title("All-Time Top Scorers")
    st.plotly_chart(top_scorers_bar(scorers_df()), use_container_width=True)


if __name__ == "__main__":
    main()
