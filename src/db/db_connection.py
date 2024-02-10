from pymongo import MongoClient
from dotenv import load_dotenv
from common.logger import logger
import os

load_dotenv()


class DBConnection:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")

        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error("Error connecting to MongoDB: %s", e)
            raise e

    def get_collection(self, collection_name):
        try:
            return self.db[collection_name]
        except Exception as e:
            logger.error("Error getting collection '%s': %s", collection_name, e)
            raise e
