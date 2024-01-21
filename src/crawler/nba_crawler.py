import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from common.utilities import fetch_html_content

load_dotenv()


def fetch_game_data(date):
    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{base_url}/games/?date={date}"
    try:
        response = fetch_html_content(url)
    except Exception as e:
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


def fetch_box_score_data(url):
    """
    Fetches the box score data from the given URL.
    Parameters:
    url (str): The URL to fetch the box score data from.
    Returns:
    str: The box score data as JSON, or None if the fetch fails.

    """
    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{base_url}{url}"
    print(f"Fetching box score data from: {url}")
    try:
        response = fetch_html_content(url)
        if response:
            print("Fetched Box Score HTML content successfully.")
        else:
            print("Failed to fetch Box Score HTML content.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    data = json.loads(script_tag.string if script_tag else "{}")

    box_score_data = []

    # Traverse the JSON to get to the 'cards' list
    props = data.get("props", {})
    page_props = props.get("pageProps", {})
    game_data = page_props.get("game", {})
    play_by_play_data = page_props.get("playByPlay", {})

    game_info = {
        "gameId": game_data.get("gameId"),
        "period": game_data.get("period"),
        "homeTeam": game_data.get("homeTeam"),
        "awayTeam": game_data.get("awayTeam"),
        "homeTeamPlayers": game_data.get("homeTeamPlayers"),
        "awayTeamPlayers": game_data.get("awayTeamPlayers"),
        "postgameCharts": game_data.get("postgameCharts"),
        "playByPlay": play_by_play_data,
    }
    box_score_data.append({"game": game_info})
    return box_score_data
