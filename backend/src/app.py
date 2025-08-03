import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from simulation.eval import evaluate_index_and_risks
from simulation.eval import simulate_blood_values
from simulation.eval import simulate_image

from .database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


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

    last_known_blood_values = {
        "ALT": 35,
        "AST": 30,
        "BUN": 15,
        "Creatinine": 0.8,
        "Glucose": 90,
    }
    blood_values = simulate_blood_values(organ, prompt, last_known_blood_values)
    index, risks = evaluate_index_and_risks(organ, prompt, {}, blood_values)
    image_path = await simulate_image(organ, prompt, rounded_ts)

    evaluation = {
        "index": index,
        "risks": risks,
        "blood_values": blood_values,
        "image_path": str(image_path),
    }

    logger.info("Simulated evaluation: %s", evaluation)

    await db.default.insert_one(
        {
            "timestamp": rounded_ts,
            "evaluation": evaluation,
            "simulated": True,
        },
    )

    return {
        "timestamp": rounded_ts,
        "evaluation": evaluation,
        "simulated": True,
    }


@app.get("/reset_simulations/")
async def reset_simulations():
    result = await db.default.delete_many({"simulated": True})
    return {
        "deleted_count": result.deleted_count,
    }


@app.post("/summarize")
async def summarize():
    return {"summary": "This is a placeholder summary from Gemini."}


class PhysicalAttributes(BaseModel):
    age: int
    height: float
    weight: float
    is_male: bool
    is_smoker: bool
    alcohol_consumption: float


@app.post("/submit-physical-attributes/")
async def submit_physical_attributes(attrs: PhysicalAttributes):
    return {"summary": "This is a placeholder summary from Gemini."}


@app.post("/add_actual_entry/")
async def add_actual_entry(steps_count: int, heart_rate: int, active_energy_burned: int):
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
