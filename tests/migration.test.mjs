import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { readPosts, walk } from '../tools/content.mjs';
import { projectRoot } from '../tools/build.mjs';

test('迁移前的全部文章短链接都保留，文章有标题和有效目录锚点', async () => {
  const expected = JSON.parse(await fs.readFile(new URL('./legacy-routes.json', import.meta.url), 'utf8'));
  const posts = await readPosts(projectRoot);
  const routes = new Set(posts.map(post => post.path.slice(1)));
  for (const route of expected) assert.ok(routes.has(route), `Missing old route: ${route}`);
  for (const post of posts) {
    assert.ok(post.title.trim(), post.path);
    assert.ok(post.cover, `Missing cover: ${post.path}`);
    assert.ok(post.assets.some(asset => asset.path === post.cover), `Missing cover asset: ${post.path}`);
    const ids = [...post.content.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
    const headings = [...post.toc.matchAll(/href="#([^"]+)"/g)].map(match => match[1]);
    for (const heading of headings) assert.ok(ids.includes(heading), `${post.path}#${heading}`);
  }
});

test('文章和配图都归入单篇目录，旧图片地址映射有对应文件', async () => {
  const files = await walk(path.join(projectRoot, 'content/posts'), entry => entry.isDirectory() && entry.name === 'code');
  for (const file of files) {
    const relative = path.relative(path.join(projectRoot, 'content/posts'), file).split(path.sep);
    if (file.endsWith('.md')) assert.equal(relative.at(-2), 'articles', file);
    else assert.ok(relative.includes('images'), file);
  }
  const aliases = JSON.parse(await fs.readFile(path.join(projectRoot, 'site/legacy-assets.json'), 'utf8'));
  const posts = await readPosts(projectRoot);
  const assets = new Set(posts.flatMap(post => post.assets.map(asset => asset.path)));
  for (const [route, source] of Object.entries(aliases)) {
    assert.ok(route.startsWith('/img/'));
    if (source === '/branding/log.png') assert.ok((await fs.stat(path.join(projectRoot, 'static/branding/log.png'))).isFile());
    else assert.ok(assets.has(source), source);
  }
});

test('依赖树不包含旧博客框架或插件', async () => {
  const lock = JSON.parse(await fs.readFile(path.join(projectRoot, 'package-lock.json'), 'utf8'));
  assert.equal(Object.keys(lock.packages).some(name => /(?:^|\/)hexo(?:-|\/|$)/.test(name)), false);
});
