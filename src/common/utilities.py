import regex
import requests
import urllib.parse
from common.logger import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
import os
import time
import imgkit
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
from parser.json_parser import JSONParser


def test_twitter():
    # Set up Chrome options
    options = Options()
    options.add_argument("--no-sandbox")  # This can help in a Linux environment
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # This can also help in a Linux environment

    # Enable performance logging
    perf_logging_prefs = {
        "enableNetwork": True,
        "enablePage": False,
    }
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_experimental_option("perfLoggingPrefs", perf_logging_prefs)

    # Initialize the driver with the appropriate options to access network logs
    driver = webdriver.Chrome(options=options)

    # Navigate to the Twitter page
    driver.get("https://twitter.com/Ballislife/status/1757227480111313193")

    # Wait for the necessary network requests to complete
    time.sleep(10)  # Adjust the sleep time as necessary

    # Retrieve the network logs
    logs = driver.get_log("performance")

    # Iterate through the logs to find the desired request payload
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            if "request" in log["params"] and "url" in log["params"]["request"]:
                url = log["params"]["request"]["url"]
                if url == "https://api.twitter.com/1.1/jot/client_event.json":
                    logger.info("Payload found:")
                    if "postData" in log["params"]["request"]:
                        # logger.info(log["params"]["request"]["postData"])
                        # This is the URL-encoded data you've captured
                        encoded_data = log["params"]["request"]["postData"]
                        # Decode the URL-encoded data
                        decoded_data = urllib.parse.unquote(encoded_data)

                        # The data appears to be in JSON format within the 'log' parameter, so parse it
                        parsed_data = urllib.parse.parse_qs(decoded_data)
                        json_data = json.loads(parsed_data["log"][0])

                        # Now, extract the media_asset_url from the JSON data
                        # Check if json_data[0] exists
                        if json_data and len(json_data) > 0:
                            if (
                                "items" in json_data[0]
                                and len(json_data[0]["items"]) > 0
                            ):
                                value = JSONParser.extract_value(
                                    json_data[0]["items"][0], ["media_asset_url"]
                                )
                                if value:
                                    logger.console(f"Video URL found: {value}")
                    else:
                        logger.info("No postData in this request")

    # Quit the driver
    driver.quit()


def get_files_in_directory(directory):
    """
    Gets all the files in the specified directory with their absolute paths.

    Parameters:
        directory (str): The directory path to list files from.

    Returns:
        list: A list of absolute file paths in the directory.
    """
    files = []
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            absolute_path = os.path.abspath(full_path)
            files.append(absolute_path)
    return files


def fetch_html_content(url):
    """
    Fetches the HTML content of the given URL using a simple HTTP request.

    Parameters:
        url (str): The URL to fetch the HTML content from.

    Returns:
        requests.Response: The response object, or None if the fetch fails.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            print(
                f"Failed to fetch page: {url} with status code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def fetch_dynamic_html_content(url, element_id, timeout=10, additional_wait_time=0):
    """
    Fetches the HTML content of a page with dynamic content (JavaScript loaded) using Selenium.

    Parameters:
        url (str): The URL to fetch the HTML content from.
        element_id (str): The ID of a specific element to wait for, indicating the page has loaded.
        timeout (int): Maximum time to wait for the element to load.
        additional_wait_time (int): Additional time to wait after the element is found, in seconds.

    Returns:
        str: The HTML content of the page after dynamic content is loaded, or None if an error occurs.
    """
    # Setup the WebDriver (this uses Chrome)
    driver = webdriver.Chrome()

    try:
        driver.get(url)

        # Wait for a specific element to be loaded
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, element_id))
        )

        # Optional: wait a bit more if needed
        time.sleep(additional_wait_time)

        # Get the page source after dynamic content is loaded
        html_content = driver.page_source
        return html_content
    except TimeoutException:
        print(f"Timeout while waiting for the element with ID {element_id} to load.")
        driver.quit()
        return []
    except WebDriverException as e:
        print(f"Web driver error: {e}")
        driver.quit()
        return []
    except Exception as e:
        print(f"Error fetching dynamic content: {e}")
        return None
    finally:
        driver.quit()


def fetch_video_urls_from_table(
    page_url,
    table_class,
    row_class,
    video_id,
    keywords=None,
    wait_time=5,
    additional_wait_time=5,
):
    """
    Fetches video URLs from a table on a web page using Selenium, with error handling.

    Parameters:
        page_url (str): URL of the page to load.
        table_class (str): Class of the table containing the video links.
        row_class (str): Class of the rows in the table to interact with.
        video_id (str): ID of the video element where the src is updated.
        keywords (list[str], optional): List of keywords to filter the rows.
        wait_time (int): Time in seconds to wait for the video to load after each click.
        additional_wait_time (int): Additional time to wait after the element is found, in seconds.

    Returns:
        list: A list of video URLs, or an empty list if an error occurs.
    """
    driver = webdriver.Chrome()

    try:
        driver.get(page_url)
        # Handling the cookie banner
        try:
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "onetrust-close-btn-handler")
                )
            )
            close_cookie_banner_button = driver.find_element(
                By.CLASS_NAME, "onetrust-close-btn-handler"
            )
            close_cookie_banner_button.click()
        except TimeoutException:
            print(
                "No cookie banner found or timeout occurred while waiting for cookie banner."
            )
        except NoSuchElementException:
            print("Cookie banner close button not found.")
        except Exception as e:
            print(f"Error while handling cookie banner: {e}")

        # Wait for the table to load after handling cookie banner
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, table_class))
        )
        # Optional: wait a bit more because sometimes the video takes time to load after clicking cookie banner
        time.sleep(additional_wait_time)
    except TimeoutException:
        print(f"Timeout while waiting for the table with class {table_class} to load.")
        driver.quit()
        return []
    except WebDriverException as e:
        print(f"Web driver error: {e}")
        driver.quit()
        return []

    video_urls = []
    try:
        video_rows = driver.find_elements(
            By.CSS_SELECTOR, f".{row_class}[data-has-video='true']"
        )
        for row in video_rows:
            # Check for keywords if provided
            if keywords and not any(
                keyword.lower() in row.text.lower() for keyword in keywords
            ):
                continue  # Skip this row if no keywords match

            clickable_element = row.find_element(
                By.CSS_SELECTOR, ".EventsTable_play__dtRDi"
            )
            ActionChains(driver).move_to_element(clickable_element).click().perform()
            time.sleep(1)
            video_url = driver.find_element(By.ID, video_id).get_attribute("src")
            if video_url:
                video_urls.append(video_url)
    except NoSuchElementException as e:
        print(f"Error finding elements: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return video_urls


def fetch_play_videos_from_play_by_play_table(
    page_url,
    table_class="GamePlayByPlay_hasPlays__LgdnK",
    row_class="GamePlayByPlayRow_article__asoO2",
    button_all_class="GamePlayByPlay_tab__BboK4",
    special_keywords=None,
    players=None,
    words_to_exclude=None,
    keywords=None,
    wait_time=5,
    additional_wait_time=5,
):
    """
    Fetches the video events from a play-by-play table on a web page using Selenium, with error handling.
    The function first waits for the table to load, then clicks the "All" tab if present.
    It then iterates through the rows, checking for matching keywords if provided.
    For each row, it moves and extracts the url to the event video from the href attribute of the anchor element.
    It handles any exceptions and returns a list of video data includinig url, text and timestamp.

    Parameters:
    page_url (str): URL of the page to load.
    table_class (str): Class of the table containing the video links.
    row_class (str): Class of the rows in the table to interact with.
    button_all_class (str): Class of the "All" tab button, if present.
    special_keywords (list[str], optional): List of special keywords to match rows, these will override normal keyword matching.
    players (list[str], optional): List of player names to filter the rows.
    words_to_exclude (list[str], optional): List of words to exclude from row text matching.
    keywords (list[str], optional): List of keywords to filter the rows.
    wait_time (int): Time in seconds to wait for elements to load.
    additional_wait_time (int): Additional time to wait after elements are found, in seconds.
    """
    driver = webdriver.Chrome()

    try:
        driver.get(page_url)
        # Handling the cookie banner
        try:
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "onetrust-close-btn-handler")
                )
            )
            close_cookie_banner_button = driver.find_element(
                By.CLASS_NAME, "onetrust-close-btn-handler"
            )
            close_cookie_banner_button.click()
        except TimeoutException:
            logger.error(
                "No cookie banner found or timeout occurred while waiting for cookie banner."
            )
        except NoSuchElementException:
            logger.error("Cookie banner close button not found.")
        except Exception as e:
            logger.error(f"Error while handling cookie banner: {e}")

        # Wait for the table to load after handling cookie banner
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, table_class))
        )
        # Optional: wait a bit more because sometimes the video takes time to load after clicking cookie banner
        time.sleep(additional_wait_time)
        # Looking for this button
        # <button type="button" data-is-active-tab="false" class="GamePlayByPlay_tab__BboK4" style="width: 20%;">ALL</button>
        try:
            # Wait for the buttons to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, f"button.{button_all_class}")
                )
            )

            # Find and click the specific button with the text "ALL"
            all_button = driver.find_element(
                By.XPATH,
                f"//button[contains(@class, '{button_all_class}') and contains(text(), 'ALL')]",
            )
            logger.console("Clicking ALL button")
            all_button.click()
        except NoSuchElementException:
            logger.error("Button with text 'ALL' not found")
        except TimeoutException:
            logger.error("Timeout waiting for buttons to be present")
        except WebDriverException as e:
            logger.error(f"Web driver error: {e}")
        # Optional: wait a bit more because sometimes the table with all the events takes time to load after clicking the "ALL" button
        time.sleep(additional_wait_time)
    except TimeoutException:
        logger.error(
            f"Timeout while waiting for the table with class {table_class} to load."
        )
        driver.quit()
        return []
    except WebDriverException as e:
        logger.error(f"Web driver error: {e}")
        driver.quit()
        return []
    video_play_by_play_event_data = []
    try:
        video_rows = driver.find_elements(By.CSS_SELECTOR, f".{row_class}")
        video_play_by_play_event_data = process_play_by_play_video_rows(
            video_rows, special_keywords, players, words_to_exclude, keywords
        )

    except Exception as e:
        logger.error(f"An error occurred during row iteration: {e}")
    finally:
        driver.quit()

    return video_play_by_play_event_data


def process_play_by_play_video_rows(
    video_rows,
    special_keywords=None,
    players=None,
    words_to_exclude=None,
    keywords=None,
):
    video_play_by_play_event_data = []
    logger.console("Looking for rows...")
    logger.console(f"Iterating through {len(video_rows)} rows...")
    for row in video_rows:
        try:
            video_event = row.find_element(
                By.CSS_SELECTOR, ".GamePlayByPlayRow_statEvent__Ru8Pr"
            )
            if not video_event:
                continue  # If no video_event is found skip row

            video_event_title = row.find_element(
                By.CSS_SELECTOR, ".GamePlayByPlayRow_descBlock__By8pv"
            ).get_attribute("data-text")

            if should_include_row_based_on_filters(
                video_event_title, special_keywords, players, words_to_exclude, keywords
            ):
                video_event_page_url = video_event.get_attribute("href")
                video_event_clock = row.find_element(
                    By.CSS_SELECTOR, ".GamePlayByPlayRow_clockElement__LfzHV"
                ).text
                video_event_pos = row.find_element(
                    By.CSS_SELECTOR, ".GamePlayByPlayRow_descBlock__By8pv"
                ).get_attribute("data-pos")
                logger.info(
                    f"{video_event_clock} {video_event_title} | Pos: {video_event_pos}"
                )
                logger.info(f"Adding event URL: {video_event_page_url}")

                # Clean data
                video_event_title = regex.sub(r"\(.*\)", "", video_event_title.strip())

                # Remove from title everything inside parenthesis
                if video_event_page_url:
                    video_event_data = {
                        "pos": video_event_pos.split("/")[0].strip().zfill(3),
                        "title": video_event_title,
                        "clock": video_event_clock,
                        "page_url": video_event_page_url,
                    }
                    video_play_by_play_event_data.append(video_event_data)
        except NoSuchElementException:
            logger.error("Video event not found in this row.")
        except Exception as e:
            logger.error(f"An error occurred while processing a row: {e}")

    return video_play_by_play_event_data


def should_include_row_based_on_filters(
    row_text, special_keywords=None, players=None, words_to_exclude=None, keywords=None
):
    row_text = row_text.lower()

    # Check for special keywords
    if special_keywords and any(
        special_keyword.lower() in row_text for special_keyword in special_keywords
    ):
        return True

    # Player check
    # The first word of row_text is the players name, so just check the first word
    if players and any(player.lower() in row_text.split(" ")[0] for player in players):
        # Words to exclude check
        if words_to_exclude and any(
            word.lower() in row_text for word in words_to_exclude
        ):
            return False

        # Keywords check - if provided, must match at least one keyword
        if keywords:
            return any(keyword.lower() in row_text for keyword in keywords)
        else:
            return True

    return False


def json_stats_to_html_image(stats_json, output_image_path):
    """
    Converts player statistics JSON into a styled HTML table and then renders it as an image.

    Parameters:
        stats_json (dict): JSON object containing player statistics.
        output_image_path (str): Path to save the generated image.
    """
    # HTML and CSS
    html_content = """
    <html>
    <head>
    <style>
      table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        color: #333;
      }
      th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
      }
      th {
        background-color: #4CAF50;
        color: white;
      }
      tr:nth-child(even) {
        background-color: #f2f2f2;
      }
      tr:hover {
        background-color: #ddd;
      }
    </style>
    </head>
    <body>
    <table>
    <tr><th>Name</th><th>Minutes</th><th>Points</th><th>Rebounds</th><th>Assists</th><th>Steals</th><th>Blocks</th><th>Turnovers</th></tr>
    """

    for player in stats_json["players"]:
        html_content += (
            f"<tr><td>{player['nameI']}</td><td>{player['statistics']['minutes']}</td>"
        )
        html_content += f"<td>{player['statistics']['points']}</td><td>{player['statistics']['reboundsTotal']}</td>"
        html_content += f"<td>{player['statistics']['assists']}</td><td>{player['statistics']['steals']}</td>"
        html_content += f"<td>{player['statistics']['blocks']}</td><td>{player['statistics']['turnovers']}</td></tr>"

    html_content += "</table></body></html>"

    # Convert HTML to Image
    imgkit.from_string(html_content, output_image_path)
