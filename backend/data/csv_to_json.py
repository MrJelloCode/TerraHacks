import pandas as pd
import json
from datetime import datetime

def convert_health_csv_to_json(csv_path: str, json_path: str = None) -> list:
    df = pd.read_csv(csv_path)

    # Drop unnamed index column if it exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    # Normalize column names (strip spaces just in case)
    df.columns = df.columns.str.strip()

    # Prepare the output list
    result = []

    for _, row in df.iterrows():
        entry = {
            "type": row["type"],
            "startDate": convert_apple_datetime(row["startDate"]),
            "endDate": convert_apple_datetime(row["endDate"]),
            "value": try_float(row["value"])
        }

        if pd.notna(row.get("unit")):
            entry["unit"] = row["unit"]

        result.append(entry)

    if json_path:
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)

    return result

def convert_apple_datetime(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S %z")
        return dt.isoformat()
    except Exception:
        return date_str  # Fallback to original if parsing fails

def try_float(value):
    try:
        return float(value)
    except:
        return value


if __name__ == "__main__":
    data = convert_health_csv_to_json("./data/apple_watch_30day_raw_data.csv", "./data/apple_watch_30day_raw_data.json")
    print(json.dumps(data[:2], indent=2))
