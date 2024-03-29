import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from common.utilities import fetch_html_content
from common.utilities import fetch_dynamic_html_content
from common.utilities import fetch_video_urls_from_table
from common.utilities import fetch_play_videos_from_play_by_play_table
from common.logger import logger

load_dotenv()


def fetch_game_data(date):
    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{base_url}/games/?date={date}"
    try:
        response = fetch_html_content(url)
        if response:
            print("Fetched games HTML content successfully.")
            # Write response to a file with the date
            filename = f"nba-games-{date}.html"
            with open(f"output/tests/{filename}", "w", encoding="utf-8") as file:
                file.write(response.text)
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


def fetch_game_player_video_data(
    game_id, player_id, team_id, context_measure="FGM", end_range=28800
):
    """
    Fetches the player video data for a given player ID.

    Parameters:
        game_id (str): The Game ID to fetch video data for.
        player_id (str): The player ID to fetch video data for.
        team_id (str): The team ID associated with the player.
        context_measure (str): Context measure for the query. Defaults to 'FGM'.
        end_range (int): End range for the query. Defaults to 28800.

    Returns:
        list: A list of video URLs extracted from the player stats page HTML.
    """
    season = os.getenv("NBA_SEASON")
    season_type = os.getenv("NBA_SEASONTYPE")

    if not season or not season_type:
        raise ValueError(
            "Season and SeasonType must be set in the environment variables."
        )

    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = (
        f"{base_url}/stats/events?"
        f"CFID=&CFPARAMS=&ContextMeasure={context_measure}&EndPeriod=0&"
        f"EndRange={end_range}&GameID={game_id}&PlayerID={player_id}&RangeType=0&"
        f"Season={season}&SeasonType={season_type}&StartPeriod=0&StartRange=0&"
        f"TeamID={team_id}&flag=3&sct=plot&section=game"
    )

    try:
        video_urls = fetch_video_urls_from_table(
            url,
            "Crom_table__p1iZz",
            "EventsTable_row__Gs8B9",
            "vjs_video_3_html5_api",
            ["dunk"],
        )
        if video_urls:
            return video_urls
        else:
            print("Failed to fetch player video HTML content.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


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


def fetch_game_play_by_play_data(
    url, special_keywords=None, players=None, words_to_exclude=None, keywords=None
):
    """
    Fetches the play-by-play data from the given URL.
    Parameters:
    url (str): The URL to fetch the play-by-play data from.
    special_keywords (list[str], optional): List of special keywords to match rows, these will override normal keyword matching.
    players (list[str], optional): List of player names to filter the rows.
    words_to_exclude (list[str], optional): List of words to exclude from row text matching.
    keywords (list): A list of keywords to filter the play-by-play events. Defaults to None.
    Returns:
    list: A list of play-by-play events extracted from the box score page HTML.
    """
    base_url = os.getenv("NBA_BASE_URL")
    if not base_url:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{base_url}{url}"
    print(f"Fetching play-by-play data from: {url}")
    try:
        play_by_play_data = fetch_play_videos_from_play_by_play_table(
            url,
            "GamePlayByPlay_hasPlays__LgdnK",
            "GamePlayByPlayRow_article__asoO2",
            "GamePlayByPlay_tab__BboK4",
            special_keywords,
            players,
            words_to_exclude,
            keywords,
        )
        if play_by_play_data:
            for event_data in play_by_play_data:
                logger.console(f"Processing event: {event_data['title']}")
                video_urls = fetch_video_urls_from_table(
                    event_data["page_url"],
                    "Crom_table__p1iZz",
                    "EventsTable_row__Gs8B9",
                    "vjs_video_3_html5_api",
                )
                if video_urls:
                    event_data["video_urls"] = video_urls
            return play_by_play_data
        else:
            print("Failed to fetch play-by-play data.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
