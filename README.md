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

## WebDriver Setup for Selenium

This project uses Selenium, which requires a WebDriver to interface with the chosen browser.

If you are using Google Chrome, download ChromeDriver from https://chromedriver.chromium.org/downloads. Ensure that you download the version that matches your Chrome browser version. Extract the downloaded file and place the `chromedriver` executable in a directory that is in your system's PATH.

## Setting Up ImageMagick for MoviePy

### Installation

MoviePy relies on ImageMagick for certain operations, such as creating text clips. Follow these steps to install ImageMagick and configure it for use with MoviePy:

Linux Mint (and Ubuntu-based distributions)

1. Install ImageMagick: Open a terminal and run:

```
sudo apt update
sudo apt install imagemagick
```

2. Verify Installation: Confirm that ImageMagick is installed correctly:

```
convert --version
```

### Configuring ImageMagick Security Policy

If you encounter an error related to ImageMagick's security policy when using MoviePy (e.g., convert-im6.q16: attempt to perform an operation not allowed by the security policy), follow these steps:

Edit the Policy File:
Open ImageMagick's policy file in a text editor with root privileges:

```
sudo nano /etc/ImageMagick-6/policy.xml
```

For ImageMagick-7, the path might be /etc/ImageMagick-7/policy.xml.

Modify the Policy:
Locate the line:

```
<policy domain="path" rights="none" pattern="@*" />
```

Comment it out by adding <!-- and -->:

```
<!-- <policy domain="path" rights="none" pattern="@*" /> -->
```

Save and Exit:
Save the file and exit the editor (in nano: Ctrl + X, then Y, and Enter).

### Security Consideration

Modifying ImageMagick's security policy can have implications. Ensure you understand these changes and only apply them if necessary for your project's functionality.

## Generating Table Images with imgkit and wkhtmltoimage

For creating highlight videos with statistical overlays, our tool uses \`imgkit\`, a Python library, to convert HTML tables into images. \`imgkit\` requires \`wkhtmltoimage\`, which is a command-line tool to render HTML into images and PDFs.

### Installation

Follow these steps to set up \`imgkit\` and \`wkhtmltoimage\`:

#### Install imgkit

\`imgkit\` is a Python package and can be installed via pip. In your terminal, run:

```bash
pip install imgkit
```

#### Install wkhtmltoimage

\`wkhtmltoimage\` needs to be installed separately.

-   **For Ubuntu/Linux Mint**:

```bash
sudo apt-get install wkhtmltopdf
```

This command installs both \ `wkhtmltopdf\` and \`wkhtmltoimage\`.

-   **For Other Operating Systems**:
    Visit the [wkhtmltopdf downloads page](https://wkhtmltopdf.org/downloads.html) to download and install it for your operating system. Ensure that \`wkhtmltoimage\` is installed and accessible in your system's PATH.

### Usage in the Project

In our project, \`imgkit\` is used to convert JSON data representing player statistics into a visually appealing HTML table. This table is then rendered as an image and overlaid on the final video to display statistics.

## Usage

To generate a highlight video:

```
python src/main.py --league NBA --date 2024-01-01
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
