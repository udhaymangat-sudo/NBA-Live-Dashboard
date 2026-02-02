#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 13:56:08 2026

@author: udhaymangat
"""
import requests
import pandas as pd
import streamlit as st

# -------------------------------
# CONFIG
# -------------------------------

NBA_SCOREBOARD_URL = (
"https://cdn.nba.com/static/json/liveData/scoreboard/"
    "todaysScoreboard_00.json"
)


# Get todays date 
from datetime import date

today = date.today().strftime("%A, %B %d, %Y")


st.set_page_config(page_title="NBA Games Today", layout="wide")
st.title(f"NBA Games - {today}")

# -------------------------------
# GET DATA
# -------------------------------
response = requests.get(NBA_SCOREBOARD_URL)
data = response.json()
games = data["scoreboard"]["games"]

# -------------------------------
# DISPLAY LOOP
# -------------------------------
for game in games:
    home = game["homeTeam"]
    away = game["awayTeam"]

    home_score = int(home["score"])
    away_score = int(away["score"])

    # Determine game state
    is_live = "Q" in game["gameStatusText"] or "Half" in game["gameStatusText"]
    is_final = "Final" in game["gameStatusText"]

    # Background and opacity
    bg_color = "#E8F5E9" if is_live else "#FFFFFF"
    opacity = 0.5 if is_final else 1.0

    container_style = (
        f"background-color:{bg_color}; padding:20px; border-radius:12px; opacity:{opacity};"
    )
    st.markdown(f"<div style='{container_style}'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1, 3])

    # Determine score color for finished games
    if is_final:
        away_color = "green" if away_score > home_score else "black"
        home_color = "green" if home_score > away_score else "black"
    else:
        away_color = home_color = "black"

    # ---------------- AWAY TEAM ----------------
    with col1:
        st.markdown(
            f"<div style='text-align:center; padding:10px; border-radius:8px'>",
            unsafe_allow_html=True
        )
        st.image(
            f"https://cdn.nba.com/logos/nba/{away['teamId']}/global/L/logo.svg",
            width=120
        )
        st.markdown(
            f"<h3>{away['teamCity']} {away['teamName']}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h1 style='color:{away_color}'>{away_score}</h1>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- CENTER ----------------
    with col2:
        st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
        if is_live:
            st.markdown("🟢 **LIVE**")
        elif is_final:
            st.markdown("🏁 **FINAL**")
        st.markdown("<h2>@</h2>", unsafe_allow_html=True)
        st.write(game["gameStatusText"])
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- HOME TEAM ----------------
    with col3:
        st.markdown(
            f"<div style='text-align:center; padding:10px; border-radius:8px'>",
            unsafe_allow_html=True
        )
        st.image(
            f"https://cdn.nba.com/logos/nba/{home['teamId']}/global/L/logo.svg",
            width=120
        )
        st.markdown(
            f"<h3>{home['teamCity']} {home['teamName']}</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h1 style='color:{home_color}'>{home_score}</h1>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()