# 现代书房设计

按用户选定的浅色效果图实现：暖米白背景、青灰色点缀、楷书标题和正文、细线分隔的文章列表与知识书架。页面仍由原有静态生成器生成，不依赖主题或外部 CDN。

首页精选文章由 `site/config.json` 的 `featuredPost` 指定稳定 ID，清空该值可恢复全部按日期排序。`categoryLabels` 仅调整界面显示名称，不改变文章分类元数据、链接与筛选逻辑。摘要使用文章已有的描述。

## 首页插画

- 使用内置 imagegen 工具生成。
- 项目路径：`static/illustrations/reading-room.png`。
- 参考图：用户选定的浅色现代书房首页效果图，仅用于插画风格与物件参考。
- 最终提示词：

```text
Use case: illustration-story. Asset type: standalone decorative hero illustration for Lucas's modern reading-room technical blog. Reference image is a STYLE AND SUBJECT reference only: match its upper-right delicate sage ink drawing, DO NOT generate the webpage or any UI. Draw four standing technical books, a paper with decorative microchip/circuit lines, small leafy plants, a ceramic mug and a fountain pen. Fine restrained gray-green ink linework with subtle hatching, warm ivory (#f7f5ef) flat background, refined bookish editorial illustration. Wide landscape composition, objects clustered across the center, modest empty margin, no border. No lettering, no text, no logos, no watermark, no webpage elements. The final image is just the isolated illustration on the uniform ivory ground; graceful and calm with no dark fills.
```
