import json
import time

import numpy as np
import torch
from neural_net import EstimateBloodAttributesNet
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from tqdm import tqdm


class BloodEstimationDataset(Dataset):
    def __init__(self, samples):
        """
        samples: list of dicts, each with keys:
        - 'series_data'
        - 'physical_attributes'
        - 'blood_values'
        """
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        # Extract and stack time series data: (24, 3)
        series = np.stack(
            [
                sample["series_data"]["HKQuantityTypeIdentifierHeartRate"],
                sample["series_data"]["HKQuantityTypeIdentifierStepCount"],
                sample["series_data"]["HKQuantityTypeIdentifierRespiratoryRate"],
            ],
            axis=1,
        )  # shape (24, 3)


        # Convert physical attributes: (6,)
        attrs = sample["physical_attributes"]
        physical = np.array(
            [
                attrs["age"],
                attrs["is_physically_active"],
                attrs["weight"],
                attrs["height"],
                attrs["alcohol_consumption"],
                attrs["is_smoker"],
            ],
            dtype=np.float32,
        )


        # Convert blood values: (6,)
        blood = np.array(
            [
                sample["blood_values"]["ALT"],
                sample["blood_values"]["AST"],
                sample["blood_values"]["GGT"],
                sample["blood_values"]["Triglycerides"],
                sample["blood_values"]["CRP"],
                sample["blood_values"]["Ferritin"],
            ],
            dtype=np.float32,
        )

        return {
            "series": torch.tensor(series, dtype=torch.float32),  # (24, 3)
            "physical": torch.tensor(physical, dtype=torch.float32),  # (6,)
            "label": torch.tensor(blood, dtype=torch.float32),  # (6,)
        }





def train_once(data, device):
    model = EstimateBloodAttributesNet().to(device)
    dataset = BloodEstimationDataset(data)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    best_epoch_loss = float("inf")
    best_state_dict = None

    for epoch in range(50):
        model.train()
        total_loss = 0.0
        start_time = time.time()

        for i, batch in enumerate(loader):
            series = batch["series"].to(device)
            physical = batch["physical"].to(device)
            label = batch["label"].to(device)

            optimizer.zero_grad()
            output = model(series, physical)
            loss = loss_fn(output, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if i == 0 and epoch == 0:
                print("\n[SAMPLE OUTPUT]")
                print("Predicted:", output[0].detach().cpu().numpy().round(3))
                print("Target:   ", label[0].detach().cpu().numpy().round(3))

        avg_loss = total_loss / len(loader)
        elapsed = time.time() - start_time
        print(f"[Epoch {epoch + 1}] Avg Loss: {avg_loss:.4f} | Time: {elapsed:.2f}s")

        if avg_loss < best_epoch_loss:
            best_epoch_loss = avg_loss
            best_state_dict = model.state_dict()

    return best_epoch_loss, best_state_dict



if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Using device: {device}")

    with open("./data/training_data.json") as f:
        data = json.load(f)

    print(f"[INFO] Loaded {len(data)} samples.")

    overall_best_loss = float("inf")
    overall_best_state = None

    for run in range(1, 101):  # 100 runs
        print(f"\n========================")
        print(f"[RUN {run}] Starting training...")
        run_loss, run_state = train_once(data, device)

        print(f"[RUN {run}] Best Loss: {run_loss:.4f}")
        if run_loss < overall_best_loss:
            overall_best_loss = run_loss
            overall_best_state = run_state
            print(f"[RUN {run}] ✅ New best overall model found!")

    print(f"\n🎉 Training complete. Best overall loss: {overall_best_loss:.4f}")
    torch.save(overall_best_state, "best_blood_estimation_model.pt")
