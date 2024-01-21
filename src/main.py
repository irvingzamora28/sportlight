import argparse
import json
import os
from datetime import datetime
from crawler.nba_crawler import fetch_game_data
from crawler.nba_crawler import fetch_box_score_data
from crawler.nba_crawler import fetch_game_player_video_data
from data_processor.nba.game_data_processor import GameDataProcessor
from data_processor.nba.box_score_data_processor import BoxScoreDataProcessor
from common.player_data_utilities import PlayerDataUtils
from common.video_downloader import VideoDownloader


def init_directories():
    # Create output/nba directory if it doesn't exist
    output_dir = "output"
    os.makedirs(os.path.join(output_dir, "nba"), exist_ok=True)
    # Create output/nba/raw directory if it doesn't exist
    os.makedirs(os.path.join(output_dir, "nba", "raw"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "tests"), exist_ok=True)


def main(league, date):
    if league.upper() == "NBA":
        try:
            init_directories()
            game_data = fetch_game_data(date)

            output_dir = "output/nba"

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/raw/nba_games_{date}.json"

            # Write data to file
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(game_data, file, ensure_ascii=False, indent=4)

            print(f"Data saved to {filename}")

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
                print(f"Game ID: {game_id}")
                box_score_url = game_data_processor.get_box_score_url(actions)
                box_score_data = fetch_box_score_data(box_score_url)
                filename = f"{output_dir}/raw/nba_box_score_{date}.json"
                # Write data to file
                with open(filename, "w", encoding="utf-8") as file:
                    json.dump(box_score_data, file, ensure_ascii=False, indent=4)
                print(f"Data saved to {filename}")

                game_data_processor = BoxScoreDataProcessor(box_score_data)
                key_players = game_data_processor.get_key_players(game_tags)
                lead_stats_players = game_data_processor.get_lead_stats_players()
                all_key_players = PlayerDataUtils.combine_players(
                    "personId", key_players, lead_stats_players
                )

                first_key_player = all_key_players[0]
                print(
                    f"Fetching player video for {first_key_player['firstName']} {first_key_player['familyName']}"
                )
                video_urls = fetch_game_player_video_data(
                    game_id, first_key_player["personId"], first_key_player["teamId"]
                )
                print(f"Video URLs:")
                for video_url in video_urls:
                    print(video_url)
                    VideoDownloader.download_video(video_url, f"{output_dir}/videos")
            else:
                print("No game data found")

        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Currently, we only support NBA. You entered: {league}")


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
