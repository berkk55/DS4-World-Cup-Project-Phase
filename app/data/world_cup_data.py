from __future__ import annotations

import pandas as pd

world_cup_winners = [
    {"year": 1930, "host": "Uruguay", "winner": "Uruguay", "runner_up": "Argentina", "goals": 70, "matches": 18, "attendance": 590549},
    {"year": 1934, "host": "Italy", "winner": "Italy", "runner_up": "Czechoslovakia", "goals": 70, "matches": 17, "attendance": 363000},
    {"year": 1938, "host": "France", "winner": "Italy", "runner_up": "Hungary", "goals": 84, "matches": 18, "attendance": 375700},
    {"year": 1950, "host": "Brazil", "winner": "Uruguay", "runner_up": "Brazil", "goals": 88, "matches": 22, "attendance": 1045246},
    {"year": 1954, "host": "Switzerland", "winner": "Germany", "runner_up": "Hungary", "goals": 140, "matches": 26, "attendance": 768607},
    {"year": 1958, "host": "Sweden", "winner": "Brazil", "runner_up": "Sweden", "goals": 126, "matches": 35, "attendance": 819810},
    {"year": 1962, "host": "Chile", "winner": "Brazil", "runner_up": "Czechoslovakia", "goals": 89, "matches": 32, "attendance": 893172},
    {"year": 1966, "host": "England", "winner": "England", "runner_up": "Germany", "goals": 89, "matches": 32, "attendance": 1563135},
    {"year": 1970, "host": "Mexico", "winner": "Brazil", "runner_up": "Italy", "goals": 95, "matches": 32, "attendance": 1603975},
    {"year": 1974, "host": "Germany", "winner": "Germany", "runner_up": "Netherlands", "goals": 97, "matches": 38, "attendance": 1865753},
    {"year": 1978, "host": "Argentina", "winner": "Argentina", "runner_up": "Netherlands", "goals": 102, "matches": 38, "attendance": 1545791},
    {"year": 1982, "host": "Spain", "winner": "Italy", "runner_up": "Germany", "goals": 146, "matches": 52, "attendance": 2109723},
    {"year": 1986, "host": "Mexico", "winner": "Argentina", "runner_up": "Germany", "goals": 132, "matches": 52, "attendance": 2394031},
    {"year": 1990, "host": "Italy", "winner": "Germany", "runner_up": "Argentina", "goals": 115, "matches": 52, "attendance": 2516215},
    {"year": 1994, "host": "USA", "winner": "Brazil", "runner_up": "Italy", "goals": 141, "matches": 52, "attendance": 3587538},
    {"year": 1998, "host": "France", "winner": "France", "runner_up": "Brazil", "goals": 171, "matches": 64, "attendance": 2785100},
    {"year": 2002, "host": "South Korea/Japan", "winner": "Brazil", "runner_up": "Germany", "goals": 161, "matches": 64, "attendance": 2705197},
    {"year": 2006, "host": "Germany", "winner": "Italy", "runner_up": "France", "goals": 147, "matches": 64, "attendance": 3359439},
    {"year": 2010, "host": "South Africa", "winner": "Spain", "runner_up": "Netherlands", "goals": 145, "matches": 64, "attendance": 3178856},
    {"year": 2014, "host": "Brazil", "winner": "Germany", "runner_up": "Argentina", "goals": 171, "matches": 64, "attendance": 3429873},
    {"year": 2018, "host": "Russia", "winner": "France", "runner_up": "Croatia", "goals": 169, "matches": 64, "attendance": 3031768},
    {"year": 2022, "host": "Qatar", "winner": "Argentina", "runner_up": "France", "goals": 172, "matches": 64, "attendance": 3404252},
]

titles_by_country = [
    {"country": "Brazil", "titles": 5, "flag": "🇧🇷"},
    {"country": "Germany", "titles": 4, "flag": "🇩🇪"},
    {"country": "Italy", "titles": 4, "flag": "🇮🇹"},
    {"country": "Argentina", "titles": 3, "flag": "🇦🇷"},
    {"country": "France", "titles": 2, "flag": "🇫🇷"},
    {"country": "Uruguay", "titles": 2, "flag": "🇺🇾"},
    {"country": "England", "titles": 1, "flag": "🏴"},
    {"country": "Spain", "titles": 1, "flag": "🇪🇸"},
]

top_scorers = [
    {"name": "Miroslav Klose", "country": "Germany", "goals": 16, "tournaments": 4},
    {"name": "Ronaldo", "country": "Brazil", "goals": 15, "tournaments": 4},
    {"name": "Gerd Müller", "country": "Germany", "goals": 14, "tournaments": 2},
    {"name": "Just Fontaine", "country": "France", "goals": 13, "tournaments": 1},
    {"name": "Pelé", "country": "Brazil", "goals": 12, "tournaments": 4},
    {"name": "Kylian Mbappé", "country": "France", "goals": 12, "tournaments": 2},
    {"name": "Sándor Kocsis", "country": "Hungary", "goals": 11, "tournaments": 1},
    {"name": "Jürgen Klinsmann", "country": "Germany", "goals": 11, "tournaments": 3},
]


def winners_df() -> pd.DataFrame:
    return pd.DataFrame(world_cup_winners)


def titles_df() -> pd.DataFrame:
    return pd.DataFrame(titles_by_country)


def scorers_df() -> pd.DataFrame:
    return pd.DataFrame(top_scorers)


def goals_per_tournament() -> pd.DataFrame:
    df = winners_df().copy()
    df["avg_goals"] = (df["goals"] / df["matches"]).round(2)
    df["year"] = df["year"].astype(str)
    return df[["year", "goals", "avg_goals"]]


def attendance_data() -> pd.DataFrame:
    df = winners_df().copy()
    df["avg_attendance"] = (df["attendance"] / df["matches"]).round().astype(int)
    df["year"] = df["year"].astype(str)
    return df[["year", "attendance", "avg_attendance"]]


def total_kpis(df: pd.DataFrame) -> dict[str, int | float]:
    tournaments = len(df)
    total_goals = int(df["goals"].sum()) if not df.empty else 0
    avg_goals = round(df["goals"].sum() / df["matches"].sum(), 2) if not df.empty else 0
    total_attendance = int(df["attendance"].sum()) if not df.empty else 0
    return {
        "tournaments": tournaments,
        "total_goals": total_goals,
        "avg_goals_per_match": avg_goals,
        "total_attendance": total_attendance,
    }
