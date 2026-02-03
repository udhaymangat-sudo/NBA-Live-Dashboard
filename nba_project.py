import requests
import pandas as pd
import streamlit as st
from difflib import get_close_matches
from datetime import datetime, timezone, timedelta
import time
import pytz


# -------------------------------
# GET TODAY'S DATE
# -------------------------------
today_utc = datetime.now(timezone.utc).date()
today = datetime.today().strftime("%A, %B %d, %Y")
# -------------------------------
# TITLES
# -------------------------------
    #Title for website 
st.set_page_config(page_title="🏀 Live NBA Scores", layout="centered")
    #Title at top of the page
st.markdown("<div style='text-align: center; font-size: 50px;font-weight: bold;'>Today's NBA Games</div>",unsafe_allow_html=True)
st.markdown(f"<div style='text-align: center; font-size: 30px; font-weight: bold;'>{today}</div>",unsafe_allow_html=True)

# -------------------------------
# RETREIVE NBA SCORES FOR TODAY
# -------------------------------
API_KEY = "a17a6e90cf7065d09edee849f3f80e98"
SPORT = "basketball_nba"
REGION = "us"
MARKETS = "totals"  # moneyline odds

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}"

response = requests.get(url)
games = response.json()

# -------------------------------
# SCORECARD INFO
# -------------------------------
for game in games:

    home_name = game["home_team"]
    away_name = game["away_team"]
    scores = game.get("scores")

    # ---------- GET SCORES ----------
    if scores and isinstance(scores, list):
        home_score = next((int(s["score"]) for s in scores if s["name"] == home_name), 0)
        away_score = next((int(s["score"]) for s in scores if s["name"] == away_name), 0)
    else:
        home_score = 0
        away_score = 0

    update_time = game.get("last_update", "")

    # ---------- GET SCORES ----------
    status_text_raw = game.get("gameStatusText", "")
    is_live = "Q" in status_text_raw or "Half" in status_text_raw
    is_final = "Final" in status_text_raw

    home_color = "green" if is_final and home_score > away_score else "black"
    away_color = "green" if is_final and away_score > home_score else "black"
    
    # ---------- GET TOTAL POINTS ---------- 
    total_points = home_score + away_score
    
    # ---------- GET OVER/UNDER ODDS ----------
    over_under_text = "N/A"
    if "bookmakers" in game and game["bookmakers"]:
       markets = game["bookmakers"][0].get("markets", [])
       for m in markets:
           if m["key"] == "totals":  # totals = over/under
               outcomes = m.get("outcomes", [])
               over_odds = next((o for o in outcomes if o["name"].lower() == "over"), None)
               over_under_text = f"O/U: {over_odds['point']} total points"
               break
    # ---------- GET GAME STATUS ----------
    commence_time = game["commence_time"]
    commence_utc = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
    utc = pytz.UTC
    pst = pytz.timezone("America/Los_Angeles")
    commence_utc = utc.localize(commence_utc.replace(tzinfo=None))
    commence_pst = commence_utc.astimezone(pst)
    commence_minus_10 = commence_pst - timedelta(minutes=10)
    time_only_str = commence_minus_10.strftime("%I:%M %p")  # "03:10:38"

    # ---------- MAP NBA TEAMS ----------
    team_ids = {"Atlanta Hawks": 1610612737,
    "Boston Celtics": 1610612738,
    "Brooklyn Nets": 1610612751,
    "Charlotte Hornets": 1610612766,
    "Chicago Bulls": 1610612741,
    "Cleveland Cavaliers": 1610612739,
    "Dallas Mavericks": 1610612742,
    "Denver Nuggets": 1610612743,
    "Detroit Pistons": 1610612765,
    "Golden State Warriors": 1610612744,
    "Houston Rockets": 1610612745,
    "Indiana Pacers": 1610612754,
    "LA Clippers": 1610612746,
    "Los Angeles Lakers": 1610612747,
    "Memphis Grizzlies": 1610612763,
    "Miami Heat": 1610612748,
    "Milwaukee Bucks": 1610612749,
    "Minnesota Timberwolves": 1610612750,
    "New Orleans Pelicans": 1610612740,
    "New York Knicks": 1610612752,
    "Oklahoma City Thunder": 1610612760,
    "Orlando Magic": 1610612753,
    "Philadelphia 76ers": 1610612755,
    "Phoenix Suns": 1610612756,
    "Portland Trail Blazers": 1610612757,
    "Sacramento Kings": 1610612758,
    "San Antonio Spurs": 1610612759,
    "Toronto Raptors": 1610612761,
    "Utah Jazz": 1610612762,
    "Washington Wizards": 1610612764}
    
# -------------------------------
# SCORECARD DISPLAY
# -------------------------------

    # ---------- CREATE GANE INFO/SCORE ROW ----------
    st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
    col_away, col_info, col_home = st.columns([4, 2, 4])

    # ---------- AWAY COLUMN ----------
    with col_away:
        logo_id = team_ids.get(away_name)
        logo_url = f"https://cdn.nba.com/logos/nba/{logo_id}/global/L/logo.svg" if logo_id else ""
   
        st.markdown(f"""
       <div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>
           <img src='{logo_url}' width='90'>
           <h3>{away_name}</h3>
           <h1 style='color:{away_color}'>{away_score}</h1>
       </div>
   """, unsafe_allow_html=True)

    # ---------- GAME INFO COLUMN ----------
    with col_info:
        st.markdown("<div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center'>@</h2>", unsafe_allow_html=True)
        
        # Status text
        # ---------- Determine game status ----------
        if scores and isinstance(scores, list) and sum(int(s.get("score") or 0) for s in scores) > 0:
    # Game has started
            is_final = "Final" in status_text_raw
            is_live = not is_final
            status_text = "🏁 FINAL" if is_final else status_text_raw  # e.g., "Q3 05:23" or "Half"
        else:
    # Game has not started yet
            is_final = False
            is_live = False
            status_text = f"Starts at {time_only_str}"
        st.markdown(f"<div style='text-align:center'><h4>{status_text}</h4></div>", unsafe_allow_html=True)
    # ---------- HOME COLUMN ----------
    with col_home:
        logo_id = team_ids.get(home_name)
        logo_url = f"https://cdn.nba.com/logos/nba/{logo_id}/global/L/logo.svg" if logo_id else ""
   
        st.markdown(f"""
       <div style='display:flex; flex-direction:column; align-items:center; text-align:center;'>
           <img src='{logo_url}' width='90'>
           <h3>{home_name}</h3>
           <h1 style='color:{home_color}'>{home_score}</h1>
       </div>
   """, unsafe_allow_html=True)
       
    # ---------- CREATE TOTAL SCORE ROW ----------
    
    col_totalpoints = st.columns([1])
    with col_totalpoints[0]:
       st.markdown(f"<div style='text-align:center'><h3>Total points: {total_points}</h3></div>", unsafe_allow_html=True)
              
    # ---------- CREATE LIVE OVER/UNDER ROW ---------
    
    col_odds = st.columns([1])
    with col_odds[0]:
       st.markdown(f"<div style='text-align:center'><h3>{over_under_text}</h3></div>", unsafe_allow_html=True)

    st.divider()

