import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from simulation.eval import full_evaluation

from .database import db
from .gemini import call_gemini_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
IMAGES_DIR = Path(__file__).parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# serve static images from the images directory
# yes yes not prod recommended
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

async def get_health_or_none():
    return await db.physical_attributes_collection.find_one({})


class SimulationRequest(BaseModel):
    organ: str
    timestamp: datetime
    prompt: str = ""


def floor_to_day(dt: datetime):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


@app.post("/get_or_simulate_day")
async def get_or_simulate_day(req: SimulationRequest):
    rounded_ts = floor_to_day(req.timestamp)

    query = {
        "timestamp": rounded_ts,
    }

    document = await db.default.find_one(query)

    if document:
        return {
            "timestamp": rounded_ts,
            "evaluation": document.get("evaluation", {}),
            "simulated": document.get("simulated", False),
        }

    organ = req.organ
    prompt = req.prompt

    # get health
    # for now theres only 1 so we can just get the first one
    result = await db.physical_attributes_collection.find_one({})
    if not result:
        raise HTTPException(status_code=404, detail="Physical attributes not found")

    physical_attributes = dict(result)
    print("Physical attributes:", physical_attributes)
    print(full_evaluation(physical_attributes))

    return {}

    # send index, risks, 3 blood values

    # index, risks = evaluate_index_and_risks(organ, prompt, {}, blood_values)
    # image_path = await simulate_image(organ, prompt, rounded_ts)

    # evaluation = {
    #     "index": index,
    #     "risks": risks,
    #     "blood_values": blood_values,
    #     "image_path": str(image_path),
    # }

    # logger.info("Simulated evaluation: %s", evaluation)

    # await db.default.insert_one(
    #     {
    #         "timestamp": rounded_ts,
    #         "evaluation": evaluation,
    #         "simulated": True,
    #     },
    # )

    # return {
    #     "timestamp": rounded_ts,
    #     "evaluation": evaluation,
    #     "simulated": True,
    # }


@app.get("/reset_simulations/")
async def reset_simulations():
    result = await db.default.delete_many({"simulated": True})
    return {
        "deleted_count": result.deleted_count,
    }



@app.post("/summarize")
async def summarize():
    health = await get_health_or_none()
    if not health:
        health = {}

    prompt = f"""Summarize the following health data in a concise manner:
    Physical Attributes: {health}

    Respond using the following JSON format:
    {{
        "summary": "Your summary here"
    }}
    """

    result = call_gemini_json(prompt)
    if "summary" in result:
        return result

    return {"summary": "Failed to fetch from Gemini."}


class PhysicalAttributes(BaseModel):
    age: int
    height: float
    weight: float
    is_physically_active: bool
    is_smoker: bool
    alcohol_consumption: float


@app.post("/submit-physical-attributes/")
async def submit_physical_attributes(attrs: PhysicalAttributes):
    update_data = attrs.model_dump()

    # Update the first document in the collection
    result = await db.physical_attributes_collection.update_one(
        {}, {"$set": update_data},
    )

    # Optional: Insert if nothing was matched
    if result.matched_count == 0:
        await db.physical_attributes_collection.insert_one(update_data)

    # Return the updated document (or the inserted one)
    updated = await db.physical_attributes_collection.find_one({})
    if "_id" in updated:
        updated["_id"] = str(updated["_id"])
    return {"updated": updated}


@app.post("/add_actual_entry/")
async def add_actual_entry(steps_count: int, heart_rate: int, active_energy_burned: int):
    # NON MVP
    pass


@app.get("/reports")
async def get_reports():
    return {"altData": [1, 2, 3, 4, 5], "bpmData": [60, 62, 61, 63, 64], "sleepData": [7, 6.5, 8, 7.5, 6]}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")
    yield


app.router.lifespan_context = lifespan
