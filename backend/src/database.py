import json
import logging
import os
from datetime import datetime
import random
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
        self._physical_attributes_collection_name = "physical_attributes"

        self._client: AsyncIOMotorClient | None = None
        self.collection: AsyncIOMotorCollection | None = None
        self.physical_attributes_collection: AsyncIOMotorCollection | None = None

    async def connect(self):
        self._client = AsyncIOMotorClient(self._uri)
        db = self._client[self._db_name]
        self.collection = db[self._collection_name]
        self.physical_attributes_collection = db[self._physical_attributes_collection_name]
        logger.info("Connected to MongoDB '%s.%s'", self._db_name, self._collection_name)

    async def populate(self, data: list[dict[str, Any]]):
        for item in data:
            await self.collection.insert_one(item)


db = MongoDB(
    DB_URI,
    DB_NAME,
    DB_COLLECTION,
)

def mongoify_raw_series(raw_data: dict[str, Any]) -> list[dict[str, Any]]:
    grouped = {}

    for entry in raw_data:
        # Convert ISO datetime to just the date (e.g., '2020-06-13')
        dt = datetime.fromisoformat(entry["startDate"])
        day_str = dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        if entry["type"] not in [
            "HKQuantityTypeIdentifierHeartRate",
            "HKQuantityTypeIdentifierStepCount",
            "HKQuantityTypeIdentifierRespiratoryRate",
        ]:
            continue

        if day_str not in grouped:
            # respiratory data not present in sample population
            grouped[day_str] = {"HKQuantityTypeIdentifierHeartRate": [], "HKQuantityTypeIdentifierStepCount": [], "HKQuantityTypeIdentifierRespiratoryRate": [random.uniform(10.0, 13.0) for _ in range(24)]}

        # Append value to correct type and date
        grouped[day_str][entry["type"]].append(entry["value"])

    # Convert to desired output format
    result = []
    for day, data in grouped.items():
        out = {"timestamp": day}
        out.update(data)
        result.append(out)

    return result

if __name__ == "__main__":
    import asyncio

    async def main():
        await db.connect()
        logger.info("Database connected successfully.")

        async with await anyio.open_file("./data/raw_series_data.json", "r") as fp:
            raw_data = json.loads(await fp.read())
            schema = mongoify_raw_series(raw_data)
        await db.populate(schema)

        async with await anyio.open_file("./data/sample_physical_data.json", "r") as fp:
            sample_physical_data = json.loads(await fp.read())

            await db.physical_attributes_collection.delete_many({})
            await db.physical_attributes_collection.insert_one(sample_physical_data)
            logger.info("Database populated with initial data.")

    asyncio.run(main())
