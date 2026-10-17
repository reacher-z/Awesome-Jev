// Papers per ISO week of first arXiv submission, stacked by README theme.
// One renderer draws the inline chart on /papers/ (painted by site/styles.css tokens) and the
// standalone light and dark SVG files the READMEs embed (painted with fixed colours).
// Palette: the six-slot categorical order validated for adjacent stacks in light and dark
// (worst adjacent CVD ΔE 9.1 light, 8.4 dark; normal-vision ΔE >= 19.3). Three light slots sit
// below 3:1 on white, so every chart ships a legend and a table of the numbers.
import { escapeHTML as esc } from '../site/resource-view.mjs';

const palette = {
  light: { series: ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300'], ink: '#111827', muted: '#4b5563', grid: '#e5e7eb', axis: '#9ca3af' },
  dark: { series: ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300'], ink: '#e6e8eb', muted: '#b0b8c4', grid: '#30363d', axis: '#6b7280' },
};
const fonts = 'system-ui, -apple-system, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, Arial, &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, sans-serif';
const day = 864e5;
const n = value => +value.toFixed(2);
const utc = value => new Date(value + 'T00:00:00Z');
const iso = date => date.toISOString().slice(0, 10);
function isoWeek(value) {
  const date = utc(value), monday = new Date(date - ((date.getUTCDay() + 6) % 7) * day);
  const thursday = new Date(+monday + 3 * day), year = thursday.getUTCFullYear();
  return { year, week: 1 + Math.floor((thursday - Date.UTC(year, 0, 1)) / day / 7), monday: iso(monday) };
}

// Every week from the first submission to the curation date, empty weeks included. The last
// week ends at the curation date when that falls before its Sunday.
export function weeklyPaperCounts(papers, themes, through) {
  const first = isoWeek(papers.map(paper => paper.first_submitted).sort()[0]).monday;
  const weeks = [];
  for (let monday = utc(first); iso(monday) <= through; monday = new Date(+monday + 7 * day)) {
    const start = iso(monday), end = [iso(new Date(+monday + 6 * day)), through].sort()[0];
    const { year, week } = isoWeek(start);
    const counts = themes.map(theme => papers.filter(paper => paper.theme === theme.id && paper.first_submitted >= start && paper.first_submitted <= end).length);
    weeks.push({ label: `${year}-W${String(week).padStart(2, '0')}`, week, start, end, partial: end < iso(new Date(+monday + 6 * day)), counts, total: counts.reduce((a, b) => a + b, 0) });
  }
  if (weeks.reduce((sum, week) => sum + week.total, 0) !== papers.length) throw new Error('Every paper needs a first-submission date on or before the curation date.');
  return weeks;
}

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
export function weekRange(week, language) {
  const [, m1, d1] = week.start.split('-').map(Number), [, m2, d2] = week.end.split('-').map(Number);
  if (language === 'zh') return `${m1}/${d1}–${m1 === m2 ? '' : m2 + '/'}${d2}`;
  return `${months[m1 - 1]} ${d1}–${m1 === m2 ? '' : months[m2 - 1] + ' '}${d2}`;
}
const weekStart = (week, language) => {
  const [, month, date] = week.start.split('-').map(Number);
  return language === 'zh' ? `${month}/${date}` : `${months[month - 1]} ${date}`;
};

export function activityText(weeks, themes, language, count) {
  const zh = language === 'zh', last = weeks.at(-1);
  const totals = weeks.map(week => `${week.label}${zh ? '：' : ': '}${week.total}`).join(zh ? '；' : '; ');
  return {
    title: zh ? '每周首次提交到 arXiv 的论文数（按主题）' : 'Papers per week of first arXiv submission, by theme',
    summary: zh
      ? `按 arXiv 首次提交的 ISO 周统计本目录 ${count} 篇论文，按主题堆叠：${totals}${last.partial ? `（${last.label} 截至 ${last.end}）` : ''}。`
      : `Stacked columns of the ${count} selected papers by ISO week of first arXiv submission, coloured by theme: ${totals}${last.partial ? ` (${last.label} through ${last.end})` : ''}.`,
    note: zh
      ? `按 ISO 周统计，日期为每周周一；只计本目录收录的论文，不代表该领域全部文献。${last.partial ? `最后一周截至整理日期 ${last.end}。` : ''}`
      : `ISO weeks, dated by their Monday. Counts cover this collection, not the whole literature.${last.partial ? ` The last week runs to the curation date, ${last.end}.` : ''}`,
    tableSummary: zh ? '查看数据表' : 'Show the numbers',
  };
}

// mode: 'light' or 'dark' for standalone files, 'inline' for the site (classes, no fixed colours).
export function activitySVG(weeks, themes, language, count, mode) {
  const inline = mode === 'inline', colors = palette[mode] || palette.light, zh = language === 'zh';
  const paint = (role, index) => inline ? `class="viz-${role}${index === undefined ? '' : index + 1}"` : `fill="${index === undefined ? colors[role] : colors.series[index]}"`;
  const stroke = role => inline ? `class="viz-${role}"` : `stroke="${colors[role]}"`;
  const text = activityText(weeks, themes, language, count);
  const width = 400, left = 30, top = 60, base = 158, plot = base - top;
  const max = Math.max(...weeks.map(week => week.total), 1);
  // The tallest column fills the plot; gridlines mark round values below it.
  const step = max <= 6 ? 2 : max <= 15 ? 5 : 10;
  const band = (width - left) / weeks.length, bar = Math.min(24, band / 2), scale = plot / max;
  const id = inline ? 'paper-activity' : 'chart';
  const out = [];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} 196" width="${width}" height="196" role="img" aria-labelledby="${id}-title ${id}-desc"${inline ? ' class="activity-chart"' : ` font-family="${fonts}"`} font-size="13">`);
  out.push(`<title id="${id}-title">${esc(text.title)}</title><desc id="${id}-desc">${esc(text.summary)}</desc>`);
  themes.forEach((theme, index) => {
    const x = (index % 3) * 134, y = index < 3 ? 5 : 26;
    out.push(`<rect x="${x}" y="${y}" width="10" height="10" rx="2" ${paint('series', index)}/><text x="${x + 15}" y="${y + 10}" ${paint('ink')}>${esc(theme.short[language])}</text>`);
  });
  for (let value = 0; value <= max; value += step) {
    const y = Math.round(base - value * scale) + 0.5; // whole-pixel hairlines stay crisp
    out.push(`<line x1="${left}" x2="${width}" y1="${y}" y2="${y}" ${stroke(value ? 'grid' : 'axis')} stroke-width="1"/><text x="${left - 8}" y="${y + 3.5}" text-anchor="end" ${paint('muted')}>${value}</text>`);
  }
  weeks.forEach((week, column) => {
    const center = n(left + band * (column + 0.5)), x = n(center - bar / 2);
    let y = base;
    const filled = week.counts.map((count, index) => [count, index]).filter(([count]) => count);
    filled.forEach(([count, index], position) => {
      // Each segment above the first leaves a 2px surface gap below it; the top one gets a rounded end.
      const yTop = y - count * scale, bottom = y - (position ? 2 : 0);
      const label = `${week.label} (${weekRange(week, language)}) · ${themes[index].short[language]}${zh ? '：' : ': '}${count}`;
      const r = Math.min(4, bottom - yTop, bar / 2);
      const shape = position === filled.length - 1
        ? `<path d="M${x} ${n(bottom)}V${n(yTop + r)}Q${x} ${n(yTop)} ${n(x + r)} ${n(yTop)}H${n(x + bar - r)}Q${n(x + bar)} ${n(yTop)} ${n(x + bar)} ${n(yTop + r)}V${n(bottom)}Z"`
        : `<rect x="${x}" y="${n(yTop)}" width="${n(bar)}" height="${n(bottom - yTop)}"`;
      out.push(`${shape} ${paint('series', index)}><title>${esc(label)}</title></${shape.startsWith('<path') ? 'path' : 'rect'}>`);
      y = yTop;
    });
    if (week.total) out.push(`<text x="${center}" y="${n(y - 6)}" text-anchor="middle" font-weight="600" ${paint('ink')}>${week.total}</text>`);
    out.push(`<text x="${center}" y="${base + 18}" text-anchor="middle" ${paint('ink')}>W${String(week.week).padStart(2, '0')}</text><text x="${center}" y="${base + 34}" text-anchor="middle" font-size="12" ${paint('muted')}>${esc(weekStart(week, language))}</text>`);
  });
  out.push('</svg>');
  return out.join(inline ? '' : '\n') + (inline ? '' : '\n');
}

export function activityTable(weeks, themes, language) {
  const zh = language === 'zh';
  const head = `<tr><th scope="col">${zh ? '主题' : 'Theme'}</th>${weeks.map(week => `<th scope="col">W${String(week.week).padStart(2, '0')}</th>`).join('')}<th scope="col">${zh ? '合计' : 'Total'}</th></tr>`;
  const rows = themes.map((theme, index) => `<tr><th scope="row">${esc(theme.short[language])}</th>${weeks.map(week => `<td>${week.counts[index]}</td>`).join('')}<td>${weeks.reduce((sum, week) => sum + week.counts[index], 0)}</td></tr>`);
  const total = `<tr><th scope="row">${zh ? '合计' : 'Total'}</th>${weeks.map(week => `<td>${week.total}</td>`).join('')}<td>${weeks.reduce((sum, week) => sum + week.total, 0)}</td></tr>`;
  return `<table><thead>${head}</thead><tbody>${rows.join('')}${total}</tbody></table>`;
}
