import json
from datetime import datetime

import numpy as np
import torch


def generate_heart_rate_series(base_hr=75):
    # create a 24-hour cycle with fluctuations
    hr = base_hr + np.sin(np.linspace(0, 2 * np.pi, 24)) * 10
    hr += np.random.normal(0, 3, 24)  # noiiiiise
    return hr.tolist()


def generate_spo2_series():
    return (np.random.normal(97, 1, 24)).tolist()


def get_hour(dt_str):
    return datetime.fromisoformat(dt_str).hour


def hourly_series_from_data(data, batch_id, key, add=False):
    day_entry = data[list(data.keys())[batch_id]]
    step_entries = day_entry.get(key, [])
    if not step_entries:
        return []
    values = [0] * 24

    for entry in step_entries:
        hour = get_hour(entry["startDate"])

        if add:
            values[hour] += entry["value"]
        elif values[hour] == 0:
            values[hour] = entry["value"]

    # Convert to numpy array for interpolation
    values = np.array(values, dtype=np.float32)

    # Find indices where values are non-zero
    nonzero_indices = np.nonzero(values)[0]
    nonzero_values = values[nonzero_indices]

    # If there's only one or no nonzero, just return zero-padded array
    if len(nonzero_indices) < 2:
        return values

    # Interpolate over zeros
    return np.interp(x=np.arange(24), xp=nonzero_indices, fp=nonzero_values)



def generate_watch_tensor(data):
    step_count = hourly_series_from_data(data, 0, "HKQuantityTypeIdentifierStepCount", add=True)
    heart_rate = hourly_series_from_data(data, 0, "HKQuantityTypeIdentifierHeartRate")

    return step_count, heart_rate

    # # concatenate along axis=1 to get shape (24, 3)
    # combined = np.concatenate([heart, spo2, steps], axis=1)

    # return torch.tensor(combined, dtype=torch.float32)  # shape: [24, 3]


def generate_blood_test_sample():
    return {
        "ALT": np.random.normal(35, 20),
        "AST": np.random.normal(30, 15),
        "GGT": np.random.normal(20, 10),
        "Bilirubin": np.random.normal(0.7, 0.3),
        "Albumin": np.random.normal(4.0, 0.5),
        "Platelets": np.random.normal(250, 50),
        "INR": np.random.normal(1.0, 0.1),
        "Triglycerides": np.random.normal(120, 30),
        "Glucose": np.random.normal(90, 10),
    }


def generate_blood_test_tensor():
    sample = generate_blood_test_sample()

    # Ensure the order of keys is consistent
    ordered_keys = ["ALT", "AST", "GGT", "Bilirubin", "Albumin", "Platelets", "INR", "Triglycerides", "Glucose"]

    values = [sample[key] for key in ordered_keys]
    return torch.tensor(values, dtype=torch.float32)  # shape: [len(ordered_keys)]


def generate_risk_score(series: torch.Tensor, blood: torch.Tensor) -> float:
    score = 0.0

    ALT, AST, GGT, Bilirubin, Albumin, Platelets, INR, Triglycerides, Glucose = blood.tolist()

    heart_rate = series[:, 0]
    spo2 = series[:, 1]
    steps = series[:, 2]

    if ALT > 55 or GGT > 40:
        score += 1 / 5
    if Albumin < 3.5 or INR > 1.2:
        score += 1 / 5
    if Triglycerides > 150 or Glucose > 100:
        score += 1 / 5
    if heart_rate.mean() > 90:
        score += 1 / 5
    if spo2.mean() < 95:
        score += 1 / 10
    if steps.sum() < 5000:
        score += 1 / 10

    return round(min(score, 1.0), 2)


def generate_test_training_sample() -> dict:
    series = generate_watch_tensor()
    blood = generate_blood_test_tensor()
    label = generate_risk_score(series, blood)

    return series, blood, label


def generate_batch_training_samples(batch_size: int) -> list:
    samples = []
    for _ in range(batch_size):
        blood, watch, label = generate_test_training_sample()
        samples.append((blood, watch, label))
    return samples


if __name__ == "__main__":
    with open("./app/grouped_watch_data.json") as fp:
        data = json.load(fp)

    for day, day_entry in data.items():
        if "series" in day_entry:
            if "HKCategoryTypeIdentifierSleepAnalysis" in day_entry["series"]:
                del data[day]["series"]["HKCategoryTypeIdentifierSleepAnalysis"]

        if "HKCategoryTypeIdentifierSleepAnalysis" in day_entry:
            del data[day]["HKCategoryTypeIdentifierSleepAnalysis"]

    with open("./app/grouped_watch_data2.json", "w") as fp:
        json.dump(data, fp, indent=2)

    # print(generate_watch_tensor(data))
