from __future__ import annotations

import base64
import textwrap
from pathlib import Path

import streamlit as st


def load_css(css_path: str) -> None:
    css = Path(css_path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def image_base64(image_path: str) -> str:
    data = Path(image_path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def hero_section(title: str, subtitle: str, image_path: str) -> None:
    image_b64 = image_base64(image_path)
    hero_html = textwrap.dedent(
        f"""
        <div class="hero" style="background-image: url('data:image/jpeg;base64,{image_b64}');">
          <div class="hero-overlay">
            <h1 class="hero-title display-font">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
          </div>
        </div>
        """
    ).strip()
    st.markdown(hero_html, unsafe_allow_html=True)


def section_title(text: str) -> None:
    st.markdown(f"<h2 class='section-title display-font'>{text}</h2>", unsafe_allow_html=True)


def kpi_grid(items: list[dict[str, str]]) -> None:
    cards = "".join(
        [
            textwrap.dedent(
                f"""
                <div class="kpi-card">
                  <div class="kpi-label">{item["label"]}</div>
                  <div class="kpi-value">{item["value"]}</div>
                  <div class="muted-text">{item.get("caption", "")}</div>
                </div>
                """
            ).strip()
            for item in items
        ]
    )
    st.markdown(f"<div class='kpi-grid'>{cards}</div>", unsafe_allow_html=True)


def champion_grid(items: list[dict[str, str]]) -> None:
    cards = "".join(
        [
            textwrap.dedent(
                f"""
                <div class="champion-card">
                  <h4 class="display-font">{item["year"]} · {item["winner"]}</h4>
                  <div class="champion-meta">Host: {item["host"]}</div>
                  <div class="champion-meta">Runner-up: {item["runner_up"]}</div>
                </div>
                """
            ).strip()
            for item in items
        ]
    )
    st.markdown(f"<div class='champion-grid'>{cards}</div>", unsafe_allow_html=True)
