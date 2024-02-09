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


def init_directories(date):
    # Create output/nba directory if it doesn't exist
    output_dir = "output"
    os.makedirs(os.path.join(output_dir, "nba"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "nba", "raw"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "nba", "videos", date), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "tests"), exist_ok=True)


def main(league, date):
    if league.upper() == "NBA":
        try:
            init_directories(date)
            game_data = fetch_game_data(date)

            output_dir = "output/nba"

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/raw/nba_games_{date}.json"

            # Write data to file
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(game_data, file, ensure_ascii=False, indent=4)

            logger.console(f"Data saved to {filename}")

            # Process only the first game card as an example
            if game_data:
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
                play_by_play_data = fetch_game_play_by_play_data(
                    play_by_play_url, ["reverse"]
                )

                for event_data in play_by_play_data:
                    for event_data_video_url in event_data.get("video_urls", []):
                        logger.console(
                            f"Starting download play-by-play event video url: {event_data_video_url}"
                        )
                        VideoDownloader.download_video(
                            event_data_video_url,
                            f"{output_dir}/videos/{game_slug}",
                            f"{event_data['pos']}_{event_data['clock']}_{event_data['title']}.mp4",
                        )
                # box_score_url = game_data_processor.get_box_score_url(actions)
                # box_score_data = fetch_box_score_data(box_score_url)
                # filename = f"{output_dir}/raw/nba_box_score_{date}.json"
                # # # Write data to file
                # with open(filename, "w", encoding="utf-8") as file:
                #     json.dump(box_score_data, file, ensure_ascii=False, indent=4)
                # logger.console(f"Data saved to {filename}")

                # directory = f"output/nba/videos/{game_slug}"
                # video_paths = get_files_in_directory(directory)
                # VideoEditor.create_highlight_video(
                #     video_paths, f"{output_dir}/videos/{game_slug}", box_score_data
                # )

                # game_data_processor = BoxScoreDataProcessor(box_score_data)
                # key_players = game_data_processor.get_key_players(game_tags)
                # lead_stats_players = game_data_processor.get_lead_stats_players()
                # all_key_players = PlayerDataUtils.combine_players(
                #     "personId", key_players, lead_stats_players
                # )

                # for key_player in all_key_players:
                #     logger.console(
                #         f"Fetching player video for {key_player['firstName']} {key_player['familyName']}"
                #     )
                #     video_urls = fetch_game_player_video_data(
                #         game_id, key_player["personId"], key_player["teamId"]
                #     )
                #     logger.console(f"Video URLs:")
                #     for video_url in video_urls:
                #         logger.console(video_url)
                #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                #         VideoDownloader.download_video(
                #             video_url,
                #             f"{output_dir}/videos",
                #             f"{key_player['firstName']}_{key_player['familyName']}_{timestamp}.mp4",
                #         )
            else:
                logger.console("No game data found")

        except Exception as e:
            logger.error(f"Error: {e}")
    else:
        logger.console(f"Currently, we only support NBA. You entered: {league}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sportlight Application")
    parser.add_argument(
        "--league", required=True, help="Specify the league (e.g., NBA)"
    )
    parser.add_argument(
        "--date", required=True, help="Specify the date in YYYY-MM-DD format"
    )

    args = parser.parse_args()
    main(args.league, args.date)
