import { resources, translations } from "./catalog.mjs";
import { englishLang, renderResource, hasCode } from "./resource-view.mjs";

document.documentElement.classList.add("js");
let language = document.documentElement.lang.startsWith("zh") ? "zh" : "en";
let activeFilter = "All";
let corpusSources = [];
let corpusCounts = {};
let corpusLoadState = "idle";
let corpusLoadPromise;
let corpusRetrying = false;
let corpusLimit = 24;
let copyTimer;
const $ = (selector) => document.querySelector(selector);
const icon = (name) =>
  `<svg class="icon" aria-hidden="true"><use href="/assets/fontawesome/icons.svg#${name}"></use></svg>`;
const categoryIcons = {
  All: "filter",
  Models: "foundation",
  Papers: "paper",
  Tools: "code",
  Datasets: "foundation",
  Guides: "guide",
  Evaluations: "evaluation",
  Foundations: "foundation",
};
function renderCopyButton(key = "copyCode") {
  $("#copy-code").innerHTML =
    icon(key === "copied" ? "check" : "copy") +
    "<span>" +
    escapeHTML(t(key)) +
    "</span>";
}
const escapeHTML = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
const safeURL = (value) => {
  try {
    const url = new URL(value);
    return /^https?:$/.test(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
};
function t(key) {
  return translations[language][key] ?? translations.en[key] ?? key;
}
// "Papers with code" narrows only categories whose entries carry an `artifacts` record.
// Elsewhere it is cleared and disabled, so it cannot empty a list of tools or models.
const artifactCategories = new Set(
  resources.filter((resource) => resource.artifacts).map((resource) => resource.category),
);
function renderResources() {
  const query = $("#resource-search").value.trim().toLocaleLowerCase();
  const codeFilter = $("#code-filter");
  codeFilter.disabled =
    activeFilter === "All"
      ? artifactCategories.size === 0
      : !artifactCategories.has(activeFilter);
  if (codeFilter.disabled) codeFilter.checked = false;
  const codeOnly = codeFilter.checked;
  const filtered = resources.filter(
    (resource) =>
      (activeFilter === "All" || resource.category === activeFilter) &&
      (!codeOnly || hasCode(resource)) &&
      `${resource.title} ${resource.by} ${resource.en} ${resource.zh} ${resource.category}`
        .toLocaleLowerCase()
        .includes(query),
  );
  $("#resource-list").innerHTML = filtered.map(resource => renderResource(resource, language, translations)).join("");
  $("#result-count").textContent = t("resourceCount")(
    filtered.length,
    resources.length,
  );
  $("#empty-state").hidden = filtered.length !== 0;
  $("#model-evidence").hidden = activeFilter !== "Models";
}
function selectFilter(filter) {
  activeFilter = filter;
  document.querySelectorAll("[data-filter]").forEach((button) => {
    const selected = button.dataset.filter === filter;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  renderResources();
}
function setLanguage(next) {
  language = next;
  // The generated HTML owns <html lang>, the title and social metadata for each URL.
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.innerHTML = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  document
    .querySelectorAll("[data-language]")
    .forEach((button) =>
      button.setAttribute(
        "aria-current",
        button.dataset.language === language ? "page" : "false",
      ),
    );
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.innerHTML =
      icon(categoryIcons[button.dataset.filter]) +
      "<span>" +
      escapeHTML(t("filter" + button.dataset.filter)) +
      "</span><span class=\"filter-count\" aria-hidden=\"true\">" +
      (button.dataset.filter === "All" ? resources.length : resources.filter(row => row.category === button.dataset.filter).length) +
      "</span>";
  });
  const repository =
    "https://github.com/reacher-z/Awesome-Jev/blob/main/";
  document.querySelector('[data-document="readme"]').href =
    repository + (language === "zh" ? "README.zh-CN.md" : "README.md");
  document.querySelector('[data-document="survey"]').href = language === "zh" ? "/zh/guide/" : "/guide/";
  renderCopyButton();
  clearTimeout(copyTimer);
  $("#copy-status").textContent = "";
  renderResources();
  renderCorpus();
}
document
  .querySelectorAll("[data-filter]")
  .forEach((button) =>
    button.addEventListener("click", () => selectFilter(button.dataset.filter)),
  );
document.querySelectorAll("[data-filter-link]").forEach((link) =>
  link.addEventListener("click", () => {
    $("#resource-search").value = "";
    selectFilter(link.dataset.filterLink);
  }),
);
$("#resource-search").addEventListener("input", renderResources);
$("#code-filter").addEventListener("change", renderResources);
document
  .querySelectorAll("form[role=search]")
  .forEach((form) =>
    form.addEventListener("submit", (event) => event.preventDefault()),
  );
$("#reset-filters").addEventListener("click", () => {
  $("#resource-search").value = "";
  $("#code-filter").checked = false;
  selectFilter("All");
  $("#resource-search").focus();
});
document.addEventListener("keydown", (event) => {
  if (
    event.key === "/" &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.altKey &&
    !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) &&
    !document.activeElement.isContentEditable
  ) {
    event.preventDefault();
    $("#resource-search").focus();
    $("#resource-search").scrollIntoView({ block: "center" });
  }
});
$("#copy-code").addEventListener("click", async () => {
  const code = $("#quickstart-code").textContent;
  try {
    if (!navigator.clipboard) throw new Error("Clipboard unavailable");
    await navigator.clipboard.writeText(code);
    renderCopyButton("copied");
    $("#copy-status").textContent = t("copied");
  } catch {
    const range = document.createRange();
    range.selectNodeContents($("#quickstart-code"));
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    renderCopyButton("copyFailed");
    $("#copy-status").textContent = t("copyFailed");
  }
  clearTimeout(copyTimer);
  copyTimer = setTimeout(() => {
    renderCopyButton();
  }, 3000);
});

function normalizeSource(source) {
  const description =
    source.description || source.summary || source.abstract || "";
  return {
    title: source.title || source.name || "",
    url: safeURL(source.url || source.link || source.source_url),
    description:
      typeof description === "string" ? description : description.en || "",
    zh:
      source.description_zh ||
      source.summary_zh ||
      (typeof description === "object" ? description.zh : "") ||
      "",
    category: source.category || source.type || source.kind || "",
    year: source.year || "",
    status: source.status || source.review_status || source.screening || "",
    relation: source.relation || "",
    verification: source.verification_level || "",
    tags: [source.topic, ...(Array.isArray(source.tags) ? source.tags : [])].filter(Boolean).join(" "),
    curation: source.curation && safeURL(source.curation.evidence_url) ? {
      url: safeURL(source.curation.evidence_url),
      note: typeof source.curation.note === "string" ? source.curation.note : "",
      date: typeof source.curation.reviewed_at === "string" ? source.curation.reviewed_at.slice(0, 10) : "",
    } : null,
    by: source.authors || source.provider || source.source || "",
  };
}
function corpusMetadata(source) {
  const levels = {
    editorial_reviewed: "levelEditorial",
    content_screened: "levelContent",
    abstract_checked: "levelAbstract",
    metadata_only: "levelMetadata",
  };
  const relationLabels = {
    direct: ["Direct", "直接相关"],
    adjacent: ["Related", "邻近领域"],
    background: ["Background", "基础背景"],
  };
  const categoryLabels = {
    Datasets: "数据集",
    "Guides and evaluations": "指南与评测",
    Models: "模型",
    Papers: "论文",
    Projects: "项目",
    "Research foundations": "基础研究",
  };
  const category =
    language === "zh"
      ? categoryLabels[source.category] || source.category
      : source.category;
  const level = levels[source.verification]
    ? t(levels[source.verification])
    : source.status || source.verification;
  const relation =
    relationLabels[source.relation]?.[language === "zh" ? 1 : 0] ||
    source.relation;
  return [category, source.year, level, relation].filter(Boolean).join(" · ");
}
function curationDisclosure(source) {
  if (!source.curation) return "";
  const { url, note, date } = source.curation;
  return `<details class="corpus-curation"><summary>${escapeHTML(t("metadataCorrection"))}</summary><p>${escapeHTML(note)}</p><a href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(t("primaryMetadata"))}${date ? ` · ${escapeHTML(date)}` : ""}</a></details>`;
}
function renderCorpus() {
  if (!$("#corpus-list")) return;
  const retryButton = $("#corpus-retry");
  if (corpusLoadState === "loaded" && document.activeElement === retryButton) {
    $("#corpus-search").focus();
  }
  $("#corpus-recovery").hidden = corpusLoadState !== "error" && !corpusRetrying;
  retryButton.disabled = corpusLoadState === "loading";
  if (corpusLoadState !== "loaded") {
    $("#corpus-status").textContent = t(
      corpusLoadState === "error" ? "corpusLoadFailed" : "corpusLoading",
    );
    return;
  }
  $("#corpus-count").textContent = corpusSources.length
    ? t("corpusCount")(corpusSources.length)
    : "";
  $("#corpus-audit-counts").textContent =
    Number.isFinite(corpusCounts.checked_sources) &&
    Number.isFinite(corpusCounts.metadata_only)
      ? t("corpusAuditCounts")(
          corpusCounts.checked_sources,
          corpusCounts.metadata_only,
        )
      : "";
  document.querySelectorAll("[data-count-key]").forEach((element) => {
    const count = corpusCounts[element.dataset.countKey];
    element.textContent = Number.isFinite(count)
      ? t("sourceCount")(count)
      : "—";
  });
  const query = $("#corpus-search").value.trim().toLocaleLowerCase();
  const filtered = corpusSources.filter((source) =>
    `${source.title} ${source.description} ${source.zh} ${source.category} ${source.tags} ${source.by} ${source.status} ${source.relation} ${source.verification} ${corpusMetadata(source)}`
      .toLocaleLowerCase()
      .includes(query),
  );
  $("#corpus-status").textContent = corpusSources.length
    ? t("corpusResults")(filtered.length, corpusSources.length)
    : t("corpusUnavailable");
  $("#corpus-list").innerHTML = filtered
    .slice(0, corpusLimit)
    .map(
      (source) => {
        const description =
          language === "zh" && source.zh ? source.zh : source.description;
        return `<article class="corpus-row"><div><h3><a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer"${englishLang(source.title, language)}>${escapeHTML(source.title)}</a></h3><p${englishLang(description, language)}>${escapeHTML(description)}</p>${curationDisclosure(source)}</div><div class="corpus-entry-meta" data-verification="${escapeHTML(source.verification)}">${escapeHTML(corpusMetadata(source))}<span aria-hidden="true">${icon("external")}</span></div></article>`;
      },
    )
    .join("");
  if (corpusSources.length && !filtered.length)
    $("#corpus-list").innerHTML =
      `<p class="corpus-empty">${escapeHTML(t("corpusEmpty"))}</p>`;
  $("#corpus-more").hidden = filtered.length <= corpusLimit;
}
function loadCorpus({ retry = false } = {}) {
  if (corpusLoadPromise) return corpusLoadPromise;
  // Visibility and disclosure events must not retry a failed request.
  if (corpusLoadState === "error" && !retry) return Promise.resolve();
  corpusRetrying = retry;
  corpusLoadState = "loading";
  renderCorpus();
  corpusLoadPromise = fetch("/data/source-index.json", { cache: "no-cache" })
    .then((response) => {
      if (!response.ok) throw new Error("Source index not available");
      return response.json();
    })
    .then((data) => {
      corpusCounts = !Array.isArray(data) && data.counts ? data.counts : {};
      const sources = Array.isArray(data)
        ? data
        : data.sources || data.resources || data.entries || [];
      corpusSources = sources
        .map(normalizeSource)
        .filter((source) => source.title && source.url);
      corpusLoadState = "loaded";
    })
    .catch(() => {
      corpusLoadState = "error";
      corpusLoadPromise = undefined;
    })
    .finally(() => {
      corpusRetrying = false;
      renderCorpus();
    });
  return corpusLoadPromise;
}
if ($("#corpus-search")) {
  $("#corpus-retry").addEventListener("click", () => loadCorpus({ retry: true }));
  $("#corpus-search").addEventListener("input", () => {
    corpusLimit = 24;
    renderCorpus();
  });
  $("#corpus-more").addEventListener("click", () => {
    corpusLimit += 24;
    renderCorpus();
  });
  const disclosure = $(".corpus-disclosure");
  disclosure?.addEventListener("toggle", () => {
    if (disclosure.open) loadCorpus();
  });
  const corpus = $("#corpus");
  if ("IntersectionObserver" in window && corpus) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        observer.disconnect();
        loadCorpus();
      }
    }, { rootMargin: "300px" });
    observer.observe(corpus);
    if (disclosure?.open) loadCorpus();
  } else {
    loadCorpus();
  }
}
// Preserve old shared language links while serving each language at its own URL.
const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
if (requestedLanguage) {
  const destination = requestedLanguage.toLowerCase().startsWith("zh") ? "/zh/" : "/";
  if (window.location.pathname !== destination) window.location.replace(destination + window.location.hash);
}
setLanguage(document.documentElement.lang.startsWith("zh") ? "zh" : "en");
