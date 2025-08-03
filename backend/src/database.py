import json
import logging
import os
from datetime import datetime
from typing import Any

import anyio
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

    async def populate(self, data: list[dict[str, Any]]):
        for item in data:
            await self._collection.insert_one(item)

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

if __name__ == "__main__":
    import asyncio

    async def main():
        await db.connect()
        logger.info("Database connected successfully.")

        async with await anyio.open_file("./data/database_schema.json", "r") as fp:
            schema = json.loads(await fp.read())
            for item in schema:
                item["timestamp"] = datetime.fromisoformat(item["timestamp"])
            await db.populate(schema)
            logger.info("Database populated with initial data.")

    asyncio.run(main())
