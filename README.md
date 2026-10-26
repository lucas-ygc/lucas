# Lucas

自己设计的浅色现代书房风格技术博客。使用 Node.js 读取 Markdown，生成可直接托管的静态 HTML、CSS 和 JavaScript，不依赖博客框架或现成主题。

## 本地开发

需要 Node.js 22 或更新版本：

```bash
npm ci
npm run dev
```

打开 http://127.0.0.1:4000 。修改文章、页面布局、样式或站点配置后，自动重新构建并刷新浏览器。构建失败会保留上一次可用页面，终端显示具体原因。修改 `tools/` 中的构建代码后需重启服务。

```bash
npm run build       # 生成 dist/
npm run preview     # 预览已构建的 dist/，没有开发脚本
npm test            # 内容解析、重复链接、Markdown 和迁移回归检查
```

## Docker 开发

安装了 Compose 时：

```bash
docker compose up --build -d
```

没有 Compose 时：

```bash
docker build --target development -t lucas-blog:dev .
docker run -d --name lucas-blog-preview --init -p 127.0.0.1:8080:4000 \
  --mount type=bind,src="$PWD/content",dst=/app/content,readonly \
  --mount type=bind,src="$PWD/site",dst=/app/site,readonly \
  --mount type=bind,src="$PWD/static",dst=/app/static,readonly \
  lucas-blog:dev
```

打开 http://127.0.0.1:8080 。所有源码只读挂载，保存后自动刷新。更换构建工具或依赖后需要重新构建镜像并重建容器。

停止 / 启动：`docker stop lucas-blog-preview` / `docker start lucas-blog-preview`。

## 写文章

每篇文章都有独立目录，文字放入 `articles/`，图片放入同级的 `images/`：

```text
content/posts/linux开发/makefile语法/
├── articles/
│   └── makefile语法.md
└── images/
    ├── 封面.png
    └── 1.png
```

文章头部示例：

```yaml
---
title: 文章标题
date: 2026-09-23 10:00:00
categories: linux开发
tags:
  - Linux
  - 开发笔记
description: 简短摘要
cover: ../images/封面.png
abbrlink: my-first-note
---
```

正文使用 Markdown，通过 `![说明](../images/图.png)` 引用本篇配图；本地编辑器可以直接预览，移动整篇文章时将整个目录一起移动。

构建后图片地址为 `/posts/短链接/images/图.png`，不会随文章目录重命名而变化。旧 `/img/...` 地址通过 `site/legacy-assets.json` 继续提供访问，该文件映射到稳定的网址，不绑定文章源文件的目录名。代码块可以指定 `c`、`bash`、`python` 等语言以启用代码高亮。

- 既有文章的 `abbrlink` 保留，访问路径仍为 `/posts/短链接.html`。
- 新文章建议自行填写唯一 `abbrlink`，只允许字母、数字、短横线和下划线。未填写时根据文件相对路径生成稳定 ID，此时重命名文件会改变地址。
- 日期必须填写 `date`，格式为 `YYYY-MM-DD` 或带时间的形式。
- `draft: true` 的文章不会发布。
- 重复短链接或分类 / 标签路径冲突会阻止构建。
- 构建只读取内容，不会改写文章。
- `cover` 使用 `../images/封面.png` 等相对路径，构建会验证文件并输出封面元数据。正文页保持现有简洁布局，不额外插入大幅封面。
- 原有 `swiper_index`、`typora-root-url` 等字段保留，但构建器不使用；图片的相对路径不需要依赖编辑器根目录设置。

首页搜索标题、摘要、分类和标签；`/` 聚焦搜索，`Esc` 清空并退出。关闭 JavaScript 时仍可浏览全部文章。

浅色现代书房布局使用暖米白背景、青灰点缀和楷书排版。首页精选文章可在 `site/config.json` 中通过 `featuredPost` 指定；`categoryLabels` 只改变分类显示名称。首页插画在 `static/illustrations/reading-room.png`，生成方式和提示词见 `docs/reading-room-design.md`。

## 目录

```text
content/posts/       分类 / 可选系列或平台 / 文章目录 / articles + images
content/pages/       关于等独立页面
site/layouts/        自己编写的 EJS 页面布局
site/config.json    名称、介绍和站点描述
site/legacy-assets.json  旧图片网址到新网址的映射
docs/               目录迁移记录与封面生成说明
static/terminal/    自定义 CSS、JavaScript 和图标
static/fonts/       文章楷体字体及授权说明
tools/              构建器和本地开发服务器
tests/              回归检查
dist/               构建产物，不提交
```

EJS 仅用于把内容填进自己编写的 HTML；Markdown、YAML 解析和代码高亮由独立库负责。所有页面资源均从本地提供。

## 文章配套代码

学习路线见 [从零搭建视觉模型](docs/vision-learning.md)。每篇文章的代码维护在自己的 `code/` 目录，输入文件、辅助模块和依赖说明随代码一起保存。`playground/` 仅用于临时实验。

在文章 YAML 头部列出文件和实验：

```yaml
code:
  files:
    - main.py
    - sample.ppm
    - requirements.txt
    - README.md
  experiments:
    - id: image-tensor
      title: 实验 01：图片如何变成张量
      file: main.py
      command: python3 main.py
```

在正文需要入口的位置插入：

````markdown
```experiment
image-tensor
```
````

生成的入口提供“查看完整代码、下载代码、复制运行命令”。源码页为 `/posts/:abbrlink/code/文件名.html`，本课下载包为 `/posts/:abbrlink/code/experiments.tar.gz`。代码页与下载包均从 `code/` 读取；修改后重新构建即可同步，不需要维护另一份源码。一个实验的下载入口包含本篇明确列出的全部配套文件。

复制的命令供项目根目录执行；下载用户将 tar.gz 解压到单独文件夹，在解压目录按 README 运行。网页只展示代码，不在浏览器或服务器执行。若浏览器不允许访问剪贴板，可手动选中下方命令复制。

构建只打包 `code.files` 中列出的文件，遗漏、越出目录、无效实验引用会导致构建失败。`code/README.md` 不被当作文章，`draft: true` 同样阻止配套代码页和下载包发布。

文章正文和标题使用本地霞鹜文楷屏幕阅读版的 WOFF2 子集，桌面正文 18px、手机 17px；代码保持等宽字体。字体包含常用汉字和现有文章用字，其他字符回退到系统楷体。字体来源、处理说明和 OFL 授权随文件保存在 `static/fonts/`。

## Gitee + EdgeOne Pages 部署

Gitee 保存源码，EdgeOne Pages 关联仓库后构建并托管网站。项目根目录的 `edgeone.json` 已配置依赖安装命令 `npm ci`、构建命令 `npm run build`、输出目录 `dist` 和 Node.js 22。

1. 将源码推送到自己的 Gitee 仓库，不上传 `node_modules/`、`dist/` 或凭据文件。根目录的 `密码` 文件已由 `.gitignore` 排除。
2. 在 EdgeOne Pages 控制台导入 Git 仓库，选择 Gitee，并完成仓库访问授权。
3. 选择仓库与生产分支，框架选择其他（自定义），项目根目录保持仓库根目录；确认构建参数与 `edgeone.json` 一致。
4. 部署完成后访问平台提供的网址，检查首页、文章、图片、专题合集与代码下载；长期访问可在控制台绑定自己的域名。

只发布 `dist/` 的内容，不能把源码根目录作为输出目录。现有文章继续使用 `/posts/:abbrlink.html`，无需添加仓库名路径，也无需配置单页应用的首页兜底重写。关联仓库后，对所选分支的后续推送会触发平台自动构建部署。

参考：[EdgeOne 配置说明](https://pages.edgeone.ai/document/edgeone-json)。

## 服务器部署（可选）

```bash
docker build --target production -t lucas-blog:production .
docker run -d --name lucas-blog --restart unless-stopped \
  -p 127.0.0.1:8080:80 lucas-blog:production
```

生产镜像仅含 Nginx 和构建后的静态文件。云服务器上为其配置域名、HTTPS 反向代理和入口；上面的端口只对本机开放。没有自动发布或推送命令。

## 内容迁移记录

120 篇文章全部整理为独立目录，原有短链接不变。381 个原图片文件全部保留，共用配图按文章复制；不属于文章的旧站点图标 `log.png` 放在 `static/branding/`。13 篇缺少可用封面的文章使用同一张新生成的临时封面，各自存放在自己的 `images/` 中。

此次修正了 8 处能确定原图位置的引用。目前仍缺少 `AI人工智能深度学习正式篇` 中的 `stride1.png` 原始配图；这是迁移前已有的缺图，没有用生成图片替代技术图示。完整路径对应记录见 `docs/article-bundles.json`，封面生成说明见 `docs/cover-generation.md`。

## 专题合集

合集入口为 `/series/`，目录与展示文案维护在 `site/series.json`。每个合集指定稳定的 `id`、标题、简介和按阅读顺序排列的文章 `abbrlink`；合集网址为 `/series/:id/`。顺序独立于发布日期和源文件夹名称，不需要给文章强加编号。

首页、文章列表与文章正文均提供合集入口。文章内目录默认折叠，上一篇／下一篇按合集顺序跳转。构建只展示非草稿文章，空合集不生成详情页；配置可以提前包含草稿 ID，但应核对拼写。单篇文章只归入一个合集，重复合集 ID 或重复收录会使构建失败。

2026-10-12 整理了 57 个文章目录，迁移明细见 `docs/article-series-migration.json`。移动文章时需保留 `abbrlink`，同时移动 `articles/`、`images/` 与 `code/` 并修正源文件路径引用。

合集页按已发布文章的 `categories` 自动分组，沿用 `categoryLabels` 显示名称。跨分类合集可出现在多个分组中，分类页提供对应合集入口；草稿不参与分类计算。文章顶部路径与封面上方提供所属合集导航。样式链接随 CSS 内容生成版本标识，避免发布后沿用旧样式缓存。
