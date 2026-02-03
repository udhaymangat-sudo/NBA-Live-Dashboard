import requests
import streamlit as st
from datetime import datetime, timezone, timedelta
import pytz

# -------------------------------
# PAGE SETUP
# -------------------------------
st.set_page_config(page_title="🏀 Live NBA Scores", layout="centered")
today = datetime.today().strftime("%A, %B %d, %Y")

st.markdown(
    "<div style='text-align:center; font-size:50px; font-weight:bold;'>Today's NBA Games</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='text-align:center; font-size:30px; font-weight:bold;'>{today}</div>",
    unsafe_allow_html=True
)
st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
# -------------------------------
# API CALL
# -------------------------------
API_KEY = "a17a6e90cf7065d09edee849f3f80e98"
SPORT = "basketball_nba"
REGION = "espnbet"
MARKETS = "totals"

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&bookmakers={REGION}&markets={MARKETS}"
games = requests.get(url).json()

# -------------------------------
# TEAM ID MAP
# -------------------------------
team_ids = {
    "Atlanta Hawks": 1610612737, "Boston Celtics": 1610612738,
    "Brooklyn Nets": 1610612751, "Charlotte Hornets": 1610612766,
    "Chicago Bulls": 1610612741, "Cleveland Cavaliers": 1610612739,
    "Dallas Mavericks": 1610612742, "Denver Nuggets": 1610612743,
    "Detroit Pistons": 1610612765, "Golden State Warriors": 1610612744,
    "Houston Rockets": 1610612745, "Indiana Pacers": 1610612754,
    "LA Clippers": 1610612746, "Los Angeles Lakers": 1610612747,
    "Memphis Grizzlies": 1610612763, "Miami Heat": 1610612748,
    "Milwaukee Bucks": 1610612749, "Minnesota Timberwolves": 1610612750,
    "New Orleans Pelicans": 1610612740, "New York Knicks": 1610612752,
    "Oklahoma City Thunder": 1610612760, "Orlando Magic": 1610612753,
    "Philadelphia 76ers": 1610612755, "Phoenix Suns": 1610612756,
    "Portland Trail Blazers": 1610612757, "Sacramento Kings": 1610612758,
    "San Antonio Spurs": 1610612759, "Toronto Raptors": 1610612761,
    "Utah Jazz": 1610612762, "Washington Wizards": 1610612764
}

# -------------------------------
# DISPLAY GAMES (GREY BOX PER GAME)
# -------------------------------
for game in games:  # <-- everything must be inside this loop

    home_name = game["home_team"]
    away_name = game["away_team"]
    scores = game.get("scores")

    home_score = next((int(s["score"]) for s in scores if s["name"] == home_name), 0) if scores else 0
    away_score = next((int(s["score"]) for s in scores if s["name"] == away_name), 0) if scores else 0
    total_points = home_score + away_score

    status_text_raw = game.get("gameStatusText", "")
    is_final = "Final" in status_text_raw

    home_color = "green" if is_final and home_score > away_score else "black"
    away_color = "green" if is_final and away_score > home_score else "black"

    # Over / Under
    over_under_text = "N/A"
    for bm in game.get("bookmakers", []):
        for m in bm.get("markets", []):
            if m["key"] == "totals":
                o = next((x for x in m["outcomes"] if x["name"].lower() == "over"), None)
                if o:
                    over_under_text = f"O/U: {o['point']} total points"

    # Game start time
    commence_utc = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
    pst = pytz.timezone("America/Los_Angeles")
    start_time = (commence_utc.astimezone(pst) - timedelta(minutes=10)).strftime("%I:%M %p")
    status_text = "🏁 FINAL" if is_final else status_text_raw or f"Starts at {start_time}"

    home_logo = team_ids.get(home_name)
    away_logo = team_ids.get(away_name)

    # -------------------------------
    # GREY BOX HTML
    # -------------------------------
    st.markdown(f"""
  <div style="
      background:#f2f2f2;
      padding:20px;
      border-radius:14px;
      margin-bottom:10px;
      box-shadow:0 6px 16px rgba(0,0,0,0.08);
  ">
      <div style="
          display:grid;
          grid-template-columns:4fr 2fr 4fr;
          text-align:center;
          align-items:center;
      ">
          <div>
              <img src="https://cdn.nba.com/logos/nba/{away_logo}/global/L/logo.svg" width="90">
              <h3>{away_name}</h3>
              <h1 style="color:{away_color}">{away_score}</h1>
          </div>
          <div>
              <h2>@</h2>
              <h4>{status_text}</h4>
          </div>
          <div>
              <img src="https://cdn.nba.com/logos/nba/{home_logo}/global/L/logo.svg" width="90">
              <h3>{home_name}</h3>
              <h1 style="color:{home_color}">{home_score}</h1>
          </div>
      </div>
      <div style="
        background:#f2f2f2;
        padding:10px;
        border-radius:0 0 14px 14px;
        margin-bottom:20px;
        text-align:center;
    ">
        <div style="border-top:1px solid #ccc; padding-top:10px;">
            <h3 style="margin:0;">Total points: {total_points}</h3>
            <h3 style="margin:0;">{over_under_text}</h3>
        </div>
  </div>
  """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)

