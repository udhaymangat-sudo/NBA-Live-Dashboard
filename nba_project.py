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


st.set_page_config(
    page_title="NBA Games Today",
    layout="centered",  # Use centered layout instead of wide
    initial_sidebar_state="collapsed"
)
st.markdown("<h1 style='text-align:center'>Udhay's NBA Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center'>{today}</h3>", unsafe_allow_html=True)

# -------------------------------
# GET DATA
# -------------------------------
response = requests.get(NBA_SCOREBOARD_URL)
data = response.json()
games = data["scoreboard"]["games"]
# -------------------------------
# GET Odds
# -------------------------------
API_KEY = "a17a6e90cf7065d09edee849f3f80e98"
SPORT = "basketball_nba"
REGION = "ca"  # Canadian sportsbooks
MARKETS = "totals"

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}"
response = requests.get(url)

odds_mapping = {}  # <-- your mapping code goes here

if response.status_code == 200:
    data = response.json()
    
    for game_odds in data:
        home_team_api = game_odds['home_team']
        away_team_api = game_odds['away_team']
        
        # Get first Canadian sportsbook total line
        total_line = None
        for bookmaker in game_odds['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        total_line = outcome.get('point')  # sometimes key is 'point' or 'price'
                    break
            if total_line:
                break
        
        # Map using combined team name key
        game_key = f"{home_team_api} vs {away_team_api}"
        odds_mapping[game_key] = total_line
else:
    st.error(f"Error fetching sportsbook odds: {response.status_code}")
# -------------------------------
# SCORE DISPLAY LOOP
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

    col1, col2, col3 = st.columns([3, 1, 3], gap="small")

    # Determine score color for finished games
    if is_final:
        away_color = "green" if away_score > home_score else "black"
        home_color = "green" if home_score > away_score else "black"
    else:
        away_color = home_color = "black"

    # ---------------- AWAY TEAM ----------------
    with col1:
       st.markdown(
    f"""
    <div style='display:flex; flex-direction:column; align-items:center; text-align:center; padding:5px; border-radius:8px;'>
        <img src='https://cdn.nba.com/logos/nba/{away['teamId']}/global/L/logo.svg' width='90'>
        <h3>{away['teamCity']} {away['teamName']}</h3>
        <h1 style='color:{away_color}'>{away_score}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

    # ---------------- CENTER ----------------
    with col2:
       st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
       st.markdown("<h2 style='text-align:center'>@</h2>", unsafe_allow_html=True)
       if is_live:
           status_text = "🟢 LIVE"
       if is_final:
           status_text = "🏁 FINAL"
       elif is_live:
               status_text = game.get("gameStatusText", "")
       else:
    # Game hasn't started yet, display scheduled start time
    # NBA API usually provides startTimeUTC or gameStatusText for pregame
        status_text = game.get("gameStatusText", "Scheduled")

    # Display centered
       st.markdown(f"<div style='text-align:center'>{status_text}</div>", unsafe_allow_html=True)
       st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- HOME TEAM ----------------
    with col3:
       st.markdown(
    f"""
    <div style='display:flex; flex-direction:column; align-items:center; text-align:center; padding:5px; border-radius:8px;'>
        <img src='https://cdn.nba.com/logos/nba/{home['teamId']}/global/L/logo.svg' width='90'>
        <h3>{home['teamCity']} {home['teamName']}</h3>
        <h1 style='color:{home_color}'>{home_score}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
