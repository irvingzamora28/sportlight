# main.py

import argparse


def main(league, date):
    print(f"League: {league}")
    print(f"Date: {date}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sportlight Application")
    parser.add_argument(
        "--league", required=True, help="Specify the league (e.g., NBA, NFL)"
    )
    parser.add_argument(
        "--date", required=True, help="Specify the date in YYYY-MM-DD format"
    )

    args = parser.parse_args()

    main(args.league, args.date)
