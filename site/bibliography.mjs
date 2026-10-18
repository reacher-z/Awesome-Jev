// Read this repository's brace-delimited BibTeX entries without rewriting their
// contents. Entries must be self-contained: literals, numbers or standard months, with
// no macro definitions, concatenations or cross-entry dependencies.
function fields(body) {
  const parts = [];
  let depth = 0, quoted = false, escaped = false, start = 0;
  for (let i = 0; i < body.length; i++) {
    const char = body[i];
    if (char === '{') depth++;
    if (char === '}') depth--;
    if (char === '"' && depth === 0 && !escaped) quoted = !quoted;
    if (depth < 0) throw new Error('Unbalanced bibliography field');
    if (char === ',' && depth === 0 && !quoted) {
      parts.push(body.slice(start, i));
      start = i + 1;
    }
    escaped = char === '\\' && !escaped;
  }
  if (depth || quoted) throw new Error('Unbalanced bibliography field');
  parts.push(body.slice(start));
  const values = new Map();
  for (const part of parts) {
    if (!part.trim()) continue;
    const match = part.match(/^\s*([a-z][\w-]*)\s*=\s*([\s\S]+?)\s*$/i);
    if (!match || values.has(match[1].toLowerCase())) throw new Error('Invalid bibliography field');
    values.set(match[1].toLowerCase(), match[2]);
  }
  return values;
}

function literal(value) {
  if (!value || !['{', '"'].includes(value[0])) throw new Error('Bibliography fields must use literals');
  const braced = value[0] === '{';
  let depth = braced ? 1 : 0, escaped = false;
  for (let i = 1; i < value.length; i++) {
    const char = value[i];
    if (char === '{') depth++;
    if (char === '}') depth--;
    const closed = braced ? depth === 0 : char === '"' && depth === 0 && !escaped;
    if (closed) {
      if (i !== value.length - 1) throw new Error('Bibliography expressions are unsupported');
      return value.slice(1, -1).trim();
    }
    if (depth < 0) break;
    escaped = char === '\\' && !escaped;
  }
  throw new Error('Unbalanced bibliography literal');
}

export function parseBibliography(source) {
  if (typeof source !== 'string') throw new Error('Invalid bibliography source');
  const header = /^[ \t]*@([a-z]+)\s*\{/gim;
  const entries = [], keys = new Set(), urls = new Set();
  let match;
  while ((match = header.exec(source))) {
    const start = match.index, bodyStart = header.lastIndex;
    let depth = 1, quoted = false, escaped = false, end = bodyStart;
    for (; end < source.length; end++) {
      const char = source[end];
      if (char === '{') depth++;
      if (char === '}') depth--;
      if (char === '"' && depth === 1 && !escaped) quoted = !quoted;
      if (depth === 0) break;
      escaped = char === '\\' && !escaped;
    }
    if (depth || quoted) throw new Error('Unbalanced bibliography entry');
    header.lastIndex = end + 1;
    if (/^comment$/i.test(match[1])) continue;
    if (/^(preamble|string)$/i.test(match[1])) throw new Error('Bibliography definitions are unsupported');
    const body = source.slice(bodyStart, end);
    const keyMatch = body.match(/^\s*([^\s,{}]+)\s*,/);
    if (!keyMatch || keys.has(keyMatch[1].toLowerCase())) throw new Error('Invalid or duplicate citation key');
    const value = fields(body.slice(keyMatch[0].length));
    if (value.has('crossref') || value.has('xdata')) throw new Error('Dependent bibliography entries are unsupported');
    for (const [name, field] of value) {
      const standardMonth = name === 'month' && /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$/i.test(field);
      if (!/^[0-9]+$/.test(field) && !standardMonth) literal(field);
    }
    const url = value.has('url') ? literal(value.get('url')) : null;
    if (url && (!/^https?:\/\//.test(url) || urls.has(url))) throw new Error('Invalid or duplicate citation URL');
    keys.add(keyMatch[1].toLowerCase()); if (url) urls.add(url);
    entries.push({key:keyMatch[1], url, text:source.slice(start, end + 1).trim()});
  }
  if (!entries.length) throw new Error('Empty bibliography');
  return entries;
}

// URLs are captured when the user requests an export. Exact version matching
// prevents a stale page from silently downloading a different paper revision.
export function selectBibliography(entries, urls) {
  const linked = entries.filter(entry => entry.url);
  const byURL = new Map(linked.map(entry => [entry.url, entry]));
  if (byURL.size !== linked.length || new Set(urls).size !== urls.length) throw new Error('Duplicate citation selection');
  return urls.map(url => {
    const entry = byURL.get(url);
    if (!entry) throw new Error('A selected paper has no matching citation');
    return entry;
  });
}

export function bibliographyText(entries) {
  return entries.length ? entries.map(entry => entry.text).join('\n\n') + '\n' : '';
}
