class PlayerDataUtils:
    @staticmethod
    def combine_players(unique_key, *player_groups):
        """
        Combines multiple lists of player dictionaries, avoiding duplicates based on a unique key.

        Parameters:
            unique_key (str): The key used to identify unique players (e.g., 'personId').
            *player_groups: Variable length list of player groups.

        Returns:
            list: A combined list of unique players.
        """
        unique_ids = set()
        combined_players = []

        for group in player_groups:
            for player in group:
                identifier = player.get(unique_key)
                if identifier and identifier not in unique_ids:
                    unique_ids.add(identifier)
                    combined_players.append(player)

        return combined_players

    @staticmethod
    def get_players_lastnames(players):
        try:
            player_names = [player["familyName"] for player in players]
            return player_names
        except KeyError:
            print("Error: 'familyName' key not found in player data")
            return None
