#!/usr/bin/env node
// Build ordinary HTML from the same curated data used by the browser.
// No remote requests, clock-based dates, dependencies, or crawler-specific output.
import { readFile, writeFile, mkdir, readdir, rm, rmdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import { weeklyPaperCounts, activitySVG, activityTable, activityText } from './paper_activity.mjs';
import { resources, translations, paperThemes } from '../site/catalog.mjs';
import { renderResource, renderModelRow, renderPaperRow, renderEvidenceLegend, evidenceOf, englishLang, escapeHTML as esc, artifactKinds, hasCode } from '../site/resource-view.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const origin = 'https://awesomejev.github.io';
const repo = 'https://github.com/reacher-z/Awesome-Jev';
const contentDate = '2026-10-17'; // Update only when curated page content changes.
const guide = JSON.parse(await readFile(resolve(root, 'data/search-guide.json'), 'utf8'));
if (typeof guide.updated!=='string' || !/^\d{4}-\d{2}-\d{2}$/.test(guide.updated)) throw new Error('Invalid search guide date.');
for (const language of ['en','zh']) {
  const doc=guide[language];
  if (!doc || ['title','description','intro'].some(key=>typeof doc[key]!=='string' || !doc[key].trim()) || !Array.isArray(doc.sections) || !doc.sections.length) throw new Error('Incomplete bilingual search guide.');
  if (new Set(doc.sections.map(section=>section.id)).size!==doc.sections.length) throw new Error('Duplicate search guide section.');
  for (const section of doc.sections) {
    if (typeof section.id!=='string' || !/^[a-z0-9-]+$/.test(section.id) || typeof section.title!=='string' || !section.title.trim() || !Array.isArray(section.paragraphs) || !section.paragraphs.length) throw new Error('Invalid search guide section.');
    for (const paragraph of section.paragraphs) {
      if (typeof paragraph.text!=='string' || !paragraph.text.trim() || !Array.isArray(paragraph.sources)) throw new Error('Invalid search guide paragraph.');
      for (const source of paragraph.sources) {
        const url=URL.canParse(source.url) ? new URL(source.url) : null;
        if (!url || url.protocol!=='https:' || url.username || url.password || typeof source.label!=='string' || !source.label.trim()) throw new Error('Invalid search guide citation.');
      }
    }
  }
}
if (JSON.stringify(guide.en.sections.map(s=>s.id))!==JSON.stringify(guide.zh.sections.map(s=>s.id))) throw new Error('Search guide translations must preserve sections.');
const topicData = JSON.parse(await readFile(resolve(root, 'data/research-topics.json'), 'utf8'));
if (topicData.schema_version !== 1 || !Array.isArray(topicData.topics)) throw new Error('Invalid research topics.');
const topics = topicData.topics;
if (new Set(topics.map(topic=>topic.slug)).size !== topics.length) throw new Error('Duplicate topic route.');
for (const topic of topics) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(topic.slug) || !/^\d{4}-\d{2}-\d{2}$/.test(topic.published) || !/^\d{4}-\d{2}-\d{2}$/.test(topic.updated) || topic.published>topic.updated) throw new Error('Invalid topic identity or dates.');
  for (const language of ['en','zh']) {
    const doc=topic[language];
    if (!doc || ['title','description','answer','scope'].some(key=>typeof doc[key]!=='string' || !doc[key].trim()) || !Array.isArray(doc.sections) || !doc.sections.length || !guide[language].sections.some(section=>section.id===topic.guide_section)) throw new Error('Incomplete bilingual research topic.');
    if (new Set(doc.sections.map(section=>section.id)).size!==doc.sections.length) throw new Error('Duplicate topic section.');
    for (const section of doc.sections) {
      if (!/^[a-z0-9-]+$/.test(section.id) || !section.title || !section.text || !Array.isArray(section.sources)) throw new Error('Invalid topic section.');
      for (const source of section.sources) {
        const url=new URL(source.url);
        if (url.protocol!=='https:' || url.username || url.password || !source.label) throw new Error('Invalid topic citation.');
      }
    }
  }
  if (JSON.stringify(topic.en.sections.map(s=>s.id))!==JSON.stringify(topic.zh.sections.map(s=>s.id))) throw new Error('Topic translations must preserve sections.');
}
const expansion = JSON.parse(await readFile(resolve(root, 'data/expansion-progress-2026-10-16.json'), 'utf8'));
const discoveryLocalization = JSON.parse(await readFile(resolve(root, 'data/discovery-translations.zh-CN.json'), 'utf8'));
if (discoveryLocalization.schema_version !== 1 || discoveryLocalization.language !== 'zh-CN' ||
    !discoveryLocalization.translations || typeof discoveryLocalization.translations !== 'object' || Array.isArray(discoveryLocalization.translations)) {
  throw new Error('Invalid Chinese discovery translations.');
}
const discoveryTranslations = discoveryLocalization.translations;
const template = await readFile(resolve(root, 'templates/index.html'), 'utf8');
// A missing interface string would silently render English on the Chinese pages.
const interfaceKeys = new Set([...Object.keys(translations.en), ...Object.keys(translations.zh),
  ...[...template.matchAll(/\bdata-i18n(?:-aria|-placeholder)?="([^"]+)"/g)].map(match => match[1])]);
const untranslated = [...interfaceKeys].filter(key => ['en','zh'].some(language => !Object.hasOwn(translations[language], key)));
if (untranslated.length) throw new Error(`Missing interface translations for ${untranslated.join(', ')}. Add every key to both languages in site/catalog.mjs.`);
// Stable URLs for unchanged bytes; changed data cannot reuse an older browser cache entry.
const assetURLs = Object.fromEntries(await Promise.all(
  ['app.js', 'catalog.mjs', 'resource-view.mjs', 'styles.css', 'model-directory.js', 'paper-directory.js'].map(async name => {
    const bytes = await readFile(resolve(root, 'site', name));
    const digest = createHash('sha256').update(bytes).digest('hex').slice(0, 12);
    return [name, `/${name}?v=${digest}`];
  }),
));
const importMap = {imports: {
  '/catalog.mjs': assetURLs['catalog.mjs'],
  '/resource-view.mjs': assetURLs['resource-view.mjs'],
}};
const papers = resources.filter(row => row.category === 'Papers');
const models = resources.filter(row => row.category === 'Models');
for (const model of models) {
  if (!model.publisher || !model.license || model.provenance !== 'modelcard') throw new Error('Model comparison requires reviewed publisher, license and model-card evidence.');
}
const unmarked = resources.filter(row => !evidenceOf(row)).map(row => row.title);
if (unmarked.length) throw new Error(`No evidence marker for the provenance of ${unmarked.join(', ')}.`);
// Artifact chips accept known kinds only, each holding one or more https URLs.
for (const {title, artifacts} of resources.filter(row => row.artifacts)) {
  const {unverified, ...links} = artifacts;
  const valid = Object.entries(links).every(([kind, urls]) => artifactKinds.includes(kind) && [urls].flat().length && [urls].flat().every(url => /^https:\/\/\S+$/.test(url)));
  if (!valid || (unverified !== undefined && !artifactKinds.includes(unverified))) throw new Error(`Invalid artifact links for ${title}.`);
}
// Every paper names one of the README sections; an artifact caveat comes in both languages.
for (const paper of papers) {
  if (!paperThemes.some(theme=>theme.id===paper.theme)) throw new Error(`Paper without a known README theme: ${paper.url}`);
  if (paper.artifact_note!==undefined && ['en','zh'].some(language=>typeof paper.artifact_note[language]!=='string' || !paper.artifact_note[language].trim())) throw new Error(`Incomplete bilingual artifact note: ${paper.url}`);
}
const activity = weeklyPaperCounts(papers, paperThemes, contentDate);
const categoryOrder = ['Papers','Models','Datasets','Projects','Tools','Evaluations','Guides and evaluations','Guides','Research foundations','Foundations'];
const relationLabels = {direct:['Directly related','直接相关'],adjacent:['Related field','邻近领域'],background:['Research background','研究背景']};
// Discovery rows name the same verification tiers as the homepage corpus legend.
const evidenceLabels = {editorial_reviewed:'levelEditorial',content_screened:'levelContent',abstract_checked:'levelAbstract'};
const categoryLabels = {Papers:'论文',Models:'模型',Datasets:'数据集',Projects:'项目',Tools:'工具',Evaluations:'评测','Guides and evaluations':'指南与评测',Guides:'指南','Research foundations':'基础研究',Foundations:'基础研究'};
if (!Array.isArray(expansion.additions) || !Number.isInteger(expansion.accepted_new_sources) || expansion.accepted_new_sources !== expansion.additions.length || !Number.isInteger(expansion.target_new_sources) || expansion.target_new_sources < 1) throw new Error('Invalid expansion report counts.');
for (const row of expansion.additions) {
  if (['title','url','category','description'].some(key=>typeof row[key]!=='string' || !row[key].trim()) || !Object.hasOwn(relationLabels,row.relation) || !Object.hasOwn(evidenceLabels,row.verification_level)) throw new Error('Invalid expansion source metadata or evidence tier.');
  // Exact source text binds a translation to the reviewed wording. A changed
  // limitation must be translated again instead of silently reusing stale text.
  const translated = discoveryTranslations[row.description];
  if (!Object.hasOwn(discoveryTranslations, row.description) || typeof translated !== 'string' || !/[\u3400-\u9fff]/u.test(translated)) {
    throw new Error('Missing Chinese discovery description translation. Update data/discovery-translations.zh-CN.json.');
  }
  const url = new URL(row.url);
  if (!['https:','http:'].includes(url.protocol) || url.username || url.password) throw new Error('Invalid expansion source URL.');
}
if (new Set(expansion.additions.map(row=>row.url)).size !== expansion.additions.length) throw new Error('Duplicate expansion source URL.');
const categoryRank = category => categoryOrder.includes(category) ? categoryOrder.indexOf(category) : categoryOrder.length;
const discoveries = [...expansion.additions].sort((a,b)=>categoryRank(a.category)-categoryRank(b.category) || a.category.localeCompare(b.category,'en') || a.title.localeCompare(b.title,'en') || a.url.localeCompare(b.url,'en'));
const discoveryCategories = [...new Set(discoveries.map(row=>row.category))];
const discoveryCounts = Object.fromEntries(discoveryCategories.map(category=>[category,discoveries.filter(row=>row.category===category).length]));
if (!expansion.by_category || Object.keys(expansion.by_category).length!==discoveryCategories.length || discoveryCategories.some(category=>expansion.by_category[category]!==discoveryCounts[category])) throw new Error('Expansion category counts do not match accepted sources.');
// A directory's date is the newest date among the entries it renders, so new content moves its sitemap lastmod.
const newestDate = dates => dates.filter(date => /^\d{4}-\d{2}-\d{2}$/.test(date)).sort().at(-1);
const discoveryDate = newestDate(expansion.additions.map(row => typeof row.retrieved_at === 'string' ? row.retrieved_at.slice(0,10) : '')) || contentDate;
const topicsDate = newestDate([contentDate, ...topics.map(topic => topic.updated)]);
const outputs = new Map();
const route = (language, section = '') => `${language === 'zh' ? '/zh/' : '/'}${section ? section + '/' : ''}`;
// Fragments written into other pages must name a guide section or a homepage element that exists.
const guideLink = (language, id) => {
  if (!guide[language].sections.some(section => section.id === id)) throw new Error(`Missing ${language} guide section #${id} linked from a generated page.`);
  return `${route(language, 'guide')}#${id}`;
};
const homeLink = (language, id) => {
  // Only a real id attribute counts, not data-id="..." or similar.
  if (!new RegExp(`(?:^|\\s)id="${id}"`).test(template)) throw new Error(`Missing homepage element #${id} in templates/index.html.`);
  return `${route(language)}#${id}`;
};
const t = (language, key) => translations[language][key] ?? translations.en[key];
const json = value => JSON.stringify(value).replace(/</g, '\\u003c');
const schemaTag = value => `<script type="application/ld+json">${json(value)}</script>`;
const identity = [
  {'@type':'Organization','@id':origin+'/#organization',name:'AwesomeJev',url:origin+'/',sameAs:[repo,'https://github.com/AwesomeJev'],description:'Independent community research collection; not affiliated with TypeSafe AI.'},
  {'@type':'WebSite','@id':origin+'/#website',name:'AwesomeJev',alternateName:'Awesome Jev',url:origin+'/',inLanguage:['en','zh-CN'],publisher:{'@id':origin+'/#organization'}}
];
function pageSchema(language, section, title, description, list, article) {
  const url = origin + route(language, section);
  const page = {'@type':list ? 'CollectionPage' : 'WebPage','@id':url+'#page',url,name:title,description,inLanguage:language==='zh'?'zh-CN':'en',isPartOf:{'@id':origin+'/#website'}};
  if (list) page.mainEntity = {'@type':'ItemList',numberOfItems:list.length,itemListElement:list.map((row, i)=>({'@type':'ListItem',position:i+1,name:row.title,url:row.url}))};
  else page.mainEntity = {'@type':'Article',headline:title,inLanguage:page.inLanguage,dateModified:article?.updated || guide.updated,...(article?{datePublished:article.published}:{}),author:{'@id':origin+'/#organization'},publisher:{'@id':origin+'/#organization'},mainEntityOfPage:{'@id':page['@id']},citation:article?.citations || [...new Set(guide[language].sections.flatMap(s=>s.paragraphs.flatMap(p=>p.sources.map(source=>source.url))))]};
  const graph = [...identity, page];
  if (section) {
    const crumbs=[{'@type':'ListItem',position:1,name:'Awesome Jev',item:origin+route(language)}];
    if (section.startsWith('topics/')) crumbs.push({'@type':'ListItem',position:2,name:language==='zh'?'研究专题':'Research topics',item:origin+route(language,'topics')});
    crumbs.push({'@type':'ListItem',position:crumbs.length+1,name:title,item:url});
    graph.push({'@type':'BreadcrumbList',itemListElement:crumbs});
  }
  return {'@context':'https://schema.org','@graph':graph};
}
// One language cluster for both the page head and the sitemap, so the two never diverge.
const alternateLinks = section => [{hreflang:'en',href:origin+route('en',section)},{hreflang:'zh-CN',href:origin+route('zh',section)},{hreflang:'x-default',href:origin+route('en',section)}];
function alternates(section) {
  return alternateLinks(section).map(({hreflang,href})=>`<link rel="alternate" hreflang="${hreflang}" href="${href}" />`).join('\n');
}
function localizeHTML(html, language) {
  html = html.replace(/<([a-z][a-z0-9]*)\b([^>]*\bdata-i18n="([^"]+)"[^>]*)>[\s\S]*?<\/\1\s*>/g, (all,tag,attrs,key)=>typeof t(language,key)==='string'?`<${tag}${attrs}>${t(language,key)}</${tag}>`:all);
  html = html.replace(/<([a-z][a-z0-9]*)\b([^>]*\bdata-i18n-(placeholder|aria)="([^"]+)"[^>]*)>/g, (all,tag,attrs,kind,key)=>{
    const name = kind === 'aria' ? 'aria-label' : 'placeholder';
    return `<${tag}${attrs.replace(new RegExp(`${name}="[^"]*"`), ()=>`${name}="${esc(t(language,key))}"`)}>`;
  });
  return html;
}
function home(language) {
  const title = language === 'zh' ? 'Awesome Jev — System One 模型与研究' : 'Awesome Jev — System One Models & Research';
  const description = t(language,'metaDescription');
  let html = template.replace('<html lang="en">',`<html lang="${language==='zh'?'zh-CN':'en'}">`);
  const values = {TITLE:esc(title),CANONICAL:origin+route(language),STRUCTURED_DATA:schemaTag(pageSchema(language,'',title,description,resources)),PAPERS_URL:route(language,'papers'),PAPERS_LABEL:language==='zh'?'论文目录':'Research papers',DISCOVERIES_URL:route(language,'discoveries'),DISCOVERIES_LABEL:language==='zh'?'新增资源':'New resources',RESOURCE_ROWS:resources.map(row=>renderResource(row,language,translations)).join('\n'),RESOURCE_COUNT:esc(t(language,'resourceCount')(resources.length,resources.length)),NOSCRIPT_NOTE:language==='zh'?'所有精选资源已列在本页。启用 JavaScript 后可使用搜索与筛选；也可浏览独立论文目录。':'All curated resources are listed on this page. Enable JavaScript to search and filter, or browse the dedicated papers directory.'};
  values.IMPORT_MAP = `<script type="importmap">${json(importMap)}</script>`;
  values.TOPICS_URL = route(language,'topics');
  values.TOPICS_LABEL = language==='zh'?'研究专题':'Research topics';
  values.MODELS_URL = route(language,'models');
  values.MODELS_LABEL = language==='zh'?'模型目录':'Model directory';
  values.CONTENT_DATE = contentDate;
  values.EVIDENCE_LEGEND = renderEvidenceLegend(language,translations,`${repo}/blob/main/docs/source-audit.md#evidence-markers`);
  values.CODE_COUNT = String(resources.filter(hasCode).length);
  values.COLLECTION_STATS = `<dl class="collection-stats">${[[resources.length,language==='zh'?'精选资源':'curated resources',homeLink(language,'collection')],[papers.length,language==='zh'?'论文':'papers',route(language,'papers')],[models.length,language==='zh'?'模型':'models',route(language,'models')],[expansion.accepted_new_sources,language==='zh'?'扩展来源':'reviewed additions',route(language,'discoveries')]].map(([number,label,url])=>`<div><dt><a href="${url}">${label}</a></dt><dd>${number}</dd></div>`).join('')}</dl>`;
  values.APP_MODULE_URL = esc(assetURLs['app.js']);
  values.STYLESHEET_URL = esc(assetURLs['styles.css']);
  // Function replacers keep `$&`, `$1` and `$$` in curated text literal.
  for (const [key,value] of Object.entries(values)) html=html.replaceAll(`{{${key}}}`,()=>value);
  html=localizeHTML(html,language)
    .replace(/(<meta\s+(?:name="description"|property="og:description"|name="twitter:description")\s+content=")[^"]*("\s*\/>)/g,(_,start,end)=>start+esc(description)+end)
    .replace(/(<meta\s+(?:property="og:title"|name="twitter:title")\s+content=")[^"]*("\s*\/>)/g,(_,start,end)=>start+esc(title)+end)
    .replace(/(<meta\s+(?:property="og:image:alt"|name="twitter:image:alt")\s+content=")[^"]*("\s*\/>)/g,(_,start,end)=>start+esc(t(language,'socialImageAlt'))+end)
    .replace(/(<meta property="og:url" content=")[^"]+/,(_,start)=>start+origin+route(language))
    .replace(/(<meta property="og:locale" content=")[^"]+/,(_,start)=>start+(language==='zh'?'zh_CN':'en_US'))
    .replace(/(<meta property="og:locale:alternate" content=")[^"]+/,(_,start)=>start+(language==='zh'?'en_US':'zh_CN'))
    .replace(/(data-language="(en|zh)")/g,(_,attr,code)=>`${attr} aria-current="${code===language?'page':'false'}"`)
    .replace(/href="\/guide\/" data-document="survey"/,`href="${route(language,'guide')}" data-document="survey"`);
  if(language==='zh')html=html.replace('href="https://github.com/reacher-z/Awesome-Jev/blob/main/README.md" data-document="readme"','href="https://github.com/reacher-z/Awesome-Jev/blob/main/README.zh-CN.md" data-document="readme"');
  html=html.replace(/<button\b([^>]*data-filter="([^"]+)"[^>]*)>([\s\S]*?)<\/button>/g,(_,attrs,category,label)=>`<button${attrs}>${label}<span class="filter-count" aria-hidden="true">${category==='All'?resources.length:resources.filter(row=>row.category===category).length}</span></button>`);
  return html;
}
// indexable=false keeps the site chrome but drops canonical, alternates, social and
// structured data, for pages served at arbitrary URLs such as 404.html.
function shell(language, section, title, description, body, list, article, indexable=true) {
  const isZh=language==='zh', pageURL=origin+route(language,section);
  // A section's link is the current page there; on a topic note it marks the current section.
  const current=navSection=>navSection===section?' aria-current="page"':section.startsWith(navSection+'/')?' aria-current="true"':'';
  return `<!doctype html>
<html lang="${isZh?'zh-CN':'en'}"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>${esc(title)} | Awesome Jev</title><meta name="description" content="${esc(description)}" />
${indexable?`<meta name="robots" content="index,follow,max-image-preview:large" /><link rel="canonical" href="${pageURL}" />
${alternates(section)}
<meta property="og:type" content="${section==='guide'||article?'article':'website'}" /><meta property="og:site_name" content="AwesomeJev" />
<meta property="og:title" content="${esc(title)}" /><meta property="og:description" content="${esc(description)}" /><meta property="og:url" content="${pageURL}" />
<meta property="og:locale" content="${isZh?'zh_CN':'en_US'}" /><meta property="og:image" content="${origin}/assets/social.png" /><meta name="twitter:card" content="summary_large_image" />`:'<meta name="robots" content="noindex" />'}
<link rel="icon" href="/favicon.svg" type="image/svg+xml" /><link rel="stylesheet" href="${assetURLs['styles.css']}" />
${indexable?schemaTag(pageSchema(language,section,title,description,list,article))+'\n':''}</head><body><a class="skip-link" href="#main">${isZh?'跳转到正文':'Skip to content'}</a><div class="page-shell">
<header class="masthead document-masthead"><a class="wordmark" href="${route(language)}"><span class="brand-mark" aria-hidden="true">aj</span>AwesomeJev.</a>
<nav class="main-nav" aria-label="${isZh?'主导航':'Main navigation'}"><a href="${route(language)}">${isZh?'资源索引':'Resources'}</a><a href="${route(language,'papers')}"${current('papers')}>${isZh?'论文':'Papers'}</a><a href="${route(language,'models')}"${current('models')}>${isZh?'模型':'Models'}</a><a href="${route(language,'topics')}"${current('topics')}>${isZh?'研究专题':'Topics'}</a><a href="${route(language,'discoveries')}"${current('discoveries')}>${isZh?'新增资源':'New resources'}</a><a href="${route(language,'guide')}"${current('guide')}>${isZh?'研究指南':'Research guide'}</a><a href="${repo}">GitHub</a></nav>
<div class="language-switch"><a href="${route('en',section)}" lang="en" hreflang="en" aria-current="${isZh?'false':'page'}">EN</a><span>/</span><a href="${route('zh',section)}" lang="zh-CN" hreflang="zh-CN" aria-current="${isZh?'page':'false'}">中文</a></div></header>
<main id="main" class="document-main${section==='models'?' model-directory':section==='papers'?' model-directory paper-directory':''}"><nav class="breadcrumbs" aria-label="${isZh?'当前位置':'Breadcrumb'}"><a href="${route(language)}">Awesome Jev</a><span aria-hidden="true"> / </span>${section.startsWith('topics/')?`<a href="${route(language,'topics')}">${isZh?'研究专题':'Research topics'}</a><span aria-hidden="true"> / </span>`:''}<span aria-current="page">${esc(section==='models'?(isZh?'模型目录':'Model directory'):title)}</span></nav>
<h1>${esc(title)}</h1><p class="document-deck">${esc(description)}</p>${body}</main>
<footer class="document-footer"><p>${isZh?'独立社区项目，与 TypeSafe AI 无隶属关系。':'Independent community project. Not affiliated with TypeSafe AI.'}</p><p><a href="${repo}">GitHub</a> · <a href="/references.bib">BibTeX</a> · <a href="${repo}/blob/main/LICENSE">MIT</a> · <a href="https://github.com/reacher-z">reacher-z</a></p></footer>
</div></body></html>\n`;
}
function topicLinks(language, currentSlug) {
  return `<nav class="document-toc" aria-label="${language==='zh'?'研究专题':'Research topics'}"><ul>${topics.filter(topic=>topic.slug!==currentSlug).map(topic=>`<li><a href="${route(language,'topics/'+topic.slug)}">${esc(topic[language].title)}</a></li>`).join('')}</ul></nav>`;
}
function topicsPage(language) {
  const isZh=language==='zh', title=isZh?'Jev 决策模型研究专题':'Jev decision model research topics';
  const description=isZh?'聚焦选项标签偏置、音频决策与图任务评测，连接原始研究、实践诊断与证据局限。':'Focused notes on option-label bias, audio decisions and graph evaluation, connecting primary research with practical diagnostics and evidence limits.';
  const body=`<p>${isZh?'每个专题提供简明回答、原始引用、建议检查与核查范围。作者报告的结果与本项目提出的评估流程分别标明。':'Each note gives a direct answer, primary references, proposed checks and review scope. Author-reported findings are distinguished from evaluation procedures proposed by this project.'}</p><div class="prose">${topics.map(topic=>`<section><h2><a href="${route(language,'topics/'+topic.slug)}">${esc(topic[language].title)}</a></h2><p>${esc(topic[language].description)}</p></section>`).join('')}</div>`;
  return shell(language,'topics',title,description,body,topics.map(topic=>({title:topic[language].title,url:origin+route(language,'topics/'+topic.slug)})));
}
function topicPage(language, topic) {
  const doc=topic[language], isZh=language==='zh';
  const citations=[...new Set(doc.sections.flatMap(section=>section.sources.map(source=>source.url)))];
  const body=`<p class="document-date">${isZh?'AwesomeJev 整理 · 更新':'By AwesomeJev · Updated'} <time datetime="${topic.updated}">${topic.updated}</time></p><div class="prose"><p><strong>${isZh?'简明回答：':'Short answer: '}</strong>${esc(doc.answer)}</p><p>${esc(doc.scope)}</p></div><nav class="document-toc" aria-label="${isZh?'本页目录':'On this page'}"><ol>${doc.sections.map(section=>`<li><a href="#${section.id}">${esc(section.title)}</a></li>`).join('')}</ol></nav><div class="prose">${doc.sections.map(section=>`<section id="${section.id}"><h2>${esc(section.title)}</h2><p>${esc(section.text)}${section.sources.length?' <span class="source-links">'+section.sources.map(source=>`<a href="${esc(source.url)}" rel="noopener noreferrer">${esc(source.label)}</a>`).join(' · ')+'</span>':''}</p></section>`).join('')}</div><p><a href="${guideLink(language,topic.guide_section)}">${isZh?'相关评估指南':'Related evaluation guide'} →</a> · <a href="${route(language,'papers')}">${isZh?'全部精选论文':'All selected papers'}</a></p><h2>${isZh?'继续阅读':'Continue reading'}</h2>${topicLinks(language,topic.slug)}`;
  return shell(language,'topics/'+topic.slug,doc.title,doc.description,body,undefined,{published:topic.published,updated:topic.updated,citations});
}
function guidePage(language) {
  const doc=guide[language], isZh=language==='zh';
  const toc=`<nav class="document-toc" aria-label="${isZh?'本页目录':'On this page'}"><ol>${doc.sections.map(s=>`<li><a href="#${esc(s.id)}">${esc(s.title)}</a></li>`).join('')}</ol></nav>`;
  const body=`<p class="document-date">${isZh?'更新':'Updated'} <time datetime="${guide.updated}">${guide.updated}</time> · <a href="${repo}/blob/main/docs/${isZh?'survey.zh-CN.md':'survey.md'}">${isZh?'完整研究综述':'Full research survey'}</a></p><p>${esc(doc.intro)}</p>${toc}<div class="prose">${doc.sections.map(s=>`<section id="${esc(s.id)}"><h2>${esc(s.title)}</h2>${s.paragraphs.map(p=>`<p>${esc(p.text)}${p.sources.length?' <span class="source-links">'+p.sources.map(source=>`<a href="${esc(source.url)}" rel="noopener noreferrer">${esc(source.label)}</a>`).join(' · ')+'</span>':''}</p>`).join('')}</section>`).join('')}</div><p><a href="${route(language,'papers')}">${isZh?'继续阅读：精选论文与版本':'Continue reading: selected papers and versions'} →</a></p>`;
  return shell(language,'guide',doc.title,doc.description,body+topicLinks(language));
}
function papersPage(language) {
  const isZh=language==='zh', title=isZh?'Jev 与类型化决策模型论文':'Jev and typed decision model papers';
  const description=isZh?'按版本日期整理的精选论文：评测、校准、路由、鲁棒性与模型架构，附原文和引用。':'Selected papers on evaluation, calibration, routing, robustness and decision-model architectures, with versioned primary sources and citations.';
  const t=key=>translations[language][key] ?? translations.en[key] ?? key;
  // The static table is complete and in catalog order (newest first), matching the ItemList;
  // paper-directory.js only adds the theme chips, the papers-with-code checkbox, search and re-sorting.
  const chip=(value,label,count,pressed,full)=>`<button type="button" class="filter-button${pressed?' active':''}" data-theme="${value}" aria-pressed="${pressed}"${full?` title="${esc(full)}"`:''}>${esc(label)}<span class="filter-count" aria-hidden="true">${count}</span></button>`;
  const controls=`<div class="paper-controls" data-paper-controls hidden><div class="filter-group" role="group" aria-label="${isZh?'筛选论文':'Filter papers'}">${chip('',isZh?'全部':'All',papers.length,true)}${paperThemes.map(theme=>chip(theme.id,theme.short[language],papers.filter(row=>row.theme===theme.id).length,false,theme[language])).join('')}<label class="filter-toggle"><input type="checkbox" id="paper-code-filter" /><span>${esc(t('filterHasCode'))}</span><span class="filter-count" aria-hidden="true">${papers.filter(hasCode).length}</span></label></div></div><div class="model-controls" data-paper-controls hidden><label class="model-search"><span>${isZh?'搜索论文':'Search papers'}</span><input id="paper-search" type="search" placeholder="${isZh?'标题、作者或主要发现':'Title, author or finding'}" autocomplete="off" /></label><label><span>${isZh?'排序':'Sort'}</span><select id="paper-sort"><option value="newest">${isZh?'最新优先':'Newest first'}</option><option value="oldest">${isZh?'最早优先':'Oldest first'}</option><option value="title">${isZh?'按标题':'Title A–Z'}</option></select></label><button id="paper-reset" type="button">${isZh?'重置':'Reset'}</button></div>`;
  const table=`<div class="model-list-meta"><p id="paper-result-count" role="status" aria-live="polite">${papers.length} / ${papers.length} ${isZh?'篇论文':'papers'}</p><p>${isZh?'均为 arXiv 预印本 · 结论为作者报告，未经复现':'All arXiv preprints · findings are author-reported, not reproduced'}</p></div><table class="paper-table"><caption class="sr-only">${isZh?'论文的版本日期、作者、主题、材料与主要发现':'Papers by version date, with authors, theme, artifacts and key finding'}</caption><thead><tr><th scope="col" aria-sort="descending">${isZh?'日期 · 版本':'Date · version'}</th><th scope="col">${isZh?'论文':'Paper'}</th><th scope="col">${isZh?'主题':'Theme'}</th><th scope="col">${isZh?'材料':'Artifacts'}</th><th scope="col">${isZh?'主要发现':'Key finding'}</th></tr></thead><tbody>${papers.map(row=>renderPaperRow(row,language,translations,paperThemes)).join('\n')}</tbody></table><p id="paper-empty" hidden>${isZh?'没有匹配项，请修改搜索或重置筛选。':'No matching papers. Change the search or reset the filters.'}</p>`;
  const body=`<p class="document-date">${isZh?'最近整理':'Last curated'} <time datetime="${contentDate}">${contentDate}</time> · ${papers.length} ${isZh?'篇论文':'papers'} · <a href="/references.bib">BibTeX</a> · <a href="/papers.json">JSON</a></p><p>${isZh?'日期对应已核查版本；简介与配套材料链接说明证据范围，不代表实验复现。':'Dates identify the reviewed versions. Summaries and linked artifacts describe evidence within its stated scope; they are not experimental reproductions.'}</p><section id="paper-list"><h2>${isZh?'精选论文':'Selected papers'} (${papers.length})</h2>${controls}${table}</section><script type="module" src="${assetURLs['paper-directory.js']}"></script><p><a href="${route(language,'guide')}">${isZh?'先读研究指南：接口、概率与评测':'Start with the research guide: interfaces, probabilities and evaluation'} →</a></p>${topicLinks(language)}`;
  return shell(language,'papers',title,description,body,papers);
}
function modelsPage(language) {
  const isZh=language==='zh';
  const title=isZh?'Jev 替代方案：决策模型':'Jev alternatives: decision models';
  const description=isZh?'按发布者、声明许可和适用范围比较独立 System One 模型，每项链接原始模型卡。':'Compare independent System One models by publisher, declared license and documented capability, with direct model-card links.';
  const body=`<p class="document-date">${models.length} ${isZh?'项精选模型':'selected models'} · ${isZh?'最近整理':'Last curated'} <time datetime="${contentDate}">${contentDate}</time> · <a href="/models.json">${isZh?'下载模型目录 JSON':'Download model directory JSON'}</a></p><details class="verification-legend"><summary>${isZh?'比较条件与许可说明':'Comparison and license notes'}<span aria-hidden="true">+</span></summary><div class="prose"><section><p>${isZh?'这些模型由独立发布者提供，并非 TypeSafe 发布的 Jev 权重。替代方案表示可供比较的研究与实现方向，不保证行为、准确率或接口完全等价。托管 Jev 的版本与能力应另查官方说明。':'These releases come from independent publishers, not TypeSafe’s Jev weights. An alternative is a candidate for comparison, not a guarantee of equivalent behavior, accuracy or interface support. Check the official documentation separately for hosted Jev versions and capabilities.'} <a href="https://docs.typesafe.ai/models">${isZh?'TypeSafe 模型说明':'TypeSafe model documentation'}</a></p><p>${isZh?'每项保留发布者、模型卡入口及简短的适用范围说明。声明许可不能从基础模型直接推断：代码、适配器、合并权重与数据可能适用不同条款。开放下载与商业使用许可也不是一回事；具体条件以对应发布者的材料为准。':'Each entry keeps its publisher, model-card link and a short scope note. Do not infer a release’s license from its base model: code, adapters, merged weights and data can have different terms. Availability for download and permission for commercial use are different questions; consult the publisher’s materials.'} <a href="${guideLink(language,'models-and-licenses')}">${isZh?'模型与许可指南':'Models and licenses guide'}</a></p><p>${isZh?'本目录不按未经统一复测的得分排名。比较时应对齐候选集、输入模态、标签来源、推理预算、硬件和评测切分，并区分公共测试、自行评测与含私有测试的完整榜单。条目说明来自已查材料，不代表本项目加载了模型或复现了结果。':'This directory does not rank releases by scores that we have not evaluated under common conditions. Match candidate sets, modalities, label sources, reasoning budgets, hardware and evaluation splits. Keep public tests, publisher-run evaluations and private-inclusive boards separate. The notes describe inspected documentation, not model execution or reproduced results.'} <a href="${guideLink(language,'decision-model-baselines')}">${isZh?'比较条件':'Comparison conditions'}</a></p></section></div></details><div class="model-controls" data-model-controls hidden><label class="model-search"><span>${isZh?'搜索模型':'Search models'}</span><input id="model-search" type="search" placeholder="${isZh?'名称、发布者或能力':'Name, publisher or capability'}" autocomplete="off" /></label><label><span>${isZh?'声明许可':'Declared license'}</span><select id="model-license"><option value="">${isZh?'全部许可':'All licenses'}</option><option value="apache">Apache-2.0</option><option value="noncommercial">CC BY-NC 4.0</option><option value="research">Qwen Research</option><option value="undeclared">${isZh?'未声明':'Not declared'}</option><option value="other">${isZh?'其他／参见模型卡':'Other / see card'}</option></select></label><button id="model-reset" type="button">${isZh?'重置':'Reset'}</button></div><div class="model-list-meta"><p id="model-result-count" role="status" aria-live="polite">${models.length} / ${models.length} ${isZh?'项模型':'models'}</p><p>${isZh?'来源：发布者模型卡 · 未统一复测':'Source: publisher model cards · no common rerun'}</p></div><table class="model-table"><caption class="sr-only">${isZh?'模型、发布者、声明许可与适用范围':'Models, publishers, declared licenses and scope'}</caption><thead><tr><th scope="col">${isZh?'模型／发布者':'Model / publisher'}</th><th scope="col">${isZh?'声明许可':'Declared license'}</th><th scope="col">${isZh?'范围与证据':'Scope and evidence'}</th></tr></thead><tbody>${models.map(row=>renderModelRow(row,language)).join('\n')}</tbody></table><p id="model-empty" hidden>${isZh?'没有匹配项，请修改搜索或重置筛选。':'No matching models. Change the search or reset the filters.'}</p><script type="module" src="${assetURLs['model-directory.js']}"></script><p><a href="${homeLink(language,'collection')}">${isZh?'继续查找运行库、训练工具与数据集':'Find runtimes, training tools and datasets'} →</a></p>`;
  return shell(language,'models',title,description,body,models);
}
function discoveriesPage(language) {
  const isZh=language==='zh', labelIndex=isZh?1:0;
  const title=isZh?'新增资源目录':'New resources';
  const description=isZh?'按类别浏览新收录的项目、模型、数据集、指南与研究论文。':'Explore recently added projects, models, datasets, guides and research papers by category.';
  const categoryLabel=category=>isZh?(categoryLabels[category] || category):category;
  const categoryId=category=>'discovery-category-'+discoveryCategories.indexOf(category);
  const toc=discoveryCategories.length?`<nav class="document-toc" aria-label="${isZh?'按分类浏览':'Browse by category'}"><ul class="discovery-category-list">${discoveryCategories.map(category=>`<li><a href="#${categoryId(category)}">${esc(categoryLabel(category))} (${discoveryCounts[category]})</a></li>`).join('')}</ul></nav>`:'';
  const cards=discoveryCategories.map(category=>`<section id="${categoryId(category)}"><h2>${esc(categoryLabel(category))} (${discoveryCounts[category]})</h2><div class="resource-list">${discoveries.filter(row=>row.category===category).map(row=>{
    const retrieved=typeof row.retrieved_at==='string'?row.retrieved_at.slice(0,10):'';
    return `<article class="resource-row" data-category="${esc(row.category)}" data-relation="${esc(row.relation)}" data-verification-level="${esc(row.verification_level)}"><div class="resource-heading"><h3 class="resource-title"><a href="${esc(row.url)}" target="_blank" rel="noopener noreferrer"${englishLang(row.title,language)}>${esc(row.title)}</a></h3><p class="resource-subtitle"><span class="resource-category">${esc(categoryLabel(row.category))}</span> · <span class="resource-provenance">${esc(relationLabels[row.relation][labelIndex])}</span> · ${isZh?'证据：':'Evidence: '}${esc(t(language,evidenceLabels[row.verification_level]))}${retrieved?` · ${isZh?'抓取于':'Retrieved'} <time datetime="${esc(retrieved)}">${esc(retrieved)}</time>`:''}</p></div><p class="resource-description">${esc(isZh?discoveryTranslations[row.description]:row.description)}</p><span class="resource-arrow" aria-hidden="true">↗</span></article>`;
  }).join('\n')}</div></section>`).join('\n');
  const baseline=typeof expansion.baseline_commit==='string' && /^[a-f0-9]{40}$/.test(expansion.baseline_commit)?` <a href="${repo}/commit/${expansion.baseline_commit}">${expansion.baseline_commit.slice(0,7)}</a>`:'';
  const body=`<p class="document-date"><strong>${discoveries.length.toLocaleString('en-US')}</strong> ${isZh?'项新增来源':'added sources'} · <time datetime="${discoveryDate}">${discoveryDate}</time> · <a href="/data/expansion-progress.json">${isZh?'下载 JSON':'Download JSON'}</a></p><p>${isZh?'条目标明与 Jev 直接相关、邻近领域或背景研究。内容筛查与摘要核查不代表全文评审、质量背书或实验复现。':'Entries distinguish direct Jev resources, related methods and research background. Source-page and abstract checks do not imply full-paper review, endorsement or experimental reproduction.'}</p>${toc}<details class="verification-legend"><summary>${isZh?'核查与计数方法':'Verification and counting method'}<span aria-hidden="true">+</span></summary><p>${isZh?'本目录相对冻结版本新增，排除旧链接、重复正文和论文题名。基线：':'This directory excludes prior URLs, repeated evidence and duplicate paper titles. Baseline:'}${baseline || (isZh?'见 JSON':'see JSON')}.</p><p><a href="${repo}/blob/main/docs/reviews/expansion-2026-10-16.md">${isZh?'查看本轮审阅记录':'Read the expansion review'}</a> · <a href="${repo}/blob/main/docs/source-audit.md">${isZh?'证据等级说明':'Evidence-level definitions'}</a></p></details><p><a href="${homeLink(language,'corpus')}">${isZh?'搜索完整来源库':'Search the complete source corpus'} →</a></p>${cards || `<p>${isZh?'本轮尚无已接受的新增来源。':'No new sources have been accepted in this expansion yet.'}</p>`}`;
  return shell(language,'discoveries',title,description,body,discoveries);
}
// A small papers-per-week chart; on wide screens it sits beside the papers page introduction.
function activityFigure(language) {
  const text=activityText(activity,paperThemes,language,papers.length);
  return `<figure class="paper-activity">${activitySVG(activity,paperThemes,language,papers.length,'inline')}<figcaption>${esc(text.title)}</figcaption><details><summary>${esc(text.tableSummary)}</summary><p>${esc(text.note)}</p>${activityTable(activity,paperThemes,language)}</details></figure>`;
}
// GitHub Pages serves one 404.html for every unknown path, in either language, so the
// page is bilingual, noindex and uses only root-absolute links and assets.
function notFoundPage() {
  const body=`<div class="prose"><section><h2>Continue browsing</h2><ul><li><a href="${route('en')}">Resource collection</a></li><li><a href="${route('en','topics')}">Research topics</a></li><li><a href="/sitemap.xml">Sitemap of every page</a></li></ul></section><section lang="zh-CN"><h2>继续浏览</h2><p>地址可能有误，或页面已经移动或下线。</p><ul><li><a href="${route('zh')}">中文资源索引</a></li><li><a href="${route('zh','topics')}">研究专题</a></li><li><a href="/sitemap.xml">网站地图（全部页面）</a></li></ul></section></div>`;
  return shell('en','','Page not found · 页面未找到','The address may be mistyped, or the page may have moved or been retired.',body,undefined,undefined,false);
}
outputs.set('site/404.html',notFoundPage());
for (const language of ['en','zh']) {
  outputs.set(`site${route(language)}index.html`,home(language));
  outputs.set(`site${route(language,'guide')}index.html`,guidePage(language));
  outputs.set(`site${route(language,'papers')}index.html`,papersPage(language).replace('<section id="paper-list">', `<details class="verification-legend paper-overview"><summary>${language==='zh'?'按主题查看论文发表趋势':'Publication activity by research theme'}<span aria-hidden="true">+</span></summary>${activityFigure(language)}</details><section id="paper-list">`));
  outputs.set(`site${route(language,'models')}index.html`,modelsPage(language));
  outputs.set(`site${route(language,'discoveries')}index.html`,discoveriesPage(language));
  outputs.set(`site${route(language,'topics')}index.html`,topicsPage(language));
  for (const topic of topics) outputs.set(`site${route(language,'topics/'+topic.slug)}index.html`,topicPage(language,topic));
}
const sections=['','guide','papers','models','discoveries','topics',...topics.map(topic=>'topics/'+topic.slug)];
const sectionDate=section=>section==='guide'?guide.updated:section==='discoveries'?discoveryDate:section==='topics'?topicsDate:section.startsWith('topics/')?topics.find(topic=>'topics/'+topic.slug===section).updated:contentDate;
outputs.set('site/sitemap.xml',`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${sections.flatMap(section=>['en','zh'].map(language=>`  <url><loc>${origin+route(language,section)}</loc><lastmod>${sectionDate(section)}</lastmod>${alternateLinks(section).map(({hreflang,href})=>`<xhtml:link rel="alternate" hreflang="${hreflang}" href="${href}" />`).join('')}</url>`)).join('\n')}\n</urlset>\n`);
outputs.set('site/data/expansion-progress.json',JSON.stringify(expansion,null,2)+'\n');
outputs.set('site/references.bib',await readFile(resolve(root,'references.bib'),'utf8'));
outputs.set('site/papers.json',JSON.stringify({title:'Awesome Jev research papers',url:origin+'/papers/',updated:contentDate,scope:'Curated direct preprints; findings remain author-reported. No experimental reproduction implied.',themes:paperThemes,papers},null,2)+'\n');
outputs.set('site/models.json',JSON.stringify({title:'Awesome Jev decision model directory',url:origin+'/models/',updated:contentDate,scope:'Independent publisher releases and model-card summaries. Declared licenses and reported capabilities are not independently reproduced results or a universal ranking.',models},null,2)+'\n');
// The READMEs embed committed SVG files (GitHub shows the -dark file in its dark theme) and the
// numbers behind them, both regenerated between the papers-by-week markers.
for (const [language,readme,suffix] of [['en','README.md',''],['zh','README.zh-CN.md','.zh-CN']]) {
  for (const mode of ['light','dark']) outputs.set(`assets/papers-by-week${mode==='dark'?'-dark':''}${suffix}.svg`,activitySVG(activity,paperThemes,language,papers.length,mode));
  const text=activityText(activity,paperThemes,language,papers.length);
  const block=`<!-- papers-by-week: generated by scripts/build_site.mjs from site/catalog.mjs -->\n<p><picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/papers-by-week-dark${suffix}.svg">\n  <img src="assets/papers-by-week${suffix}.svg" width="400" alt="${esc(text.summary)}">\n</picture><br><sub>${esc(text.title)}${language==='zh'?'。':'. '}${esc(text.note)}</sub></p>\n\n<details><summary>${esc(text.tableSummary)}</summary>\n\n${activityTable(activity,paperThemes,language)}\n\n</details>\n<!-- /papers-by-week -->`;
  const source=await readFile(resolve(root,readme),'utf8'), markers=/<!-- papers-by-week:[^\n]*-->[\s\S]*?<!-- \/papers-by-week -->/;
  if(!markers.test(source))throw new Error(`${readme} lacks the papers-by-week markers.`);
  outputs.set(readme,source.replace(markers,()=>block));
}
// llms.txt lists the sitemap's routes in both languages, so a new topic note appears automatically.
const pageSummaries={
  '':{en:['Resource collection','curated primary sources and verification labels.'],zh:['资源索引','精选一手来源与核查标签。']},
  guide:{en:['Research guide','source-backed answers about Jev, typed decisions, probabilities and evaluation.'],zh:['研究指南','有来源支撑的 Jev、类型化决策、概率与评测解答。']},
  papers:{en:['Papers','versioned preprints; findings remain author-reported.'],zh:['论文目录','按版本整理的预印本；结论仍为作者报告。']},
  models:{en:['Decision model directory','independent releases, declared licenses and model-card evidence.'],zh:['模型目录','独立发布的模型、声明许可与模型卡证据。']},
  discoveries:{en:['New resources','new direct resources, related work and background research with evidence labels.'],zh:['新增资源','新增的直接相关资源、相关研究与背景研究，附证据标签。']},
  topics:{en:['Research topics','focused, source-backed notes with direct answers and evaluation limits.'],zh:['研究专题','有来源支撑的专题笔记，附简明回答与评估局限。']},
};
const pageSummary=(language,section)=>{
  const topic=topics.find(topic=>'topics/'+topic.slug===section);
  const [label,note]=topic?[topic[language].title,topic[language].description]:pageSummaries[section]?.[language] ?? [];
  if(!label||!note)throw new Error(`Missing llms.txt summary for ${route(language,section)}`);
  return `- [${label}](${origin+route(language,section)}): ${note}`;
};
outputs.set('site/llms.txt',`# Awesome Jev\n\n> Independent, bilingual collection of Jev and typed decision model research, models, datasets and tools. Not affiliated with TypeSafe AI.\n\n## Main pages\n\n${sections.map(section=>pageSummary('en',section)).join('\n')}\n\n## Chinese pages\n\n${sections.map(section=>pageSummary('zh',section)).join('\n')}\n\n## Source formats\n\n- [Guide, curated resources and research topics in Markdown](${origin}/llms-full.txt)\n- [Paper metadata](${origin}/papers.json)\n- [Model metadata](${origin}/models.json)\n- [Expansion report](${origin}/data/expansion-progress.json)\n- [BibTeX](${origin}/references.bib)\n- [Repository](${repo})\n- [Verification methodology](${repo}/blob/main/docs/source-audit.md)\n\nThis optional file is a reading aid, not an indexing or ranking mechanism. Respect source versions and distinguish vendor claims, preprint findings, and independently reproduced evidence.\n`);
outputs.set('site/llms-full.txt',`# Awesome Jev\n\nIndependent community project, not affiliated with TypeSafe AI.\nCanonical website: ${origin}/\nCurated snapshot: ${contentDate}. Findings are author-reported; no model experiments reproduced here.\n\n# ${guide.en.title}\n\n${guide.en.intro}\n\n${guide.en.sections.map(s=>`## ${s.title}\n\n${s.paragraphs.map(p=>(p.text+' '+p.sources.map(source=>`[${source.label}](${source.url})`).join(' · ')).trimEnd()).join('\n\n')}`).join('\n\n')}\n\n# Curated resources\n\n${resources.map(row=>`## ${row.title}\n\n${row.category} · ${row.by}\n\n${row.en}\n\nPrimary source: ${row.url}`).join('\n\n')}\n`);
outputs.set('site/llms-full.txt', outputs.get('site/llms-full.txt') + '\n# Research topics\n\n' + topics.map(topic=>`## ${topic.en.title}\n\nCanonical page: ${origin+route('en','topics/'+topic.slug)}\nUpdated: ${topic.updated}\n\n${topic.en.answer}\n\n${topic.en.scope}\n\n${topic.en.sections.map(section=>`### ${section.title}\n\n${section.text} ${section.sources.map(source=>`[${source.label}](${source.url})`).join(' · ')}`.trimEnd()).join('\n\n')}`).join('\n\n') + '\n');
const check=process.argv.includes('--check');
let stale=0;
for (const [name,content] of outputs) {
  if (/\{\{[A-Z_]+\}\}/.test(content)) throw new Error(`Unresolved template value in ${name}`);
  const path=resolve(root,name);
  if(check){if(await readFile(path,'utf8').catch(()=>null)!==content){console.error(`Stale generated page: ${name}`);stale++;}}
  else {await mkdir(dirname(path),{recursive:true});await writeFile(path,content);}
}
// The build owns every index.html route under site/ (not assets or hand-maintained
// files such as the Search Console verification page). A route it no longer
// produces would stay deployed and indexable, so --check reports it and a build deletes it.
const routeFiles=async dir=>(await Promise.all((await readdir(resolve(root,dir),{withFileTypes:true})).map(entry=>
  entry.isDirectory()?(dir==='site'&&entry.name==='assets'?[]:routeFiles(`${dir}/${entry.name}`)):entry.name==='index.html'?[`${dir}/${entry.name}`]:[]))).flat();
for (const name of (await routeFiles('site')).filter(name=>!outputs.has(name)).sort()) {
  if(check){console.error(`Orphaned generated page: ${name}`);stale++;continue;}
  await rm(resolve(root,name));
  for (let dir=dirname(name);dir!=='site';dir=dirname(dir)) {if((await readdir(resolve(root,dir))).length)break;await rmdir(resolve(root,dir));}
  console.log(`Removed orphaned generated page: ${name}`);
}
if(stale)process.exitCode=1;
else console.log(`${check?'Checked':'Built'} ${outputs.size} static outputs; ${resources.length} curated resources, ${papers.length} papers, ${discoveries.length} new sources, ${[...outputs.keys()].filter(name=>name.endsWith('.html')).length} HTML pages.`);
