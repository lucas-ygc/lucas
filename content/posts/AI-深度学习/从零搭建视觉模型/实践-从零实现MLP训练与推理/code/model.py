"""自己定义网络结构；梯度交给 PyTorch 自动求导。"""
from torch import nn

SIZE = 16
CLASSES = ["横条纹", "竖条纹"]


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten(start_dim=1)
        self.hidden = nn.Linear(SIZE * SIZE, 32)
        self.relu = nn.ReLU()
        self.output = nn.Linear(32, len(CLASSES))

    def forward(self, images):
        x = self.flatten(images)
        x = self.relu(self.hidden(x))
        return self.output(x)
