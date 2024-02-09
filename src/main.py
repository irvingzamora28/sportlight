import argparse
import json
import os
from datetime import datetime
from crawler.nba_crawler import fetch_game_data
from crawler.nba_crawler import fetch_box_score_data
from crawler.nba_crawler import fetch_game_player_video_data
from crawler.nba_crawler import fetch_game_play_by_play_data
from data_processor.nba.game_data_processor import GameDataProcessor
from data_processor.nba.box_score_data_processor import BoxScoreDataProcessor
from common.player_data_utilities import PlayerDataUtils
from common.video_downloader import VideoDownloader
from common.utilities import get_files_in_directory
from common.video_editor import VideoEditor
from common.utilities import json_stats_to_html_image
from common.logger import logger

OUTPUT_DIR = "output"
NBA_DIR = "nba"
RAW_DIR = "raw"
VIDEOS_DIR = "videos"
TESTS_DIR = "tests"
OUTPUT_NBA_DIR = f"{OUTPUT_DIR}/{NBA_DIR}"
OUTPUT_NBA_VIDEOS_DIR = f"{OUTPUT_DIR}/{NBA_DIR}/{VIDEOS_DIR}"


def init_directories(date):
    os.makedirs(os.path.join(OUTPUT_DIR, NBA_DIR), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, NBA_DIR, RAW_DIR), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, NBA_DIR, VIDEOS_DIR, date), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, TESTS_DIR), exist_ok=True)


def process_game_data(game_data, date, keywords):
    first_game_card = game_data[0]
    actions_path = ["gameCard", "actions"]
    game_data_processor = GameDataProcessor([first_game_card])
    actions = game_data_processor.get_actions(actions_path)
    tags_path = [
        "gameCard",
        "hero_configuration",
        "gameRecap",
        "taxonomy",
        "tags",
    ]
    game_tags = game_data_processor.get_game_tags(tags_path)
    game_id = game_data_processor.get_game_id()
    logger.console(f"Game ID: {game_id}")
    game_slug = game_data_processor.get_game_slug(
        [
            "gameCard",
            "hero_configuration",
            "gameRecap",
            "taxonomy",
            "games",
        ]
    )
    logger.console(f"Game slug: {game_slug}")
    play_by_play_url = game_data_processor.get_play_by_play_url(actions)
    logger.console(f"Looking for keywords in play by play: {keywords}")
    play_by_play_data = fetch_game_play_by_play_data(play_by_play_url, keywords)

    for event_data in play_by_play_data:
        for event_data_video_url in event_data.get("video_urls", []):
            logger.console(
                f"Starting download play-by-play event video url: {event_data_video_url}"
            )
            VideoDownloader.download_video(
                event_data_video_url,
                f"{OUTPUT_NBA_VIDEOS_DIR}/{date}/{game_slug}",
                f"{event_data['pos']}_{event_data['clock']}_{event_data['title']}.mp4",
            )

    box_score_url = game_data_processor.get_box_score_url(actions)
    box_score_data = fetch_box_score_data(box_score_url)
    filename = f"{OUTPUT_NBA_DIR}/raw/nba_box_score_{date}.json"
    logger.console(f"Saving box score data to {filename}")
    # # Write data to file
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(box_score_data, file, ensure_ascii=False, indent=4)
    logger.console(f"Data nba_box_score saved to {filename}")

    directory = f"{OUTPUT_NBA_VIDEOS_DIR}/{date}/{game_slug}"
    video_paths = get_files_in_directory(directory)
    VideoEditor.create_highlight_video(
        video_paths, f"{OUTPUT_NBA_VIDEOS_DIR}/{date}/{game_slug}", box_score_data
    )


def handle_nba(league, date, keywords):
    try:
        init_directories(date)
        game_data = fetch_game_data(date)
        if game_data:
            process_game_data(game_data, date, keywords)
        else:
            logger.console("No game data found")
    except Exception as e:
        logger.error(f"Error processing {league} data: {e}")


def main(league, date, keywords):
    if league.upper() == "NBA":
        handle_nba(league, date, keywords)
    else:
        logger.console(f"Currently, we only support NBA. You entered: {league}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Sportlight Application")
    parser.add_argument(
        "--league", required=True, help="Specify the league (e.g., NBA)"
    )
    parser.add_argument(
        "--date", required=True, help="Specify the date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--keywords",
        nargs="*",
        default=["dunk"],
        help="Specify an array of keywords",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.league, args.date, args.keywords)
