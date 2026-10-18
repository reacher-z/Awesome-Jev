import {bindDirectoryView} from './directory-view.mjs';

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
    const matches = (!license.value || row.dataset.licenseGroup === license.value) && (row.dataset.search || row.textContent).toLocaleLowerCase().includes(query);
    row.hidden = !matches;
    if (matches) visible++;
  }
  count.textContent = `${visible} / ${rows.length} ${zh ? '项模型' : 'models'}`;
  empty.hidden = visible !== 0;
}
search.addEventListener('input', () => { filter(); view.commit(); });
license.addEventListener('change', () => { filter(); view.commit(); });
document.querySelector('#model-reset').addEventListener('click', () => {
  search.value = '';
  license.value = '';
  filter();
  view.commit();
  search.focus();
});
controls.hidden = false;
const view = bindDirectoryView({
  schema:{q:{default:''}, license:{default:'',values:[...license.options].map(option=>option.value)}},
  read:()=>({q:search.value, license:license.value}),
  apply:state=>{ search.value=state.q; license.value=state.license; filter(); },
  languageLinks:document.querySelectorAll('.language-switch a'),
  copyButton:document.querySelector('#directory-copy-link'),
  status:document.querySelector('#directory-share-status'),
  messages:{copied:zh?'链接已复制':'Link copied', failed:zh?'无法复制，请复制浏览器地址栏中的链接。':'Copy unavailable. Copy the link from your browser’s address bar.'},
});
