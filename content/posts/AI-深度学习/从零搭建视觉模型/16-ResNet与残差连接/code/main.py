"""残差分支形状与投影。运行方式与练习见 README.md。"""
import torch
from torch import nn
torch.manual_seed(7)
torch.set_num_threads(2)
class Block(nn.Module):
    def __init__(self,cin,cout,stride=1):
        super().__init__()
        self.main = nn.Sequential(nn.Conv2d(cin,cout,3,stride,padding=1),nn.ReLU(),nn.Conv2d(cout,cout,3,padding=1))
        self.skip = nn.Identity() if cin==cout and stride==1 else nn.Conv2d(cin,cout,1,stride)
    def forward(self,x):
        main,skip = self.main(x),self.skip(x)
        assert main.shape == skip.shape
        return torch.relu(main+skip)
x = torch.randn(2,8,16,16,requires_grad=True)
for cout,stride in [(8,1),(16,2)]:
    block = Block(8,cout,stride)
    y = block(x)
    y.mean().backward()
    assert torch.isfinite(x.grad).all()
    print('input',tuple(x.shape),'output',tuple(y.shape),'skip',type(block.skip).__name__)
