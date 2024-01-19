# Sportlight: Sports Highlight Video Generator

## Overview

Sportlight is an innovative project aimed at generating highlight videos from various sports leagues, including NBA, LigaMX, and eventually expanding to UEFA Champions League, Bundesliga, LaLiga, NFL, MLB, and more. This tool crawls league-specific pages, collects scores and video data, and creatively compiles this into engaging highlight reels.

## Features

-   **Data Extraction**: Crawlers for each league to fetch scores and videos.
-   **Video Generation**: Automated video editing to compile highlights.
-   **Scalability**: Easily adaptable to include new leagues and data sources.
-   **Maintainable Architecture**: Modular design for easy updates and maintenance.

## Setup and Requirements

Python 3.x

Libraries: requests, BeautifulSoup, dotenv, moviepy (for video editing)
.env file for API and base URLs

## Getting Started

To set up Sportlight on your local machine:

```
git clone git@github.com:irvingzamora28/sportlight.git
cd sportlight
pip install -r requirements.txt
```

## Usage

To generate a highlight video:

```
python main.py --league NBA --date 2024-01-01
```

## Future Enhancements

-   AI-based video selection for most exciting moments.
-   Customizable video templates for different leagues.
-   Social media integration for direct sharing.

## Contribution Guidelines

-   Follow PEP8 standards for Python code.
-   Write modular, well-documented code.
-   Test new features thoroughly before integration.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
