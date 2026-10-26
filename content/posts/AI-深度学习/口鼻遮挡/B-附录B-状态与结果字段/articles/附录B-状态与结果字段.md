---
title: 口鼻遮挡工程实录：B 附录B-状态与结果字段
date: 2026-08-16 00:00:00
categories: AI-深度学习
tags:
  - 口鼻遮挡
  - 计算机视觉
  - Hi3516CV610
description: 按帧、人头、区域、时序和复核层级解释 JSON 与状态含义。
abbrlink: nose-mouth-occlusion-b
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；正文依据 2026-10-12 核对的实现整理。历史实测保留真实日期，教学数字不代表实测；本次未重新执行板端推理。

[返回系列目录](/posts/nose-mouth-occlusion-01.html) · 本篇为 14 章＋4 份附录中的一篇。

## 先看字段处于哪一层

顶层描述一帧或一次运行；`heads[]` 描述每个头部；`heads[].nose/mouth` 描述区域；`heads[].review` 描述附加物体复核。不能把 `report.status=OK` 当作鼻嘴正常，也不能把一个头的复核结论应用给其他头。

调试接口会在处理器原始报告上补充 session、参数及模型指纹。不同入口、错误分支或旧版本可能缺字段，读取时应先检查存在性和 valid，不把缺失数值默认转成零。

## 顶层常用字段

| 字段 | 含义与单位 |
| --- | --- |
| `status`、`error` | 外层处理状态与错误文本 |
| `model` | 历史模型组合标识，名称不保证包含全部阶段 |
| `head_model` | 当前头模型解码类型 |
| `decision_policy` | 当前策略标识，本文为 `unet_first_then_response` |
| `source_size` | 原图宽高，像素 |
| `observed_monotonic` | 处理器观察时刻，秒；不是 UTC |
| `frame_id` | 帧标识；调试层会写入其图像帧编号 |
| `run_id` | 调试推理运行编号，同图重测可以产生新运行 |
| `session` | 调试会话标识 |
| `policy` | 处理器使用的规则值 |
| `parameters` | 调试层记录的完整 policy/models |
| `models` | 调试层模型路径和 `fnv1a64` 指纹 |
| `heads` | 所有人头记录，允许空数组 |
| `timing` | 阶段及整轮耗时，毫秒 |
| `world_review` | 复核开关、总调用数、错误数与整体耗时 |

`timing.head_ms/yunet_ms/pipnet_ms/unet_ms/world_ms` 在对应调用累加，包含输入 planar 转换及模型运行生命周期的计时范围；`world_total_ms` 还包括其复核后处理。`total_ms` 不是采集到浏览器显示的全链路时延。

## 每个人头的主字段

| 字段 | 解释 |
| --- | --- |
| `head_xyxy` | 原图中的头框 `[x1,y1,x2,y2]` |
| `head_score` | 头部检测分数 |
| `face` | 选定脸的信息，无脸时 null |
| `face.bbox_xywh`、`face.score` | 原图脸框与 YuNet 分数 |
| `crop_xywh` | PIPNet/U-Net 共同人脸裁剪 |
| `points` | 98 个原图像素坐标 |
| `peak`、`gap`、`dispersion` | 98 点原始响应、峰差与预测分散度 |
| `state` | 当前主状态，可能含时序升级后的 SIDE 状态 |
| `segmentation_state` | 姿态分流前的区域融合结果 |
| `legacy_state` | 同帧旧规则结果，未做旧规则时序确认 |
| `decision_source` | `UNET_CLEAR`、`INVALID_REGION` 或 `FUSION` |
| `pose_state` | 独立姿态诊断，可能为 FRONT、SIDE、TILTED、SIDE_LEFT/RIGHT、UNKNOWN |
| `unet_ran`、`unet_reason` | U-Net 是否完成运行及阶段原因 |
| `track_id` | 当前短时轨迹 ID |

## 主状态字典

| 状态 | 进入条件 | 持续确认 |
| --- | --- | --- |
| `NO_FACE` | 有头无符合选择条件的脸 | 默认参与异常确认 |
| `ROI_INVALID` | 找到脸但共同裁剪不可用 | 不自动确认遮挡 |
| `INFERENCE_ERROR` | 单头推理、输出或处理失败 | 不自动确认遮挡 |
| `UNCERTAIN` | 局部 ROI 无效或证据冲突，且未被其他当前分支接管 | 不自动确认遮挡 |
| `VISIBLE` | 两个有效区域覆盖均达标 | 不是异常候选 |
| `NOSE_OCCLUSION_SUSPECT` | 鼻部低覆盖且弱响应，最终未被姿态分流 | 默认参与异常确认 |
| `MOUTH_OCCLUSION_SUSPECT` | 嘴部对应条件成立 | 默认参与异常确认 |
| `NOSE+MOUTH_OCCLUSION_SUSPECT` | 两部位对应条件均成立 | 默认参与异常确认 |
| `SIDE_LEFT/RIGHT_CANDIDATE` | 鼻嘴同侧接触条件成立，尚未持续满足门槛 | 由 pose_action 控制异常确认 |
| `SIDE_LEFT/RIGHT_SUSPECTED` | 同方向形态持续满足时间和次数 | side_sustained 为真；confirmed 另看 pose_action |
| `POSE` | 未放行时可靠眼线明显倾斜，且无优先 SIDE 候选 | 由 pose_action 控制 |
| `LANDMARK_UNRELIABLE` | 旧规则的明显轮廓越界 | 当前仅用于 legacy 对照 |

没有头不是 `NO_FACE`，而是没有该头部记录。`CONFIRMED` 是界面可使用的标记，JSON 核心为 `persistence.confirmed` 布尔值，不是此处的独立模型分类。

## 区域与几何字段

| 字段组 | 关键子字段 |
| --- | --- |
| `nose` / `mouth` | valid、reason、pixels、visible_fraction、mean_probability、dispersion_max、unstable_landmarks、response_checked |
| `pipnet.nose/mouth` | peak_mean、gap_mean、dispersion_mean、weak_fraction、weak_ids、suspect |
| `unet_clearance` | valid、clear、reason |
| `posture` | valid、reason、coordinates_valid、coordinates、roll_degrees、nose_offset、mouth_offset、face_width_ratio |
| `outline` | valid、hull_xy、boundary_ids、outside_ids、unreliable，以及鼻嘴有符号距离与越界统计 |
| `lateral` | valid、candidate、side、sides.LEFT/RIGHT 下的鼻嘴中心距离、接触比例、可靠性 |
| `unet_points` | 鼻嘴 point_ids、visible_fractions、valid_count、point_count、mean_visible_fraction、radius_pixels_256 |

ROI reason 主要包括 `landmarks_outside_crop`、`degenerate_region`、`small_or_clipped_region`。`unet_clearance.reason` 成功为 `both_regions_visible`，有效但不足为 `coverage_below_threshold`，无效时带鼻或嘴及具体原因。

## 时序字段

`persistence.duration_seconds` 为当前同状态持续秒数；`observations` 为计入次数；`abnormal_candidate` 表示是否属于当前异常候选集合；`confirmed` 同时要求异常候选、足够时长和至少三次观察；`side_sustained` 专门表示侧向持续满足门槛。

不要从 duration 单独反推 confirmed，也不要把 track_id 相同当作状态从未改变。

## 物体复核字段

| 字段 | 解释 |
| --- | --- |
| `review.base_state/final_state` | 均保留进入复核的原状态 |
| `ran`、`status`、`reason`、`error` | 是否复核、支持程度、跳过或失败原因 |
| `trigger`、`affected_regions` | 疑似遮挡或低可见冲突，及待复核部位 |
| `roi` | 扩大头框的原图 xyxy |
| `input_mode`、`crop_fallback` | 整图/自动策略及实际是否补查 |
| `reused_inference`、`inference_calls` | 是否使用本帧已完成的整图结果及新增调用数 |
| `detections` | 相关检测类别、分数、原图框和 full/crop 来源 |
| `matches` | 每个候选的 eligible、region_coverage、supported_regions、evidence 等 |
| `objects` | 各部位主要物体名称去重后的列表 |
| `world_ms` | 该头复核经过的时间，含共享行为影响 |

`supported` 至少表示一个部位有证据，不保证所有待复核部位都得到证据。需继续检查 `matches[].supported_regions` 和 `evidence`。

## 教学 JSON 片段

```json
{
  "state": "MOUTH_OCCLUSION_SUSPECT",
  "decision_source": "FUSION",
  "unet_clearance": {"valid": true, "clear": false, "reason": "coverage_below_threshold"},
  "nose": {"valid": true, "visible_fraction": 0.9, "response_checked": false},
  "mouth": {"valid": true, "visible_fraction": 0.2, "response_checked": true},
  "persistence": {"duration_seconds": 2.4, "observations": 3, "abnormal_candidate": true, "confirmed": true, "side_sustained": false},
  "review": {"base_state": "MOUTH_OCCLUSION_SUSPECT", "final_state": "MOUTH_OCCLUSION_SUSPECT", "status": "supported"}
}
```

这是删减字段后的教学示例，不是实板导出文件，不能作为完整协议样本直接导入。

---

[上一篇：附录A-参数字典](/posts/nose-mouth-occlusion-a.html) · [系列目录](/posts/nose-mouth-occlusion-01.html) · [下一篇：附录C-模型与代码索引](/posts/nose-mouth-occlusion-c.html)
