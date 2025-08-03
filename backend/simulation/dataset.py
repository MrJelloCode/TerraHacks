import torch
from neural_net import HealthScoreNet
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset


class OrganHealthDataset(Dataset):
    def __init__(self, data_list):
        self.data = data_list

        self.blood_keys = ["ALT", "AST", "GGT", "Triglycerides", "CRP", "Ferritin"]
        self.physical_keys = ["age", "weight", "sex", "height", "alcohol_consumption", "is_smoker"]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]

        # Convert series_data to [3, 24] float32 tensor
        series = torch.tensor(sample["series_data"], dtype=torch.float32)

        # Convert physical attributes to [6] float32 tensor
        physical = torch.tensor([sample["physical_attributes"][key] for key in self.physical_keys], dtype=torch.float32)

        # Convert blood values to [6] float32 tensor (target)
        blood = torch.tensor([sample["blood_values"][key] for key in self.blood_keys], dtype=torch.float32)

        return {
            "series": series,             # [3, 24]
            "physical": physical,         # [6]
            "blood": blood,               # [6]
        }


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = HealthScoreNet().to(device)
    dataset = OrganHealthDataset(5)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(5):
        total_loss = 0
        for batch in loader:
            series = batch["series"].to(device)  # [B, 24, 3]
            label = batch["label"].to(device)    # [B]

            optimizer.zero_grad()
            out = model(series)
            loss = loss_fn(out, label)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"[Epoch {epoch+1}] Loss: {total_loss/len(loader):.4f}")


    torch.save(model.state_dict(), "health_score_model.pt")
