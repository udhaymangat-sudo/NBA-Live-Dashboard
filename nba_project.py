#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 13:56:08 2026

@author: udhaymangat
"""
import streamlit as st
import requests
from datetime import datetime
from difflib import get_close_matches

st.set_page_config(page_title="NBA Live Scores & O/U", layout="wide")

# -------------------------------
# FETCH NBA GAMES
# -------------------------------
nba_games_url = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2026/scores/games.json"
# Example URL; replace with actual endpoint for today’s games
games_response = requests.get(nba_games_url)
if games_response.status_code != 200:
    st.error("Failed to fetch NBA games.")
    st.stop()

games_data = games_response.json()
games = games_data.get("games", [])  # Adjust according to your JSON structure

# -------------------------------
# FETCH ODDS FROM OddsAPI
# -------------------------------
API_KEY = "a17a6e90cf7065d09edee849f3f80e98"
SPORT = "basketball_nba"
REGION = "ca"
MARKETS = "totals"

odds_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}"
odds_response = requests.get(odds_url)
odds_mapping = {}
if odds_response.status_code == 200:
    data = odds_response.json()
    for game_odds in data:
        home_team_api = game_odds['home_team']
        away_team_api = game_odds['away_team']

        total_line = None
        for bookmaker in game_odds['bookmakers']:
            for market in bookmaker['markets']:
                if market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        total_line = outcome.get('point')
                    break
            if total_line:
                break

        game_key = f"{home_team_api} vs {away_team_api}"
        odds_mapping[game_key] = total_line
else:
    st.error(f"Error fetching sportsbook odds: {odds_response.status_code}")

# -------------------------------
# TEAM NAME MAP (NBA.com city -> OddsAPI)
# -------------------------------
team_name_map = {
    "Atlanta": "Atlanta Hawks",
    "Boston": "Boston Celtics",
    "Brooklyn": "Brooklyn Nets",
    "Charlotte": "Charlotte Hornets",
    "Chicago": "Chicago Bulls",
    "Cleveland": "Cleveland Cavaliers",
    "Dallas": "Dallas Mavericks",
    "Denver": "Denver Nuggets",
    "Detroit": "Detroit Pistons",
    "Golden State": "Golden State Warriors",
    "Houston": "Houston Rockets",
    "Indiana": "Indiana Pacers",
    "LA Clippers": "LA Clippers",
    "Los Angeles": "LA Lakers",
    "Memphis": "Memphis Grizzlies",
    "Miami": "Miami Heat",
    "Milwaukee": "Milwaukee Bucks",
    "Minnesota": "Minnesota Timberwolves",
    "New Orleans": "New Orleans Pelicans",
    "New York": "New York Knicks",
    "Oklahoma City": "Oklahoma City Thunder",
    "Orlando": "Orlando Magic",
    "Philadelphia": "Philadelphia 76ers",
    "Phoenix": "Phoenix Suns",
    "Portland": "Portland Trail Blazers",
    "Sacramento": "Sacramento Kings",
    "San Antonio": "San Antonio Spurs",
    "Toronto": "Toronto Raptors",
    "Utah": "Utah Jazz",
    "Washington": "Washington Wizards"
}

# -------------------------------
# DASHBOARD HEADER
# -------------------------------
today_str = datetime.now().strftime("%A, %B %d, %Y")
st.markdown(f"<h1 style='text-align:center'>NBA Games</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center'>{today_str}</h3>", unsafe_allow_html=True)
st.divider()

# -------------------------------
# HELPER FUNCTION: Fuzzy match OddsAPI key
# -------------------------------
def get_total_line(home_name, away_name, odds_keys):
    game_key = f"{home_name} vs {away_name}"
    matches = get_close_matches(game_key, odds_keys, n=1, cutoff=0.6)
    if matches:
        return odds_mapping[matches[0]]
    else:
        return "N/A"

# -------------------------------
# DISPLAY GAMES
# -------------------------------
for game in games:
    home = game["homeTeam"]
    away = game["awayTeam"]

    # Safe scores
    home_score = int(home.get("score", 0)) if home.get("score") else 0
    away_score = int(away.get("score", 0)) if away.get("score") else 0

    status_text_raw = game.get("gameStatusText", "")
    is_live = "Q" in status_text_raw or "Half" in status_text_raw
    is_final = "Final" in status_text_raw

    # Colors for winning team
    home_color = "green" if is_final and home_score > away_score else "black"
    away_color = "green" if is_final and away_score > home_score else "black"

    col_home, col_info, col_away = st.columns([3,2,3])

    # ---------- HOME COLUMN ----------
    with col_home:
        st.markdown(f"""
            <div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>
                <img src='https://cdn.nba.com/logos/nba/{home['teamId']}/global/L/logo.svg' width='90'>
                <h3>{home['teamCity']} {home['teamName']}</h3>
                <h1 style='color:{home_color}'>{home_score}</h1>
            </div>
        """, unsafe_allow_html=True)

    # ---------- MIDDLE COLUMN ----------
    with col_info:
        st.markdown("<div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>", unsafe_allow_html=True)

        # LIVE / FINAL badge
        if is_live:
            st.markdown("<div style='text-align:center'>🟢 <b>LIVE</b></div>", unsafe_allow_html=True)
        elif is_final:
            st.markdown("<div style='text-align:center'>🏁 <b>FINAL</b></div>", unsafe_allow_html=True)

        # @ symbol
        st.markdown("<h2 style='text-align:center'>@</h2>", unsafe_allow_html=True)

        # Arena info
        arena = game.get("arena")
        if arena:
            st.markdown(f"<div style='text-align:center'>{arena.get('name','')}, {arena.get('city','')}</div>", unsafe_allow_html=True)

        # Status text
        if is_final:
            status_text = "FINAL"
        elif is_live:
            status_text = status_text_raw
        else:
            status_text = "Scheduled"
        st.markdown(f"<div style='text-align:center'>{status_text}</div>", unsafe_allow_html=True)

        # ---------- SPORTSBOOK TOTAL LINE ----------
        home_mapped = team_name_map.get(home['teamCity'], home['teamCity'])
        away_mapped = team_name_map.get(away['teamCity'], away['teamCity'])
        total_line = get_total_line(home_mapped, away_mapped, odds_mapping.keys())
        st.markdown(f"<div style='text-align:center; margin-top:5px;'>O/U: {total_line}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- AWAY COLUMN ----------
    with col_away:
        st.markdown(f"""
            <div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>
                <img src='https://cdn.nba.com/logos/nba/{away['teamId']}/global/L/logo.svg' width='90'>
                <h3>{away['teamCity']} {away['teamName']}</h3>
                <h1 style='color:{away_color}'>{away_score}</h1>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
