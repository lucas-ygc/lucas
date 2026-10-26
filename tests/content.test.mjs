import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { parseDocument, normalizeDate, renderMarkdown, normalizeAsset, readPosts } from '../tools/content.mjs';

test('文章日期保持原样，拒绝无效日期', () => {
  const { metadata, body } = parseDocument('---\ntitle: 测试\ndate: 2023-02-27 14:47:39\nabbrlink: "0"\n---\n正文', 'test.md');
  assert.equal(metadata.date, '2023-02-27 14:47:39');
  assert.equal(metadata.abbrlink, '0');
  assert.equal(body, '正文');
  assert.equal(normalizeDate(metadata.date, 'test.md'), metadata.date);
  assert.throws(() => normalizeDate('2023-02-30', 'test.md'));
  assert.throws(() => normalizeDate(undefined, 'test.md'));
});

test('章节锚点唯一、目录可跳转，代码不会被当成 HTML', () => {
  const { content, toc } = renderMarkdown('# 中文标题\n\n## 中文标题\n\n## 中文标题-1\n\n```html\n<script>alert(1)</script>\n```');
  assert.match(content, /id="中文标题"/);
  assert.match(content, /id="中文标题-1"/);
  assert.match(content, /id="中文标题-1-1"/);
  assert.match(toc, /href="#中文标题-1"/);
  assert.doesNotMatch(content, /<script>alert/);
  assert.match(content, /class="highlight"/);
});

test('兼容旧文章图片路径，同时保留外部图片', () => {
  assert.equal(normalizeAsset('../../../img/网络/图.png'), '/img/网络/图.png');
  assert.equal(normalizeAsset('../../..../../../img/网络/图.png'), '/img/网络/图.png');
  assert.equal(normalizeAsset('https://example.com/a.png'), 'https://example.com/a.png');
  assert.equal(normalizeAsset('plot.png', '/posts/abc.html'), '/posts/abc/plot.png');
  assert.equal(normalizeAsset('../images/图.png', '/posts/abc.html'), '/posts/abc/images/图.png');
  assert.throws(() => normalizeAsset('../images/../../outside.png', '/posts/abc.html'));
  const { content } = renderMarkdown('![说明](../../../img/test.png)');
  assert.match(content, /src="\/img\/test.png"/);
  const bundled = renderMarkdown('![配图](../images/图.png)\n\n[下载](../images/附件.pdf)\n\n<img src="../images/图.png">', '/posts/abc.html').content;
  assert.match(bundled, /\/posts\/abc\/images\//);
  assert.doesNotMatch(bundled, /\.\.\/images/);
});

test('重复短链接让构建失败，草稿不会发布，读取不会改写文章', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'lucas-content-test-'));
  const directory = path.join(root, 'content/posts/example/articles');
  await fs.mkdir(directory, { recursive: true });
  await fs.mkdir(path.join(root, 'content/posts/example/images'), { recursive: true });
  const document = '---\ntitle: 测试\ndate: 2026-09-23\nabbrlink: abc\n---\n正文';
  try {
    await fs.writeFile(path.join(directory, 'first.md'), document);
    await fs.writeFile(path.join(directory, 'draft.md'), '---\ndraft: true\n---\n草稿');
    assert.equal((await readPosts(root)).length, 1);
    assert.equal(await fs.readFile(path.join(directory, 'first.md'), 'utf8'), document);
    await fs.writeFile(path.join(directory, 'second.md'), document);
    await assert.rejects(readPosts(root), /短链接重复/);
  } finally { await fs.rm(root, { recursive: true, force: true }); }
});
