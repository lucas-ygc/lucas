# 海思 NPU 转换系列维护记录

文章编排日期：2026-08-01 至 2026-08-16。技术整理和 CPU 验证：2026-10-12。

## 内容与来源

12 章与 4 份附录，限定 Hi3516CV610、Hi3516C V610R001C01SPC020 与 SVP_NNN_PC_V5.0.2.3。依据本地 10 份厂商 PDF、项目脚本和板级实现整理。基线 JSON 保存文档、源码、源模型与教学文件哈希。厂商 PDF、参考提取文本、权重和真实样本均不随博客分发。

## 教学代码与验证

第 12 章包含 6 个可查看及下载文件。源码 ONNX 检查通过，合成图下 12 个输出的 CPU 等价性通过，最大绝对差约 1.103e-6。比较器的 padding、数值门槛、截断、输出名和 dtype 共 5 项检查通过。转换 shell 语法检查通过。本次未执行 ATC、PC 功能仿真或板端推理。站点构建、现有测试和链接检查结果见同目录验证记录。

## 编辑约定

采用 pages:write-page 写作检查要求，遵循博客既有 Markdown、元数据和独立文章目录。源程序路径与历史脚本存在差异时，以当前文件为准，不把旧 MediaConfig 路径当成部署前提。后续 SDK 更新必须重核参数表和文档节号；日期与实测时间分别维护。

## 封面生成

使用 imagegen 技能与内置 image_gen 生成不透明概念插图，每篇保存本地封面副本。插图表示张量经编译进入嵌入式处理器，不是设备照片或测试结果。两幅 SVG 为本地代码绘制。

最终提示词：

```text
Use case: scientific-educational. Asset type: landscape cover illustration for an embedded AI model conversion technical manual. A refined conceptual cutaway of a neural network being compiled: translucent stacked tensor planes and a small connected-node graph on one side, precise orderly transformation paths through a compiler-like glass chamber, resolving into an embedded vision processor on a modest circuit board. Warm ivory paper background, blue-gray technical linework, restrained sage green and copper accents, soft studio lighting, elegant quiet study atmosphere. Wide balanced composition suitable for a blog thumbnail, keep essential elements comfortably within the central area, clean generous negative space. High-quality editorial scientific illustration, detailed but uncluttered. No text, numbers, letters, logos, watermarks, brand markings or fake user interfaces. Not an actual board photograph or benchmark result. Opaque background.
```

## 阅读入口

- [海思NPU模型转换 01 平台工具与文档地图](/posts/hi3516-npu-convert-01.html)
- [海思NPU模型转换 02 搭建转换环境](/posts/hi3516-npu-convert-02.html)
- [海思NPU模型转换 03 拿到模型后的检查](/posts/hi3516-npu-convert-03.html)
- [海思NPU模型转换 04 导出和整理ONNX](/posts/hi3516-npu-convert-04.html)
- [海思NPU模型转换 05 预处理与AIPP](/posts/hi3516-npu-convert-05.html)
- [海思NPU模型转换 06 校准数据与量化](/posts/hi3516-npu-convert-06.html)
- [海思NPU模型转换 07 执行ATC转换](/posts/hi3516-npu-convert-07.html)
- [海思NPU模型转换 08 输出与后处理约定](/posts/hi3516-npu-convert-08.html)
- [海思NPU模型转换 09 PC仿真与精度比对](/posts/hi3516-npu-convert-09.html)
- [海思NPU模型转换 10 板端最小推理闭环](/posts/hi3516-npu-convert-10.html)
- [海思NPU模型转换 11 转换失败与性能排查](/posts/hi3516-npu-convert-11.html)
- [海思NPU模型转换 12 项目案例与交付清单](/posts/hi3516-npu-convert-12.html)
- [海思NPU模型转换 A 附录A文档检索表](/posts/hi3516-npu-convert-a.html)
- [海思NPU模型转换 B 附录BATC与AIPP参数表](/posts/hi3516-npu-convert-b.html)
- [海思NPU模型转换 C 附录C错误现象与排查表](/posts/hi3516-npu-convert-c.html)
- [海思NPU模型转换 D 附录D项目目录及交付模板](/posts/hi3516-npu-convert-d.html)
