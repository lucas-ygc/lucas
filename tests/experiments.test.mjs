import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { buildSite, projectRoot } from '../tools/build.mjs';
import { readPosts, renderMarkdown } from '../tools/content.mjs';

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'lucas-experiments-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  await fs.cp(path.join(projectRoot, 'site/layouts'), path.join(root, 'site/layouts'), { recursive: true });
  await fs.copyFile(path.join(projectRoot, 'site/config.json'), path.join(root, 'site/config.json'));
  await fs.writeFile(path.join(root, 'site/legacy-assets.json'), '{}');
  for (const directory of ['content/posts/lesson/articles', 'content/posts/lesson/images', 'content/posts/lesson/code', 'content/pages', 'static']) await fs.mkdir(path.join(root, directory), { recursive: true });
  const code = path.join(root, 'content/posts/lesson/code');
  await fs.writeFile(path.join(code, 'main.py'), 'print("<script>alert(1)</script>")\n');
  await fs.writeFile(path.join(code, 'README.md'), 'Code instructions');
  await fs.writeFile(path.join(code, 'not-published.txt'), 'local only');
  await fs.mkdir(path.join(code, '.venv'));
  await fs.writeFile(path.join(code, '.venv/example.md'), 'not an article');
  const article = path.join(root, 'content/posts/lesson/articles/lesson.md');
  const document = '---\ntitle: 实验\ndate: 2026-09-23\nabbrlink: lesson\ncode:\n  files: [main.py, README.md]\n  experiments:\n    - id: first\n      title: 实验 01\n      file: main.py\n      command: python3 main.py\n---\n```experiment\nfirst\n```\n';
  await fs.writeFile(article, document);
  return { root, code, article, document };
}

test('文章实验入口、源码页与下载包同源，附属 Markdown 不被当作文章', async t => {
  const { root, code, article, document } = await fixture(t);
  let result = await buildSite(root);
  assert.equal(result.posts.length, 1);
  const html = await fs.readFile(path.join(root, 'dist/posts/lesson.html'), 'utf8');
  assert.match(html, /查看完整代码/);
  assert.match(html, /href="\/posts\/lesson\/code\/main.py.html"/);
  assert.match(html, /data-copy-command="cd &#39;content\/posts\/lesson\/code&#39; &amp;&amp; python3 main.py"/);
  const source = await fs.readFile(path.join(root, 'dist/posts/lesson/code/main.py.html'), 'utf8');
  assert.doesNotMatch(source, /<script>alert\(1\)<\/script>/);
  assert.match(source, /&lt;script&gt;/);
  const archive = gunzipSync(await fs.readFile(path.join(root, 'dist/posts/lesson/code/experiments.tar.gz')));
  assert.ok(archive.includes(Buffer.from('Code instructions')));
  assert.ok(!archive.includes(Buffer.from('local only')));
  await fs.writeFile(path.join(code, 'main.py'), 'print("changed-source")\n');
  result = await buildSite(root);
  assert.match(await fs.readFile(path.join(root, 'dist/posts/lesson/code/main.py.html'), 'utf8'), /changed-source/);
  assert.equal(await fs.readFile(article, 'utf8'), document);
  await fs.writeFile(article, document.replace('title: 实验', 'draft: true\ntitle: 实验'));
  result = await buildSite(root);
  assert.equal(result.posts.length, 0);
  await assert.rejects(fs.access(path.join(root, 'dist/posts/lesson/code/experiments.tar.gz')));
});

test('内嵌源码默认折叠、安全转义并随代码文件更新，保留下载与命令', async t => {
  const { root, code, article, document } = await fixture(t);
  const inlineDocument = document.replace('code:\n', 'code:\n  inline: true\n').replace('      file: main.py', '      file: main.py\n      related_files: [README.md]');
  await fs.writeFile(article, inlineDocument);
  await buildSite(root);
  const output = path.join(root, 'dist/posts/lesson.html');
  let html = await fs.readFile(output, 'utf8');
  assert.equal((html.match(/<details class="experiment-source">/g) || []).length, 2);
  assert.doesNotMatch(html, /<details[^>]*\bopen\b/);
  assert.match(html, /查看完整代码：main.py/);
  assert.match(html, /Code instructions/);
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>alert\(1\)<\/script>/);
  assert.match(html, /下载代码/);
  assert.match(html, /data-copy-command=/);
  await fs.writeFile(path.join(code, 'main.py'), 'print("inline-updated")\n');
  await buildSite(root);
  html = await fs.readFile(output, 'utf8');
  assert.match(html, /inline-updated/);
  assert.equal(await fs.readFile(article, 'utf8'), inlineDocument);
  await fs.writeFile(article, inlineDocument.replace('related_files: [README.md]', 'related_files: [not-published.txt]'));
  await assert.rejects(readPosts(root), /未列出/);
});

test('实验文件必须明确列出，缺失、越界和失效的实验引用阻止构建', async t => {
  const { root, code, article, document } = await fixture(t);
  await fs.writeFile(article, document.replace('files: [main.py, README.md]', 'files: [README.md]'));
  await assert.rejects(readPosts(root), /未列出/);
  await fs.writeFile(article, document.replace('files: [main.py, README.md]', 'files: [../outside.py]'));
  await assert.rejects(readPosts(root), /无效的代码文件路径/);
  await fs.writeFile(article, document);
  await fs.rm(path.join(code, 'main.py'));
  await fs.writeFile(path.join(root, 'outside.py'), 'private');
  await fs.symlink(path.join(root, 'outside.py'), path.join(code, 'main.py'));
  await assert.rejects(readPosts(root), /越出目录/);
  await fs.rm(path.join(code, 'main.py'));
  await assert.rejects(readPosts(root), /ENOENT/);
  assert.throws(() => renderMarkdown('```experiment\nmissing\n```'), /未定义的实验/);
});
