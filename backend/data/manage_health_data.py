import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def normalize_day(timestamp: str) -> str:
    """Extracts the YYYY-MM-DD day from ISO timestamp."""
    return datetime.fromisoformat(timestamp).date().isoformat()

def group_apple_watch_data(data):
    """Groups Apple Watch health data by day and type."""
    grouped = defaultdict(lambda: defaultdict(list))

    for entry in data:
        # Fallback if only one of startDate/date is present
        timestamp = entry.get("startDate") or entry.get("date")
        if not timestamp:
            continue  # skip invalid entries

        day = normalize_day(timestamp)
        type_ = entry["type"]

        grouped[day][type_].append({k: v for k, v in entry.items() if k not in ["type"]})

    return grouped

def grouped_data_to_mongodb(data):
    new_data = []

    for key, value in data.items():
        if "HKQuantityTypeIdentifierStepCount" in value:
            value["step_count"] = value.pop("HKQuantityTypeIdentifierStepCount")
        if "HKQuantityTypeIdentifierHeartRate" in value:
            value["heart_rate"] = value.pop("HKQuantityTypeIdentifierHeartRate")
        if "HKQuantityTypeIdentifierActiveEnergyBurned" in value:
            value["active_energy_burned"] = value.pop("HKQuantityTypeIdentifierActiveEnergyBurned")

        for k in list(value.keys()):
            if k.startswith("HK"):
                del value[k]  # Remove any keys that start with "HK" that arent the ones we want


        new_data.append({
            "timestamp": datetime.strptime(key, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ"),  # noqa: DTZ007
            "series": value,
            "blood_values": {},
            "evaluation": {},
        })

    return new_data

if __name__ == "__main__":
    with Path("./data/apple_watch_30day_raw_data.json").open() as fp:
        data = json.load(fp)
        grouped_data = group_apple_watch_data(data)

    mongodb_data = grouped_data_to_mongodb(grouped_data)
    with open("./data/database_schema.json", "w") as file:
        json.dump(mongodb_data, file, indent=2)

