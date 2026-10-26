---
title: 口鼻遮挡工程实录：11 YOLO-World物体复核
date: 2026-08-11 00:00:00
categories: AI-深度学习
tags:
  - 口鼻遮挡
  - 计算机视觉
  - Hi3516CV610
description: 解释固定词表、DFL 解码、整图共享、裁剪补查及物体证据边界。
abbrlink: nose-mouth-occlusion-11
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；正文依据 2026-10-12 核对的实现整理。历史实测保留真实日期，教学数字不代表实测；本次未重新执行板端推理。

[返回系列目录](/posts/nose-mouth-occlusion-01.html) · 本篇为 14 章＋4 份附录中的一篇。

## 为什么增加遮挡物复核

四阶段可能得到“分割低覆盖但关键点响应稳定”的冲突。手或纸巾遮在嘴前时，关键点仍可能预测稳定，因此 `UNCERTAIN` 里包含值得进一步查看的样本。World 为这类情况添加“附近识别到了什么”的证据。

YOLO-World 的研究入口见 [官方仓库](https://github.com/AILab-CVC/YOLO-World)。本项目 PC 使用的权重、接口和导出实现另有具体版本，不能把官方研究方法、Ultralytics 权重和板端固定词表 OM 当作同一个可互换文件。

## 触发条件是确定的

| 四阶段结果 | 当前 World 行为 |
| --- | --- |
| `VISIBLE` | 直接跳过 |
| `NOSE/MOUTH/NOSE+MOUTH_OCCLUSION_SUSPECT` | 复核状态中对应部位 |
| `UNCERTAIN` 且两 ROI 有效、未放行 | 复核低于对应可见阈值的部位 |
| `NO_FACE`、无效 ROI、`POSE`、SIDE、推理错误 | 不触发遮挡物复核 |
| `review_enabled=0` | 全部跳过 |

某个部位是疑似遮挡，另一个部位只是冲突时，当前代码按最终疑似状态包含的部位复核，不自动将所有低覆盖区域都加入。这与 `UNCERTAIN` 分支的行为不同。

## 64 类词表如何变成纯图像模型

PC 导出时用文本编码器计算固定词表特征，并把文本相关计算折叠为常量卷积。板端只输入图片，不需要每帧输入字符串，也不运行完整文本编码器。

`world64.json` 保存类别顺序、英文 prompt、中文 label 及模型元数据。改 label 只改变显示文字；直接改 prompt 字段也不会改变已经编进 OM 的语义。更换识别词表必须重新导出、转换并配套替换模型与元数据。

当前构造器检查 schema=1、class_count=64、input_size=640、reg_max=16，且词条非空、不重复。这些格式检查不是模型和元数据密码学绑定验证，部署仍应核对两个文件的指纹与导出记录。

## 输出与 DFL 解码

板端三个尺度分别为 80×80、40×40、20×20，每个网格有 128 个通道：前 64 个为四边各 16 个 DFL 分桶，后 64 个为类别 logits。每格选得分最高类别，sigmoid 后与检测阈值比较。

某一边距离通过 softmax 分桶期望计算：`d=Σ(k×softmax(logits)[k])`，k 为 0～15。网格中心加 0.5 后结合 stride 8/16/32，将四边距离转换成框。这里没有 YOLOv5 的 anchor 宽高解码。

NMS 只对相同类别互相抑制，最多保留 80 个候选，再去除 padding、还原缩放并加上裁剪原点。手和手臂属于不同类别，可能同时保留。

## 整图共享与裁剪补查

同一帧首次触发时运行整图 World，结果由其他头共享。某个人头没有任何充分物体证据且允许 fallback 时，对其扩为 1.6 倍的头框裁剪，再运行一次。

当前代码条件是 `primary.empty()`：只要已有任一部位的主要物体证据，就不会仅为了补齐另一部位再裁剪。这是具体实现边界，不能表述成“每个缺证据的部位都会补查”。

多个人头共用整图推理后，每头的 `world_ms` 可能只反映其自己的处理阶段。统计整帧成本应使用顶层 `world_review.calls` 与 `total_ms`，不要将每头共享结果误算成多次推理。

## 物体证据如何成立

将物体框映射到同一脸部 256 坐标，重新使用四阶段的鼻嘴凸包和 padding，计算：

```text
region_coverage = 位于物体框内的口鼻 mask 像素数 / 口鼻 mask 总像素数
```

这是物体框覆盖口鼻区域的比例，不是框与 ROI 的 IoU。一个很大的框可以覆盖 100% 嘴 ROI，但 IoU 很小。

默认 score 至少 0.25、覆盖至少 0.6，且支持部位的 `unstable_landmarks=false` 才形成证据；person 与 human face 被排除为遮挡物。0.15 是原始检测显示门槛，必须不高于证据分数门槛。

每个部位以最高分候选作为主要物体，其余候选仍保留。若一框同时覆盖多个待复核区域，代码要求其支持区域的稳定性共同通过。不能只检查其中一个部位就宣称该框已获支持。

## 复核状态与原结论

| `review.status` | 含义 |
| --- | --- |
| `skipped` | 开关关闭或不满足触发条件 |
| `supported` | 至少一个部位存在达到阈值的物体证据 |
| `candidate` | 存在可疑重叠，但分数、覆盖或稳定性不足 |
| `unverified` | 未找到匹配证据 |
| `error` | 复核推理或相关处理失败 |

所有情况都保留原 `state` 和 `persistence`。未检出手不能证明没有手；支持物体也没有自动把冲突状态改成遮挡。二维框重叠没有深度关系，还存在大框误覆盖的可能。

2026-09-21 的三图验证记录为无遮挡跳过、手与纸巾样本显示相应物体，单次第五阶段约 1.21～1.34 秒。这是有限样例与接口联调，不是 64 类准确率报告。

入口：`WorldOcclusionReview.cpp`、`yoloworld_occluder/export_board.py`、`test_review.py`、`GenerateTestTools/npu/CASCADE.md`。

---

[上一篇：跟踪与持续确认](/posts/nose-mouth-occlusion-10.html) · [系列目录](/posts/nose-mouth-occlusion-01.html) · [下一篇：模型转换与海思部署](/posts/nose-mouth-occlusion-12.html)
