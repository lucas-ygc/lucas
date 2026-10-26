# AGENTS.md — Lucas

## 项目

自定义浅色现代书房风格的静态技术博客。Node.js 22 读取 Markdown 并生成 HTML，没有博客框架、主题系统或自动部署插件。GitHub 仅保存源码，部署目标为自有云服务器。

## 命令

```bash
npm ci
npm run dev      # 本机 127.0.0.1:4000，监听内容与页面变化并刷新浏览器
npm run build    # 静态产物 dist/
npm run preview  # 预览已构建的静态文件
npm test
```

Docker 开发使用 `docker compose up --build -d`，本机端口 8080。没有 Compose 时的命令见 README.md。生产镜像使用 Dockerfile 的 production 阶段，只有 Nginx 与静态文件。

## 目录

- `content/posts/`：分类 / 可选的系列或平台目录 / 文章目录 / `articles/文章名.md` 与 `images/`。每篇文章与其配图放在同一个文章目录，正文用 `../images/...` 引用图片。
- 文章目录可包含 `code/`，配套代码、示例输入和依赖说明在这里维护并运行。文章元数据 `code.files` 明确列出可展示和下载的文件，`code.experiments` 定义实验入口。
- `content/pages/`：独立页面。
- `site/layouts/`：从零编写的 EJS 页面布局。
- `static/terminal/`：样式、交互脚本和图标。
- `static/fonts/`：本地文章楷体字体及授权，正文和文章标题用楷体，代码保持等宽。
- `site/config.json`：站点文案配置。
- `site/series.json`：合集标题、简介与按阅读顺序排列的文章稳定 ID；网页入口 `/series/`，草稿不展示。
- `site/legacy-assets.json`：原 `/img/...` 网址到新图片网址的兼容映射，保留旧链接。
- `site/legacy-posts.json`：旧文章地址到新地址的静态重定向映射，构建时生成跳转页，保留旧链接。
- `docs/article-series-migration.json`：系列与专题目录整理的迁移清单，保留文章稳定 ID。
- `docs/article-bundles.json`：目录迁移清单，包含补充封面和未解决的旧缺图。
- `tools/content.mjs`：元数据、Markdown、代码高亮和目录生成。
- `tools/build.mjs`：页面生成与静态资源复制。
- `tools/experiments.mjs`：实验文件读取、入口生成和 tar.gz 下载包。
- `tools/dev.mjs`：本地 HTTP 服务、文件监听和浏览器刷新。
- `tests/`：内容解析和迁移回归测试。

## 内容约束

- 发布日期使用 `date`，必须是有效日期。
- `abbrlink` 是文章的稳定 ID，原有值不得随意改变。
- 地址保持 `/posts/:abbrlink.html`。重复 ID 必须让构建失败。
- 文章图片输出到 `/posts/:abbrlink/images/`，保持源目录内部结构；`cover` 使用 `../images/...`，必须指向本篇现有图片。
- 整理文章时连同 `articles/` 和 `images/` 一起移动，不重新分离成集中图片库。
- 配套代码连同 `code/` 一起移动；每篇实验自带输入文件和辅助模块，不能依赖其他文章代码目录。`playground/` 只留临时实验。
- `code/` 中的 Markdown 不作为文章，虚拟环境、缓存、数据集和运行产物不自动发布。构建只打包 `code.files`，不会执行代码；草稿的代码页和下载包也不发布。
- 新文章可以指定由字母、数字、短横线、下划线组成的 ID；缺省时从相对路径生成。
- `categories` 与 `tags` 可使用字符串或数组，分类沿用现有拼写。
- `draft: true` 不发布。
- 构建不得改写 Markdown。未知的旧元数据字段可保留但不参与显示。

## 重要约束

- 站点名称使用 Lucas。
- 保持暖米白底、青灰点缀和清晰的楷书中文排版，导航可直接点击，适配手机。
- 不使用外部 CDN 加载页面必需资源。
- 不提交 `node_modules/`、`dist/`、临时构建目录与日志。
- git 操作需用户明确指令，禁止自动 commit / push / deploy。
- CSS 与 JavaScript 注释使用 `/* ... */` 块注释。
- 框架迁移或路由更改后检查既有文章链接与图片，修改构建流程后运行 `npm test` 和 `npm run build`。
