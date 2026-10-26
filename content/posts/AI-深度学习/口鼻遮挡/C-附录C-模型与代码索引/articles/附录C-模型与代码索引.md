---
title: 口鼻遮挡工程实录：C 附录C-模型与代码索引
date: 2026-08-17 00:00:00
categories: AI-深度学习
tags:
  - 口鼻遮挡
  - 计算机视觉
  - Hi3516CV610
description: 固定模型接口、源码入口、许可证来源与实际文件 SHA-256 基线。
abbrlink: nose-mouth-occlusion-c
cover: ../images/封面.png
draft: false
---

> 系列编排日期为 2026 年 8 月；正文依据 2026-10-12 核对的实现整理。历史实测保留真实日期，教学数字不代表实测；本次未重新执行板端推理。

[返回系列目录](/posts/nose-mouth-occlusion-01.html) · 本篇为 14 章＋4 份附录中的一篇。

## 实现基线与证据优先级

本附录记录整理时实际读取的源码与模型文件。文章编排日期属于八月，基线采集时间见下方自动生成记录。没有执行 Git 操作，也没有将工作区状态伪称为某个提交。

发生冲突时，当前执行代码及当前配置优先于早期 README；历史测试数据按当时模型和条件保留。SHA-256 只能标识本地文件内容，不能证明模型准确率或证明它就是某个公开发布版本。

## 模块入口索引

以下 `App/` 为 `application/Apps/Stream/Src/Npu/`，`Shared/` 为 `application/Dependent/shared/`。

| 职责 | 文件及关键符号 |
| --- | --- |
| 五阶段组织 | `App/Common/StreamNpuOcclusionProcessor.cpp`：infer、decodeHeads、onFrame |
| 人脸解码 | `App/Postprocess/YuNet.cpp`：decodeYuNet |
| 关键点解码 | `App/Postprocess/PipNet.cpp`：decodePipNet |
| meanface 邻接 | `App/Postprocess/PipNetMeanfaceData.h` |
| 裁剪约定 | `App/Postprocess/OcclusionCore.h`：faceCrop |
| 区域/几何/融合 | `App/Postprocess/FaceOcclusionPolicy.cpp`：region、posture、outline、lateral、evaluateFace |
| 时序 | 同文件：FaceTracks::assign、observe |
| 第五阶段 | `App/Postprocess/WorldOcclusionReview.cpp`：detect、run |
| 调试协议 | `App/Common/StreamNpuDebug.cpp` |
| 板端资源 | `application/Board/HI3516CV610_00S/Src/BoardNpu.cpp` |
| 持久化默认 | `application/Platform/Params/HI3516CV610_00S/config_table.json` |
| PC 对照 | `Shared/head_pipnet_unet/preview.py`、policy.py、geometry.py |
| 规则回放 | `Shared/head_pipnet_unet/hi3516/check_policy.py`、check_cascade.py |
| 上位机说明 | `GenerateTestTools/npu/README.md`、CASCADE.md |

## 模型契约速查

| 文件 | 输入 | 紧凑输出 |
| --- | --- | --- |
| `head_yolov5s_p34.om` | BGR planar U8，640×640 | FP32，21×80×80 与 21×40×40 |
| `face_detection_yunet_320.om` | BGR planar U8，320×320 | 三尺度 cls/obj/bbox/kps 共十二输出 |
| `pipnet_98.om` | BGR planar U8，256×256 | 三个 98×8×8、两个 980×8×8 |
| `faceocc.om` | BGR planar U8，256×256 | 单通道 256×256 logits |
| `world64.om` | BGR planar U8，640×640 | 三尺度 128×80²、128×40²、128×20² |
| `world64.json` | 与 OM 配套的元数据 | 64 类词表、导出指纹及格式信息 |

以上省略 batch=1。输入同为 BGR 字节，不代表 AIPP 后的颜色和归一化相同。输出形状以当前后处理实际约定为准。

## 模型来源与许可记录

YuNet 的公开入口是 [OpenCV Zoo](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)；PIPNet 方法入口是 [PIPNet](https://github.com/jhb86253817/PIPNet)，本地 ONNX 适配来自项目所记录的 yakhyo/pipnet-onnx 路线；FaceOcc 使用 [FaceExtraction](https://github.com/face3d0725/FaceExtraction) 的原始权重；World 方法入口是 [YOLO-World](https://github.com/AILab-CVC/YOLO-World)，本项目权重通过 Ultralytics 接口使用。

项目保留 FaceOcc MIT 声明、头部检测相关 GPL-3.0 来源记录、Ultralytics AGPL-3.0 与 YOLO-World 官方 GPL-3.0 来源记录。历史 LUVLi 路线保留上游 AGPL-3.0-or-later 与 DU-Net 部分 Apache-2.0 声明。具体代码、权重与数据的许可证应分别查看随附文件，不用一个模型名称替代全部许可核对；本文不分发这些权重或本地人脸样本。

## 复现所需环境与缺口

板端需要对应 Hi3516 SDK、Stream 构建产物、SD 卡模型及正确配置；PC 数值对照依赖各脚本中的 Python/OpenCV/NumPy/ONNX Runtime 或 PyTorch 环境；OM 转换依赖已有 SVP 容器；上位机依赖 Qt。现有 README 记录的机器包版本属于历史环境，不等同于本次重新创建并验证过的锁定依赖。

部分脚本默认读取 `.temp/` 内校准图、导出的原始张量或实板日志，仓库入口存在不等于这些数据齐全。缺失时先准备同规格数据和路径，不使用博客概念封面充当真实校准样本。

本次发现旧文档引用的 `application/Doc/五阶段遮挡复核板端接入.md` 不存在；该引用仅作为历史缺口记录，板端三图与性能描述采用已读到的 CASCADE/README，不宣称补读了缺失报告。

## 当前文件指纹

下表由本地现有文件生成。体积单位为字节，哈希为完整 SHA-256。源码表限定核心链路与转换入口，完整清单另保存在本系列维护记录中。

基线采集：2026-10-12。

### 模型文件

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `application/Platform/Module/HI3516CV610_00S/head_yolov5s_p34.om` | 11724223 | `8af87c017e9b48c9a7bc0300efb26c0914a50e4c87f25190dc2ab94f25644266` |
| `application/Platform/Module/HI3516CV610_00S/head_crowdhuman.om` | 44796121 | `0575f5f7cd3ad0ccf13dde88d5d1a1e9edc0efbf2d7801c0535b2e9797349c21` |
| `application/Platform/Module/HI3516CV610_00S/face_detection_yunet_320.om` | 378408 | `65eb4591ba41e6bb8e50171aae5fe9b37eec4817e362d0abf4448728eb5391ad` |
| `application/Platform/Module/HI3516CV610_00S/pipnet_98.om` | 25412033 | `33bbd8fbe6f371efa4fd5a6d40814cc18c5f5212d0c796d70fc52abe00c3e906` |
| `application/Platform/Module/HI3516CV610_00S/faceocc.om` | 29420017 | `e4120d085157078820931bf30dc7e4abc0e6946d1eb1666c4cfc97092bdeeefc` |
| `application/Platform/Module/HI3516CV610_00S/world64.om` | 26814468 | `39a3be2797354e84daa46ca988586a0a3a47228ad924759793460cebe18a34e1` |
| `application/Platform/Module/HI3516CV610_00S/world64.json` | 6390 | `91b4d1e1757c001e3e533c7439de56b2aabb32e262463d3b15522b907032b570` |

### 核心源码与转换入口

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `application/Apps/Stream/Src/Npu/Common/StreamNpuOcclusionProcessor.cpp` | 25897 | `d6f3d8346711f3e7f9e85b7753413267664184cb64a6c53d226cd3e777374f28` |
| `application/Apps/Stream/Src/Npu/Common/StreamNpuDebug.cpp` | 38786 | `fce81ef675f637083ff84b9c1ca1f86dbb20965790dffcfebf27cd3cd2f416cd` |
| `application/Apps/Stream/Src/Npu/Postprocess/FaceOcclusionPolicy.h` | 1929 | `ac8c3fe9a6a10cf06b397b6374ce25892ca36eb4edd201dc2a9ba9d5025689e4` |
| `application/Apps/Stream/Src/Npu/Postprocess/FaceOcclusionPolicy.cpp` | 31747 | `4be2c456d3787f40af27fedab0928f63f5e2f1ee2f47b09ca9bef02dae3e8dfb` |
| `application/Apps/Stream/Src/Npu/Postprocess/PipNet.cpp` | 7025 | `6f93d7cab4b5f1cbf5357c024fe515b72a7c667f7974a752b04331f49a75be9d` |
| `application/Apps/Stream/Src/Npu/Postprocess/PipNetMeanfaceData.h` | 78970 | `2c3fc71007272fcff910716da16bbb2bab11ee4fa1260856e291278e0f5d3ccd` |
| `application/Apps/Stream/Src/Npu/Postprocess/YuNet.cpp` | 8666 | `521e954b382fdc80e22d2cb60eec67308577ac8e63321a34ae7185296a70ec11` |
| `application/Apps/Stream/Src/Npu/Postprocess/OcclusionCore.h` | 2491 | `965f95fc2841c5d8d74707a8a91e5593425d914db6f0f431d86245292af7eadd` |
| `application/Apps/Stream/Src/Npu/Postprocess/WorldOcclusionReview.h` | 1550 | `681c6e9eb44f4fc04d08f18b172756bc19d38093fdddcac000c2c7b89bf319e0` |
| `application/Apps/Stream/Src/Npu/Postprocess/WorldOcclusionReview.cpp` | 19459 | `800ff61b8b0ba5e4269b595f3ccb9802f526cd5a9af1045ad96c8832e88d7d1d` |
| `application/Board/HI3516CV610_00S/Src/BoardNpu.cpp` | 29394 | `28f6b5168668f5e16dfef12d1139338a3637bb85138a1d5f0f76f56db9dd40fd` |
| `application/Platform/Params/HI3516CV610_00S/config_table.json` | 6061 | `4deacc1a69c7137a98e9b5e5a0aae934a8c4032d22b7d3e9b18502f968bb60a6` |
| `application/Upgrade/Scripts/PackApps.sh` | 1569 | `bbc6f8fa98285067d9be1fd067ad2253a693636f9202058db55e3ecdc10cf953` |
| `SDK/Tools/Npu/YuNet/BuildOm.sh` | 2297 | `aa77689959f9fe7e88b9c7b540bef6ce305a493957a5d9614f56a4925b5cea4d` |
| `SDK/Tools/Npu/YuNet/MakeInput255Onnx.py` | 1580 | `b39870e199fac7a8f5532b7535eb845c2e181d18e5576945ae8314169adabe7d` |
| `SDK/Tools/Npu/YuNet/aipp.cfg` | 236 | `257b1a77512198b43ae1138add42fdc32d82d9cb7bc65902f17c73d041546cd7` |
| `SDK/Tools/Npu/PipNet/BuildOm.sh` | 1794 | `07f9787060e771cfc78169c9a997e3847b87657f52addc9c19e633c5365b085a` |
| `SDK/Tools/Npu/PipNet/aipp.cfg` | 248 | `26adfb2250dfee3cb092caef06329ef6bbf40e70e361f3dcec8e254056ed34ad` |
| `application/Dependent/shared/head_detection_yolov5s/prepare_board.py` | 2427 | `b89b6b2e501637da9cdc8db58e771e7ad82adde172fd4eb0047e7220a175e149` |
| `application/Dependent/shared/head_detection_yolov5s/build_om.sh` | 828 | `eb78e9de450ca36527aae24ffccf39ff73baf5cc89350fb0a2eb6649e04f251c` |
| `application/Dependent/shared/unet_occlusion/hi3516/export_model.py` | 3019 | `e6928ec0e5bc80d74a12fc1b069d83ae259320146f1a19fa26b9bcde88ca3696` |
| `application/Dependent/shared/unet_occlusion/hi3516/build_om.sh` | 936 | `92ebdb8e9e4052dd153d4b7f11d410b13a0289058c43b06eb3d4fafbf2e56cbb` |
| `application/Dependent/shared/yoloworld_occluder/export_board.py` | 7962 | `488dbec2bedc7be3e27464362917ba48df25cd34cf545d608e9b45e4c6ef9c60` |
| `application/Dependent/shared/yoloworld_occluder/build_board.sh` | 1337 | `f029dc9063e2e00e0a8f7dbbee804261ac1400014af42e9045106ff9540d0083` |
| `application/Dependent/shared/yoloworld_occluder/aipp_board.cfg` | 337 | `cc3e2002ea7716c13a724a9eb7dfdb6b70803bde306f571bf5d076fe464e7f70` |
| `GenerateTestTools/npu/CASCADE.md` | 10501 | `67554409ae49744568df5a17706544ccb6a9ee7764336833060606f58cffc837` |
| `GenerateTestTools/npu/README.md` | 2001 | `157335eb0885c635f365e67e2e23337826257fead4f7bcc31d5b80cbab996a6e` |

---

[上一篇：附录B-状态与结果字段](/posts/nose-mouth-occlusion-b.html) · [系列目录](/posts/nose-mouth-occlusion-01.html) · [下一篇：附录D-完整教学样例](/posts/nose-mouth-occlusion-d.html)
