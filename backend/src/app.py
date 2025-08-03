import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from simulation.eval import evaluate_blood_values
from simulation.eval import evaluate_risk_score

from .database import db
from .gemini import call_gemini_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
IMAGES_DIR = Path(__file__).parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# serve static images from the images directory
# yes yes not prod recommended
app.mount("/images/", StaticFiles(directory=IMAGES_DIR), name="images")


async def get_health_or_none():
    return await db.physical_attributes_collection.find_one({})


class SimulationRequest(BaseModel):
    timestamp: datetime
    prompt: str = ""


@app.get("/get_or_simulate_day/")
async def get_or_simulate_day(req: SimulationRequest):
    rounded_ts = req.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    query = {
        "timestamp": rounded_ts,
    }

    document = await db.collection.find_one(query)

    if document:
        return {
            "timestamp": rounded_ts,
            "evaluation": document.get("evaluation", {}),
            "simulated": document.get("simulated", False),
        }

    # get health
    # for now theres only 1 so we can just get the first one
    result = await db.physical_attributes_collection.find_one({})
    if not result:
        raise HTTPException(status_code=404, detail="Physical attributes not found")

    physical_attributes = dict(result)

    # get watch data for today
    print(rounded_ts)
    series_document = await db.collection.find_one({"timestamp": rounded_ts.isoformat()})

    if not series_document:
        series_data = [[0]*24, [0]*24, [0]*24]
    else:
        series_data = [
            series_document["HKQuantityTypeIdentifierHeartRate"][:24],
            series_document["HKQuantityTypeIdentifierStepCount"][:24],
            series_document["HKQuantityTypeIdentifierRespiratoryRate"][:24],
        ]
    print("Here is my series data:", series_data)


    if req.prompt != "":
        prompt = f"""
        Analyze the following prompt:
        {req.prompt}

        Try to replace values in the following JSON object with values that the prompt suggests:
        i.e. if the prompt says "I am 30 years older", then change the age in the JSON object to 30 years older.
        {json.dumps(physical_attributes, indent=2)}

        Note the following about the attributes:
        - age: integer, in years
        - height: float, in cm
        - weight: float, in kg
        - is_physically_active: boolean, true if they exercise regularly
        - is_smoker: boolean, true if they smoke
        - alcohol_consumption: float from 0 to 1, where 0 is no alcohol and 1 is alcohol addiction

        Take note of implicit effects, such as alcohol consumption usually means older age and a lot more weight. Height translates to age sometimes, etc.

        Return back with only the JSON object with the updated values. Do not say anything else.
        """  # noqa: S608

        new_physical_attributes = call_gemini_json(prompt)
        if not new_physical_attributes:
            raise HTTPException(status_code=500, detail="Failed to get response from Gemini")
    else:
        new_physical_attributes = physical_attributes

    print("Physical attributes:", new_physical_attributes)

    blood_values = evaluate_blood_values(series_data, new_physical_attributes)
    risk_score = evaluate_risk_score(blood_values)

    return {
        "blood_values": blood_values,
        "index": risk_score["index_score"],
        "risks": risk_score["risks"],
    }


@app.post("/summarize")
async def summarize():
    health = await get_health_or_none()
    if not health:
        health = {}

    prompt = f"""Summarize the following health data in a concise manner:
    Physical Attributes: {json.dumps(health, indent=2)}

    Make a lot of assumptions about the person based on the data.
    For example, if the person is 30 years old, they are likely to be in their prime and have a lot of energy.
    If they are 60 years old, they are likely to have some health issues.

    Keep it short, no more than 3 sentences.

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


@app.get("/get-physical-attributes/")
async def get_physical_attributes():
    result = await db.physical_attributes_collection.find_one({})
    if not result:
        raise HTTPException(status_code=404, detail="Physical attributes not found")
    return dict(result)


@app.post("/submit-physical-attributes/")
async def submit_physical_attributes(attrs: PhysicalAttributes):
    update_data = attrs.model_dump()

    # Update the first document in the collection
    result = await db.physical_attributes_collection.update_one(
        {},
        {"$set": update_data},
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
    # unfortunately apple has decided to lock healthkit behind a paywall
    # thus we are just using archived/placeholder data
    pass


@app.get("/reports")
async def get_reports():
    # unfortunately apple has decided to lock healthkit behind a paywall
    # thus we are just using archived/placeholder data
    return {"altData": [1, 2, 3, 4, 5], "bpmData": [60, 62, 61, 63, 64], "sleepData": [7, 6.5, 8, 7.5, 6]}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")
    yield


app.router.lifespan_context = lifespan
