# Sportlight: Sports Highlight Video Generator

## Overview

Sportlight is an innovative project aimed at generating highlight videos from various sports leagues, including NBA, LigaMX, and eventually expanding to UEFA Champions League, Bundesliga, LaLiga, NFL, MLB, and more. This tool crawls league-specific pages, collects scores and video data, and creatively compiles this into engaging highlight reels.

## Features

-   **Data Extraction**: Crawlers for each league to fetch scores and videos.
-   **Video Generation**: Automated video editing to compile highlights.
-   **Data Storage**: Utilizing PyMongo and MongoDB for efficient data management.
-   **Scalability**: Easily adaptable to include new leagues and data sources.
-   **Maintainable Architecture**: Modular design for easy updates and maintenance.

## Setup and Requirements

-   Python 3.x
-   Libraries:
    -   requests
    -   BeautifulSoup
    -   dotenv
    -   moviepy
    -   pymongo
    -   pandas
    -   matplotlib
    -   seaborn
    -   scipy>=1.4.1
    -   torch, torchvision, torchaudio (for CPU version)
    -   PyQt5 for GUI development
-   MongoDB database setup for data storage.
-   .env file for API, base URLs, and database connection strings.
-   FFmpeg for video processing (See FFmpeg installation guide below).
-   OpenCV for computer vision tasks like object detection.
-   Installation of Python Libraries:

```bash
pip install requests BeautifulSoup dotenv moviepy pymongo pandas matplotlib seaborn
pip install 'scipy>=1.4.1'
pip install PyQt5 pyqt5-tools opencv-python
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## MongoDB and PyMongo Setup

Sportlight uses MongoDB, a NoSQL database, to store and manage data efficiently, and PyMongo, the Python driver for MongoDB. Follow these steps for setting up MongoDB and integrating it with the project:

1. Install MongoDB: Follow the instructions on the [MongoDB Official Website](https://www.mongodb.com/try/download/community) to install MongoDB on your system or set up a cloud-based instance using MongoDB Atlas.

2. Install PyMongo: Use pip to install PyMongo, which allows your Python application to interact with MongoDB.

```
pip install pymongo
```

3. Configure MongoDB Connection: Update your .env file or configuration module with the MongoDB connection string.

4. Use MongoDB for Data Operations: Implement data-related functions using PyMongo in the project.

## FFmpeg Installation

Sportlight requires FFmpeg for video processing tasks. Follow these steps to install FFmpeg on your system:

### Linux Mint (Debian Edition)

1. Open the Terminal.
2. Update your package list:
    ```
    sudo apt-get update
    ```
3. Install FFmpeg:
    ```
    sudo apt-get install ffmpeg
    ```
4. Verify the installation by checking the version of FFmpeg:
    ```
    ffmpeg -version
    ```

For other operating systems, please visit the [FFmpeg official website](https://ffmpeg.org/download.html) for installation instructions.

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

## Usage of OpenCV

OpenCV (Open Source Computer Vision Library) is an open-source computer vision and machine learning software library. It's a key library for computer vision tasks and is used extensively in real-world applications and projects.

### Purpose of OpenCV in This Project

In this project, OpenCV is utilized for processing and analyzing video frames. We use it to detect and track the basketball in video footage by analyzing each frame for color and shape patterns that match a basketball. OpenCV provides robust tools for image transformation, contour detection, and color space conversion, which are crucial for the detection algorithm.

### Installation Instructions

To run the scripts in this project, you need to have OpenCV installed in your Python environment. You can install OpenCV using pip, which is the Python package installer. Follow these steps to install:

1. Open your command line interface (CLI).
2. Ensure that you have Python and pip installed on your system. You can check this by running `python --version` and `pip --version` in the CLI.
3. Install the OpenCV Python package by running the following command:

```bash
pip install opencv-python
```

4. Once the installation is complete, you can verify it by running `pip show opencv-python` in the CLI, which will display information about the installed package.

After installing OpenCV, you can run the scripts included in this project to detect and track the basketball in the provided video footage.

## Usage of PyQt for GUI Development

PyQt is a set of Python bindings for the Qt application framework and runs on all platforms supported by Qt including Windows, macOS, Linux, iOS, and Android. PyQt is used in this project to create a user-friendly GUI for manual adjustment and verification of basketball positions in video frames.

### Installation Instructions

To set up the PyQt environment for this project, follow these steps:

1. Open your command line interface (CLI).
2. Install PyQt5 using pip:

```bash
pip install PyQt5
```

3. Verify the installation:

```bash
pip show PyQt5
```

This will display information about the installed PyQt package.

### Usage in the Project

In our project, \`imgkit\` is used to convert JSON data representing player statistics into a visually appealing HTML table. This table is then rendered as an image and overlaid on the final video to display statistics.

## Usage

To generate a highlight video:

```
python src/main.py --league NBA --date 2024-01-01
```

## Running Tests

This project uses Python's built-in \`unittest\` framework for automated testing.

To run all tests, navigate to the root directory of this project and execute the following command:

```bash
python -m unittest discover -s tests
```

This command will discover and run all test cases in the \`tests\` directory.

## Future Enhancements

-   AI-based video selection for most exciting moments.
-   Customizable video templates for different leagues.
-   Social media integration for direct sharing.

## TODO

-   [ ] Debug, when fetching videos from table row in headless mode, it gets an error
-   [ ] Allow customizing player/team logos and colors for stats table creation
-   [ ] In decisively close games in the end, include the latests plays until the game ends
-   [ ] Add caching for downloaded media files to avoid redundant downloads
-   [ ] Allow creating player video highlights for various games throughout a season
-   [ ] Add support for multiple video templates that can be selected (portrait, landscape etc.)
-   [ ] Add support for additional sports leagues beyond NBA

## Contribution Guidelines

-   Follow PEP8 standards for Python code.
-   Write modular, well-documented code.
-   Test new features thoroughly before integration.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
