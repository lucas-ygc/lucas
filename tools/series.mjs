export function collectSeries(definitions, posts) {
  const byId = new Map(posts.map(post => [post.abbrlink, post]));
  const ids = new Set();
  const members = new Set();
  return definitions.map(definition => {
    if (!/^[a-zA-Z0-9_-]+$/.test(definition.id) || ids.has(definition.id)) throw new Error(`合集 ID 无效或重复: ${definition.id}`);
    if (!definition.title || !Array.isArray(definition.articles)) throw new Error(`合集缺少标题或文章目录: ${definition.id}`);
    ids.add(definition.id);
    const entries = definition.articles.flatMap(id => {
      if (members.has(id)) throw new Error(`文章重复归入合集: ${id}`);
      members.add(id);
      return byId.has(id) ? [byId.get(id)] : [];
    });
    const categories = [...new Map(entries.flatMap(post => post.categories || []).map(category => [category.name, category])).values()];
    const series = { id: definition.id, title: definition.title, description: definition.description || '', path: `/series/${definition.id}/`, posts: entries, categories };
    const neighbor = post => post ? { title: post.title, path: post.path } : null;
    entries.forEach((post, index) => {
      post.series = { title: series.title, path: series.path, position: index + 1, total: entries.length, previous: neighbor(entries[index - 1]), next: neighbor(entries[index + 1]) };
    });
    return series;
  }).filter(series => series.posts.length);
}

export function groupSeries(series) {
  const groups = new Map();
  for (const collection of series) {
    const categories = collection.categories.length ? collection.categories : [{ name: '未分类', path: '' }];
    for (const category of categories) {
      if (!groups.has(category.name)) groups.set(category.name, { ...category, collections: [] });
      groups.get(category.name).collections.push(collection);
    }
  }
  return [...groups.values()];
}
