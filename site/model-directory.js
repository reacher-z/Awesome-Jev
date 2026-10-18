const controls = document.querySelector('[data-model-controls]');
const search = document.querySelector('#model-search');
const license = document.querySelector('#model-license');
const rows = [...document.querySelectorAll('.model-row')];
const count = document.querySelector('#model-result-count');
const empty = document.querySelector('#model-empty');
const zh = document.documentElement.lang.startsWith('zh');
function filter() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const row of rows) {
    const matches = (!license.value || row.dataset.licenseGroup === license.value) && row.textContent.toLocaleLowerCase().includes(query);
    row.hidden = !matches;
    if (matches) visible++;
  }
  count.textContent = `${visible} / ${rows.length} ${zh ? '项模型' : 'models'}`;
  empty.hidden = visible !== 0;
}
search.addEventListener('input', filter);
license.addEventListener('change', filter);
document.querySelector('#model-reset').addEventListener('click', () => {
  search.value = '';
  license.value = '';
  filter();
  search.focus();
});
controls.hidden = false;
filter();
