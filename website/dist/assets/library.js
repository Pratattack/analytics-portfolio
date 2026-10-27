'use strict';
function matchingProjects(projects, query = '', category = 'all', dataKind = 'all') {
  const terms = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean)
    .map(term => term.length > 4 && !term.endsWith('ss') ? term.replace(/s$/, '') : term);
  return projects.filter(p => {
    const searchable = [p.title, p.shortTitle, p.question, p.audience, p.data, p.methods, p.findings, p.implications, p.limitations, p.category, p.dataKind, ...p.tools].join(' ').toLocaleLowerCase();
    return (category === 'all' || p.category === category) &&
      (dataKind === 'all' || p.dataKind === dataKind) && terms.every(term => searchable.includes(term));
  });
}
if (typeof module !== 'undefined') module.exports = { matchingProjects };
if (typeof document !== 'undefined') {
  const form = document.getElementById('filters');
  const search = document.getElementById('search');
  const category = document.getElementById('category');
  const data = document.getElementById('data-kind');
  const rows = [...document.querySelectorAll('.library-row')];
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  if ([...category.options].some(o => o.value === params.get('area'))) category.value = params.get('area');
  if ([...data.options].some(o => o.value === params.get('data'))) data.value = params.get('data');
  function update() {
    const found = matchingProjects(portfolioProjects, search.value, category.value, data.value);
    const slugs = new Set(found.map(p => p.slug));
    rows.forEach(row => { row.hidden = !slugs.has(row.dataset.slug); });
    document.getElementById('result-count').textContent = `${found.length} ${found.length === 1 ? 'project' : 'projects'}`;
    document.getElementById('no-results').hidden = found.length !== 0;
    const state = new URLSearchParams();
    if (search.value.trim()) state.set('q', search.value.trim());
    if (category.value !== 'all') state.set('area', category.value);
    if (data.value !== 'all') state.set('data', data.value);
    history.replaceState(null, '', location.pathname + (state.size ? '?' + state : ''));
  }
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  document.getElementById('clear-search').addEventListener('click', () => { form.reset(); search.focus(); });
  update();
}
