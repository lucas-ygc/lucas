# 实际运行记录

日期：2026-10-24。Python 3.13.9，Linux CPU 环境。将本包文件单独复制到临时目录执行，确认没有依赖其他文章目录。

```bash
python3 main.py
```

退出码 0，代码中的断言通过。

```text
7 classes (1, 2, 8, 8) max error 5.21540641784668e-08
7 boxes (1, 4, 8, 8) max error 5.960464477539063e-08
8 classes (1, 2, 8, 8) max error 4.470348358154297e-08
8 boxes (1, 4, 8, 8) max error 5.960464477539063e-08
9 classes (1, 2, 8, 8) max error 4.470348358154297e-08
9 boxes (1, 4, 8, 8) max error 5.960464477539063e-08
```

## 验证范围

默认输入是构造数据或包内样例；只证明本课计算、接口和特定断言通过，不代表真实数据精度或板端性能。

## 环境版本

- torch: 2.13.0
- torchvision: 0.28.0
- numpy: 2.3.5
- onnx: 1.22.0
- onnxruntime: 1.28.0
- scipy: 1.16.3
- OpenCV (cv2): 5.0.0

上表记录可用环境，具体使用的库以 requirements.txt 为准；脚本均在 CPU 执行。

## 运行提示

```text
/tmp/edge-vision-verify-6ml57f39/main.py:17: DeprecationWarning: You are using the legacy TorchScript-based ONNX export. Starting in PyTorch 2.9, the new torch.export-based ONNX exporter has become the default. Learn more about the new export logic: https://docs.pytorch.org/docs/stable/onnx_export.html. For exporting control flow: https://pytorch.org/tutorials/beginner/onnx/export_control_flow_model_to_onnx_tutorial.html
  torch.onnx.export(net,(x,),str(path),input_names=['images'],output_names=['classes','boxes'],opset_version=17,dynamo=False)
```
