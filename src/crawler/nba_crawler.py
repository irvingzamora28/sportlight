import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def fetch_game_data(date):
    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{base_url}?date={date}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch data from {url}")

    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    data = json.loads(script_tag.string if script_tag else "{}")

    games_data = []

    # Traverse the JSON to get to the 'cards' list
    props = data.get("props", {})
    page_props = props.get("pageProps", {})
    game_card_feed = page_props.get("gameCardFeed", {})
    modules = game_card_feed.get("modules", [])

    # Assuming 'modules' is a list, we need to iterate over it to find 'cards'
    for module in modules:
        if "cards" in module:
            cards = module["cards"]
            for card in cards:
                card_data = card.get("cardData", {})
                game_info = {
                    "hero_configuration": card_data.get("heroConfiguration"),
                    "game_id": card_data.get("gameId"),
                    "home_team": card_data.get("homeTeam"),
                    "away_team": card_data.get("awayTeam"),
                    "images": card_data.get("images"),
                    "actions": card_data.get("actions"),
                }
                games_data.append({"gameCard": game_info})
    return games_data
