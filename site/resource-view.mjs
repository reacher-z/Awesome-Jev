export const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"})[char]);
const icon = name => `<svg class="icon" aria-hidden="true"><use href="/assets/fontawesome/icons.svg#${name}"></use></svg>`;
const categoryIcons={Papers:"paper",Models:"foundation",Tools:"code",Datasets:"foundation",Evaluations:"evaluation",Guides:"guide",Foundations:"foundation"};
function localizedMetadata(value, language) {
  if (language !== "zh") return value;
  const labels = {
    "Official cookbook": "官方实践教程",
    "API concepts": "API 概念",
    "Probability & routing": "概率与路由",
    "Limitations · reviewed October 2, 2026":
      "已知局限 · 2026 年 10 月 2 日审阅",
    "Interactive evaluation explorer": "交互式评测浏览器",
    "Workflow integration": "工作流集成",
    "four datasets": "四个数据集",
    "Coding agents": "编码 agent",
    "Cookbooks & demos": "教程与演示",
    "Hugging Face · community": "Hugging Face · 社区",
    "TypeSafe · September 15, 2026": "TypeSafe · 2026 年 9 月 15 日",
    "Author PDF": "作者提供的 PDF",
    "Training mixture": "训练混合数据",
    "Evaluation archive": "评测运行归档",
  };
  return Object.entries(labels).reduce(
    (text, [source, translated]) => text.replace(source, translated),
    value,
  );
}
function provenance(resource) {
  return (
    resource.provenance ||
    (resource.category === "Papers"
      ? "preprint"
      : resource.category === "Foundations"
        ? "background"
        : "community")
  );
}
export function renderResource(resource, language, translations) {
 const t=key=>translations[language][key] ?? translations.en[key] ?? key;
 return `<article class="resource-row"><div class="resource-heading"><h3 class="resource-title"><a href="${escapeHTML(resource.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(resource.title)}</a></h3><p class="resource-subtitle"><span class="resource-category">${icon(categoryIcons[resource.category])}${escapeHTML(t("filter" + resource.category))}</span> · ${escapeHTML(localizedMetadata(resource.by, language))} · <span class="resource-provenance">${escapeHTML(t(provenance(resource)))}</span></p></div><p class="resource-description">${escapeHTML(resource[language])}</p><span class="resource-arrow" aria-hidden="true">${icon("external")}</span></article>`;
}

export function renderModelRow(resource, language) {
 const zh=language==='zh';
 const license=zh ? ({'Not declared':'未声明','Apache-2.0 weights; MIT server':'权重 Apache-2.0；服务代码 MIT'})[resource.license] || resource.license : resource.license;
 const group=resource.license==='CC BY-NC 4.0'?'noncommercial':resource.license==='Qwen Research'?'research':resource.license==='Not declared'?'undeclared':resource.license.startsWith('Apache-2.0')?'apache':'other';
 return `<tr class="model-row" data-license-group="${group}"><th scope="row"><a href="${escapeHTML(resource.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(resource.title)} ${icon('external')}</a><span class="model-publisher">${escapeHTML(resource.publisher)}</span></th><td class="model-license" data-label="${zh?'声明许可':'Declared license'}">${escapeHTML(license)}</td><td class="model-scope" data-label="${zh?'范围与证据':'Scope and evidence'}">${escapeHTML(resource[language])}</td></tr>`;
}
