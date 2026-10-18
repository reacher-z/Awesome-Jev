import {bindDirectoryView} from './directory-view.mjs';
import {parseBibliography, selectBibliography, bibliographyText} from './bibliography.mjs';

const body = document.querySelector('.paper-table tbody');
const rows = [...body.rows];
const headers = document.querySelectorAll('.paper-table thead th');
const themes = [...document.querySelectorAll('.paper-controls [data-theme]')];
const themeSelect = document.querySelector('#paper-theme');
const code = document.querySelector('#paper-code-filter');
const search = document.querySelector('#paper-search');
const sort = document.querySelector('#paper-sort');
const count = document.querySelector('#paper-result-count');
const empty = document.querySelector('#paper-empty');
const zh = document.documentElement.lang.startsWith('zh');
const exportButton = document.querySelector('#paper-export');
const exportStatus = document.querySelector('#paper-export-status');
let exportBusy = false, bibliographyPromise, downloadURL;
const visibleRows = () => [...body.rows].filter(row => !row.hidden);
function refreshExport() {
  const total = visibleRows().length;
  exportButton.disabled = exportBusy || total === 0;
  exportButton.textContent = exportBusy ? (zh ? '准备中…' : 'Preparing…')
    : `${zh ? '导出 BibTeX' : 'Download BibTeX'} (${total})`;
}
function clearExportFeedback() {
  exportStatus.replaceChildren();
  if (downloadURL) URL.revokeObjectURL(downloadURL);
  downloadURL = undefined;
}
async function loadBibliography() {
  if (!bibliographyPromise) {
    bibliographyPromise = (async () => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(exportButton.dataset.bibliography, {credentials:'omit', referrerPolicy:'no-referrer', signal:controller.signal});
        if (!response.ok) throw new Error('Bibliography unavailable');
        return parseBibliography(await response.text());
      } finally { clearTimeout(timeout); }
    })().catch(error => { bibliographyPromise = undefined; throw error; });
  }
  return bibliographyPromise;
}
exportButton.addEventListener('click', async () => {
  if (exportBusy) return;
  // Snapshot the clicked view, including its current display order. A filter
  // change during the fetch must not silently change the requested export.
  const urls = visibleRows().map(row => row.querySelector('.paper-title').getAttribute('href'));
  if (!urls.length) return;
  exportBusy = true;
  clearExportFeedback();
  exportButton.setAttribute('aria-busy', 'true');
  refreshExport();
  try {
    const selected = selectBibliography(await loadBibliography(), urls);
    downloadURL = URL.createObjectURL(new Blob([bibliographyText(selected)], {type:'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = `awesome-jev-${selected.length}-papers.bib`;
    link.textContent = zh ? '保存 .bib 文件' : 'Save .bib file';
    exportStatus.replaceChildren(document.createTextNode(zh ? `已准备 ${selected.length} 条引用。 ` : `${selected.length} citations ready. `), link);
    link.click();
  } catch {
    const link = document.createElement('a');
    link.href = '/references.bib';
    link.textContent = zh ? '打开完整书目' : 'Open the full bibliography';
    exportStatus.replaceChildren(document.createTextNode(zh ? '无法准备筛选引用，请重试、刷新页面或' : 'Could not prepare these citations. Retry, reload, or '), link);
  } finally {
    exportBusy = false;
    exportButton.removeAttribute('aria-busy');
    refreshExport();
  }
});
exportButton.hidden = false;
const title = row => row.querySelector('.paper-title').textContent;
let theme = '';
function press(button, pressed) {
  button.setAttribute('aria-pressed', String(pressed));
  button.classList.toggle('active', pressed);
}
function syncTheme() {
  for (const button of themes) press(button, button.dataset.theme === theme);
  themeSelect.value = theme;
}
function update() {
  clearExportFeedback();
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const row of rows) {
    const matches = (!theme || row.dataset.theme === theme) && (!code.checked || row.dataset.code === 'true') && (row.dataset.search || row.textContent).toLocaleLowerCase().includes(query);
    row.hidden = !matches;
    if (matches) visible++;
  }
  count.textContent = `${visible} / ${rows.length} ${zh ? '篇论文' : 'papers'}`;
  empty.hidden = visible !== 0;
  body.classList.toggle('paper-results-expanded', visible > 0 && visible <= 3);
  refreshExport();
}
// The static order is newest first; the other orders are derived from it.
function reorder() {
  clearExportFeedback();
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
    syncTheme();
    update();
    view.commit();
  });
}
themeSelect.addEventListener('change', () => { theme = themeSelect.value; syncTheme(); update(); view.commit(); });
code.addEventListener('change', () => { update(); view.commit(); });
search.addEventListener('input', () => { update(); view.commit(); });
sort.addEventListener('change', () => { reorder(); view.commit(); });
document.querySelector('#paper-reset').addEventListener('click', () => {
  search.value = '';
  sort.value = 'newest';
  code.checked = false;
  theme = '';
  syncTheme();
  reorder();
  update();
  view.commit();
  search.focus();
});
for (const controls of document.querySelectorAll('[data-paper-controls]')) controls.hidden = false;
const view = bindDirectoryView({
  schema:{
    q:{default:''},
    theme:{default:'', values:themes.map(button=>button.dataset.theme)},
    code:{default:'', values:['','1']},
    sort:{default:'newest', values:['newest','oldest','title']},
  },
  read:()=>({q:search.value, theme, code:code.checked?'1':'', sort:sort.value}),
  apply:state=>{
    search.value=state.q;
    theme=state.theme;
    code.checked=state.code==='1';
    sort.value=state.sort;
    syncTheme();
    reorder();
    update();
  },
  languageLinks:document.querySelectorAll('.language-switch a'),
  copyButton:document.querySelector('#directory-copy-link'),
  status:document.querySelector('#directory-share-status'),
  messages:{copied:zh?'链接已复制':'Link copied', failed:zh?'无法复制，请复制浏览器地址栏中的链接。':'Copy unavailable. Copy the link from your browser’s address bar.'},
});
