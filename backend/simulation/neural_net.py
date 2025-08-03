import torch
from torch import nn


class EstimateBloodAttributesNet(nn.Module):
    def __init__(self):
        super().__init__()

        # Time-series branch (24 x 3 -> conv1d)
        self.series_branch = nn.Sequential(
            nn.Conv1d(in_channels=3, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),  # (B, 64, 1)
            nn.Flatten(),             # (B, 64)
        )

        # Static branch (6 attributes -> dense)
        self.static_branch = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
        )

        # Combined head
        self.combined_head = nn.Sequential(
            nn.Linear(64 + 64, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 6),  # [ALT, AST, GGT, TRI, CRP, FERRITIN]
        )

    def forward(self, series_input, static_input):
        """
        series_input: (B, 24, 3)
        static_input: (B, 6)
        output: (64, 6)
        """
        x_series = series_input.permute(0, 2, 1)  # → (B, 3, 24)
        series_out = self.series_branch(x_series)
        static_out = self.static_branch(static_input)
        combined = torch.cat([series_out, static_out], dim=1)
        return self.combined_head(combined)
