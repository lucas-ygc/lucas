(() => {
  'use strict';
  document.querySelectorAll('[data-copy-command]').forEach(button => {
    let timer;
    button.addEventListener('click', async () => {
      const command = button.dataset.copyCommand;
      const status = button.parentElement.querySelector('.copy-status');
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(command);
        button.textContent = '已复制';
        status.textContent = '运行命令已复制';
      } catch {
        button.textContent = '复制运行命令';
        status.textContent = '无法自动复制，请选中下方命令复制';
      }
      clearTimeout(timer);
      timer = setTimeout(() => { button.textContent = '复制运行命令'; status.textContent = ''; }, 3000);
    });
  });
  const list = document.querySelector('[data-filterable]');
  if (!list) return;
  const rows = [...list.querySelectorAll('.post-row')];
  const search = document.querySelector('#post-search');
  const filters = [...document.querySelectorAll('[data-category]')];
  const more = document.querySelector('.load-more');
  let category = '';
  let limit = 10;
  const render = () => {
    const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const matches = rows.filter(row => (!category || JSON.parse(row.dataset.categories).includes(category)) && terms.every(term => row.dataset.search.includes(term)));
    const visible = new Set(matches.slice(0, limit));
    rows.forEach(row => { row.hidden = !visible.has(row); });
    document.querySelector('[data-result-count]').textContent = `${matches.length} 篇记录`;
    document.querySelector('.empty-state').hidden = matches.length > 0;
    more.hidden = matches.length <= limit;
    more.textContent = `更多文章 ↓  (${Math.min(limit, matches.length)} / ${matches.length})`;
  };
  search.addEventListener('input', () => { limit = 10; render(); });
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.category;
    limit = 10;
    filters.forEach(filter => { const active = filter === button; filter.classList.toggle('active', active); filter.setAttribute('aria-pressed', String(active)); });
    render();
  }));
  more.addEventListener('click', () => {
    const previous = rows.filter(row => !row.hidden);
    limit += 10;
    render();
    rows.find(row => !row.hidden && !previous.includes(row))?.querySelector('h3 a')?.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.target.closest('input, textarea, select, [contenteditable]')) { event.preventDefault(); search.focus(); }
    if (event.key === 'Escape' && document.activeElement === search) { search.value = ''; limit = 10; render(); search.blur(); }
  });
  document.querySelector('.nav-search')?.addEventListener('click', event => {
    event.preventDefault();
    search.focus();
    search.scrollIntoView({ block: 'center' });
  });
  if (location.hash === '#post-search') search.focus();
  render();
})();
