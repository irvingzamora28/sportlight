import argparse
import json
import os
import sys
from PyQt5.QtWidgets import QApplication
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
from common.utilities import test_twitter
from common.utilities import clean_basketball_coordinates
from common.utilities import write_to_file
from common.video_editor import VideoEditor
from common.utilities import json_stats_to_html_image
from common.image_utilities import ImageUtilities
from common.image_processor import ImageProcessor
from common.logger import logger
from common.video_player import VideoPlayer
from common.video_gui import BasketballVideoGUI
from PIL import Image, ImageDraw, ImageFont

import io

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


def process_game_data(
    game_data,
    date,
    special_keywords,
    players,
    words_to_exclude,
    keywords,
    max_games=None,
    team=None,
):
    for idx, game_card in enumerate(game_data):
        write_to_file(game_card, f"{OUTPUT_NBA_DIR}/game_card_{idx}.json")
        if max_games is not None and idx >= max_games:
            break
        actions_path = ["gameCard", "actions"]
        game_data_processor = GameDataProcessor([game_card])
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
        logger.console(f"Words to exclude: {words_to_exclude}")
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
        if team is not None:
            if game_slug.find(team) == -1 and game_id.find(team) == -1:
                continue
                
        box_score_url = game_data_processor.get_box_score_url(actions)
        box_score_data = fetch_box_score_data(box_score_url)
        filename = f"{OUTPUT_NBA_DIR}/raw/nba_box_score_{game_slug}_{date}.json"
        logger.console(f"Saving box score data to {filename}")
        # Write data to file
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(box_score_data, file, ensure_ascii=False, indent=4)
        logger.console(f"Data nba_box_score saved to {filename}")

        # If players is empty, get key players
        if not players:
            # Get key players
            box_score_data_processor = BoxScoreDataProcessor(box_score_data)
            key_players = box_score_data_processor.get_key_players(game_tags)
            # Print key players
            for player in key_players:
                logger.console(f"{player['familyName']}")
            lead_stats_players = box_score_data_processor.get_lead_stats_players()
            all_key_players = PlayerDataUtils.combine_players(
                "personId", key_players, lead_stats_players
            )

        all_players_lastnames = PlayerDataUtils.get_players_lastnames(all_key_players)
        logger.console(f"All players lastnames: {all_players_lastnames}")
        play_by_play_url = game_data_processor.get_play_by_play_url(actions)
        logger.console(
            f"Looking for special_keywords in play by play: {special_keywords}"
        )
        play_by_play_data = fetch_game_play_by_play_data(
            play_by_play_url,
            special_keywords,
            all_players_lastnames,
            words_to_exclude,
            keywords,
        )

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

        directory = f"{OUTPUT_NBA_VIDEOS_DIR}/{date}/{game_slug}"
        video_paths = get_files_in_directory(directory)
        VideoEditor.create_highlight_video(
            video_paths, f"{OUTPUT_NBA_VIDEOS_DIR}/{date}/{game_slug}", box_score_data
        )


def handle_nba(
    league, date, special_keywords, players, words_to_exclude, keywords, max_games, team
):
    try:
        init_directories(date)
        game_data = fetch_game_data(date)
        if game_data:
            process_game_data(
                game_data,
                date,
                special_keywords,
                players,
                words_to_exclude,
                keywords,
                max_games,
                team
            )
        else:
            logger.console("No game data found")
    except Exception as e:
        logger.error(f"Error processing {league} data: {e}")


def main(
    league, date, special_keywords, players, words_to_exclude, keywords, max_games, team
):
    if league.upper() == "NBA":
        input_video = "/home/irving/webdev/irving/sportlight/output/nba/videos/175_06:28_James 2' Running Dunk .mp4"
        # imageprocessor = ImageProcessor()

        # READ BASKETBALL_DETECTIONS
        # basketball_detections_filename = (
        #     os.path.basename(input_video).split(".")[0] + "_detections.json"
        # )
        # basketball_detections = {}

        # with open(basketball_detections_filename) as f:
        #     basketball_detections_data = json.load(f)
        #     basketball_detections = {
        #         int(k): v for k, v in basketball_detections_data.items()
        #     }
        # logger.console(
        #     f"Loaded {len(basketball_detections)} basketball frame detections from {basketball_detections_filename}"
        # )
        # logger.console(basketball_detections)

        # cleaned_coordinates = clean_basketball_coordinates(basketball_detections)
        # logger.console(cleaned_coordinates)

        # gui = BasketballVideoGUI(
        #     input_video, cleaned_coordinates, basketball_detections_filename
        # )
        # gui.run()

        # handle_nba(
        #     league,
        #     date,
        #     special_keywords,
        #     players,
        #     words_to_exclude,
        #     keywords,
        #     max_games,
        #     team
        # )
        
        imageUtilities = ImageUtilities()
        
        input_dir = "resources/image/nba/min/"
        output_dir = "resources/image/nba/min/"
        imageUtilities.make_image_transparent(input_dir, output_dir)


        
        # DETECT BASKETBALL
        # basketball_detections = imageprocessor.detect_video_basketball(input_video)
        # basketball_detections = imageprocessor.detect_video_basketball_pytorch(
        #     input_video
        # )
        # imageprocessor.display_x_coord_line_on_video(input_video, basketball_detections)

        # I need to store the basketball_detections in a json file named with the same name as the input video
        # basketball_detections_filename = (
        #     os.path.basename(input_video).split(".")[0] + "_detections.json"
        # )
        # # Write detections to json file
        # with open(basketball_detections_filename, "w") as f:
        #     json.dump(basketball_detections, f, indent=4)

        # logger.console(f"Detected {len(basketball_detections)} basketball frames")
        # logger.console(f" basketball detections: {basketball_detections}")
        # VideoEditor.edit_video(
        #     input_video,
        #     f"{OUTPUT_NBA_VIDEOS_DIR}/video_transition_yolov5175_06:28_James 2' Running Dunk.mp4",
        #     basketball_detections,
        # )
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
        "--special_keywords",
        nargs="*",
        default=["dunk"],
        help="Specify an array of special_keywords. Special keywords are used to filter play-by-play data for videos. Videos will be downloaded if the play-by-play text contains any of the special keywords",
    )
    parser.add_argument(
        "--keywords",
        nargs="*",
        default=["dunk"],
        help="Specify an array of keywords. Keywords are used to filter play-by-play data, these are used in conjuction with players names to select videos to download.",
    )
    parser.add_argument(
        "--players",
        nargs="*",
        default=[],
        help="Specify an array of player names. Player names are used in conjuction with keywords to select videos to download.",
    )
    parser.add_argument(
        "--words_to_exclude",
        nargs="*",
        default=[],
        help="Specify an array of words to exclude from the play-by-play text search. Videos will NOT be downloaded if the play-by-play text contains any of the excluded words.",
    )
    parser.add_argument(
        "--max_games",
        type=int,
        default=None,
        help="Specify the maximum number of games to process",
    )
    
    parser.add_argument(
        "--team",
        type=str,
        default=None,
        help="Specify the team slug or the game id to process",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(
        args.league,
        args.date,
        args.special_keywords,
        args.players,
        args.words_to_exclude,
        args.keywords,
        args.max_games,
        args.team
    )
