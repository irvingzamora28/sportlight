import argparse
from crawler.nba_crawler import fetch_nba_html


def main(league, date):
    if league.upper() == "NBA":
        try:
            html_content = fetch_nba_html(date)
            print(html_content)  # For now, just print the fetched HTML
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
