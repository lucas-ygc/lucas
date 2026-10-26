import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import yaml from 'js-yaml';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import { readExperiments, experimentCard } from './experiments.mjs';

export const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
export const plainText = value => String(value ?? '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
export const url = value => encodeURI('/' + String(value).replace(/^\/+/, '')).replace(/#/g, '%23').replace(/\?/g, '%3F');

export function parseDocument(text, filename) {
  const match = text.replace(/^\uFEFF/, '').match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) throw new Error(`${filename}: 缺少文章头部元数据`);
  const metadata = yaml.load(match[1], { schema: yaml.JSON_SCHEMA });
  if (!metadata || typeof metadata !== 'object' || Array.isArray(metadata)) throw new Error(`${filename}: 元数据必须是键值对象`);
  return { metadata, body: text.replace(/^\uFEFF/, '').slice(match[0].length) };
}

export function normalizeDate(value, filename) {
  const date = String(value ?? '').match(/^(\d{4})-(\d{2})-(\d{2})(?:$|[ T])/);
  if (!date || new Date(`${date[1]}-${date[2]}-${date[3]}T00:00:00Z`).toISOString().slice(0, 10) !== date[0].slice(0, 10)) {
    throw new Error(`${filename}: 请填写有效的 date，例如 2026-09-23 10:00:00`);
  }
  return String(value);
}

export function formatDate(value, format) {
  const date = typeof value === 'number' ? new Date(value).toISOString() : String(value);
  const [year, month, day] = date.slice(0, 10).split('-');
  return format.replace(/YYYY|MM|DD|M/g, token => ({ YYYY: year, MM: month, DD: day, M: String(Number(month)) })[token]);
}

export function slugify(value) {
  return String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[\u0000-\u001f]/g, '').replace(/[\s~`!@#$%^&*()\-_+=[\]{}|\\;:"'<>,.?/]+/g, '-').replace(/^-+|-+$/g, '');
}

export function normalizeAsset(value, postPath = '') {
  const href = String(value).replace(/\\/g, '/');
  if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(href)) return href;
  const imageRoot = href.match(/^(?:[./]+)?img\/(.+)$/);
  if (imageRoot) return `/img/${imageRoot[1]}`;
  if (href.startsWith('../images/') && postPath) {
    const asset = path.posix.normalize(href.slice(3));
    if (!asset.startsWith('images/')) throw new Error('文章图片路径不能越出 images 目录');
    return `${postPath.replace(/\.html$/, '')}/${asset}`;
  }
  if (!href.startsWith('/') && postPath) return path.posix.join(postPath.replace(/\.html$/, ''), href);
  return href;
}

export function renderMarkdown(body, postPath = '', experiments = []) {
  const headings = [];
  const ids = new Map();
  const usedIds = new Set();
  const md = new MarkdownIt({ html: true, linkify: true, breaks: false });
  hljs.configure({ classPrefix: '' });
  md.renderer.rules.fence = (tokens, index) => {
    const token = tokens[index];
    const language = token.info.trim().split(/\s+/)[0];
    if (language === 'experiment') {
      const id = token.content.trim();
      const experiment = experiments.find(item => item.id === id);
      if (!experiment) throw new Error(`文章引用了未定义的实验: ${id}`);
      return experimentCard(experiment);
    }
    const highlighted = language && hljs.getLanguage(language)
      ? hljs.highlight(token.content, { language, ignoreIllegals: true }).value
      : escapeHTML(token.content);
    const lines = Array.from({ length: token.content.replace(/\n$/, '').split('\n').length }, (_, i) => i + 1).join('\n');
    return `<figure class="highlight"><table><tbody><tr><td class="gutter" aria-hidden="true"><pre>${lines}</pre></td><td class="code"><pre><code>${highlighted}</code></pre></td></tr></tbody></table></figure>\n`;
  };
  md.renderer.rules.heading_open = (tokens, index, options, env, self) => {
    const token = tokens[index];
    const inline = tokens[index + 1];
    const text = (inline.children || []).map(child => ['text', 'code_inline'].includes(child.type) ? child.content : child.type === 'image' ? child.content : '').join('');
    const base = slugify(text) || 'section';
    let count = ids.get(base) || 0;
    let id = count ? `${base}-${count}` : base;
    while (usedIds.has(id)) id = `${base}-${++count}`;
    ids.set(base, count + 1);
    usedIds.add(id);
    token.attrSet('id', id);
    headings.push({ id, text, level: Number(token.tag.slice(1)) });
    return self.renderToken(tokens, index, options);
  };
  const image = md.renderer.rules.image;
  md.renderer.rules.image = (tokens, index, options, env, self) => {
    const token = tokens[index];
    token.attrSet('src', normalizeAsset(token.attrGet('src'), postPath));
    token.attrSet('loading', 'lazy');
    return image(tokens, index, options, env, self);
  };
  md.renderer.rules.link_open = (tokens, index, options, env, self) => {
    const href = tokens[index].attrGet('href');
    if (href?.startsWith('../images/')) tokens[index].attrSet('href', normalizeAsset(href, postPath));
    return self.renderToken(tokens, index, options);
  };
  for (const type of ['html_inline', 'html_block']) {
    md.renderer.rules[type] = (tokens, index) => tokens[index].content.replace(/(<img\b[^>]*\bsrc=)(["'])(.*?)\2/gi, (_, prefix, quote, source) => `${prefix}${quote}${escapeHTML(normalizeAsset(source, postPath))}${quote}`);
  }
  const html = md.render(body);
  const toc = headings.length ? `<ol>${headings.map(heading => `<li style="margin-left:${Math.max(0, heading.level - 1) * 10}px"><a href="#${escapeHTML(heading.id)}">${escapeHTML(heading.text)}</a></li>`).join('')}</ol>` : '<p class="muted small">这篇记录暂无章节目录。</p>';
  return { content: html, toc };
}

export async function walk(directory, skip = () => false) {
  const result = [];
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (skip(entry, file)) continue;
    if (entry.isDirectory()) result.push(...await walk(file, skip));
    else if (entry.isFile()) result.push(file);
  }
  return result.sort();
}

export async function readPosts(root) {
  const directory = path.join(root, 'content/posts');
  const posts = [];
  const links = new Map();
  const list = value => (Array.isArray(value) ? value.flat(Infinity) : value == null ? [] : [value]).map(String).filter(Boolean);
  for (const file of await walk(directory, entry => entry.isDirectory() && ['images', 'code'].includes(entry.name))) {
    if (!file.endsWith('.md')) continue;
    const relative = path.relative(directory, file).split(path.sep).join('/');
    if (relative.split('/').includes('images')) continue;
    if (path.basename(path.dirname(file)) !== 'articles') throw new Error(`${relative}: 请把正文放在文章目录的 articles/ 下`);
    const { metadata, body } = parseDocument(await fs.readFile(file, 'utf8'), relative);
    if (metadata.draft === true) continue;
    const abbrlink = String(metadata.abbrlink ?? createHash('sha256').update(relative).digest('hex').slice(0, 12));
    if (!/^[a-zA-Z0-9_-]+$/.test(abbrlink)) throw new Error(`${relative}: abbrlink 只能包含字母、数字、下划线或短横线`);
    if (links.has(abbrlink)) throw new Error(`短链接重复 ${abbrlink}: ${links.get(abbrlink)} 与 ${relative}`);
    links.set(abbrlink, relative);
    const postPath = `/posts/${abbrlink}.html`;
    const imageDirectory = path.join(path.dirname(path.dirname(file)), 'images');
    const assets = (await walk(imageDirectory)).map(source => ({
      source: path.relative(root, source).split(path.sep).join('/'),
      path: `${postPath.replace(/\.html$/, '')}/images/${path.relative(imageDirectory, source).split(path.sep).join('/')}`,
    }));
    const cover = metadata.cover ? normalizeAsset(String(metadata.cover), postPath) : '';
    if (cover && !/^https?:\/\//.test(cover) && !assets.some(asset => asset.path === cover)) throw new Error(`${relative}: 封面文件不存在或不在本篇文章的 images/ 下`);
    const title = String(metadata.title || path.basename(file, '.md'));
    const code = await readExperiments(root, file, metadata.code, postPath);
    const post = {
      title, abbrlink, path: postPath, slug: relative.replace(/\/articles\//, '/').replace(/\.md$/, ''), cover, assets, code,
      date: normalizeDate(metadata.date, relative),
      description: String(metadata.description || ''),
      categories: list(metadata.categories).map(name => ({ name, path: `/categories/${slugify(name)}/` })),
      tags: list(metadata.tags).map(name => ({ name, path: `/tags/${slugify(name)}/` })),
      ...renderMarkdown(body, postPath, code.experiments)
    };
    posts.push(post);
  }
  return posts.sort((a, b) => b.date.localeCompare(a.date) || a.path.localeCompare(b.path));
}
