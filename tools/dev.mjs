import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { buildSite, projectRoot } from './build.mjs';
import { walk } from './content.mjs';

const preview = process.argv.includes('--preview');
const port = Number(process.env.PORT || 4000);
const host = process.env.HOST || '127.0.0.1';
const output = path.join(projectRoot, 'dist');
const clients = new Set();
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.xml': 'application/xml', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.pdf': 'application/pdf' };
const reloadScript = '<script>const updates=new EventSource("/__reload");updates.onmessage=()=>location.reload();</script>';
async function fingerprint() {
  const files = (await Promise.all(['content', 'site', 'static'].map(directory => walk(path.join(projectRoot, directory), (entry, file) => entry.isDirectory() && file.split(path.sep).includes('code') && ['.venv', '__pycache__', 'node_modules', '.git', 'outputs', 'data', 'checkpoints'].includes(entry.name))))).flat();
  const signatures = await Promise.all(files.map(async file => {
    try {
      const info = await fs.stat(file);
      return `${file}:${info.ino}:${info.size}:${info.mtimeMs}:${info.ctimeMs}`;
    } catch (error) { if (error.code === 'ENOENT') return `${file}:deleted`; throw error; }
  }));
  return signatures.join('\n');
}
let lastSnapshot = preview ? '' : await fingerprint();
if (!preview) await buildSite();
else await fs.access(path.join(output, 'index.html'));

const server = http.createServer(async (request, response) => {
  if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405, { Allow: 'GET, HEAD' }); response.end(); return; }
  if (!preview && request.url === '/__reload') {
    response.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    response.write(': connected\n\n');
    clients.add(response);
    request.on('close', () => clients.delete(response));
    return;
  }
  try {
    const requested = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const filename = path.resolve(output, '.' + requested);
    if (filename !== output && !filename.startsWith(output + path.sep)) { response.writeHead(403); response.end(); return; }
    let target = filename;
    try {
      const info = await fs.stat(target);
      if (info.isDirectory()) {
        if (!requested.endsWith('/')) { response.writeHead(308, { Location: encodeURI(requested + '/') }); response.end(); return; }
        target = path.join(target, 'index.html');
      }
      let data = await fs.readFile(target);
      const extension = path.extname(target);
      if (!preview && extension === '.html') data = Buffer.from(data.toString().replace('</body>', reloadScript + '</body>'));
      response.writeHead(200, { 'Content-Type': types[extension] || 'application/octet-stream', 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' });
      response.end(request.method === 'HEAD' ? undefined : data);
    } catch (error) {
      if (!['ENOENT', 'ENOTDIR'].includes(error.code)) throw error;
      response.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      response.end(request.method === 'HEAD' ? undefined : await fs.readFile(path.join(output, '404.html')));
    }
  } catch (error) {
    response.writeHead(error instanceof URIError ? 400 : 500);
    response.end('Request failed');
  }
});

server.listen(port, host, () => console.log(`Lucas ${preview ? 'preview' : 'dev'} → http://${host}:${port}`));
let timer;
let building = false;
let pending = false;
let polling = false;
async function rebuild() {
  if (building) { pending = true; return; }
  building = true;
  try {
    await buildSite();
    for (const client of clients) client.write('data: reload\n\n');
  } catch (error) { console.error(`Build failed; keeping last working preview: ${error.message}`); }
  finally {
    building = false;
    if (pending) { pending = false; schedule(); }
  }
}
function schedule() { clearTimeout(timer); timer = setTimeout(rebuild, 150); }
/* 轮询元数据以兼容 Docker 挂载及编辑器通过重命名完成的原子保存。 */
const poller = preview ? undefined : setInterval(async () => {
  if (polling) return;
  polling = true;
  try {
    const snapshot = await fingerprint();
    if (snapshot !== lastSnapshot) { lastSnapshot = snapshot; schedule(); }
  } catch (error) { console.error(`File scan failed: ${error.message}`); }
  finally { polling = false; }
}, 750);
const heartbeat = setInterval(() => { for (const client of clients) client.write(': heartbeat\n\n'); }, 20000);
function close() {
  clearTimeout(timer); clearInterval(heartbeat); clearInterval(poller);
  for (const client of clients) client.end();
  server.close();
}
process.on('SIGINT', close);
process.on('SIGTERM', close);
