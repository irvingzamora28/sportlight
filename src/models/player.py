class Player:
    def __init__(self, id, name, jersey_num, position, slug, team_code, team_history):
        self.id = id
        self.name = name
        self.jersey_num = jersey_num
        self.position = position
        self.slug = slug
        self.team_code = team_code
        self.team_history = team_history

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "jerseyNum": self.jersey_num,
            "position": self.position,
            "slug": self.slug,
            "team_code": self.team_code,
            "teamhistory": self.team_history,
        }
