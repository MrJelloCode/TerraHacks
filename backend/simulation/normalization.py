def normalize_physical_attributes(attrs):
    """
    Normalize the physical_attributes dict to values between 0 and 1.
    """
    # Define min/max ranges
    ranges = {
        "age": (18, 40),
        "weight": (40.0, 130.0),
        "height": (140.0, 210.0),
        "alcohol_consumption": (0.0, 1.0),
    }

    return {
        "age": (attrs["age"] - ranges["age"][0]) / (ranges["age"][1] - ranges["age"][0]),
        "is_physically_active": float(attrs["is_physically_active"]),
        "weight": (attrs["weight"] - ranges["weight"][0]) / (ranges["weight"][1] - ranges["weight"][0]),
        "height": (attrs["height"] - ranges["height"][0]) / (ranges["height"][1] - ranges["height"][0]),
        "alcohol_consumption": (attrs["alcohol_consumption"] - ranges["alcohol_consumption"][0])
        / (ranges["alcohol_consumption"][1] - ranges["alcohol_consumption"][0]),
        "is_smoker": float(attrs["is_smoker"]),
    }


BLOOD_VALUES_RANGE = {
    "ALT": (0, 100),
    "AST": (0, 100),
    "GGT": (0, 150),
    "Triglycerides": (0, 400),
    "CRP": (0, 10),
    "Ferritin": (0, 1000),
}


def normalize_blood_values(blood_values):
    # Define min/max ranges
    ranges = BLOOD_VALUES_RANGE

    return {k: (float(v) - ranges[k][0]) / (ranges[k][1] - ranges[k][0]) for k, v in blood_values.items()}


def denormalize_blood_values(normalized_blood_values):
    # Define min/max ranges (same as in normalize)
    ranges = BLOOD_VALUES_RANGE

    return {
        k: normalized_blood_values[k] * (ranges[k][1] - ranges[k][0]) + ranges[k][0] for k in normalized_blood_values
    }


def normalize_series_data(series_data):
    ranges = {
        "HKQuantityTypeIdentifierHeartRate": (40.0, 180.0),
        "HKQuantityTypeIdentifierStepCount": (0.0, 3000.0),
        "HKQuantityTypeIdentifierRespiratoryRate": (10.0, 25.0),
    }

    normalized = {}

    for k, values in series_data.items():
        min_val, max_val = ranges[k]
        normalized[k] = [(v - min_val) / (max_val - min_val) if v is not None else 0.0 for v in values]

    return normalized

