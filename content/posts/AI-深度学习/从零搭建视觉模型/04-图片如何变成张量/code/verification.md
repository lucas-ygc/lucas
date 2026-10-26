# 图片如何变成张量运行验证

2026-09-23 在当前开发机器上实际执行，以下为脚本的标准输出。

- Python：3.13.9
- PyTorch：2.13.0+cu130
- NumPy：2.3.5
- Pillow：10.4.0
- 计算设备：CPU

## 默认 6 像素图片

```text
原始图片: mode=RGB, size(W,H)=(3, 2)
处理后图片: mode=RGB, size(W,H)=(3, 2)
NumPy HWC: shape=(2, 3, 3), dtype=uint8
左上角 RGB: [255, 0, 0]
Tensor HWC: shape=(2, 3, 3), dtype=torch.uint8
Tensor CHW: shape=(3, 2, 3), dtype=torch.uint8
CHW 左上角 RGB: [255, 0, 0]
float CHW: shape=(3, 2, 3), dtype=torch.float32, range=[0.0000, 1.0000]
模型输入 NCHW: shape=(1, 3, 2, 3), dtype=torch.float32, device=cpu
输入左上角 RGB: [1.0, 0.0, 0.0]
缩放前的 R 通道:
[[255   0   0]
 [255   0 255]]
缩放前的 G 通道:
[[  0 255   0]
 [255   0 128]]
缩放前的 B 通道:
[[  0   0 255]
 [255   0   0]]
```

## 缩放至宽 320、高 224

```text
原始图片: mode=RGB, size(W,H)=(3, 2)
处理后图片: mode=RGB, size(W,H)=(320, 224)
NumPy HWC: shape=(224, 320, 3), dtype=uint8
左上角 RGB: [255, 0, 0]
Tensor HWC: shape=(224, 320, 3), dtype=torch.uint8
Tensor CHW: shape=(3, 224, 320), dtype=torch.uint8
CHW 左上角 RGB: [255, 0, 0]
float CHW: shape=(3, 224, 320), dtype=torch.float32, range=[0.0000, 1.0000]
模型输入 NCHW: shape=(1, 3, 224, 320), dtype=torch.float32, device=cpu
输入左上角 RGB: [1.0, 0.0, 0.0]
```

## 灰度图片输入

使用临时的 2×1 灰度图片，像素值为 0、128，验证显式转为 RGB 后的形状和数值范围。

```text
原始图片: mode=L, size(W,H)=(2, 1)
处理后图片: mode=RGB, size(W,H)=(2, 1)
NumPy HWC: shape=(1, 2, 3), dtype=uint8
左上角 RGB: [0, 0, 0]
Tensor HWC: shape=(1, 2, 3), dtype=torch.uint8
Tensor CHW: shape=(3, 1, 2), dtype=torch.uint8
CHW 左上角 RGB: [0, 0, 0]
float CHW: shape=(3, 1, 2), dtype=torch.float32, range=[0.0000, 0.5020]
模型输入 NCHW: shape=(1, 3, 1, 2), dtype=torch.float32, device=cpu
输入左上角 RGB: [0.0, 0.0, 0.0]
缩放前的 R 通道:
[[  0 128]]
缩放前的 G 通道:
[[  0 128]]
缩放前的 B 通道:
[[  0 128]]
```

另外验证了不存在的图片路径和非正整数尺寸：均返回清晰错误，退出码为 2。

这份记录是示例代码验证结果；第一、二题的实际练习总结保留在文章中。

## 文章目录迁移验证

代码已迁入本篇 `code/`，示例输入与辅助模块都在当前目录。2026-09-23 将生成的 tar.gz 下载包解压到独立临时目录后运行本课全部实验，执行成功；无需访问 `playground/` 或其他文章目录。

## 2026-10-06 完结验证

文章六道折叠参考答案在 CPU 上逐段运行，输出与文中记录一致。第三题检查三种输入尺寸、float32、CPU、数值范围与原图橙色；第四题检查共享内存与独立副本；第五题检查 permute 和 reshape 的像素差异；第六题检查两图批次与原图保持不变。后四题为复习参考答案，不代表逐题提交的个人作业记录。
