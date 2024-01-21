from parser.json_parser import JSONParser


class BoxScoreDataProcessor:
    """
    A class to process box score data.

    Attributes:
        box_score_data (list): A list of box_score data in JSON format.
    """

    def __init__(self, box_score_data_json):
        """
        The constructor for BoxScoreDataProcessor class.

        Parameters:
            box_score_data_json (list): A list of box score data in JSON format.
        """
        self.game_data = box_score_data_json

    def get_key_players(self, game_tags):
        """
        Extracts key players based on game tags.

        Parameters:
            game_tags (dict): A dictionary of game tags with player slugs as keys.

        Returns:
            list: A list of key player data whose slugs match the game tags.
        """
        key_players = []
        for game in self.game_data:
            # Extract player data from both home and away teams
            home_players = JSONParser.extract_value(
                game, ["game", "homeTeam", "players"]
            )
            away_players = JSONParser.extract_value(
                game, ["game", "awayTeam", "players"]
            )
            # Combine both player lists
            all_players = (
                home_players + away_players if home_players and away_players else []
            )
            # Filter players based on game tags
            for player in all_players:
                player_slug = player.get("playerSlug")
                if player_slug in game_tags:
                    key_players.append(player)

        return key_players

    def get_lead_stats_players(self):
        """
        Extracts players that lead in key stats like points, rebounds, etc.

        Returns:
            list: A list of player dictionaries with stats leaders.
        """
        stats_leaders = []
        for game in self.game_data:
            # Extract player stats for home and away teams
            home_player_stats = JSONParser.extract_value(
                game, ["game", "postgameCharts", "homeTeam", "statistics"]
            )
            away_player_stats = JSONParser.extract_value(
                game, ["game", "postgameCharts", "awayTeam", "statistics"]
            )

            # Extract player lists for home and away teams
            home_players = JSONParser.extract_value(
                game, ["game", "homeTeam", "players"]
            )
            away_players = JSONParser.extract_value(
                game, ["game", "awayTeam", "players"]
            )

            # Get leader IDs
            leader_ids = {
                home_player_stats.get("playerPtsLeaderId"),
                home_player_stats.get("playerRebLeaderId"),
                home_player_stats.get("playerAstLeaderId"),
                home_player_stats.get("playerBlkLeaderId"),
                away_player_stats.get("playerPtsLeaderId"),
                away_player_stats.get("playerRebLeaderId"),
                away_player_stats.get("playerAstLeaderId"),
                away_player_stats.get("playerBlkLeaderId"),
            }

            # Combine both player lists
            all_players = (home_players or []) + (away_players or [])

            # Find and append the player info for each leader
            for player_id in leader_ids:
                player_info = next(
                    (
                        player
                        for player in all_players
                        if player.get("personId") == player_id
                    ),
                    None,
                )
                if player_info:
                    stats_leaders.append(player_info)

        return stats_leaders
