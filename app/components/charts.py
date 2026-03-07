from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_COLORS = ["#2ea65a", "#f1c453", "#4fa3ff", "#e05858", "#8e7dff"]


def apply_dark_layout(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        title=title,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        height=360,
    )
    return fig


def goals_bar(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(df, x="year", y="goals", color_discrete_sequence=[CHART_COLORS[0]])
    return apply_dark_layout(fig, "Goals per Tournament")


def titles_pie(df: pd.DataFrame) -> go.Figure:
    fig = px.pie(df, names="country", values="titles", hole=0.5, color_discrete_sequence=CHART_COLORS)
    return apply_dark_layout(fig, "Titles by Country")


def avg_goals_line(df: pd.DataFrame) -> go.Figure:
    fig = px.line(df, x="year", y="avg_goals", markers=True, color_discrete_sequence=[CHART_COLORS[1]])
    return apply_dark_layout(fig, "Average Goals per Match")


def attendance_area(df: pd.DataFrame) -> go.Figure:
    fig = px.area(df, x="year", y="attendance", color_discrete_sequence=[CHART_COLORS[2]])
    fig.update_traces(opacity=0.6)
    return apply_dark_layout(fig, "Attendance Over Time")


def top_scorers_bar(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df.sort_values("goals"),
        x="goals",
        y="name",
        orientation="h",
        color_discrete_sequence=[CHART_COLORS[3]],
    )
    return apply_dark_layout(fig, "All-Time Top Scorers")


def scatter_goals_matches(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="matches",
        y="goals",
        size="attendance",
        color="winner",
        color_discrete_sequence=CHART_COLORS,
        hover_data=["year", "host"],
    )
    return apply_dark_layout(fig, "Goals vs Matches")


def radar_countries(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    metrics = ["titles", "goals", "matches"]
    for _, row in df.iterrows():
        fig.add_trace(
            go.Scatterpolar(
                r=[row["titles"], row["goals"], row["matches"]],
                theta=metrics,
                fill="toself",
                name=row["country"],
            )
        )
    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(visible=True)),
        margin=dict(l=30, r=30, t=50, b=30),
        height=360,
        title="Country Performance Radar",
        legend_title_text="",
    )
    return fig

