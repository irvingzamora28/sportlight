import requests
import os
from bs4 import BeautifulSoup


class VideoDownloader:
    @staticmethod
    def extract_video_url(html_content):
        """
        Extracts the video URL from the HTML content.

        Parameters:
            html_content (str): The HTML content containing the video.

        Returns:
            str: The extracted video URL, or None if not found.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        video_tag = soup.find("video", class_="vjs-tech")
        if video_tag and video_tag.get("src"):
            return video_tag["src"]
        return None

    @staticmethod
    def download_video(video_url, output_directory="videos", filename=None):
        """
        Downloads the video from the given URL.

        Parameters:
            video_url (str): URL of the video to be downloaded.
            output_directory (str): Directory to save the downloaded video.
            filename (str, optional): Custom filename for the downloaded video. If None, the filename is derived from the URL.

        Returns:
            str: Filename of the downloaded video, or None if the download fails.
        """
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Use the specified filename or derive from the URL
        local_filename = os.path.join(
            output_directory, filename if filename else video_url.split("/")[-1]
        )

        try:
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return local_filename
        except Exception as e:
            print(f"Error downloading the video: {e}")
            return None
