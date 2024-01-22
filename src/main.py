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


def init_directories():
    # Create output/nba directory if it doesn't exist
    output_dir = "output"
    os.makedirs(os.path.join(output_dir, "nba"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "nba", "raw"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "tests"), exist_ok=True)


def main(league, date):
    if league.upper() == "NBA":
        try:
            init_directories()
            # directory = "output/nba/videos"
            # video_paths = get_files_in_directory(directory)
            # stats_json = {
            #     "players": [
            #         {
            #             "personId": 1628384,
            #             "firstName": "OG",
            #             "familyName": "Anunoby",
            #             "nameI": "O. Anunoby",
            #             "statistics": {
            #                 "minutes": "35:01",
            #                 "reboundsOffensive": 3,
            #                 "reboundsDefensive": 3,
            #                 "reboundsTotal": 6,
            #                 "assists": 1,
            #                 "steals": 2,
            #                 "blocks": 0,
            #                 "turnovers": 1,
            #                 "foulsPersonal": 6,
            #                 "points": 17,
            #                 "plusMinusPoints": 19,
            #             },
            #         },
            #         {
            #             "personId": 203944,
            #             "firstName": "Julius",
            #             "familyName": "Randle",
            #             "nameI": "J. Randle",
            #             "statistics": {
            #                 "minutes": "36:19",
            #                 "reboundsOffensive": 3,
            #                 "reboundsDefensive": 6,
            #                 "reboundsTotal": 9,
            #                 "assists": 0,
            #                 "steals": 0,
            #                 "blocks": 0,
            #                 "turnovers": 6,
            #                 "foulsPersonal": 5,
            #                 "points": 39,
            #                 "plusMinusPoints": 2,
            #             },
            #         },
            #         {
            #             "personId": 1628392,
            #             "firstName": "Isaiah",
            #             "familyName": "Hartenstein",
            #             "nameI": "I. Hartenstein",
            #             "statistics": {
            #                 "minutes": "39:09",
            #                 "reboundsOffensive": 4,
            #                 "reboundsDefensive": 5,
            #                 "reboundsTotal": 9,
            #                 "assists": 3,
            #                 "steals": 3,
            #                 "blocks": 3,
            #                 "turnovers": 1,
            #                 "foulsPersonal": 3,
            #                 "points": 7,
            #                 "plusMinusPoints": 10,
            #             },
            #         },
            #         {
            #             "personId": 1628973,
            #             "firstName": "Jalen",
            #             "familyName": "Brunson",
            #             "nameI": "J. Brunson",
            #             "statistics": {
            #                 "minutes": "40:40",
            #                 "reboundsOffensive": 0,
            #                 "reboundsDefensive": 4,
            #                 "reboundsTotal": 4,
            #                 "assists": 14,
            #                 "steals": 1,
            #                 "blocks": 0,
            #                 "turnovers": 2,
            #                 "foulsPersonal": 4,
            #                 "points": 16,
            #                 "plusMinusPoints": 16,
            #             },
            #         },
            #         {
            #             "personId": 1628978,
            #             "firstName": "Donte",
            #             "familyName": "DiVincenzo",
            #             "nameI": "D. DiVincenzo",
            #             "statistics": {
            #                 "minutes": "25:37",
            #                 "reboundsOffensive": 1,
            #                 "reboundsDefensive": 3,
            #                 "reboundsTotal": 4,
            #                 "assists": 2,
            #                 "steals": 1,
            #                 "blocks": 1,
            #                 "turnovers": 1,
            #                 "foulsPersonal": 0,
            #                 "points": 15,
            #                 "plusMinusPoints": 15,
            #             },
            #         },
            #         {
            #             "personId": 1628404,
            #             "firstName": "Josh",
            #             "familyName": "Hart",
            #             "nameI": "J. Hart",
            #             "statistics": {
            #                 "minutes": "28:49",
            #                 "reboundsOffensive": 2,
            #                 "reboundsDefensive": 9,
            #                 "reboundsTotal": 11,
            #                 "assists": 2,
            #                 "steals": 0,
            #                 "blocks": 0,
            #                 "turnovers": 1,
            #                 "foulsPersonal": 2,
            #                 "points": 8,
            #                 "plusMinusPoints": -12,
            #             },
            #         },
            #     ]
            # }
            # Generate HTML table image from stats JSON
            # stats_image_path = "output/stats_image.png"
            # json_stats_to_html_image(stats_json, stats_image_path)
            # VideoEditor.create_highlight_video(
            #     video_paths, "output/final_highlight.mp4", stats_json
            # )
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
                game_slug = game_data_processor.get_game_slug(
                    [
                        "gameCard",
                        "hero_configuration",
                        "gameRecap",
                        "taxonomy",
                        "games",
                    ]
                )
                print(f"Game slug: {game_slug}")
                play_by_play_url = game_data_processor.get_play_by_play_url(actions)
                play_by_play_data = fetch_game_play_by_play_data(play_by_play_url)
                print(f"Play-by-play data fetched {play_by_play_data}")
                # box_score_data = fetch_box_score_data(box_score_url)
                # filename = f"{output_dir}/raw/nba_box_score_{date}.json"
                # # Write data to file
                # with open(filename, "w", encoding="utf-8") as file:
                #     json.dump(box_score_data, file, ensure_ascii=False, indent=4)
                # print(f"Data saved to {filename}")

                # game_data_processor = BoxScoreDataProcessor(box_score_data)
                # key_players = game_data_processor.get_key_players(game_tags)
                # lead_stats_players = game_data_processor.get_lead_stats_players()
                # all_key_players = PlayerDataUtils.combine_players(
                #     "personId", key_players, lead_stats_players
                # )

                # for key_player in all_key_players:
                #     print(
                #         f"Fetching player video for {key_player['firstName']} {key_player['familyName']}"
                #     )
                #     video_urls = fetch_game_player_video_data(
                #         game_id, key_player["personId"], key_player["teamId"]
                #     )
                #     print(f"Video URLs:")
                #     for video_url in video_urls:
                #         print(video_url)
                #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                #         VideoDownloader.download_video(
                #             video_url,
                #             f"{output_dir}/videos",
                #             f"{key_player['firstName']}_{key_player['familyName']}_{timestamp}.mp4",
                #         )
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
