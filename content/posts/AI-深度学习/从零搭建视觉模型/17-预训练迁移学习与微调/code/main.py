"""冻结主干与 BatchNorm 状态。运行方式与练习见 README.md。"""
import torch
from torch import nn
torch.manual_seed(7)
torch.set_num_threads(2)
# 随机初始化的小主干，仅验证冻结机制，不宣称迁移学习精度。
backbone = nn.Sequential(nn.Linear(4,8),nn.BatchNorm1d(8),nn.ReLU())
head = nn.Linear(8,2)
for p in backbone.parameters(): p.requires_grad_(False)
x = torch.randn(16,4)+2
y = torch.arange(16)%2
before_mean = backbone[1].running_mean.clone()
backbone.train(); backbone(x)
assert not torch.equal(before_mean,backbone[1].running_mean)
backbone.eval()
before = {k:v.clone() for k,v in backbone.state_dict().items()}
head_before = head.weight.detach().clone()
opt = torch.optim.SGD(head.parameters(),lr=0.1)
opt.zero_grad()
nn.functional.cross_entropy(head(backbone(x)),y).backward()
opt.step()
for k,v in backbone.state_dict().items(): assert torch.equal(before[k],v)
assert not torch.equal(head_before,head.weight)
print('requires_grad=False 仍会更新训练模式 BN；eval 后主干固定，分类头更新')
