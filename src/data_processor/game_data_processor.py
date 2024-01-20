import requests
from parser.json_parser import JSONParser


class GameDataProcessor:
    """
    A class to process game data and extract video URLs.

    Attributes:
        game_data (list): A list of game data in JSON format.
    """

    def __init__(self, game_data_json):
        """
        The constructor for GameDataProcessor class.

        Parameters:
            game_data_json (list): A list of game data in JSON format.
        """
        self.game_data = game_data_json

    def download_video(video_url, output_path):
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
            return True
        return False

    def get_video_html(self, video_properties_path):
        """
        Fetches the HTML content of the first available video URL found in the game data.

        Returns:
            str: HTML content of the video page, or None if not found.
        """
        for game in self.game_data:
            video_url = JSONParser.extract_value(game, video_properties_path)

            if video_url:
                response = requests.get(video_url)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"Failed to fetch video page: {video_url}")
                    return None
            else:
                print("Video URL not found in the game data.")
                return None

    def get_actions(self, actions_properties_path):
        """
        Fetches a list of action items from the game data
        Returns:
        list: A list of action dictionaries, or empty list if not found
        """
        actions = []
        for game in self.game_data:
            actions = JSONParser.extract_value(game, actions_properties_path)
            if actions:
                return actions
            else:
                print("Actions not found in the game data.")
                return []

    def get_box_score_url(self, actions):
        """
        Extracts the resourceUrl for the action titled "Box Score".

        Parameters:
            actions (list): A list of action items, each containing a title and resourceLocator.

        Returns:
            str: The resourceUrl of the "Box Score" action, or None if not found.
        """
        box_score_url = JSONParser.find_value_in_list(
            actions, "title", "Box Score", ["resourceLocator", "resourceUrl"]
        )
        return box_score_url
