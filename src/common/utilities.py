import requests


def fetch_html_content(url):
    """
    Fetches the HTML content of the given URL.

    Parameters:
        url (str): The URL to fetch the HTML content from.

    Returns:
        str: The HTML content of the page, or None if the fetch fails.
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
