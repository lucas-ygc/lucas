"""CPU 训练、验证选优、最终测试；运行产物默认放在本目录 outputs/。"""
import argparse
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
from dataset import make_dataset, save_image
from model import MLP, SIZE, CLASSES

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "outputs"
PREPROCESS = {"mode": "L", "size": SIZE, "scale": 255, "layout": "NCHW"}


def evaluate(model, loader):
    model.eval()
    total_loss = correct = count = 0
    with torch.no_grad():
        for images, labels in loader:
            logits = model(images)
            total_loss += nn.functional.cross_entropy(logits, labels, reduction="sum").item()
            correct += (logits.argmax(1) == labels).sum().item()
            count += len(labels)
    return total_loss / count, correct / count


def load_model(path):
    data = torch.load(path, map_location="cpu", weights_only=True)
    if data.get("architecture") != "mlp-256-32-2-v1" or data.get("classes") != CLASSES or data.get("preprocess") != PREPROCESS:
        raise ValueError("检查点结构、类别或预处理约定不匹配")
    model = MLP()
    model.load_state_dict(data["model"], strict=True)
    return model.eval(), data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.1)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or not 0 < args.lr < float("inf"):
        parser.error("epochs、batch-size 和有限学习率必须大于 0")
    torch.set_num_threads(1)
    torch.manual_seed(7)
    print(f"{args}")
    args.out.mkdir(parents=True, exist_ok=True)
    train = DataLoader(make_dataset(512, 100), batch_size=args.batch_size, shuffle=True,
                       generator=torch.Generator().manual_seed(42))
    validation = DataLoader(make_dataset(128, 200), batch_size=args.batch_size)
    test = DataLoader(make_dataset(128, 300), batch_size=args.batch_size)
    model = MLP()
    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)
    loss_function = nn.CrossEntropyLoss()
    initial_loss, initial_accuracy = evaluate(model, validation)
    print(f"训练前 val_loss={initial_loss:.4f}, val_accuracy={initial_accuracy:.1%}")
    best_loss = float("inf")
    checkpoint = args.out / "best.pt"
    history = ["epoch,train_loss,val_loss,val_accuracy"]
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = count = 0
        for images, labels in train:
            optimizer.zero_grad()
            logits = model(images)
            loss = loss_function(logits, labels)
            if not torch.isfinite(loss):
                raise RuntimeError("损失非有限值，请检查学习率与输入")
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(labels)
            count += len(labels)
        val_loss, accuracy = evaluate(model, validation)
        train_loss = total_loss / count
        history.append(f"{epoch},{train_loss:.8f},{val_loss:.8f},{accuracy:.8f}")
        print(f"epoch {epoch:02d}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_accuracy={accuracy:.1%}")
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save({"architecture": "mlp-256-32-2-v1", "model": model.state_dict(),
                        "classes": CLASSES, "preprocess": PREPROCESS,
                        "epoch": epoch, "val_loss": val_loss}, checkpoint)
            restored, _ = load_model(checkpoint)
            reference = validation.dataset.tensors[0][:2]
            with torch.no_grad():
                torch.testing.assert_close(model(reference), restored(reference))
    (args.out / "history.csv").write_text("\n".join(history) + "\n")
    best_model, data = load_model(checkpoint)
    test_loss, test_accuracy = evaluate(best_model, test)
    print(f"最佳 epoch={data['epoch']}, test_loss={test_loss:.4f}, test_accuracy={test_accuracy:.1%}")
    # 演示图片来自另一随机种子，不参与训练、选优或最终测试统计。
    demo = make_dataset(2, 400)
    for index, name in enumerate(["horizontal.png", "vertical.png"]):
        save_image(demo.tensors[0][index], args.out / name)
    print(f"保存至 {args.out.resolve()}；只验证合成条纹，不代表真实图片识别能力。")


if __name__ == "__main__":
    main()
