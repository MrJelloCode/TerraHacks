from torch import nn


class HealthScoreNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
        )

        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=64,
            num_layers=1,
            batch_first=True,
        )

        self.head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),      # Output range: [0, 1]
        )

    def forward(self, x):
        # watching x for [batch_size, 24, 3]

        batch_size = x.size(0)  # noqa: F841

        x = self.encoder(x)  # [batch_size, 24, 64]
        _, (h_n, _) = self.lstm(x)  # h_n: [1, batch_size, 64]
        h_final = h_n[-1]  # [batch_size, 64]

        out = self.head(h_final)  # [batch_size, 1]
        return out.squeeze(1)     # [batch_size]
