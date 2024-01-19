# nba_crawler.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_nba_html(date):
    if os.getenv("NBA_BASE_URL") is None:
        raise ValueError("NBA_BASE_URL is not set in the environment variables.")

    url = f"{os.getenv('NBA_BASE_URL')}?date={date}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        raise ConnectionError(f"Failed to fetch data from {url}")


if __name__ == "__main__":
    # Example usage
    html_content = fetch_nba_html("2024-01-01")
    print(html_content)
