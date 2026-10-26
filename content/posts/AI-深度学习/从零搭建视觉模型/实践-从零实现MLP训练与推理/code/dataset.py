"""生成独立随机种子的条纹样本；训练与图片推理使用相同量化。"""
import torch
from PIL import Image
from torch.utils.data import TensorDataset
from model import SIZE


def make_dataset(count, seed):
    generator = torch.Generator().manual_seed(seed)
    images = torch.empty(count, 1, SIZE, SIZE)
    labels = torch.arange(count, dtype=torch.long) % 2
    for index, label in enumerate(labels):
        image = torch.rand(SIZE, SIZE, generator=generator) * 0.15
        position = torch.randint(1, SIZE - 4, (1,), generator=generator).item()
        width = torch.randint(2, 5, (1,), generator=generator).item()
        if label.item() == 0:
            image[position:position + width, :] += 0.75
        else:
            image[:, position:position + width] += 0.75
        images[index, 0] = (image * 255).round() / 255
    return TensorDataset(images, labels)


def save_image(tensor, path):
    values = (tensor.reshape(-1) * 255).round().to(torch.uint8).tolist()
    image = Image.new("L", (SIZE, SIZE))
    image.putdata(values)
    image.save(path)


def load_image(path):
    with Image.open(path) as source:
        image = source.convert("L")
        if image.size != (SIZE, SIZE):
            raise ValueError(f"本实验只接受 {SIZE}×{SIZE} 图片，收到 {image.size}")
        values = list(image.getdata())
    return torch.tensor(values, dtype=torch.float32).reshape(1, 1, SIZE, SIZE) / 255
