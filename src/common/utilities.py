import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    except Exception as e:
        print(f"Error fetching dynamic content: {e}")
        return None
    finally:
        driver.quit()
