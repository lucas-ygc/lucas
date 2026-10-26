---
title: 嵌入式视觉模型进阶 16：外观特征与 ReID：怎样比较两个目标
date: 2026-10-24 00:00:00
categories: AI-深度学习
tags:
  - 嵌入式视觉模型进阶
  - 计算机视觉
  - 嵌入式部署
description: 通过归一化向量、相似度与运动门控理解外观关联。
abbrlink: edge-vision-16-reid-embeddings
draft: false
cover: ../images/封面.svg
code:
  inline: true
  files:
    - main.py
    - README.md
    - requirements.txt
    - verification.md
    - .gitignore
  experiments:
    - id: practice
      title: 实验：外观特征与 ReID：怎样比较两个目标
      file: main.py
      command: python3 main.py
---

> **第 16 / 30 课。** 前置：[上一课](/posts/edge-vision-15-bytetrack-association.html)。本篇的运行范围以实验说明和验证记录为准，构造样例不代表真实任务精度或板端性能。

## 从类别分数换成特征向量

分类 head 输出有限类别的分数；ReID 编码器输出描述外观的向量。比较两个向量需要统一预处理、权重和特征维度，不能拿不同模型的坐标空间直接计算相似度。

常见做法对向量 L2 归一化，再计算点积，等价于余弦相似度。零向量没有可靠方向，应拒绝而不是除零。相似度也不是天然的同一人概率。

## 外观与运动一起使用

仅靠外观会把穿着相近的不同目标合并，仅靠位置在交叉遮挡时容易交换身份。可以先用运动和类别排除不可能的配对，再在剩余候选中组合几何与外观代价。

代码用两个正交方向构造身份特征，故意交换几何最优匹配，观察外观信息如何恢复关联。它不包含训练好的 ReID 网络，因此不代表真实行人识别效果。

## 特征库不能无条件更新

若每帧把新框特征写入轨迹，错误框会污染历史，随后更容易继续错配。可根据检测质量、遮挡程度、匹配分数和更新时间选择更新，或维护有限长度特征库。

指数滑动平均必须在更新后重新归一化；其系数控制新观测与历史的权衡。长期离开场景后重新识别需要更强的验证策略，不能直接沿用帧间关联阈值。

## 练习与验收

让两个特征越来越相似，比较最佳匹配与次佳匹配差距。再输入全零向量确认被拒绝。真实项目需按不同摄像头、光照和遮挡统计误关联，阈值只在验证集选择。

参考结论：相似度差距过小时应允许不匹配，强制给每个检测一个旧 ID 会隐藏歧义。新增外观模型还会增加裁剪、推理、特征缓存与跨设备数据搬移成本。

## 配套实验与运行记录

```experiment
practice
```

在本篇代码目录执行 `python3 main.py`。依赖安装、可选入口见包内 `README.md`；实际运行结果见 [`verification.md`](/posts/edge-vision-16-reid-embeddings/code/verification.md.html)。下载包包含本课使用的辅助模块与样例。

## 参考与进一步阅读

[原始论文或官方文档](https://arxiv.org/abs/1703.07402)用于核对结构、接口和适用范围。本篇代码是围绕教学目标编写的最小实验；除明确注明的完整入口外，不视为对应论文模型的完整复现。

---

[完整进阶目录](/series/edge-vision-advanced/) · [入门系列](/series/vision-learning/) · [上一篇](/posts/edge-vision-15-bytetrack-association.html) · [下一篇](/posts/edge-vision-17-ptz-follow.html)
