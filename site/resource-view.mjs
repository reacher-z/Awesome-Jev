export const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"})[char]);
const icon = name => `<svg class="icon" aria-hidden="true"><use href="/assets/fontawesome/icons.svg#${name}"></use></svg>`;
const categoryIcons={Papers:"paper",Models:"foundation",Tools:"code",Datasets:"foundation",Evaluations:"evaluation",Guides:"guide",Foundations:"foundation"};
// Descriptive parts of `by` ("Publisher · descriptor · license"), matched whole so a
// short phrase such as "runtime" cannot rewrite part of a longer one. Names, venues,
// dates, versions and license identifiers stay as written.
function localizedMetadata(value, language) {
  if (language !== "zh") return value;
  const labels = {
    "Official cookbook": "官方实践教程",
    "API concepts": "API 概念",
    "Probability & routing": "概率与路由",
    "Limitations": "已知局限",
    "reviewed October 2, 2026": "2026 年 10 月 2 日审阅",
    "Interactive evaluation explorer": "交互式评测浏览器",
    "Workflow integration": "工作流集成",
    "four datasets": "四个数据集",
    "Coding agents": "编码 agent",
    "Cookbooks & demos": "教程与演示",
    "community": "社区",
    "September 15, 2026": "2026 年 9 月 15 日",
    "Author PDF": "作者提供的 PDF",
    "Training mixture": "训练混合数据",
    "Evaluation archive": "评测运行归档",
    "Apache-2.0 weights; MIT server": "权重 Apache-2.0；服务代码 MIT",
    "Qwen2.5-Omni-3B derivative": "Qwen2.5-Omni-3B 衍生模型",
    "license not declared": "未声明许可",
    "browser port": "浏览器移植版",
    "WebGPU port": "WebGPU 移植版",
    "training code": "训练代码",
    "multimodal runtime": "多模态运行时",
    "independent runtime": "独立运行时",
    "runtime": "运行时",
    "MIT code": "代码 MIT",
    "Thai/English pipeline": "泰英双语流水线",
    "policy and replay": "策略与回放",
    "decision learning": "决策学习",
    "experimental generator": "实验性生成器",
    "browser comparison": "浏览器对比",
    "RAG evaluation": "RAG 评测",
    "partial public split": "部分公开切分",
    "recorded-output analysis": "已记录输出分析",
    "Community evaluation": "社区评测",
    "100 queries": "100 个查询",
    "single run": "单次运行",
    "CC BY-NC 4.0 data": "数据 CC BY-NC 4.0",
    "Methodology v1.0": "方法说明 v1.0",
    "community survey v0.5": "社区综述 v0.5",
    "author report": "作者报告",
  };
  return value
    .split(" · ")
    .map((part) => (Object.hasOwn(labels, part) ? labels[part] : part))
    .join(" · ");
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
// Chinese pages show most titles and some fallbacks in English; mark them so screen
// readers switch voice (WCAG 3.1.2 Language of Parts).
export const englishLang = (text, language) =>
  language === "zh" && !/[\u3400-\u9fff]/u.test(String(text ?? "")) ? ' lang="en"' : "";
export function renderResource(resource, language, translations) {
 const t=key=>translations[language][key] ?? translations.en[key] ?? key;
 return `<article class="resource-row"><div class="resource-heading"><h3 class="resource-title"><a href="${escapeHTML(resource.url)}" target="_blank" rel="noopener noreferrer"${englishLang(resource.title, language)}>${escapeHTML(resource.title)}</a></h3><p class="resource-subtitle"><span class="resource-category">${icon(categoryIcons[resource.category])}${escapeHTML(t("filter" + resource.category))}</span> · ${escapeHTML(localizedMetadata(resource.by, language))} · <span class="resource-provenance">${escapeHTML(t(provenance(resource)))}</span></p></div><p class="resource-description">${escapeHTML(resource[language])}</p><span class="resource-arrow" aria-hidden="true">${icon("external")}</span></article>`;
}

export function renderModelRow(resource, language) {
 const zh=language==='zh';
 const license=zh ? ({'Not declared':'未声明','Apache-2.0 weights; MIT server':'权重 Apache-2.0；服务代码 MIT'})[resource.license] || resource.license : resource.license;
 const group=resource.license==='CC BY-NC 4.0'?'noncommercial':resource.license==='Qwen Research'?'research':resource.license==='Not declared'?'undeclared':resource.license.startsWith('Apache-2.0')?'apache':'other';
 return `<tr class="model-row" data-license-group="${group}"><th scope="row"><a href="${escapeHTML(resource.url)}" target="_blank" rel="noopener noreferrer"${englishLang(resource.title, language)}>${escapeHTML(resource.title)} ${icon('external')}</a><span class="model-publisher">${escapeHTML(resource.publisher)}</span></th><td class="model-license" data-label="${zh?'声明许可':'Declared license'}">${escapeHTML(license)}</td><td class="model-scope" data-label="${zh?'范围与证据':'Scope and evidence'}">${escapeHTML(resource[language])}</td></tr>`;
}
