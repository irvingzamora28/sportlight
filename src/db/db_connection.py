from pymongo import MongoClient
from dotenv import load_dotenv
from common.logger import logger
import os
from models.schemas import team_schema, player_schema

load_dotenv()


class DBConnection:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")

        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.setup_schema()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise e

    def get_collection(self, collection_name):
        try:
            return self.db[collection_name]
        except Exception as e:
            logger.error(f"Error getting collection '{collection_name}': {e}")
            raise e

    def setup_schema(self):
        # Apply the schema to the 'teams' collection
        self.apply_collection_schema("teams", team_schema)

        # Apply the schema to the 'players' collection
        self.apply_collection_schema("players", player_schema)

    def apply_collection_schema(self, collection_name, schema):
        try:
            self.db.command(
                "collMod", collection_name, validator=schema, validationLevel="strict"
            )
            logger.info(f"Schema applied to '{collection_name}' collection")
        except Exception as e:
            # If the collection does not exist, create it with the schema
            if "ns does not exist" in str(e):
                self.db.create_collection(
                    collection_name, validator=schema, validationLevel="strict"
                )
                logger.info(
                    f"Schema applied and '{collection_name}' collection created"
                )
            else:
                logger.error(f"Error setting up schema for '{collection_name}': {e}")
                raise e
