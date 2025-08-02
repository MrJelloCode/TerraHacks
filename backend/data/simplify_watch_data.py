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

# list = ["2025-07-08", 68, 78, 102] | example of an input list
list = [timestamp, step_count, heart_rate, active_energy_burned]

def inputting_data(list):
   return {"timestamps": list[0],
     "step_count": list[1],
     "heart_rate": list[2],
     "active_energy_burned": list[3]}


if __name__ == "__main__":
    with Path("./app/apple_watch_7day_raw_data.json").open() as fp:
        data = json.load(fp)
        grouped_data = group_apple_watch_data(data)

    with Path("./app/grouped_watch_data.json").open("w") as fp:
        json.dump(grouped_data, fp, indent=2)
