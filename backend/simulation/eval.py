import torch
from neural_network.neural_net import EstimateBloodAttributesNet
from normalization import normalize_physical_attributes, denormalize_blood_values

risk_mapping = [
    "Non-Alcoholic Fatty Liver Disease (NAFLD)",
    "Alcoholic Liver Disease (ALD)",
    "Hepatic Inflammation (early hepatitis / injury)",
    "Liver Fibrosis Risk",
    "Metabolic Syndrome / Insulin Resistance",
    "Iron Overload / Hemochromatosis",
    "Cirrhosis Suspected",
    "Liver Enzyme Pattern Suggesting Toxicity",
    "Obesity-linked Hepatic Stress",
    "Systemic Inflammation-Driven Liver Stress",
]

BLOOD_KEYS = ["ALT", "AST", "GGT", "Triglycerides", "CRP", "Ferritin"]


def evaluate_blood_values(physical_attributes: dict) -> dict:
    """
    Given physical attributes, predict blood values using a pre-trained model.
    Assumes a dummy series input for now (can be replaced with real time-series).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model + weights
    model = EstimateBloodAttributesNet().to(device)
    model.load_state_dict(torch.load("blood_estimation_model.pt", map_location=device))
    model.eval()

    # Normalize input
    normalized_attrs = normalize_physical_attributes(physical_attributes)
    static_tensor = (
        torch.tensor(
            [
                normalized_attrs["age"],
                normalized_attrs["is_physically_active"],
                normalized_attrs["weight"],
                normalized_attrs["height"],
                normalized_attrs["alcohol_consumption"],
                normalized_attrs["is_smoker"],
            ],
            dtype=torch.float32,
        )
        .unsqueeze(0)
        .to(device)
    )  # shape: (1, 6)

    # Dummy 24×3 time-series input (can replace with real data)
    series_tensor = torch.zeros((1, 24, 3), dtype=torch.float32).to(device)

    # Inference
    with torch.no_grad():
        output = model(series_tensor, static_tensor)  # shape: (1, 6)

    predicted_blood_values = output.squeeze(0).cpu().numpy()

    return denormalize_blood_values({BLOOD_KEYS[i]: float(predicted_blood_values[i]) for i in range(len(BLOOD_KEYS))})


def simulate_image(organ: str, prompt: str, series: dict, index: float, risks_formatted: str) -> str:
    image_id = round(index * 10) - 1
    return f"images/simulated_{organ}_{image_id}.png"


if __name__ == "__main__":
    phsattributes = {
        "_id": "malaravan",
        "age": 18,
        "is_physically_active": True,
        "weight": 50.5,
        "height": 177.0,
        "alcohol_consumption": 0.0,
        "is_smoker": False,
    }

    blood_values = evaluate_blood_values(phsattributes)
    print("Predicted Blood Values:", blood_values)
