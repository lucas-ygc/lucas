"""小型 U-Net 的一次训练步。运行方式与练习见 README.md。"""
import torch
from torch import nn
import torch.nn.functional as F

torch.manual_seed(7)
torch.set_num_threads(2)

class TinyUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(nn.Conv2d(3, 8, 3, padding=1), nn.ReLU())
        self.low = nn.Sequential(nn.Conv2d(8, 16, 3, padding=1), nn.ReLU())
        self.dec = nn.Sequential(nn.Conv2d(24, 8, 3, padding=1), nn.ReLU(),
                                 nn.Conv2d(8, 1, 1))

    def forward(self, x):
        skip = self.enc(x)
        low = self.low(F.max_pool2d(skip, 2))
        up = F.interpolate(low, size=skip.shape[-2:], mode='bilinear',
                           align_corners=False)
        return self.dec(torch.cat([skip, up], dim=1))

mask = torch.zeros(2, 1, 32, 32)
mask[:, :, 8:24, 10:22] = 1
images = mask.repeat(1, 3, 1, 1) * 0.7 + torch.rand(2, 3, 32, 32) * 0.2
model = TinyUNet()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
optimizer.zero_grad()
logits = model(images)
assert logits.shape == mask.shape
loss = F.binary_cross_entropy_with_logits(logits, mask)
loss.backward()
optimizer.step()
print(tuple(logits.shape), bool(torch.isfinite(loss)))

with torch.no_grad():
    prediction = model(images).sigmoid() >= 0.5
    truth = mask.bool()
    intersection = (prediction & truth).sum().item()
    union = (prediction | truth).sum().item()
    print('一步训练后合成掩码 IoU:', intersection/union if union else 1.0)
