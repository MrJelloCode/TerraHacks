# import torch
# import torch.nn as nn
# from transformers import TimeSeriesTransformerConfig, TimeSeriesTransformerModel


# class OrganIndexNet(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.config = TimeSeriesTransformerConfig(
#             input_size=3,               # 3 features per time step
#             context_length=24,          # 24 time steps
#             prediction_length=0,
#             d_model=32,
#             encoder_layers=2,
#             num_heads=4,
#             num_time_features=0,
#             lags_sequence=[1]           # required, but we keep it safe
#         )
#         self.model = TimeSeriesTransformerModel(self.config)
#         self.pool = nn.AdaptiveAvgPool1d(1)  # [B, d_model, T] → [B, d_model, 1]

#         self.head = nn.Sequential(
#             nn.Linear(self.config.d_model, 1)
#         )


#     def forward(self, series):
#         """
#         series: [B, 24, 3]
#         """
#         # Transpose to [B, 3, 24] = [B, input_size, context_length]
#         x = series.permute(0, 2, 1)

#         B, C, T = x.shape

#         # Required dummy inputs
#         past_observed_mask = torch.ones_like(x)
#         past_time_features = torch.zeros(B, 0, T).to(x.device)

#         out = self.model(
#             past_values=x,
#             past_time_features=past_time_features,
#             past_observed_mask=past_observed_mask
#         ).last_hidden_state  # [B, d_model, T]

#         pooled = self.pool(out).squeeze(-1)  # [B, d_model]
#         return self.head(pooled).squeeze(-1)  # [B]



import torch.nn as nn

class HealthScoreNet(nn.Module):
    def __init__(self):
        super(HealthScoreNet, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU()
        )

        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=64,
            num_layers=1,
            batch_first=True
        )

        self.head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),      # Output range: [0, 1]
        )

    def forward(self, x):
        # x: [batch_size, 24, 3]
        # batch_size = x.size(0)

        x = self.encoder(x)  # [batch_size, 24, 64]
        _, (h_n, _) = self.lstm(x)  # h_n: [1, batch_size, 64]
        h_final = h_n[-1]  # [batch_size, 64]

        out = self.head(h_final)  # [batch_size, 1]
        return out.squeeze(1)     # [batch_size]
