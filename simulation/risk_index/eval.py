import torch
from neural_net import HealthScoreNet

from generate_test_data import generate_test_training_sample

# load NN
model = HealthScoreNet()
model.load_state_dict(torch.load("health_score_model.pt"))
model.eval()

input_tensor, _, _ = generate_test_training_sample()
input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension

# Run through model
with torch.no_grad():
    output = model(input_tensor)

print("Predicted health score:", output.item())