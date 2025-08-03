import torch
from neural_net import HealthScoreNet
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset


class HealthDataset(Dataset):
    def __init__(self, series_data, static_data, labels):
        """
        series_data: (N, 24, 3)
        static_data: (N, 6)
        labels: (N, 6)
        """
        self.series_data = torch.tensor(series_data, dtype=torch.float32)
        self.static_data = torch.tensor(static_data, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32)

    def __len__(self):
        return len(self.series_data)

    def __getitem__(self, idx):
        return {
            "series": self.series_data[idx],
            "static": self.static_data[idx],
            "labels": self.labels[idx],
        }

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = HealthScoreNet().to(device)
    dataset = HealthSeriesDataset(5)
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
