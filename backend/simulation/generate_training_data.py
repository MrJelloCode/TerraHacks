
import json
import os
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
import numpy as np

MAX_SERIES_VALUES_PER_DAY = 144

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



def call_gemini_json(prompt: str, api_key: str = GEMINI_API_KEY) -> dict:
    """
    Sends a prompt to Gemini (PaLM) and returns parsed JSON result.
    """
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    try:
        content = response.text
        if "```json" in content:
            content = content.split("```json")[-1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        msg = f"Could not parse response as JSON: {e}\nRaw response:\n{response.text}"
        raise ValueError(msg) from e


def downsample_to_24(values):
    """
    Takes a list of N float values and downsamples to 24 values by averaging.
    """
    values = np.array(values, dtype=float)
    n = len(values)

    # Break n into 24 roughly equal bins
    bin_edges = np.linspace(0, n, 25, dtype=int)  # 25 edges = 24 bins
    output = []

    for i in range(24):
        start, end = bin_edges[i], bin_edges[i + 1]
        avg = values[start:end].mean() if end > start else 0.0
        output.append(avg)

    return output


def group_series_data(data):
    """Groups series data by day and type."""
    grouped = {}

    for entry in data:
        timestamp = entry.get("startDate")
        if not timestamp:
            continue

        dt = datetime.fromisoformat(timestamp)
        dt_midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        day = dt_midnight.date().isoformat()
        type_ = entry["type"]

        arr = [
            "HKQuantityTypeIdentifierHeartRate",
            "HKQuantityTypeIdentifierStepCount",
            "HKQuantityTypeIdentifierBasalEnergyBurned",
        ]

        if type_ not in arr:
            continue

        if day not in grouped:
            grouped[day] = [[], [], []]
        grouped[day][arr.index(type_)].append(entry["value"])

    return [{"series_data": [downsample_to_24(v) for v in entry]} for entry in grouped.values()]


def generate_training_data(series_training_data):
    training_data = []

    for entry in series_training_data:
        series_data = entry["series_data"]

        average_bpm = np.mean(series_data[0])
        average_steps = np.mean(series_data[1])
        average_kcal = np.mean(series_data[2])

        # physical_attributes = call_gemini_json("stuff")
        # blood_values = call_gemini_json("stuff")

        training_data.append({
            "series_data": series_data,
            "physical_attributes": {},
            "blood_values": {},
        })

    return training_data


if __name__ == "__main__":
    PATH_PREFIX = Path(__file__).parent.parent
    RAW_DATA_FP = PATH_PREFIX / "data/raw_series_data.json"
    OUTPUT_DATA_FP = PATH_PREFIX / "data/training_data.json"

    with RAW_DATA_FP.open() as fp:
        data = json.load(fp)
        grouped_data = group_series_data(data)

    training_data = generate_training_data(grouped_data)

    with OUTPUT_DATA_FP.open("w") as fp:
        json.dump(training_data, fp, indent=2)
