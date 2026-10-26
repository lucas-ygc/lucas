import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { collectSeries, groupSeries } from '../tools/series.mjs';
import { buildSite, projectRoot } from '../tools/build.mjs';
import os from 'node:os';
import path from 'node:path';

test('合集按配置顺序阅读，只包含已发布文章，导航不泄漏草稿', () => {
  const posts = ['last', 'first'].map(abbrlink => ({ abbrlink, title: abbrlink, path: `/posts/${abbrlink}.html` }));
  const series = collectSeries([{ id: 'course', title: '教程', articles: ['first', 'draft', 'last'] }, { id: 'empty', title: '草稿合集', articles: ['other-draft'] }], posts);
  assert.equal(series.length, 1);
  assert.deepEqual(series[0].posts.map(post => post.abbrlink), ['first', 'last']);
  assert.equal(posts[0].series.previous.path, '/posts/first.html');
  assert.equal(posts[1].series.next.path, '/posts/last.html');
  assert.equal(posts[1].series.previous, null);
  assert.equal(posts[0].series.next, null);
  assert.equal(posts[0].series.total, 2);
  assert.throws(() => collectSeries([{ id: '../bad', title: '错误', articles: [] }], []));
  assert.throws(() => collectSeries([{ id: 'one', title: '重复', articles: ['a', 'a'] }], []));
});

test('静态合集页面、文章标记和目录使用稳定链接，并隐藏草稿', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'lucas-series-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.cp(path.join(projectRoot, 'site/layouts'), path.join(root, 'site/layouts'), { recursive: true });
  await fs.copyFile(path.join(projectRoot, 'site/config.json'), path.join(root, 'site/config.json'));
  await fs.writeFile(path.join(root, 'site/legacy-assets.json'), '{}');
  await fs.writeFile(path.join(root, 'site/series.json'), JSON.stringify([{ id: 'course', title: '合集 <标题>', articles: ['first', 'draft', 'last'] }]));
  for (const directory of ['content/pages', 'static']) await fs.mkdir(path.join(root, directory), { recursive: true });
  for (const id of ['first', 'draft', 'last']) {
    const dir = path.join(root, 'content/posts', id, 'articles');
    await fs.mkdir(dir, { recursive: true });
    await fs.mkdir(path.join(root, 'content/posts', id, 'images'), { recursive: true });
    await fs.writeFile(path.join(dir, 'post.md'), `---\ntitle: ${id}\ndate: 2026-10-12\nabbrlink: ${id}\ncategories: AI-深度学习\ndraft: ${id === 'draft'}\n---\n正文\n`);
  }
  const { files } = await buildSite(root);
  const collection = files.get('/series/course/index.html');
  assert.match(collection, /合集 &lt;标题&gt;/);
  assert.ok(collection.indexOf('/posts/first.html') < collection.indexOf('/posts/last.html'));
  assert.doesNotMatch(collection, /\/posts\/draft/);
  assert.match(files.get('/posts/first.html'), /aria-label="合集阅读顺序"/);
  assert.match(files.get('/posts/first.html'), /href="\/posts\/first.html" aria-current="page"/);
  assert.match(files.get('/index.html'), /class="series-badge"/);
  assert.match(files.get('/series/index.html'), /AI 与深度学习/);
  assert.match(files.get('/posts/first.html'), /href="\/series\/"/);
});

test('合集分类来自已发布文章，分类去重且草稿不参与分组', () => {
  const posts = [
    { abbrlink: 'a', categories: [{ name: 'AI', path: '/categories/ai/' }] },
    { abbrlink: 'b', categories: [{ name: 'AI', path: '/categories/ai/' }, { name: '系统', path: '/categories/system/' }] }
  ];
  const groups = groupSeries(collectSeries([{ id: 'course', title: '课程', articles: ['a', 'draft', 'b'] }], posts));
  assert.deepEqual(groups.map(group => group.name), ['AI', '系统']);
  assert.ok(groups.every(group => group.collections.length === 1));
});
