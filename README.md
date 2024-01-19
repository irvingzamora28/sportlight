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

## Project Structure

Sportlight is structured to ensure scalability and maintainability. Here is an overview of the project directory:

-   `src/`: Source code of the project.

    -   `main.py`: The main entry point for the Sportlight application. It orchestrates the workflow of the tool, including invoking the appropriate crawlers and the video generator based on user input or configurations.
    -   `crawler/`: Contains different modules for crawling various sports leagues.
    -   `video_generator/`: Handles the compilation and editing of videos.
    -   `common/`: Shared resources like constants and utility functions.
    -   `schemas/`: Definitions of data models and schemas.

-   `tests/`: Test suites for different components of the project.
-   `.env`: Environment variables for configuration.
-   `requirements.txt`: Required Python packages.
-   `README.md`: Documentation and guidelines.

Each module is designed to function independently, allowing for easy updates and addition of new features or leagues.

The desired project structure is the following:

```
Sportlight/
│
├── src/
│ ├── main.py # Main entry point of the application
│ ├── crawler/
│ │ ├── **init**.py
│ │ ├── nba_crawler.py
│ │ ├── nfl_crawler.py
│ │ ├── mlb_crawler.py
│ │ ├── liga_mx_crawler.py
│ │ └── ... (other league crawlers as needed)
│ │
│ ├── video_generator/
│ │ ├── **init**.py
│ │ ├── video_editor.py
│ │ └── score_integrator.py
│ │
│ ├── common/
│ │ ├── **init**.py
│ │ ├── constants.py
│ │ └── utils.py
│ │
│ └── schemas/
│ ├── **init**.py
│ └── data_models.py
│
├── tests/
│ ├── crawler_tests/
│ ├── video_generator_tests/
│ └── common_tests/
│
├── .env
├── requirements.txt
└── README.md
```

The main workflow is:

1. Crawl data from league APIs/websites using appropriate crawler module.
2. Extract scores, videos, stats using schemas from common/schemas.
3. Pass extracted data to video generator to compile highlight video.
4. Save final video file.

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
