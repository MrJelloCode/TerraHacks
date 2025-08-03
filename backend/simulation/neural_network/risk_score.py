import json
import time
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from neural_net import RiskScoreNet


class RiskScoreDataset(Dataset):
    def __init__(self, samples, num_risks=10):
        self.samples = samples
        self.num_risks = num_risks

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        blood = np.array([
            sample["blood_values"]["ALT"],
            sample["blood_values"]["AST"],
            sample["blood_values"]["GGT"],
            sample["blood_values"]["Triglycerides"],
            sample["blood_values"]["CRP"],
            sample["blood_values"]["Ferritin"],
        ], dtype=np.float32)

        index = float(sample["index"])

        risks = np.zeros(self.num_risks, dtype=np.float32)
        for r in sample["risks"]:
            if 0 <= r < self.num_risks:
                risks[r] = 1.0

        return {
            "blood": torch.tensor(blood),
            "index": torch.tensor(index).float(),
            "risks": torch.tensor(risks),
        }


def train_once(data, device, num_risks=10):
    model = RiskScoreNet().to(device)
    dataset = RiskScoreDataset(data, num_risks=num_risks)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    loss_index_fn = nn.MSELoss()
    loss_risks_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    best_epoch_loss = float("inf")
    best_state_dict = None

    for epoch in range(5):
        model.train()
        total_loss = 0.0
        start_time = time.time()

        for i, batch in enumerate(loader):
            blood = batch["blood"].to(device)
            index = batch["index"].to(device)
            risks = batch["risks"].to(device)

            optimizer.zero_grad()
            pred_index, pred_risks = model(blood)

            loss_index = loss_index_fn(pred_index, index)
            loss_risks = loss_risks_fn(pred_risks, risks)
            loss = loss_index + loss_risks

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            if i == 0 and epoch == 0:
                print("\n[SAMPLE OUTPUT]")
                print("Pred Index: ", pred_index[0].item(), " | Target: ", index[0].item())
                print("Pred Risks: ", pred_risks[0].detach().cpu().numpy().round(2))
                print("Target Risks:", risks[0].detach().cpu().numpy())

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

    for run in range(1, 101):
        print(f"\n========================")
        print(f"[RUN {run}] Starting training...")
        run_loss, run_state = train_once(data, device)

        print(f"[RUN {run}] Best Loss: {run_loss:.4f}")
        if run_loss < overall_best_loss:
            overall_best_loss = run_loss
            overall_best_state = run_state
            print(f"[RUN {run}] ✅ New best overall model found!")

    print(f"\n🎉 Training complete. Best overall loss: {overall_best_loss:.4f}")
    torch.save(overall_best_state, "best_risk_score_model.pt")
