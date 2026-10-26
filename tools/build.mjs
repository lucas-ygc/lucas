import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import ejs from 'ejs';
import { readPosts, parseDocument, renderMarkdown, formatDate, plainText, url, walk } from './content.mjs';
import { createCodeArchive } from './experiments.mjs';
import { collectSeries, groupSeries } from './series.mjs';

export const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function legacyPostRedirect(target) {
  return `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=${target}">
<link rel="canonical" href="${target}">
<title>文章已迁移</title>
</head>
<body>
<p>这篇文章已迁移到 <a href="${target}">新地址</a>，页面会自动跳转。</p>
<script>location.replace(${JSON.stringify(target)});</script>
</body>
</html>
`;
}

export async function buildSite(root = projectRoot) {
  const config = JSON.parse(await fs.readFile(path.join(root, 'site/config.json'), 'utf8'));
  const posts = await readPosts(root);
  let definitions = [];
  try { definitions = JSON.parse(await fs.readFile(path.join(root, 'site/series.json'), 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const series = collectSeries(definitions, posts);
  let styleVersion = '';
  try { styleVersion = createHash('sha256').update(await fs.readFile(path.join(root, 'static/terminal/site.css'))).digest('hex').slice(0, 12); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const group = type => {
    const groups = new Map();
    const paths = new Map();
    for (const post of posts) for (const item of post[type]) {
      if (paths.has(item.path) && paths.get(item.path) !== item.name) throw new Error(`分类或标签路径冲突: ${item.name}`);
      paths.set(item.path, item.name);
      if (!groups.has(item.name)) groups.set(item.name, { ...item, posts: [], length: 0 });
      const entry = groups.get(item.name);
      if (!entry.posts.includes(post)) { entry.posts.push(post); entry.length++; }
    }
    return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
  };
  const categories = group('categories');
  const tags = group('tags');
  const site = { posts, categories, tags, series, seriesGroups: groupSeries(series), categoriesByCount: [...categories].sort((a, b) => b.length - a.length), tagsByCount: [...tags].sort((a, b) => b.length - a.length) };
  const templates = new Map();
  for (const file of await walk(path.join(root, 'site/layouts'))) {
    if (file.endsWith('.ejs')) templates.set(path.relative(path.join(root, 'site/layouts'), file).replace(/\.ejs$/, '').split(path.sep).join('/'), ejs.compile(await fs.readFile(file, 'utf8'), { filename: file }));
  }
  const files = new Map();
  const page = (route, template, data = {}) => {
    const context = {
      config, site, page: { title: '', description: '', path: route, ...data },
      url, formatDate, plainText, styleVersion,
      truncate: (text, { length }) => text.length <= length ? text : text.slice(0, length - 1) + '…',
    };
    context.partial = (name, locals = {}) => templates.get(name)({ ...context, ...locals });
    const body = templates.get(template)(context);
    const output = route.endsWith('/') ? `${route}index.html` : route;
    if (files.has(output)) throw new Error(`页面路径重复: ${output}`);
    files.set(output, templates.get('layout')({ ...context, body }));
  };
  page('/', 'index', { type: 'home' });
  page('/series/', 'series', { title: '专题合集', type: 'series' });
  for (const collection of series) page(collection.path, 'series', { title: collection.title, description: collection.description, type: 'series', collection });
  page('/archives/', 'archive', { title: '归档', type: 'archive' });
  const archivePaths = new Set();
  for (const post of posts) {
    const [year, month] = post.date.split('-');
    archivePaths.add(`${year}/`);
    archivePaths.add(`${year}/${month}/`);
  }
  for (const archive of archivePaths) {
    const [year, month] = archive.split('/');
    page(`/archives/${archive}`, 'archive', { title: `${year}${month ? '-' + month : ''} 归档`, type: 'archive', year, month });
  }
  posts.forEach((post, index) => page(post.path, 'post', { ...post, type: 'post', prev: posts[index - 1], next: posts[index + 1] }));
  for (const post of posts) for (const source of post.code.files) {
    if (source.path) page(source.path, 'code', { type: 'code', title: `${source.name} · 配套代码`, post, source });
  }
  for (const type of ['categories', 'tags']) {
    page(`/${type}/`, 'page', { title: type === 'tags' ? '标签' : '工作目录', type });
    for (const item of site[type]) {
      const layout = type === 'tags' ? 'tag' : 'category';
      page(item.path, layout, { title: item.name, type: layout, [layout]: item.name, posts: item.posts });
    }
  }
  for (const file of await walk(path.join(root, 'content/pages'))) {
    if (!file.endsWith('.md')) continue;
    const name = path.relative(path.join(root, 'content/pages'), file).replace(/\.md$/, '').split(path.sep).join('/');
    const { metadata, body } = parseDocument(await fs.readFile(file, 'utf8'), name);
    page(`/${name}/`, 'page', { title: metadata.title || name, type: name, ...renderMarkdown(body) });
  }
  page('/404.html', 'page', { title: '没有找到这个页面', type: 'error', content: '<p>这条路径暂时没有内容。</p><p><a href="/">回到文章列表 →</a></p>' });

  const staging = path.join(root, '.dist-next');
  const output = path.join(root, 'dist');
  const previous = path.join(root, '.dist-previous');
  await fs.rm(staging, { recursive: true, force: true });
  await fs.cp(path.join(root, 'static'), staging, { recursive: true });
  for (const post of posts) {
    if (post.code.files.length) {
      const target = path.join(staging, post.code.download);
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.writeFile(target, createCodeArchive(post.code.files));
    }
    for (const asset of post.assets) {
      const target = path.join(staging, asset.path);
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.copyFile(path.join(root, asset.source), target);
    }
  }
  const legacyAssets = JSON.parse(await fs.readFile(path.join(root, 'site/legacy-assets.json'), 'utf8'));
  for (const [route, source] of Object.entries(legacyAssets)) {
    const target = path.join(staging, route);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.copyFile(path.join(staging, source), target);
  }
  for (const [route, html] of files) {
    const target = path.join(staging, route);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, html);
  }
  let legacyPosts = {};
  try { legacyPosts = JSON.parse(await fs.readFile(path.join(root, 'site/legacy-posts.json'), 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  for (const [route, target] of Object.entries(legacyPosts)) {
    const dest = path.join(staging, route);
    await fs.mkdir(path.dirname(dest), { recursive: true });
    await fs.writeFile(dest, legacyPostRedirect(target));
    try {
      await fs.access(path.join(staging, target));
    } catch {
      console.warn(`[legacy-posts] 目标页面不存在，重定向会失效: ${target}`);
    }
  }
  await fs.rm(previous, { recursive: true, force: true });
  try { await fs.rename(output, previous); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  await fs.rename(staging, output);
  await fs.rm(previous, { recursive: true, force: true });
  console.log(`Built ${posts.length} articles, ${files.size} pages → dist/`);
  return { posts, files };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  buildSite().catch(error => { console.error(error.message); process.exitCode = 1; });
}
