class Team:
    def __init__(self, id, name, code, conference):
        self.id = id
        self.name = name
        self.code = code
        self.conference = conference

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "conference": self.conference,
        }
