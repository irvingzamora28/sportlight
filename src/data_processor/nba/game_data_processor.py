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
    
    def get_game_team_data(self, home=True):
        """
        Returns the home team data
        """
        return JSONParser.extract_value(self.game_data[0], ["gameCard", "home_team" if home else "away_team"])

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

    def get_game_slug(self, slug_properties_path):
        """
        Fetches the game slug from the game data

        Returns:
        str: A slug string for this game, or empty string if not found
        """
        for game in self.game_data:
            slug = JSONParser.extract_value(game, slug_properties_path)
            if slug:
                # This returns this {'0022300451': 'MIN @ NYK (0022300451)'}, we need to return 'MIN@NYK'
                slug = list(slug.values())[0].split("(")[0].replace(" ", "")
                return slug
            else:
                print("Game slug not found in the game data.")
                return ""

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

    def get_play_by_play_url(self, actions):
        """
        Extracts the resourceUrl for the action titled "Game Details" and then forms the play by play url.

        Parameters:
            actions (list): A list of action items, each containing a title and resourceLocator.

        Returns:
            str: The resourceUrl of the "Game Details" action, or None if not found.
        """
        play_by_play_url = JSONParser.find_value_in_list(
            actions, "title", "Game Details", ["resourceLocator", "resourceUrl"]
        )
        return f"{play_by_play_url}/play-by-play"
