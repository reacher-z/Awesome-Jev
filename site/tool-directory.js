import {bindDirectoryView} from './directory-view.mjs';

const controls = [...document.querySelectorAll('[data-tool-controls]')];
const buttons = [...document.querySelectorAll('[data-task]')];
const search = document.querySelector('#tool-search');
const publisher = document.querySelector('#tool-publisher');
const rows = [...document.querySelectorAll('.tool-row')];
const count = document.querySelector('#tool-result-count');
const empty = document.querySelector('#tool-empty');
const zh = document.documentElement.lang.startsWith('zh');
let task = '';
function filter() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const row of rows) {
    const matches = (!task || row.dataset.tasks.split(' ').includes(task)) &&
      (!publisher.value || row.dataset.publisher === publisher.value) &&
      row.dataset.search.toLocaleLowerCase().includes(query);
    row.hidden = !matches;
    if (matches) visible++;
  }
  for (const button of buttons) {
    const selected = button.dataset.task === task;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  }
  count.textContent = `${visible} / ${rows.length} ${zh ? '项工具' : 'tools'}`;
  empty.hidden = visible !== 0;
}
for (const button of buttons) button.addEventListener('click', () => {
  task = button.dataset.task;
  filter();
  view.commit();
});
search.addEventListener('input', () => { filter(); view.commit(); });
publisher.addEventListener('change', () => { filter(); view.commit(); });
document.querySelector('#tool-reset').addEventListener('click', () => {
  task = '';
  search.value = '';
  publisher.value = '';
  filter();
  view.commit();
  search.focus();
});
const view = bindDirectoryView({
  schema:{q:{default:''},task:{default:'',values:buttons.map(button=>button.dataset.task)},publisher:{default:'',values:[...publisher.options].map(option=>option.value)}},
  read:()=>({q:search.value,task,publisher:publisher.value}),
  apply:state=>{ search.value=state.q; task=state.task; publisher.value=state.publisher; filter(); },
  languageLinks:document.querySelectorAll('.language-switch a'),
  copyButton:document.querySelector('#directory-copy-link'),
  status:document.querySelector('#directory-share-status'),
  messages:{copied:zh?'链接已复制':'Link copied',failed:zh?'无法复制，请复制浏览器地址栏中的链接。':'Copy unavailable. Copy the link from your browser’s address bar.'},
});
for (const control of controls) control.hidden = false;
