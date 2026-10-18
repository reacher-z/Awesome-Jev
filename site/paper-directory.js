const body = document.querySelector('.paper-table tbody');
const rows = [...body.rows];
const headers = document.querySelectorAll('.paper-table thead th');
const themes = [...document.querySelectorAll('.paper-controls [data-theme]')];
const code = document.querySelector('#paper-code-filter');
const search = document.querySelector('#paper-search');
const sort = document.querySelector('#paper-sort');
const count = document.querySelector('#paper-result-count');
const empty = document.querySelector('#paper-empty');
const zh = document.documentElement.lang.startsWith('zh');
const title = row => row.querySelector('.paper-title').textContent;
let theme = '';
function press(button, pressed) {
  button.setAttribute('aria-pressed', String(pressed));
  button.classList.toggle('active', pressed);
}
function update() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const row of rows) {
    const matches = (!theme || row.dataset.theme === theme) && (!code.checked || row.dataset.code === 'true') && row.textContent.toLocaleLowerCase().includes(query);
    row.hidden = !matches;
    if (matches) visible++;
  }
  count.textContent = `${visible} / ${rows.length} ${zh ? '篇论文' : 'papers'}`;
  empty.hidden = visible !== 0;
}
// The static order is newest first; the other orders are derived from it.
function reorder() {
  const order = sort.value === 'oldest' ? [...rows].reverse()
    : sort.value === 'title' ? [...rows].sort((a, b) => title(a).localeCompare(title(b), zh ? 'zh-CN' : 'en'))
    : rows;
  body.append(...order);
  headers[0].setAttribute('aria-sort', sort.value === 'title' ? 'none' : sort.value === 'oldest' ? 'ascending' : 'descending');
  headers[1].setAttribute('aria-sort', sort.value === 'title' ? 'ascending' : 'none');
}
for (const button of themes) {
  button.addEventListener('click', () => {
    theme = button.dataset.theme;
    for (const other of themes) press(other, other === button);
    update();
  });
}
code.addEventListener('change', update);
search.addEventListener('input', update);
sort.addEventListener('change', reorder);
document.querySelector('#paper-reset').addEventListener('click', () => {
  search.value = '';
  sort.value = 'newest';
  code.checked = false;
  theme = '';
  for (const button of themes) press(button, button.dataset.theme === '');
  reorder();
  update();
  search.focus();
});
for (const controls of document.querySelectorAll('[data-paper-controls]')) controls.hidden = false;
// A restored search, sort or checkbox (back navigation) applies at once.
reorder();
update();
