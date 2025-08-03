import json
import os
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from google import genai
from google.genai import types
from normalization import normalize_blood_values
from normalization import normalize_physical_attributes
from normalization import normalize_series_data

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini_json(prompt: str) -> dict:
    """
    Sends a prompt to Gemini (PaLM) and returns parsed JSON result.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=512),
        ),
    )

    try:
        content = response.text
        print("Gemini response:", content)
        if "```json" in content:
            content = content.split("```json")[-1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print("Error parsing Gemini response:", content, e)
        return None


def group_series_data(data):
    """Groups series data by day and type."""
    grouped = {}
    arr = [
        "HKQuantityTypeIdentifierHeartRate",
        "HKQuantityTypeIdentifierStepCount",
        "HKQuantityTypeIdentifierRespiratoryRate",
    ]

    for k in arr:
        for entry in data[k]["records"]["data"]:
            timestamp = entry.get("start_date")
            if not timestamp:
                continue

            dt = datetime.fromisoformat(timestamp)
            dt_midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            day = dt_midnight.date().isoformat()
            hour = dt.hour % 24
            type_ = entry["type"]

            if type_ not in arr:
                continue

            if day not in grouped:
                grouped[day] = {k: [[] for _ in range(24)] for k in arr}

            grouped[day][type_][hour].append(entry["value"])

    for day_entry in grouped.values():
        for type_entry in day_entry:
            for hour in range(24):
                if type_entry in ["HKQuantityTypeIdentifierHeartRate", "HKQuantityTypeIdentifierRespiratoryRate"]:
                    day_entry[type_entry][hour] = np.mean(day_entry[type_entry][hour])
                else:
                    day_entry[type_entry][hour] = np.sum(day_entry[type_entry][hour]) if day_entry[type_entry][hour] else 0.0

    for day_entry in grouped.values():
        for type_entry in day_entry:
            if type_entry in ["HKQuantityTypeIdentifierHeartRate", "HKQuantityTypeIdentifierRespiratoryRate"]:
                bpm = day_entry[type_entry]
                bpm_series = pd.Series(bpm)

                # Interpolate missing values linearly (forward + backward)
                bpm_interpolated = bpm_series.interpolate(method="linear", limit_direction="both")

                # Convert back to NumPy array if needed
                bpm_filled = bpm_interpolated.to_numpy()

                day_entry[type_entry] = list(bpm_filled.tolist())

    # turn int64s into floats and also check for days that still have NaNs (therefore invalid)
    def clean_day_entry(day_entry):
        for type_entry in day_entry:
            for i in range(len(day_entry[type_entry])):
                if np.isnan(day_entry[type_entry][i]):
                    return False  # Invalid day_entry
                day_entry[type_entry][i] = float(day_entry[type_entry][i])
        return True

    for day_entry in grouped.values():
        if not clean_day_entry(day_entry):
            day_entry.clear()

    return [{"series_data": entry} for entry in grouped.values() if entry != {}]



def generate_training_data(series_training_data, fp):
    i = 0
    for entry in series_training_data:
        print("Processing entry:", i)
        i += 1
        series_data = entry["series_data"]

        average_bpm = float((np.mean(series_data["HKQuantityTypeIdentifierHeartRate"])) * random.uniform(0.9, 1.1))
        average_steps = float(
            (np.mean(series_data["HKQuantityTypeIdentifierStepCount"])) * random.uniform(0.8, 1.2)
        )
        average_respiratory_rate = float(
            (np.mean(series_data["HKQuantityTypeIdentifierRespiratoryRate"])) * random.uniform(0.9, 1.1)
        )

        prompt = f"""
Given the following three values by the user:

average daily heart rate (bpm): {average_bpm}
average daily step count (steps): {average_steps}
average respiratory rate (count/min): {average_respiratory_rate}


Generate the following physical attribute data for a synthetic personality, try to be more healthy than not (low weight, tall, not too much alcohol, younger), but also realistic:

age: integer between 18 and 40
weight: float in kg (reasonable based on calories burned)
height: float in cm (reasonable based on weight)
alcohol_consumption: float between 0 (none) and 1 (alcohol addiction), most people should be between 0 and 0.3
is_smoker: boolean based on alcohol consumption and BPM
is_physically_active: boolean based on step count and BPM


Determine a "index score" based on the values, a float that represents general health from 0 to 1. Use this index score as reference for how un/healthy the following data should be, 0 is dying and 1 is excellent health.
The index score should have variance. The average index score should be around 0.5, but can be lower or higher based on the three variables. Try to be higher more often than not, since the provided data is an underestimation.

The index score is based on the health of the individual, having more weight and being older should lower the index score, while being younger and more active should increase it. Alcohol is bad. Smoking is bad. Physically active is always good.  
Youth will almost always have less risk, so avoid giving them low index scores.

Keep index scores reasonable, so that the following rules apply:
- A person with an index score of 0.9 should have no risks at all.
- A person with an index score of 0.8+ should have no risks at all.
- A person with an index score of 0.7 should have at most one risk, and it must be mild.
- A person with an index score of 0.6 should have at most two risks, and they should be less severe (e.g. NAFLD, ALD, or mild hepatic inflammation).
- A person with an index score below 0.5 should have at least one risk, and it should be more severe (e.g. liver fibrosis, cirrhosis suspected).

A person must not have more than 3 risks, and the risks should be realistic based on the index score. Try to diversify individuals so that the data is not too homogeneous.


For example,
{{
    "age": 32,
    "is_physically_active": true,
    "weight": 64.5,
    "height": 168.0,
    "alcohol_consumption": 0.09,
    "is_smoker": False
}}
should have an index score of 0.9.

{{
    'age': 28,
    'is_physically_active': True,
    'weight': 78.5,
    'height': 182.0,
    'alcohol_consumption': 0.08,
    'is_smoker': False
}}
should have an index score of 0.85.

Once you obtain these attributes, use them alongside the original 3 variables to find suitable blood values, specifically: ALT, AST, GGT, Triglycerides, CRP, Ferritin

Then, from the following list of 'risks', output using its index:
1. Non-Alcoholic Fatty Liver Disease (NAFLD)
2. Alcoholic Liver Disease (ALD)
3. Hepatic Inflammation (early hepatitis / injury)
4. Liver Fibrosis Risk
5. Metabolic Syndrome / Insulin Resistance
6. Iron Overload / Hemochromatosis
7. Cirrhosis Suspected
8. Liver Enzyme Pattern Suggesting Toxicity
9. Obesity-linked Hepatic Stress
10. Systemic Inflammation-Driven Liver Stress


Your output should be in the format of, and it should be valid JSON:
{{
    physical_attributes: {{ key: value }},
    blood_values: {{ key: value }},
    index: 0.0,
    risks: []
}}

Say nothing else, only output the JSON.
"""

        output = call_gemini_json(prompt)
        if not output:
            print("Invalid output from Gemini, skipping entry")
            continue

        try:
            physical_attributes = output["physical_attributes"]
            blood_values = output["blood_values"]
            index = float(output["index"])
            risks = output["risks"]
        except Exception as e:
            print("Error parsing Gemini output:", output, e)
            continue


        with open(fp) as f:
            stored_training_data = json.load(f)
            stored_training_data.append(
                {
                    "series_data": normalize_series_data(series_data),
                    "physical_attributes": normalize_physical_attributes(physical_attributes),
                    "blood_values": normalize_blood_values(blood_values),
                    "index": index,
                    "risks": risks,
                },
            )

        # Save the training data to file
        with open(fp, "w") as f:
            json.dump(stored_training_data, f, indent=2)



if __name__ == "__main__":
    PATH_PREFIX = Path(__file__).parent.parent
    RAW_DATA_FP = PATH_PREFIX / "data/prod_health_data.json"
    OUTPUT_DATA_FP = PATH_PREFIX / "data/training_data.json"

    with RAW_DATA_FP.open() as fp:
        data = json.load(fp)
        grouped_data = group_series_data(data)

    print(f"Grouped {len(grouped_data)} days of series data")
    print("Generating training data...")
    
    with open(OUTPUT_DATA_FP, "w") as f:
        json.dump([], f)

    # Pick 10 random entries from grouped_data
    grouped_data_sample = random.sample(grouped_data, min(100, len(grouped_data)))
    training_data = generate_training_data(grouped_data_sample, OUTPUT_DATA_FP)

    print(":)")
