"""增强、Dropout 与早停。运行方式与练习见 README.md。"""
import torch
from torch import nn
torch.manual_seed(7)
image = torch.arange(12).reshape(1,3,4).float()/11
flipped = image.flip(-1)
assert torch.equal(flipped.flip(-1),image)
print('原图第一行:',image[0,0].tolist(),'翻转:',flipped[0,0].tolist())
drop = nn.Dropout(0.5)
x = torch.ones(1000)
train = drop(x)
drop.eval()
assert torch.equal(drop(x),x)
print('训练时置零比例:',float((train==0).float().mean()))
# 示意验证损失，用于观察早停，不是实测训练曲线。
values = [0.9,0.7,0.6,0.64,0.68,0.7]
best, stale, best_epoch = float('inf'),0,0
for epoch,value in enumerate(values,1):
    if value < best: best,stale,best_epoch = value,0,epoch
    else: stale += 1
    if stale >= 2:
        print('早停轮次:',epoch,'应恢复轮次:',best_epoch)
        break
assert best_epoch == 3 and epoch == 5
