import fs from 'node:fs/promises';
import path from 'node:path';
import { gzipSync } from 'node:zlib';
import hljs from 'highlight.js';

hljs.configure({ classPrefix: '' });

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const href = value => encodeURI(value).replace(/#/g, '%23').replace(/\?/g, '%3F');
const quote = value => "'" + value.replace(/'/g, "'\\''") + "'";

export async function readExperiments(root, articleFile, metadata, postPath) {
  if (!metadata) return { files: [], experiments: [] };
  if (!Array.isArray(metadata.files) || !Array.isArray(metadata.experiments)) throw new Error('code 需要 files 和 experiments 列表');
  const directory = path.join(path.dirname(path.dirname(articleFile)), 'code');
  if ((await fs.lstat(directory)).isSymbolicLink()) throw new Error('code 目录不能是符号链接');
  const realDirectory = await fs.realpath(directory);
  const base = postPath.replace(/\.html$/, '') + '/code';
  const download = `${base}/experiments.tar.gz`;
  const files = [];
  const names = new Set();
  for (const name of metadata.files) {
    if (typeof name !== 'string' || name.includes('\\') || name.split('/').some(part => !part || part === '.' || part === '..') || path.isAbsolute(name)) throw new Error(`无效的代码文件路径: ${name}`);
    if (names.has(name)) throw new Error(`重复的代码文件: ${name}`);
    names.add(name);
    const source = path.join(directory, name);
    const realSource = await fs.realpath(source);
    if (!realSource.startsWith(realDirectory + path.sep) || !(await fs.stat(source)).isFile()) throw new Error(`代码文件越出目录或不是文件: ${name}`);
    const data = await fs.readFile(source);
    let text;
    try { text = new TextDecoder('utf-8', { fatal: true }).decode(data); } catch { text = null; }
    if (text?.includes('\0')) text = null;
    const extension = path.extname(name).slice(1);
    const language = hljs.getLanguage(extension) ? extension : 'plaintext';
    files.push({ name, data, text, path: text === null ? null : `${base}/${name}.html`, highlighted: text === null ? null : hljs.highlight(text, { language, ignoreIllegals: true }).value });
  }
  const ids = new Set();
  const experiments = metadata.experiments.map(item => {
    if (!item || typeof item.id !== 'string' || !/^[a-zA-Z0-9_-]+$/.test(item.id) || ids.has(item.id)) throw new Error(`无效或重复的实验 ID: ${item?.id}`);
    ids.add(item.id);
    const file = files.find(file => file.name === item.file);
    if (!file?.path) throw new Error(`实验引用了未列出或非 UTF-8 文本的代码文件: ${item.file}`);
    if (typeof item.command !== 'string' || !item.command.trim()) throw new Error(`实验缺少运行命令: ${item.id}`);
    const relativeDirectory = path.relative(root, directory).split(path.sep).join('/');
    const inlineFiles = [];
    if (metadata.inline === true) {
      if (item.related_files !== undefined && !Array.isArray(item.related_files)) throw new Error(`实验 related_files 需要列表: ${item.id}`);
      for (const name of new Set([item.file, ...(item.related_files || [])])) {
        const source = files.find(file => file.name === name);
        if (!source?.path) throw new Error(`实验引用了未列出或非 UTF-8 文本的代码文件: ${name}`);
        inlineFiles.push({ name: source.name, highlighted: source.highlighted });
      }
    }
    return { id: item.id, title: String(item.title || item.file), file: item.file, path: file.path, inlineFiles, download, command: item.command, projectCommand: `cd ${quote(relativeDirectory)} && ${item.command}` };
  });
  return { files, experiments, download };
}

export function experimentCard(experiment) {
  const inline = experiment.inlineFiles?.length > 0;
  const source = inline ? experiment.inlineFiles.map(file => `<details class="experiment-source"><summary>查看完整代码：${escape(file.name)}</summary><pre><code>${file.highlighted}</code></pre></details>`).join('\n') : '';
  return `<section class="experiment-card" id="experiment-${escape(experiment.id)}" aria-label="${escape(experiment.title)}">
<h3>${escape(experiment.title)}</h3>
${source}
<div class="experiment-actions">${inline ? '' : `<a href="${href(experiment.path)}">查看完整代码</a>`}<a href="${href(experiment.download)}" download>下载代码</a><button type="button" data-copy-command="${escape(experiment.projectCommand)}">复制运行命令</button><span class="copy-status" role="status"></span></div>
<p class="experiment-hint">在项目根目录执行；下载包解压后，在解压目录执行 <code>${escape(experiment.command)}</code>。</p>
<pre class="experiment-command"><code>${escape(experiment.projectCommand)}</code></pre>
</section>`;
}

/* 下载包使用标准 tar + gzip；固定时间戳以便重复构建得到相同文件。 */
export function createCodeArchive(files) {
  const chunks = [];
  for (const { name, data } of files) {
    if (Buffer.byteLength(name) > 100) throw new Error(`下载包文件名不能超过 100 字节: ${name}`);
    const header = Buffer.alloc(512);
    const write = (value, offset, size) => header.write(value, offset, size, 'utf8');
    const octal = (value, offset, size) => write(value.toString(8).padStart(size - 1, '0') + '\0', offset, size);
    write(name, 0, 100);
    octal(0o644, 100, 8); octal(0, 108, 8); octal(0, 116, 8);
    octal(data.length, 124, 12); octal(0, 136, 12);
    header.fill(32, 148, 156);
    write('0', 156, 1); write('ustar\0', 257, 6); write('00', 263, 2);
    const checksum = header.reduce((sum, value) => sum + value, 0);
    write(checksum.toString(8).padStart(6, '0') + '\0 ', 148, 8);
    chunks.push(header, data, Buffer.alloc((512 - data.length % 512) % 512));
  }
  chunks.push(Buffer.alloc(1024));
  return gzipSync(Buffer.concat(chunks));
}
