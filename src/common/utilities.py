import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

import time


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
