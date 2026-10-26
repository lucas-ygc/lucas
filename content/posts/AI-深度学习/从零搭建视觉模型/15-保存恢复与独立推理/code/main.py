"""保存加载与精确恢复下一步。运行方式与练习见 README.md。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import torch
from torch import nn
torch.manual_seed(7)
torch.set_num_threads(2)
x,y = torch.randn(4,3),torch.tensor([0,1,0,1])
model = nn.Linear(3,2)
optimizer = torch.optim.SGD(model.parameters(),lr=0.1,momentum=0.9)
def step(net,opt):
    opt.zero_grad()
    loss = nn.functional.cross_entropy(net(x),y)
    loss.backward(); opt.step()
    return loss.item()
step(model,optimizer)
with TemporaryDirectory() as d:
    p = Path(d)/'checkpoint.pt'
    torch.save({'model':model.state_dict(),'optimizer':optimizer.state_dict(),
                'rng':torch.get_rng_state(),'classes':['airplane','automobile']},p)
    state = torch.load(p,weights_only=True)
    restored = nn.Linear(3,2)
    restored.load_state_dict(state['model'])
    resumed = torch.optim.SGD(restored.parameters(),lr=0.1,momentum=0.9)
    resumed.load_state_dict(state['optimizer'])
    torch.testing.assert_close(model(x),restored(x),rtol=0,atol=0)
    step(model,optimizer)
    torch.set_rng_state(state['rng'])
    step(restored,resumed)
    for a,b in zip(model.parameters(),restored.parameters()):
        torch.testing.assert_close(a,b,rtol=0,atol=0)
print('保存加载输出一致；恢复动量后下一步参数完全一致')
