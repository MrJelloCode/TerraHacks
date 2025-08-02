import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

from .database import db  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


class SimulationRequest(BaseModel):
    organ: str
    timestamp: datetime


def floor_to_day(dt: datetime):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


@app.post("/get_or_simulate_day/")
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

    return {
        "timestamp": rounded_ts,
        "evaluation": {},
        "simulated": True,
    }


@app.post("/summarize/")
async def summarize():
    # Placeholder for Gemini or LLM-based summary generation
    return {"summary": "This is a placeholder summary from Gemini."}


@app.post("/graph/primary/")
async def graph_primary():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"graph_{timestamp}.png"
    path = IMAGES_DIR / filename

    x = list(range(10))
    y = [i**2 for i in x]

    plt.figure()
    plt.plot(x, y, label="x^2")
    plt.title("Placeholder Graph")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(visible=True)
    plt.savefig(path)
    plt.close()

    return {"filename": filename}

@app.post("/graph/secondary/")
async def graph_secondary():
    pass

@app.post("/get_blood_values/")
async def get_blood_values():
    pass

@app.get("/images/{img}")
async def get_image(img: str):
    path = IMAGES_DIR / img
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")
    yield

app.router.lifespan_context = lifespan
