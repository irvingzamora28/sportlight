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

    def get_game_id(self):
        """
        Returns the id of the first game.
        """
        return JSONParser.extract_value(self.game_data[0], ["gameCard", "game_id"])

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

    def get_game_tags(self, tags_properties_path):
        """
        Fetches a list of action items from the game data
        Returns:
        list: A list of action dictionaries, or empty list if not found
        """
        actions = []
        for game in self.game_data:
            actions = JSONParser.extract_value(game, tags_properties_path)
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
