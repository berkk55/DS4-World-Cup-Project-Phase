from __future__ import annotations

import random
import time
from pathlib import Path

import streamlit as st

from components.ui import load_css
from data.world_cup_data import scorers_df, titles_df, winners_df


ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(page_title="World Cup Chat", page_icon="💬", layout="wide")
load_css(str(ROOT / "styles" / "theme.css"))


def generate_response(question: str) -> str:
    q = question.lower()
    winners = winners_df()
    titles = titles_df()
    scorers = scorers_df()

    if "who won" in q or "winner" in q:
        year_match = [token for token in q.split() if token.isdigit() and len(token) == 4]
        if year_match:
            year = int(year_match[0])
            entry = winners[winners["year"] == year]
            if not entry.empty:
                row = entry.iloc[0]
                return (
                    f"🏆 The {row['year']} World Cup was held in **{row['host']}** and won by "
                    f"**{row['winner']}**, defeating {row['runner_up']} in the final. "
                    f"There were {row['goals']} goals across {row['matches']} matches."
                )
            return "I don't have data for that year. The dataset covers 1930–2022."
        latest = winners.iloc[-1]
        return (
            f"The most recent World Cup ({latest['year']}) was won by **{latest['winner']}**, "
            f"beating {latest['runner_up']} in the final hosted in {latest['host']}."
        )

    if "most titles" in q or "most cups" in q or "most world cup" in q:
        top = titles.iloc[0]
        ranking = "\n".join([f"{row['flag']} {row['country']}: {row['titles']}" for _, row in titles.iterrows()])
        return f"**{top['country']}** leads with **{top['titles']} titles**!\n\n{ranking}"

    if "top scorer" in q or "most goals" in q or "goal scorer" in q:
        top = scorers.iloc[0]
        top5 = "\n".join(
            [f"{i + 1}. {row['name']} ({row['country']}) — {row['goals']} goals" for i, row in scorers.head(5).iterrows()]
        )
        return (
            f"⚽ **{top['name']}** ({top['country']}) is the all-time top scorer with "
            f"**{top['goals']} goals** across {top['tournaments']} tournaments.\n\nTop 5:\n{top5}"
        )

    if "attendance" in q or "spectators" in q or "crowd" in q:
        highest = winners.sort_values("attendance", ascending=False).iloc[0]
        return (
            f"🏟️ The highest total attendance was at the **{highest['year']} World Cup** in "
            f"{highest['host']} with **{highest['attendance']:,}** spectators across "
            f"{highest['matches']} matches."
        )

    if "host" in q or "where was" in q:
        year_match = [token for token in q.split() if token.isdigit() and len(token) == 4]
        if year_match:
            year = int(year_match[0])
            entry = winners[winners["year"] == year]
            if not entry.empty:
                row = entry.iloc[0]
                return f"The {row['year']} World Cup was hosted by **{row['host']}**."
        recent_hosts = "\n".join([f"• {row.year}: {row.host}" for row in winners.tail(5).itertuples()])
        return f"Here are some recent hosts:\n{recent_hosts}"

    if "how many" in q and "tournament" in q:
        return f"There have been **{len(winners)} FIFA World Cup tournaments** from 1930 to 2022."

    if "total goals" in q or "all goals" in q:
        total = int(winners["goals"].sum())
        return f"⚽ A total of **{total:,} goals** have been scored across all World Cup tournaments."

    if any(word in q for word in ["hello", "hi", "hey"]):
        return (
            "Hey there! ⚽ I'm your World Cup data assistant. Ask me about winners, top scorers, "
            "attendance records, host countries, or any tournament from 1930 to 2022!"
        )

    return (
        "I can answer questions about FIFA World Cup history (1930–2022). Try asking:\n\n"
        "• \"Who won the 2006 World Cup?\"\n"
        "• \"Which country has the most titles?\"\n"
        "• \"Who is the all-time top scorer?\"\n"
        "• \"What was the highest attendance?\"\n"
        "• \"How many tournaments have there been?\""
    )


st.markdown("<h1 class='display-font'>World Cup Chat</h1>", unsafe_allow_html=True)
st.markdown("<p class='muted-text'>Ask questions about FIFA World Cup history.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to the World Cup Chat! ⚽ Ask me about winners, scorers, attendance, "
                "hosts, and more."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a World Cup question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(0.6 + random.random() * 0.8)
        response = generate_response(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
