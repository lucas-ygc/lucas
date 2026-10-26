# 云服务器部署记录

部署日期：2026-09-24。公网访问地址：http://111.230.151.39/ 。当前使用 HTTP 和 IP 地址访问，尚未配置域名与 HTTPS。

## 运行方式

- 系统：Ubuntu 24.04，Docker。
- 容器：`lucas-blog`，镜像：`nginx:stable-alpine`。
- 端口：宿主机 80 → 容器 80。
- 重启策略：`unless-stopped`。
- 发布目录：`/home/ubuntu/lucas-blog/releases/20261013-isp-complete/public`。
- Nginx 配置：`/home/ubuntu/lucas-blog/config/nginx.conf`，来自项目 `docker/lucas.nginx.conf`。
- 页面与配置均以只读挂载方式提供给容器。

本地执行 `npm test` 和 `npm run build` 后，只上传 `dist/` 的静态产物；服务器不执行文章配套 Python 代码，也不存放项目凭据文件。`draft: true` 的文章、代码页和下载包不会发布。

本次采用服务器 Nginx 镜像挂载本地构建产物，没有在服务器拉取源码或运行 Node.js 构建。后续修改本地文章不会自动同步到服务器，需要明确执行一次新的发布。

## 维护

登录服务器后：

```bash
sudo docker ps --filter name=lucas-blog
sudo docker logs --tail 50 lucas-blog
sudo docker exec lucas-blog nginx -t
sudo docker restart lucas-blog
```

发布更新时使用新的独立版本目录，先验证静态产物和 Nginx 配置，再将容器挂载切换到新目录；保留上一版目录供回退。不要把未完成上传的目录直接作为线上页面目录。

本地凭据文件 `密码` 已加入 `.gitignore` 和 `.dockerignore`。不在本文记录账号密码。

## 2026-09-28 基础概念文章正式发布

本次以原线上版本为基础，只更新 `posts/vision-foundations-pixels-tensors.html` 和对应 `images/封面.png`。文章补齐四道折叠答案、易错记录、完成日期与后续学习说明；封面改为浅色书房风格的六色像素与 RGB 通道网格插画。

旧发布目录 `/home/ubuntu/lucas-blog/releases/20260924-1044/public` 保留，旧容器以 `lucas-blog-backup-20260924` 名称停止保存。新版本继续使用 `lucas-blog`、80 端口与 `unless-stopped` 重启策略。

## 2026-10-06 图片如何变成张量正式发布

本次基于上一版复制出独立发布目录 `20261006-image-tensor/public`，更新正式文章、六道折叠参考答案、配套代码页与下载包，以及首页、分类、标签和归档等入口。文章稳定地址为 `/posts/vision-01-image-tensor.html`，原发布日期与 ID 保持不变，文内记录学习完成日期。

封面替换为六色像素卡片转为 RGB 通道网格的浅色书房插画，文件名仍为 `images/封面.png`。生成记录见 [封面提示词](image-tensor-cover-generation.md)。

发布前通过六道示例代码运行、`npm test` 与 `npm run build`，服务器 Nginx 配置及文章检查通过。上一版目录 `20260928-foundations/public` 保留，对应旧容器停止并保存为 `lucas-blog-backup-20261006`，可用于回退。

## 2026-10-06 MLP 入门发布

发布地址：`/posts/vision-mlp-basics.html`。第一题答案与实际练习总结默认折叠，第二至四题留待后续完成；发布不代表整章学习完结。两个配套实验、源码页与下载包同步发布，CNN 继续保持草稿。

本次基于 `20261006-image-tensor/public` 创建独立版本 `20261006-mlp/public`，更新 MLP 文章与资产、首页、分类、标签和归档入口。新增书房风格的 MLP 封面，文件为本篇 `images/封面.png`，提示词见 [生成记录](mlp-cover-generation.md)。

测试、构建、独立下载包运行和服务器配置检查通过。旧容器以 `lucas-blog-backup-before-mlp` 名称停止保存，上一版目录保留供回退。

## 2026-10-12 CNN 章节发布

新增 `/posts/vision-tiny-cnn.html`，记录阅读完成日期，包含四道默认折叠的复习参考答案、书房风格封面及配套代码页、下载包。更新首页、分类、标签和归档入口。封面保存在本篇 `images/封面.png`，生成提示词见 [CNN 封面记录](cnn-cover-generation.md)。

新版本 `20261012-cnn/public` 基于上一版复制后覆盖本次产物。旧容器停止保留为 `lucas-blog-backup-before-cnn`，旧发布目录 `20261006-mlp/public` 保留供回退。网站测试、构建、CNN 四题验证与独立代码包运行通过，服务器配置及文章检查通过。

下一章《让模型开始学习：损失、梯度与训练循环》已在本地准备，仍为草稿，配套代码不会发布。本次也没有覆盖线上 MLP 正文，其 2026-10-12 补充答案仍为本地更新。

## 2026-10-12 ISP 输出文章发布

发布 `/posts/isp-output-model-input.html`，补充 NV12 与 4:2:0 的关系、NV12／NV21 的 UV 顺序、每像素平均 1.5 字节，以及图像像素数量与色度采样数量的区别。四道练习仍待完成。封面采用暖米白书房中的 Y／UV 平面与 RGB 网格插画，生成记录见 [封面提示词](isp-output-cover-generation.md)。

基于 `20261012-cnn/public` 创建 `20261012-isp-output/public`，仅更新本篇正文、图片与页面入口。入口按线上已有文章加本篇共 126 篇生成，避免将其他本地文章的未发布地址列入导航；其他文章正文和资产保持原线上版本。前两篇 ISP 文章仍为草稿。

`npm test`、`npm run build`、服务器 Nginx 配置检查通过；公网正文、封面、NV12 布局图与首页均和发布产物一致，前两篇草稿返回 404。上一版目录保留，旧容器停止保存为 `lucas-blog-backup-before-isp-output`，可用于回退。

## 2026-10-12 全量文章与专题合集发布

整理 57 个文章目录，正文、图片和配套代码一起移动，修正路径引用，169 篇源文章完整保留。迁移记录见 `article-series-migration.json`。全部 166 篇非草稿文章同步上线，包括海思 NPU 转换 16 篇与口鼻遮挡 18 篇；三个既有草稿保持未发布。既有文章、配图和代码页网址均保持不变。

新增 `/series/` 合集书架及六个合集详情页：首页侧栏、主导航、文章列表和文章正文均有入口；正文内合集目录默认折叠，支持按阅读顺序切换章节。配置保存在 `site/series.json`，草稿不会出现在公开目录中。

发布目录为 `20261012-collections/public`。通过差异文件传输生成完整构建副本，逐项校验全部 1229 个文件的 SHA-256，再逐一通过服务器 HTTP 校验。`npm test` 四组测试与 `npm run build` 通过，共 166 篇文章、340 个页面。内部链接检查未发现新增失效链接；旧文的 `stride1.png` 缺图仍为历史迁移清单已记录的问题。

上一版 `20261012-isp-output/public` 保留，旧容器停止保存为 `lucas-blog-backup-before-all-articles`，可用于回退。

本次公网直连核验通过：首页、六个合集页面、海思与口鼻遮挡文章、封面、代码下载包和样式均与本地构建一致；三个草稿地址返回 404。

## 2026-10-12 合集分类与文章入口调整

合集页按已发布文章分类分组，分类页增加相关合集入口。文章顶部路径显示所属合集，合集目录移至封面上方。CSS 链接加入内容哈希版本，避免更新后继续使用缓存中的旧样式。抽查原线上海思第 12 篇的主导航与合集面板均存在，尚未复现用户所述入口消失现象；本次调整增强入口可见性，不将缓存或布局位置视作已确认根因。

13 项测试、构建和新增链接检查通过，166 篇文章、340 页保持不变。新发布目录 `20261012-collections-categories/public`；服务器静态文件及 HTTP 内容校验覆盖全部 1229 个文件。旧容器保留为 `lucas-blog-backup-before-collection-categories`，上一版 `20261012-collections/public` 可用于回退。

## 2026-10-13 ISP 全系列参考答案与发布

ISP 三篇全部正式发布，保留原有日期字段与稳定 ID。第一篇三道、第二篇四道参考答案原已齐全，本次补齐第三篇四道答案，共 11 道，全部默认折叠。第三篇补充 NV12 容量、RGB24 stride 偏移、reshape／换轴／类型转换的区别，以及 NV12 到模型输入的完整步骤与最终形状。前两篇分别使用本篇已有 Bayer 排列、ISP 处理概览 SVG 作为封面。

合集 `/series/isp-basics/` 自动显示三篇及正确阅读顺序；正文的下一篇链接同步补充。13 项测试、构建与三篇链接检查通过，共 168 篇正式文章、346 页。服务器逐项校验 1237 个文件及其 HTTP 内容。其他草稿保持原状态。

新版本为 `20261013-isp-complete/public`，旧版 `20261012-collections-categories/public` 保留；旧容器保存为 `lucas-blog-backup-before-isp-complete`，可用于回退。
