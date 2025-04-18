# Prereqs: python3 and pip3 install requests pytz

import requests
from datetime import datetime, timedelta
import pytz

# ----- CONFIGURATION -----
ESTIMATED_DURATIONS = {
    "Orioles": timedelta(hours=3),
    "Ravens": timedelta(hours=3.5),
}

TZ = pytz.timezone("America/New_York")
today = datetime.now(TZ).date()
end_date = today + timedelta(days=20)

def send_to_discord(message):
    try:
        with open("webhook.txt", "r") as f:
            webhook_url = f.read().strip()
    except FileNotFoundError:
        print("webhook.txt not found!")
        return

    payload = {
        "content": message
    }
    response = requests.post(webhook_url, json=payload)

    if response.status_code != 204:
        print(f"Failed to send Discord message: {response.status_code} - {response.text}")
    else:
        print("✅ Discord message sent.")

def is_game_of_interest(game_dt, team):
    if game_dt.weekday() >= 5:  # Saturday or Sunday
        return False

    estimated_end = game_dt + ESTIMATED_DURATIONS[team]
    end_time = estimated_end.time()

    return (datetime.strptime("15:30", "%H:%M").time() <= end_time <= datetime.strptime("17:30", "%H:%M").time())

def fetch_orioles_games():
    team_id = 110  # Orioles
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={end_date}&gameTypes=R"
    response = requests.get(url)
    data = response.json()

    games = []
    for date_info in data.get("dates", []):
        for game in date_info["games"]:
            if game["teams"]["home"]["team"]["id"] != team_id:
                continue  # Not a home game

            game_dt = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc).astimezone(TZ)
            if is_game_of_interest(game_dt, "Orioles"):
                games.append(f"⚾ Orioles home game on {game_dt.strftime('%A %Y-%m-%d %I:%M %p')} (est. end: {(game_dt + ESTIMATED_DURATIONS['Orioles']).strftime('%I:%M %p')})")

    return games

def fetch_ravens_games():
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/bal/schedule"
    response = requests.get(url)
    data = response.json()

    games = []
    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue

        comp = competitions[0]
        home_team = comp.get("competitors", [])[0] if comp.get("competitors") else {}

        if not home_team.get("home", False):
            continue

        game_dt = datetime.strptime(event["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc).astimezone(TZ)
        if not (today <= game_dt.date() <= end_date):
            continue

        if is_game_of_interest(game_dt, "Ravens"):
            games.append(f"🏈 Ravens home game on {game_dt.strftime('%A %Y-%m-%d %I:%M %p')} (est. end: {(game_dt + ESTIMATED_DURATIONS['Ravens']).strftime('%I:%M %p')})")

    return games

# Main logic
orioles_games = fetch_orioles_games()
ravens_games = fetch_ravens_games()
all_games = orioles_games + ravens_games

if all_games:
    message = "**📅 Upcoming Orioles/Ravens Home Games Ending 3:30–5:30 PM (Mon–Fri):**\n\n" + "\n".join(all_games)
    send_to_discord(message)
else:
    print("No games of interest this week.")
