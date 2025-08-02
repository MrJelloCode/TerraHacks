import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from .database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()



class SimulationRequest(BaseModel):
    prompt: str
    timestamp: datetime

@app.post("/simulate/")
async def simulate(req: SimulationRequest):
    result = f"Simulated response for: {req.prompt} at {req.timestamp}"
    return {"result": result}


@app.get("/risk_index/")
async def risk_index(timestamp: datetime):
    index = 4.0
    return {"risk_index": index, "timestamp": timestamp}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")
    yield

app.router.lifespan_context = lifespan
