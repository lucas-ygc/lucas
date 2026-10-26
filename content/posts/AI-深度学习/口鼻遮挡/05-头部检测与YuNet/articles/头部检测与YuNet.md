---
title: 口鼻遮挡工程实录：05 头部检测与YuNet
date: 2026-08-05 00:00:00
categories: AI-深度学习
tags:
  - 口鼻遮挡
  - 计算机视觉
  - Hi3516CV610
description: 核对 YOLOv5s-P34、YuNet 的输出解码、分数、NMS 与人脸选择。
abbrlink: nose-mouth-occlusion-05
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；正文依据 2026-10-12 核对的实现整理。历史实测保留真实日期，教学数字不代表实测；本次未重新执行板端推理。

[返回系列目录](/posts/nose-mouth-occlusion-01.html) · 本篇为 14 章＋4 份附录中的一篇。

## 为什么先检测头，再检测脸

只靠人脸检测会丢失“有头但看不到脸”这一信息。头部检测提供分析对象与短时跟踪框，YuNet 再在局部区域找脸。没有脸时保留 `NO_FACE`，而不是直接让对象从结果中消失。

代价是增加一个模型，也引入头部漏检这一入口风险。头模型漏检后，后面的网络没有机会纠正。因此评估必须统计头部召回，不能只对成功裁出的人脸计算准确率。

## 本地使用的两个头模型

| 特性 | YOLOv5m-CrowdHuman | YOLOv5s-P34-CrowdHuman |
| --- | --- | --- |
| 配置名 | `yolov5m` | `yolov5s_p34` |
| 输入 | 640×384 | 640×640 |
| 输出尺度 | stride 8、16、32 | stride 8、16 |
| 每个尺度通道 | 3 anchors × 7 = 21 | 3 anchors × 7 = 21 |
| 类别 | person、head | person、head |

每个 anchor 的 7 个值为框参数 4 个、objectness 1 个、类别 2 个。当前板端读取原始 logits。P34 的发布 ONNX 曾输出已经解码的 `[1,24000,7]`，转换准备脚本则截取两个卷积输出，板端再解码。两种输出不能混用。

当前 OM 为 `[1,21,80,80]` 和 `[1,21,40,40]`。21 来自每格三个 anchor，每个 anchor 七个数；不是 21 个类别。两组 anchor 常量固定在主流程 `decodeHeads()`，更换训练模型时必须一起检查。

## YOLOv5 头框解码

设网格坐标为 `(gx,gy)`、步长为 s、anchor 宽高为 `(aw,ah)`：

```text
cx = (2×sigmoid(tx) − 0.5 + gx) × s
cy = (2×sigmoid(ty) − 0.5 + gy) × s
w  = (2×sigmoid(tw))² × aw
h  = (2×sigmoid(th))² × ah
score = sigmoid(objectness) × sigmoid(head_logit)
```

当前实现还要求 head logit 高于 person logit，随后以默认 `head_score=0.25` 筛选。分数较低可能是小头、侧面、遮挡、光照或模型误检，没有单一原因。

NMS 在模型坐标中先执行，再映射并裁切回原图。提前裁切会改变框面积与 IoU，在图像边缘产生不同抑制结果。候选排序后最多保留 30000 个进入筛选，NMS 最多保留 300 个；这不是“只支持两个人”，PC 工具的展示人数限制也不能当成板端限制。

## IoU 与 NMS 算例

两个 100×100 框水平错开 20 像素，交集为 80×100，IoU 为 `8000/(10000+10000−8000)=0.667`。默认头 NMS 阈值 0.45，较低分框会被抑制。

NMS 阈值越低，重叠目标越容易被合并；越高，重复框越容易保留。多人拥挤场景应同时观察漏掉相邻头部和保留重复头框两类错误。

## YuNet 的十二个输出

YuNet 用 stride 8、16、32 三个尺度，每个尺度有分类、objectness、框回归和五点输出，共十二个输出。当前输入 320 时，对应网格为 40×40、20×20、10×10。每个尺度框回归有 4 个值，五点输出有 10 个值。

输出按 `[1,H×W,C]` 空间展平，而不是随意当作 NCHW。当前分类和 objectness 已经过 sigmoid，不能再做一次。解码分数为：

```text
score = sqrt(clamp(cls,0,1) × clamp(obj,0,1))
cx = (gx + dx) × stride
cy = (gy + dy) × stride
w = exp(dw) × stride
h = exp(dh) × stride
```

默认 `face_score=0.6`、`face_nms=0.3`。YuNet 原始模型与示例见 [OpenCV Zoo 的 YuNet 目录](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)；本文具体输出解释以本地 `YuNet.cpp` 和生产 320 OM 为准。

## 一头多脸候选怎么处理

扩大头框可能把旁边的人脸也包含进来。当前代码将 YuNet 框映射回原图，仅保留中心位于原始头框内的候选，选择最高分人脸。没有符合条件的候选即保留 `NO_FACE`。

这是一条几何选择规则，不是人脸身份识别。两头重叠、头框不准或误检时，仍可能选错。调试时需同时显示原头框、扩大搜索区、候选脸框和最终脸框，单看最终关键点很难找到归属错误。

YuNet 的五点在早期预览中用于画双眼、鼻尖和嘴角，当前精细鼻嘴分析使用 PIPNet98；不能把两种点位索引或用途混在一起。

## 检测阶段的验证清单

同图依次核对模型输入、原始输出顺序、anchor/stride、分数计算、NMS、逆变换和候选选择。模型路径与 `head_model` 必须配对；YuNet 必须是 320 版本。修改阈值后首先核对目标数量和框归属，再解释后续状态变化。

源码：`StreamNpuOcclusionProcessor.cpp::decodeHeads()`、`YuNet.cpp::decodeYuNet()`；转换来源：`head_detection_yolov5s/prepare_board.py` 与其 README。

---

[上一篇：图像预处理与坐标转换](/posts/nose-mouth-occlusion-04.html) · [系列目录](/posts/nose-mouth-occlusion-01.html) · [下一篇：PIPNet98关键点与响应](/posts/nose-mouth-occlusion-06.html)
