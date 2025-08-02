import torch
from neural_net import HealthScoreNet

# Load the NN model
model = HealthScoreNet()
model.load_state_dict(torch.load("health_score_model.pt"))
model.eval()


def simulate_blood_values(organ: str, prompt: str, last_known: dict) -> dict:
    # Simple simulation: add random noise to last known values
    # TODO: add negative or positive noise based on the prompt
    # use gemini to evaluate change
    noise = torch.randn_like(torch.tensor(list(last_known.values())))
    return {k: v + n.item() for k, v, n in zip(last_known.keys(), last_known.values(), noise, strict=False)}


def generate_hnn_input_tensor(organ: str, prompt: str, series: dict, blood_values: dict) -> torch.Tensor:
    return torch.tensor.empty()


def evaluate_index_and_risks(organ: str, prompt: str, series: dict, blood_values: dict) -> dict:
    input_tensor, _, _ = generate_hnn_input_tensor(organ, prompt, series, blood_values)

    input_tensor = input_tensor.unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)

    index = output["index"].item()
    risks = output["risks"]
    return index, risks


def simulate_image(organ: str, prompt: str, series: dict, index: float, risks_formatted: str) -> str:
    image_id = round(index * 10) - 1
    return f"images/simulated_{organ}_{image_id}.png"
