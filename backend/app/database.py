import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger("terrahacks-simulation.db")


class DatabaseNotConnectedError(Exception):
    def __init__(self):
        msg = "Database not connected. Call `connect()` first."
        super().__init__(msg)


class MongoDB:
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "mydb",
        collection_name: str = "records",
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

    @property
    def collection(self) -> AsyncIOMotorCollection:
        if not self._collection:
            err = DatabaseNotConnectedError()
            raise err
        return self._collection

    async def insert_document(self, document: dict) -> str:
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def fetch_document(self, filter_query: dict) -> Any:
        return await self.collection.find_one(filter_query)

    async def fetch_all_documents(self, limit: int = 1000) -> list[dict]:
        cursor = self.collection.find({})
        return await cursor.to_list(length=limit)

    async def clear_collection(self):
        await self.collection.delete_many({})

db = MongoDB()
