import torch
from neural_network.neural_net import EstimateBloodAttributesNet
from neural_network.neural_net import RiskScoreNet
from normalization import denormalize_blood_values
from normalization import normalize_blood_values
from normalization import normalize_physical_attributes

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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

blood_model = EstimateBloodAttributesNet().to(device)
blood_model.load_state_dict(torch.load("best_blood_estimation_model.pt", map_location=device))
blood_model.eval()

risk_model = RiskScoreNet().to(device)
risk_model.load_state_dict(torch.load("best_risk_score_model.pt", map_location=device))
risk_model.eval()


def evaluate_blood_values(physical_attributes: dict) -> dict:
    """
    Given physical attributes, predict blood values using a pre-trained model.
    Assumes a dummy series input for now (can be replaced with real time-series).
    """
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

    # Dummy 24x3 time-series input (can replace with real data)
    series_tensor = torch.zeros((1, 24, 3), dtype=torch.float32).to(device)

    # Inference
    with torch.no_grad():
        output = blood_model(series_tensor, static_tensor)  # shape: (1, 6)

    predicted_blood_values = output.squeeze(0).cpu().numpy()

    return denormalize_blood_values({BLOOD_KEYS[i]: float(predicted_blood_values[i]) for i in range(len(BLOOD_KEYS))})


def evaluate_risk_score(blood_values: dict[str, float]) -> dict:
    """
    Given real (denormalized) blood values, predict index and risk vector
    using a pre-trained RiskScoreNet.
    """
    # Normalize input blood values
    normalized_blood = normalize_blood_values(blood_values)
    blood_tensor = torch.tensor([list(normalized_blood.values())], dtype=torch.float32).to(device)  # shape: (1, 6)

    # Inference
    with torch.no_grad():
        index_pred, risks_pred = risk_model(blood_tensor)  # index: (1,), risks: (1, 10)

    # Extract and convert
    index_score = float(index_pred.item())  # still normalized
    risks_probs = risks_pred.squeeze(0).cpu().numpy()  # shape (10,)
    risks_binary = (risks_probs > 0.5).astype(int)  # Convert to binary vector

    return {
        "index_score": round(index_score, 4),
        "risks": [risk_mapping[i] for i in range(len(risk_mapping)) if risks_binary[i] == 1],
    }


def full_evaluation(physical_attributes: dict) -> dict:
    blood_values = evaluate_blood_values(physical_attributes)
    return evaluate_risk_score(blood_values)


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

    risk_score = evaluate_risk_score(blood_values)
    print("Risk Score:", risk_score)
