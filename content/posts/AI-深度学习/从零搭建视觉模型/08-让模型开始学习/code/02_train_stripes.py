"""用合成横竖条纹学习训练循环；仅 CPU，不下载或写入数据。"""
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader


def make_dataset(count, seed):
    generator = torch.Generator().manual_seed(seed)
    images = torch.empty((count, 3, 32, 32), dtype=torch.float32)
    labels = torch.empty(count, dtype=torch.long)
    for index in range(count):
        label = index % 2  # 0=横条纹，1=竖条纹；两类数量相同（count 为偶数）。
        image = torch.rand((3, 32, 32), generator=generator) * 0.15
        position = torch.randint(4, 24, (1,), generator=generator).item()
        width = torch.randint(3, 6, (1,), generator=generator).item()
        if label == 0:
            image[:, position:position + width, :] += 0.75
        else:
            image[:, :, position:position + width] += 0.75
        images[index] = image
        labels[index] = label
    return TensorDataset(images, labels)


class TinyCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)
        self.flatten = nn.Flatten(start_dim=1)
        self.classifier = nn.Linear(8 * 16 * 16, 2)

    def forward(self, images):
        features = self.conv(images)
        features = self.relu(features)
        features = self.pool(features)
        features = self.flatten(features)
        scores = self.classifier(features)
        return scores


def evaluate(model, loader, loss_function):
    model.eval()
    total_loss = 0.0
    correct_count = 0
    sample_count = 0
    with torch.no_grad():
        for images, labels in loader:
            scores = model(images)
            loss = loss_function(scores, labels)
            predictions = scores.argmax(dim=1)
            batch_count = labels.shape[0]
            total_loss += loss.item() * batch_count
            correct_count += (predictions == labels).sum().item()
            sample_count += batch_count
    return total_loss / sample_count, correct_count / sample_count


def main():
    torch.set_num_threads(1)  # 小实验限制 CPU 线程数，避免线程开销。
    torch.manual_seed(7)
    train_data = make_dataset(256, seed=100)
    validation_data = make_dataset(64, seed=200)
    train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
    validation_loader = DataLoader(validation_data, batch_size=32, shuffle=False)

    model = TinyCNN()
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    epochs = 20
    initial_loss, initial_accuracy = evaluate(model, validation_loader, loss_function)
    print(f"训练前验证: loss={initial_loss:.4f}, accuracy={initial_accuracy:.1%}")

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        sample_count = 0
        for images, labels in train_loader:
            optimizer.zero_grad()
            scores = model(images)
            loss = loss_function(scores, labels)
            loss.backward()
            optimizer.step()

            batch_count = labels.shape[0]
            total_loss += loss.item() * batch_count
            sample_count += batch_count

        training_loss = total_loss / sample_count
        validation_loss, accuracy = evaluate(model, validation_loader, loss_function)
        print(f"epoch {epoch + 1:02d}: train_loss={training_loss:.4f}, "
              f"val_loss={validation_loss:.4f}, val_accuracy={accuracy:.1%}")

    print("这只是合成条纹任务的验证结果，不代表能识别真实场景。")


if __name__ == "__main__":
    main()
