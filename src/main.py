import argparse
import json
import os
from datetime import datetime
from crawler.nba_crawler import fetch_game_data
from data_processor.game_data_processor import GameDataProcessor


def main(league, date):
    if league.upper() == "NBA":
        try:
            game_data = fetch_game_data(date)

            # Create output directory if it doesn't exist
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/nba_games_{timestamp}.json"

            # Write data to file
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(game_data, file, ensure_ascii=False, indent=4)

            print(f"Data saved to {filename}")

            # Process only the first game card as an example
            if game_data:
                first_game_card = game_data[0]
                actions_path = ["gameCard", "actions"]
                processor = GameDataProcessor([first_game_card])
                actions = processor.get_actions(actions_path)
                print(actions)
                box_score_url = processor.get_box_score_url(actions)
                print(f"Box score URL: {box_score_url}")

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
