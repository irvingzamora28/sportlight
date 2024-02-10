team_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "name", "code", "conference"],
        "properties": {
            "id": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "code": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "conference": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
        },
    }
}

player_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "id",
            "name",
            "jerseyNum",
            "position",
            "slug",
            "team_code",
            "teamhistory",
        ],
        "properties": {
            "id": {
                "bsonType": "int",
                "description": "must be an integer and is required",
            },
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "jerseyNum": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "position": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "slug": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "team_code": {
                "bsonType": "string",
                "description": "must be a string and is required",
            },
            "teamhistory": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["team_code", "date"],
                    "properties": {
                        "team_code": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                        },
                        "date": {
                            "bsonType": "string",
                            "description": "must be a string and is required",
                        },
                    },
                },
            },
        },
    }
}
