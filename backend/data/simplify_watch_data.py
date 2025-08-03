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
        new_data.append({
            "timestamp": key,
            "simulated": value,
            "evaluation": {}
        })

    return new_data

if __name__ == "__main__":
    # with Path("./app/apple_watch_7day_raw_data.json").open() as fp:
    #     data = json.load(fp)
    #     grouped_data = group_apple_watch_data(data)

    # with Path("./app/grouped_watch_data.json").open("w") as fp:
    #     json.dump(grouped_data, fp, indent=2)

    with open("grouped_watch_data.json") as file:
        data = json.load(file)
    
    mongodb_data = grouped_data_to_mongodb(data)
    with open("database_schema.json", "w") as file:
        json.dump(mongodb_data, file, indent=2)

