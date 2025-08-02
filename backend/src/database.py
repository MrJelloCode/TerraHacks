import logging
import json
import os
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger("terrahacks-simulation.db")

DB_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")
DB_COLLECTION = os.getenv("MONGO_COLLECTION_NAME")


class DatabaseNotConnectedError(Exception):
    def __init__(self):
        msg = "Database not connected. Call `connect()` first."
        super().__init__(msg)


class MongoDB:
    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_name: str,
    ):
        self._uri = uri
        self._db_name = db_name
        self._collection_name = collection_name

        self._client: AsyncIOMotorClient | None = None
        self._collection: AsyncIOMotorCollection | None = None

    async def connect(self):
        self._client = AsyncIOMotorClient(self._uri)
        db = self._client[self._db_name]
        self._collection = db[self._collection_name]
        logger.info("Connected to MongoDB '%s.%s'", self._db_name, self._collection_name)
        
        record = await db.find_one()
        if record is None:
            logger.info("Initializing database with schema.")
            await self.setup_collection()

    async def setup_collection(self):
        with open("database_schema.json") as file:
            database_schema = json.load(file)

        await self.collection.insert_many(database_schema)     


    @property
    def collection(self) -> AsyncIOMotorCollection:
        if not self._collection:
            err = DatabaseNotConnectedError()
            raise err
        return self._collection


db = MongoDB(
    DB_URI,
    DB_NAME,
    DB_COLLECTION,
)
