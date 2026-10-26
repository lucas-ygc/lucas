---
title: 口鼻遮挡工程实录：A 附录A-参数字典
date: 2026-08-15 00:00:00
categories: AI-深度学习
tags:
  - 口鼻遮挡
  - 计算机视觉
  - Hi3516CV610
description: 集中记录检测、响应、分割、姿态、时序与 World 参数及其调整影响。
abbrlink: nose-mouth-occlusion-a
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；正文依据 2026-10-12 核对的实现整理。历史实测保留真实日期，教学数字不代表实测；本次未重新执行板端推理。

[返回系列目录](/posts/nose-mouth-occlusion-01.html) · 本篇为 14 章＋4 份附录中的一篇。

## 参数字典的使用约定

下表默认值来自整理时 `FacePolicyConfig`、`WorldReviewConfig` 与平台配置表。设备已保存值可以覆盖仓库默认，实际运行必须先读板端。区间为当前代码校验范围，不代表推荐调参范围；所有识别阈值均为实验规则，未经生产标注集校准。

多数参数的影响相互耦合。例如提高可见率门槛，会让更多部位进入响应融合，但不保证最终遮挡数量单调增加，因为姿态分支和无效 ROI 也参与决策。

## 检测与模型选择

| 名称 | 默认值／范围 | 单位与用途 | 增大与减小的影响 |
| --- | --- | --- | --- |
| `head_model` | 配置 `yolov5s_p34`；缺省回退 `yolov5m` | 决定输入尺寸、输出尺度与 anchors | 枚举值，必须与 head OM 配套 |
| `head_score` | 0.25；0.001～1 | 头部 objectness×head 分数门槛 | 增大减少低分头框，也可能漏小头；减小反之 |
| `head_nms` | 0.45；0.001～1 | 头框 NMS IoU 门槛 | 增大保留更多重叠框；减小更强抑制 |
| `face_score` | 0.6；0.001～1 | YuNet 人脸分数门槛 | 增大减少弱脸候选；减小可能引入误检 |
| `face_nms` | 0.3；0.001～1 | 人脸 NMS IoU 门槛 | 增大保留重叠脸候选；减小更强抑制 |
| `head_padding` | 0.15；0～1 | YuNet 搜索区每侧相对头宽/高扩展比例 | 增大增加上下文，也更容易包含邻人 |

平台 JSON 没有显式写 `face_nms` 时，C++ 默认仍为 0.3；回读的完整 policy 可以包含它。不要把“JSON 中没有写”解释为“功能关闭”。

## PIPNet 响应与局部可靠性

| 名称 | 默认值／范围 | 含义 | 调整影响 |
| --- | --- | --- | --- |
| `peak_min` | 0.08；0～10 | 单点原始响应最小值，低于它为弱点 | 增大更易判弱，也影响姿态/轮廓锚点 |
| `gap_min` | 0.01；0～10 | 峰与次高响应最小差值 | 增大更易判响应歧义；不改变预测坐标 |
| `spread_max` | 0.05；0～1 | 归一化裁剪坐标中的预测分散度上限 | 减小更易判弱，也让参考锚点更严格 |
| `roi_spread_max` | 0.08；0～1 | 区域不稳定标记及部分几何/复核可靠性参考 | 减小更易不稳定；当前不单独否决高覆盖放行 |
| `weak_fraction` | 0.25；0.001～1 | 区域逐点弱条件成立的比例门槛 | 减小更易形成区域弱响应 |

校验要求 `roi_spread_max >= spread_max`。鼻部响应为九点，嘴部为二十点。三项单点条件以 OR 组合，再统计比例，不是先将 peak/gap/spread 求平均后判断。

## 分割与 ROI

| 名称 | 默认值／范围 | 单位与含义 | 调整影响 |
| --- | --- | --- | --- |
| `mask_threshold` | 0.5；0.001～0.999 | 像素概率门槛 | 在 ROI 固定时增大不会增加可见像素 |
| `nose_visible` | 0.6；0～1 | 鼻 ROI 达标覆盖比例 | 增大让鼻部放行更严格 |
| `mouth_visible` | 0.6；0～1 | 嘴 ROI 达标覆盖比例 | 增大让嘴部放行更严格 |
| `roi_padding` | 2；整数 0～16 | 256 坐标系中的膨胀参数 | 增大扩大 ROI，覆盖变化不保证单调，可能触边 |

嘴部面积使用外唇十二点。逐点诊断半径当前硬编码为 2 像素，圆内十三个采样位置；不是这张 policy 表中的可调参数。

## 姿态与轮廓

| 名称 | 默认值／范围 | 单位与用途 | 调整影响 |
| --- | --- | --- | --- |
| `outside_margin` | 0.02；0.001～0.49 | 脸宽比例，轮廓明显越界诊断 | 增大容忍更多诊断越界，当前不否决可见放行 |
| `side_near` | 0.04；0.001～0.49 | 接触带向脸内延伸的脸宽比例 | 增大允许更靠内的点进入接触带 |
| `side_max_outside` | 0.15；0.001～0.49 | 接触带向脸外延伸上限 | 增大容忍更远外偏，也可能接纳漂移 |
| `side_contact_fraction` | 0.5；0.001～1 | 鼻嘴各组位于接触带的最小比例 | 增大侧向候选更严格 |
| `roll_degrees` | 30；1～90 | 度，可靠眼线倾斜绝对值门槛 | 减小更易触发倾斜分流 |
| `pose_action` | `observe` 或 `abnormal` | 姿态是否参与持续异常候选 | observe 仍显示侧向持续，但不作为异常确认 |

旧 PC 参数 `side_offset`、`side_ratio` 不作为当前板端可写 policy 的主侧向触发参数。几何可靠性还包含代码常量，不应以修改 JSON 的方式假定它们可调。

## 时序

| 名称 | 默认值／范围 | 单位 | 调整影响 |
| --- | --- | --- | --- |
| `hold_seconds` | 2；0.01～3600 | 单调观察时间的秒数 | 增大确认更慢，短事件更易被过滤 |
| `track_gap` | 板端 10、PC 默认 2；0.01～3600 | 相邻观测可关联的最大秒数 | 增大容忍慢推理，也增加跨时间误关联风险 |

至少三次观测、IoU≥0.3 为当前代码固定条件。track_gap 不保留已经在某次处理帧中漏检的旧轨迹。

## World 复核

| 名称 | 默认值／范围 | 用途 | 调整影响 |
| --- | --- | --- | --- |
| `review_enabled` | 1；0 或 1 | 第五阶段开关 | 0 时不要求 World 文件参与运行 |
| `review_confidence` | 0.15；0.001～0.999 | 解码候选分数门槛 | 减小会引入更多低分候选和后处理成本 |
| `review_score` | 0.25；0.001～0.999 | 物体证据分数门槛 | 增大证据更严格；主遮挡状态仍不改写 |
| `review_coverage` | 0.6；0.001～1 | 物体框覆盖口鼻 mask 的比例 | 增大要求更多区域被框覆盖 |
| `review_expansion` | 1.6；1～4 | 围绕头框中心放大宽高的倍数 | 增大上下文多、小物体缩放后更小 |
| `review_nms` | 0.45；0.001～1 | 同类框 NMS IoU | 增大保留更多重叠同类框 |
| `review_crop_fallback` | 1；0 或 1 | 整图无充分证据时裁剪补查 | 开启可增加调用次数和延迟 |

要求 `review_confidence <= review_score`。所有证据门槛只影响复核字段，不改写四阶段状态与持续确认。

## 模型路径与运行配置映射

| 调试 models 键 | 持久化字段 | 通常板端路径 |
| --- | --- | --- |
| `head` | `modelPathHead` | `/tmp/mmc/Module/head_yolov5s_p34.om` |
| `yunet` | `modelPathYunet` | `/tmp/mmc/Module/face_detection_yunet_320.om` |
| `pipnet` | `modelPathPipnet` | `/tmp/mmc/Module/pipnet_98.om` |
| `faceocc` | `modelPathFaceOcc` | `/tmp/mmc/Module/faceocc.om` |
| `world` | `modelPathWorld` | `/tmp/mmc/Module/world64.om` |
| `world_metadata` | `worldMetadataPath` | `/tmp/mmc/Module/world64.json` |

`effect`、`model`、`inputImagePath`、`vpuInputChn` 是运行配置，不等同于算法阈值。仓库默认关闭 AI 特效且保留静态测试图片路径；启用实时业务需有意识地设置。旧 `occlusionMeanThreshPermille` 等双模型参数仍可能出现在配置中，但当前五阶段决策使用 `occlusionPolicy`，不能混调。

来源：`FaceOcclusionPolicy.h/.cpp`、`WorldOcclusionReview.h/.cpp`、`StreamNpuDebug.cpp`、`Platform/Params/HI3516CV610_00S/config_table.json`。

---

[上一篇：测试评估与问题复盘](/posts/nose-mouth-occlusion-14.html) · [系列目录](/posts/nose-mouth-occlusion-01.html) · [下一篇：附录B-状态与结果字段](/posts/nose-mouth-occlusion-b.html)
