from pathlib import Path
import argparse
import copy
import random
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms

parser = argparse.ArgumentParser(description='CIFAR-10 飞机/汽车分类基线')
parser.add_argument('--smoke', action='store_true', help='使用构造图片检查流程，不代表真实精度')
parser.add_argument('--download', action='store_true', help='显式允许下载 CIFAR-10')
parser.add_argument('--data', default='data')
parser.add_argument('--output', default='runs')
parser.add_argument('--epochs', type=int, default=5)
args = parser.parse_args()
if args.epochs < 1:
    parser.error('--epochs 必须大于 0')
torch.manual_seed(7)
torch.set_num_threads(2)

class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Linear(16, 2)

    def forward(self, x):
        return self.head(self.features(x).flatten(1))

if args.smoke:
    from torch.utils.data import TensorDataset
    raw = TensorDataset(torch.rand(80,3,32,32), torch.arange(80)%2)
    train_ids, val_ids = list(range(64)),list(range(64,80))
    print('SMOKE: 随机图片，仅检查训练、验证和保存流程')
else:
    raw = datasets.CIFAR10(args.data, train=True, download=args.download,
                           transform=transforms.ToTensor())
    train_ids, val_ids = [], []
    for label in (0, 1):
        ids = [i for i, y in enumerate(raw.targets) if y == label]
        random.Random(7 + label).shuffle(ids)
        train_ids.extend(ids[:1000])
        val_ids.extend(ids[1000:1200])
assert not (set(train_ids) & set(val_ids))
train_loader = DataLoader(Subset(raw, train_ids), batch_size=32,
                          shuffle=True, num_workers=0)
val_loader = DataLoader(Subset(raw, val_ids), batch_size=64,
                        shuffle=False, num_workers=0)
model = TinyCNN()
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

@torch.no_grad()
def evaluate():
    model.eval()
    total_loss = correct = count = 0
    for images, labels in val_loader:
        logits = model(images)
        total_loss += loss_fn(logits, labels).item() * len(labels)
        correct += (logits.argmax(1) == labels).sum().item()
        count += len(labels)
    return total_loss / count, correct / count

best_loss, best_state, best_epoch = float('inf'), None, 0
for epoch in range(1, args.epochs + 1):
    model.train()
    total_loss = count = 0
    for images, labels in train_loader:
        optimizer.zero_grad()
        logits = model(images)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(labels)
        count += len(labels)
    val_loss, val_acc = evaluate()
    print(epoch, total_loss / count, val_loss, val_acc)
    if val_loss < best_loss:
        best_loss = val_loss
        best_state = copy.deepcopy(model.state_dict())
        best_epoch = epoch

Path(args.output).mkdir(parents=True, exist_ok=True)
torch.save({
    'smoke': args.smoke, 'model': best_state, 'epoch': best_epoch,
    'classes': ['airplane', 'automobile'],
    'input': {'size': [32, 32], 'color': 'RGB', 'scale': '0..1'},
    'train_ids': train_ids, 'val_ids': val_ids,
}, Path(args.output) / 'best.pt')

loaded = torch.load(Path(args.output)/'best.pt', weights_only=True)
model.load_state_dict(loaded['model'])
model.eval()
with torch.no_grad():
    probe = torch.zeros(1,3,32,32)
    assert model(probe).shape == (1,2)
print('保存并重新加载:',Path(args.output)/'best.pt','best_epoch:',best_epoch)
