"""Patch、token 与 ViT 前向计算。运行方式与练习见 README.md。"""
import torch
from torch import nn

torch.manual_seed(7)
torch.set_num_threads(2)

class TinyViT(nn.Module):
    def __init__(self):
        super().__init__()
        self.patch = nn.Conv2d(3, 32, kernel_size=8, stride=8)
        self.position = nn.Parameter(torch.zeros(1, 16, 32))
        self.encoder = nn.TransformerEncoderLayer(
            d_model=32, nhead=4, dim_feedforward=64,
            dropout=0.0, batch_first=True,
        )
        self.head = nn.Linear(32, 2)

    def forward(self, x):
        if x.shape[-2:] != (32, 32):
            raise ValueError('This teaching model requires 32x32 input')
        tokens = self.patch(x).flatten(2).transpose(1, 2)
        tokens = self.encoder(tokens + self.position)
        return self.head(tokens.mean(dim=1))

model = TinyViT().eval()
with torch.no_grad():
    output = model(torch.rand(2, 3, 32, 32))
assert output.shape == (2, 2)
print(tuple(output.shape))
