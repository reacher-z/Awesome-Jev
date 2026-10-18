const PREFIX = '#view?';

export const defaultView = schema => Object.fromEntries(Object.entries(schema).map(([key, rule]) => [key, rule.default]));

function normalizedView(state, schema) {
  return Object.fromEntries(Object.entries(schema).map(([key, rule]) => {
    const value = typeof state[key] === 'string' ? state[key] : rule.default;
    return [key, !rule.values || rule.values.includes(value) ? value : rule.default];
  }));
}

export function decodeView(fragment, schema) {
  if (!fragment.startsWith(PREFIX)) return defaultView(schema);
  return normalizedView(Object.fromEntries(new URLSearchParams(fragment.slice(PREFIX.length))), schema);
}

export function encodeView(state, schema) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(normalizedView(state, schema))) {
    if (value !== schema[key].default) params.set(key, value);
  }
  return params.size ? PREFIX + params.toString() : '';
}

// Fragments keep search terms out of HTTP requests. No storage, analytics or
// network calls are needed; normal canonical URLs continue to serve every row.
export function bindDirectoryView({schema, read, apply, languageLinks, copyButton, status, messages}, browser = window) {
  const links = [...languageLinks].map(link => ({link, url:new URL(link.href, browser.location.href)}));
  function fragment() {
    return encodeView(read(), schema) || (browser.location.hash.startsWith(PREFIX) ? '' : browser.location.hash);
  }
  function syncLinks() {
    for (const {link, url} of links) {
      const target = new URL(url);
      target.hash = fragment();
      link.href = target.href;
    }
  }
  function restore() {
    apply(decodeView(browser.location.hash, schema));
    status.textContent = '';
    syncLinks();
  }
  function commit() {
    const url = new URL(browser.location.href);
    url.hash = encodeView(read(), schema);
    browser.history.replaceState(browser.history.state, '', url.href);
    status.textContent = '';
    syncLinks();
  }
  copyButton.addEventListener('click', async () => {
    const url = new URL(browser.location.pathname, browser.location.origin);
    url.hash = fragment();
    try {
      await browser.navigator.clipboard.writeText(url.href);
      status.textContent = messages.copied;
    } catch {
      status.textContent = messages.failed;
    }
  });
  browser.addEventListener('hashchange', restore);
  browser.addEventListener('popstate', restore);
  browser.addEventListener('pageshow', restore);
  restore();
  return {commit};
}
