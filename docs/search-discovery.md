# Search discovery and AI-search readiness

Guidance checked against official documentation on **2026-10-17**. These changes make content easier to discover and inspect; they do not guarantee crawling, indexing, rankings, or citations in an AI answer. Search visibility and account-level settings must be checked separately from a successful deployment.

The generated sitemap currently contains **18 canonical HTML pages**, with English/Chinese pairs for the collection, guide, papers, models, discoveries, topic directory and three research notes. The [model directory](https://awesomejev.github.io/models/) and [topic directory](https://awesomejev.github.io/topics/) give focused entry points alongside the full collection. Submission receipts and historical route counts are recorded below.

## Authoring and building the public pages

Edit the shared sources, then rebuild from the repository root:

```sh
node scripts/build_site.mjs
node scripts/build_site.mjs --check
```

The first command generates the public files. `--check` makes no changes and fails if a generated file is missing or differs from its source. The build uses local files only; it does not fetch sources or refresh verification dates.

| Content | Source to edit |
| --- | --- |
| Curated entries and interface translations | [site/catalog.mjs](../site/catalog.mjs) |
| Chinese discovery descriptions | [data/discovery-translations.zh-CN.json](../data/discovery-translations.zh-CN.json) |
| Homepage layout | [templates/index.html](../templates/index.html) |
| Shared resource-row rendering | [site/resource-view.mjs](../site/resource-view.mjs) |
| English and Chinese guide text and citations | [data/search-guide.json](../data/search-guide.json) |
| Bilingual research topics and review scope | [data/research-topics.json](../data/research-topics.json) |
| Bibliography | [references.bib](../references.bib) |
| Page generation, metadata, and sitemap rules | [scripts/build_site.mjs](../scripts/build_site.mjs) |

`site/app.js` enhances the browser interface; the resource catalog now belongs in `site/catalog.mjs`. Do not maintain a second copy of the entries in the application script.

The build adds content-hash URLs for the entry script, its imported modules and CSS. The homepage import map keeps browser-rendered entries consistent with its static HTML when the shared catalog changes; authors do not need to bump query versions by hand.

The Chinese discoveries page translates the resource descriptions as well as the navigation. Its translations are bound to the exact English summary, and missing or outdated mappings stop the build. Preserve the same source links, evidence tiers and limitations in both languages. Google determines page language from visible content; translating the navigation alone does not make the main content Chinese. [Google multilingual-site guidance](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

Do not hand-edit generated outputs. The build owns every `index.html` under `site/`, in both languages and for every route, including the model directory, topic directory and each topic note. It also owns `site/sitemap.xml`, `site/references.bib`, `site/papers.json`, `site/models.json`, `site/llms.txt`, `site/llms-full.txt`, and the published `site/data/expansion-progress.json` copy. Change their source files or generator, rebuild, and include both source and output changes in the same review. Update the generator's `contentDate` or the guide's `updated` date only when the corresponding substantive content changes; a no-op scan does not justify a new date.

## Public content and crawlability

Serve the curated resource entries and guide text in the initial HTML, with normal links. JavaScript can enhance filtering and search. Google can render JavaScript, but recommends pre-rendering where useful because other crawlers may not execute it. Do not describe client-rendered content as inherently unindexable by Google. [Google JavaScript SEO guidance](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

The public guide is authored in [data/search-guide.json](../data/search-guide.json), with parallel English and Chinese content and paragraph-level source links. Keep those citations visible in the generated guide pages. Maintain the distinction between provider descriptions, author-reported studies, source screening, and experiments actually reproduced by this project.

Use stable language URLs, such as `/` and `/zh/`, and `/guide/` and `/zh/guide/`. Each translated page should serve its own language without requiring a button click, use a self-consistent canonical URL, and list reciprocal `hreflang` alternatives including itself. Keep the language switch usable as ordinary links. [Google localized-page guidance](https://developers.google.com/search/docs/specialty/international/localized-versions)

Keep an accurate XML sitemap at the site root, referenced by `robots.txt`. Include canonical first-party pages that should be searchable; external papers in the resource collection do not belong in this site's sitemap. Update `lastmod` when the page's substantive content changes, not whenever a collector or build runs. Google and Bing ignore the optional `priority` and `changefreq` fields. [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) · [Bing sitemap guidance](https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/)

Do not generate thousands of near-empty pages from the broad source corpus just to increase indexable URL counts. Curated explanations, transparent evidence notes, and useful navigation provide more value than mechanically repeating titles and links. [Google generative-AI optimization guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)

## Structured data and answer-oriented writing

Structured data must describe what readers can actually see. A resource collection can use ordinary website/collection/list semantics; the explanatory guide can describe its real title, author or maintainer, language, sources, and update date. Do not invent reviews, ratings, qualifications, or evidence that the project did not produce. Valid markup is not a guarantee of a rich result. [Google structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)

Question headings are useful when they answer readers' real questions. They do not imply special search eligibility. Google's FAQ rich-result feature was retired in May 2026; do not promise FAQ rich results from this guide. [Google documentation updates](https://developers.google.com/search/updates)

Google explicitly says it does not use `llms.txt` to improve visibility or ranking. Such a file may be maintained as an optional navigation aid for other tools, but it is not an indexing requirement or an AEO shortcut. There is no special structured-data type required for Google's generative search features. [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)

## Google: what an owner should check

Pages must meet ordinary Search requirements and be indexed with snippet eligibility to appear as supporting links in AI Overviews or AI Mode. The site's generative-AI inclusion control must also permit participation, as described below. [Google AI-feature requirements](https://developers.google.com/search/docs/appearance/ai-features)

The Search Console **Settings → Search generative AI** control defaults to inclusion; a child property can inherit a parent's setting. Check the effective setting rather than assuming a new manual opt-in is always necessary. This control is separate from ordinary Search inclusion and from AI-training controls. The project's inherited effective setting was confirmed in Search Console as **Current control: Include** on 2026-10-16. [Search generative AI control](https://support.google.com/webmasters/answer/16908024)

An owner can verify the exact `https://awesomejev.github.io/` URL-prefix property, inspect a live URL, submit the sitemap, and monitor indexing and search performance. Use the owner's actual verification file or tag; never add a placeholder verification token and call the site verified. Account verification and a submitted sitemap do not themselves prove indexing. [Search Console ownership verification](https://support.google.com/webmasters/answer/9008080) · [Google sitemap submission](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap#submit-sitemap)

**Observed project status, 2026-10-16:** Google Search Console ownership verification succeeded using the site's HTML verification file, and the inherited effective Search generative AI control is **Include**. Keep the verification file publicly accessible; do not record the owner's account name or email in this repository.

- The homepage's live test reported **URL is available to Google** and **Page can be indexed**.
- Each of the six canonical HTML pages—`/`, `/zh/`, `/guide/`, `/zh/guide/`, `/papers/`, and `/zh/papers/`—was submitted once and received **Indexing requested** confirmation and the message that the URL was added to a priority crawl queue. These are confirmed requests, not confirmed index inclusion; do not submit the same pages repeatedly to try to advance their queue position.
- The six-page `https://awesomejev.github.io/sitemap.xml` was submitted and the submission was acknowledged. Its Sitemaps report still showed **Couldn't fetch**, type **Unknown**, and **0 discovered pages** at the latest check. A separate live inspection of that exact URL succeeded: **Crawl allowed? Yes**, **Page fetch Successful**, inspected as **Google Inspection Tool smartphone**. A successful live fetch does not establish successful sitemap processing or invalidate the report's unresolved failure. Recheck processing later; no site-side defect has been established from these observations.

**Follow-up confirmed on 2026-10-16:** URL Inspection for the canonical homepage `https://awesomejev.github.io/` now reports **URL is on Google** and **Page is indexed**. This is index-inclusion evidence for the homepage only, not confirmation for the other five pages, a ranking position, or an AI-answer citation. The sitemap report still showed its earlier retrieval failure when rechecked; the two observations are recorded separately.

Ownership verification, an inclusive AI control, successful live tests, and queued requests do not establish indexing or appearance in an AI answer. Record subsequent processing results separately instead of replacing these observations with an assumption of success.

## Bing and IndexNow

For normal discovery, retain crawlable internal links and a root sitemap referenced in `robots.txt`. Bing Webmaster Tools can verify sitemap processing and indexing through an owner account. Accurate modification dates matter; a fresh build timestamp is not evidence that page content changed. [Bing sitemap guidance](https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/)

IndexNow is an optional change-notification protocol. It requires a valid key and a UTF-8 verification file on the same host as the submitted URLs. A root-level key file covers the host; a key hosted in a subdirectory covers only the corresponding URL prefix. Submit only this site's added, changed, or removed page URLs, not the external source URLs collected in its ledgers. A `200` response means receipt, and `202` means key verification is pending; neither guarantees crawling or indexing. [IndexNow protocol](https://www.indexnow.org/documentation) · [Bing's IndexNow setup](https://www.bing.com/indexnow/IndexNowView/IndexNowGetStartedView)

**GitHub Pages compatibility is an implementation inference:** GitHub Pages serves static repository files, so it can serve the required verification file. A separate post-deployment process could then submit changed first-party URLs. This does not mean GitHub Pages automatically enables IndexNow for this site. Verify the key file is live before making any submission. [GitHub Pages hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) · [IndexNow verification](https://www.indexnow.org/documentation)

**Observed project status, 2026-10-16:** Bing Webmaster Tools verification is blocked at the owner's passkey interaction and is not confirmed. IndexNow received one POST containing the six canonical page URLs: `/`, `/zh/`, `/guide/`, `/zh/guide/`, `/papers/`, and `/zh/papers/`. The response was **HTTP 202: key validation pending**. This confirms receipt pending key validation, not completed verification, crawling, or indexing. No automatic retry was made.

**Later release receipt, 2026-10-16:** after publishing `67edcc3`, one additional POST notified IndexNow of the four changed HTML pages (`/`, `/zh/`, `/papers/`, `/zh/papers/`). It returned **HTTP 200**, confirming successful receipt. This supersedes the earlier pending-validation status for this later notification, but does not prove indexing or Bing Webmaster Tools account verification. The two unchanged guide pages were not resubmitted.

For future content changes, [scripts/submit_indexnow.py](../scripts/submit_indexnow.py) defaults to a local dry run with no network requests:

```sh
python3 scripts/submit_indexnow.py
```

After deploying actual changes, select the changed canonical pages with repeatable `--url` arguments. Inspect that selection without `--submit` first. The explicit submission command verifies the live proof file and selected pages, then sends one POST:

```sh
python3 scripts/submit_indexnow.py --url https://awesomejev.github.io/guide/
python3 scripts/submit_indexnow.py --submit --url https://awesomejev.github.io/guide/
```

These are maintenance examples, not a request to resubmit an unchanged page. Omitting `--url` selects all current sitemap pages; use an explicit changed-page selection for subsequent releases. Record the actual response each time; do not use repeated notices to bypass pending validation or rate limits.

## OpenAI search crawlers

`OAI-SearchBot` is the relevant crawler for discovery in ChatGPT search. OpenAI recommends allowing it in `robots.txt` and not blocking its published IP ranges at the hosting layer. `GPTBot` has a separate training purpose, and its setting is independent. `ChatGPT-User` is for user-triggered visits, not the search-index control. Do not conflate these agents or change a training preference merely to enable search discovery. [Official OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)

An unrestricted public `User-agent: *` rule already permits compliant search crawlers unless a more specific rule overrides it. A public HTTP response and a permissive robots file establish accessibility, not that OpenAI or another service has indexed or selected the page.

## Release checks

- Run `node scripts/build_site.mjs --check` after generating pages; source changes and generated outputs must agree.
- Inspect the fetched HTML without JavaScript: important headings, explanations, resource links, and citations should be present.
- Confirm each language page returns HTTP 200 with the intended language, title, canonical, and reciprocal alternatives.
- Check sitemap URLs, actual modification dates, and the live `robots.txt` response.
- Check JSON-LD against visible content and avoid unsupported claims about search features.
- Keep publication, search-engine submission, index inclusion, and observed traffic as separate statuses.

## 中文说明

优先把精选资源、指南正文和引用直接写入静态 HTML，让 JavaScript 只增强搜索与筛选。英文和中文使用独立可访问的 URL、相符的 canonical 和互相指向的 `hreflang`；sitemap 只列本站规范页面，更新时间应对应内容实质变化。

维护时修改 `site/catalog.mjs` 中的共享资源与翻译、`templates/index.html` 首页模板、`data/search-guide.json` 双语指南或根目录 `references.bib`，再执行 `node scripts/build_site.mjs`，并用 `node scripts/build_site.mjs --check` 检查一致性。不要直接编辑生成文件：`site/` 下所有语言、所有路由的 `index.html`（含模型目录、专题目录和各专题页）均由构建生成，sitemap、站点引用副本、论文与模型 JSON、`llms` 文件和发布的 `site/data/expansion-progress.json` 副本也是如此；`site/app.js` 只负责浏览器交互，不再保存另一份资源目录。

这些措施改善可抓取性，不保证收录、排名或 AI 引用。Google 明确表示 `llms.txt` 不提升其排名；问答式正文也不意味着 FAQ 富结果。Search Console 的生成式 AI 控制默认包含，但子属性可能继承上级设置。截至 2026-10-16，Google 站点所有权已通过 HTML 文件验证，控制界面也已确认继承后的有效设置为 **Current control: Include**。保留公开验证文件，不在仓库记录账号姓名或邮箱。

Google 首页实时测试显示可访问、可索引；六个规范 HTML 页面 `/`、`/zh/`、`/guide/`、`/zh/guide/`、`/papers/`、`/zh/papers/` 均各提交一次，并分别收到 **Indexing requested** 确认，已加入优先抓取队列，不代表已收录。六页 sitemap 已提交并收到提交确认，但最近一次 Sitemaps 报表仍显示 **Couldn't fetch／Unknown／发现 0 页**。对同一个 sitemap URL 的独立实时测试则显示允许抓取、抓取成功，由 Google Inspection Tool smartphone 执行。实时测试成功不等于 sitemap 已处理成功，也不能覆盖报表的未解决状态；后续需复查，当前观察尚未确立本站存在需修复的缺陷。

Bing 验证停在所有者的通行密钥交互步骤，尚未确认完成。IndexNow 已通过一次 POST 提交上述六个规范页面 URL，返回 **HTTP 202，密钥验证待完成**；这不代表已验证、已抓取或已收录，没有自动重试。脚本默认 dry run，不发网络请求；未来部署实质变更后，用 `--url` 选择变更页面，核对预览，再显式使用 `--submit` 发送一次通知。不要重复提交未变化页面，也不要提交外站论文链接。OpenAI 搜索使用 `OAI-SearchBot`，与用于训练的 `GPTBot` 相互独立。所有外部验证、提交和收录状态都应以实际结果记录，不能由本地文件推断。

**后续确认（2026-10-16）：** Google URL 检查现已明确显示规范首页 `https://awesomejev.github.io/` 为 **URL is on Google／Page is indexed**。这一确认只适用于首页，不代表另外五页、排名或 AI 回答引用已经确认；sitemap 报表复查仍保留此前的读取失败状态，两者分开记录。

**后续通知（2026-10-16）：** 发布 `67edcc3` 后，仅将四个实际改变的 HTML 页面（`/`、`/zh/`、`/papers/`、`/zh/papers/`）通过一次 IndexNow POST 通知，返回 **HTTP 200**，确认已接收。未改变的两篇指南没有重复提交；这一回执仍不代表已收录或 Bing 站长账号验证完成。

## Expansion release follow-up

On 2026-10-16, release `f8194d4` published the English and Chinese `/discoveries/` directories with 655 verified-depth additions and expanded the sitemap to eight canonical pages. One IndexNow POST for the eight changed pages returned **HTTP 200**, confirming receipt, not index inclusion.

The Google URL Inspection request for `https://awesomejev.github.io/discoveries/` returned **Quota Exceeded** and was not accepted. The Chinese directory was not submitted after that service limit. Retry only after the quota resets; do not switch accounts or repeatedly submit to try to bypass the limit. The new directories remain reachable through ordinary internal links and the sitemap. This does not alter the earlier confirmed indexing of the homepage or turn the two new directories into confirmed indexed pages.

**中文：** `f8194d4` 已发布包含655项新增来源的中英文目录，sitemap扩为八页；八个更新页面通过一次IndexNow通知返回HTTP 200。Google对英文新增目录的手动索引请求返回“Quota Exceeded”，未受理；因此未再提交中文目录。待服务配额重置后再申请，保持普通站内链接与sitemap发现入口；首页已收录的确认不等于这两个新目录也已收录。

**Subsequent release receipt, 2026-10-16:** `d640802` added 58 sources and four curated promotions; `00e33fe` added six direct preprints and Chinese descriptions for all 719 discovery entries. After both releases were live, one IndexNow POST notified only the four substantively changed pages: `/`, `/zh/`, `/discoveries/`, and `/zh/discoveries/`. The response was **HTTP 200**. The unchanged paper and guide pages were not submitted again. This records notification receipt, not indexing or a completed Bing account verification; no further Google indexing request was made while its quota limit remained unresolved.

**后续通知（2026-10-16）：** `d640802` 新增58项来源，`00e33fe` 再增6篇直接相关预印本，并补齐719项新增资源的中文简介。确认上线后，仅将两次发布中实质变化的四页（首页、中文首页、两种语言的新增目录）通过一次 IndexNow POST 通知，返回 **HTTP 200**。未重复提交内容未变的论文和指南页；这一结果仍只表示接收通知，不代表收录或 Bing 账号验证完成。Google 配额问题未解决期间未再申请索引。

**Implementation and guide release, 2026-10-16:** after `d022f30` deployed, one IndexNow POST for eight substantively changed canonical pages returned **HTTP 200**. Both homepages and paper directories gained three curated studies, both guides gained the table/evidence diagnostic section, and both discovery directories gained two implementation repositories and more specific summaries. Live checks confirmed 78 curated entries, 35 selected papers, 43 bibliography entries, and 721 discoveries in each language. This is a publication and notification record; it adds no new claim about Google indexing or Bing account verification.

**实现与指南更新（2026-10-16）：** `d022f30` 部署后，八个正文均有实质变化的规范页面通过一次 IndexNow 通知返回 **HTTP 200**。线上已核对78项精选、35篇精选论文、43条书目及每种语言721项新增资源；首页、论文目录、指南和新增目录均有对应内容更新。此处记录发布与通知结果，不新增 Google 收录或 Bing 账号验证成功的主张。

**Confidence and tool-verification release, 2026-10-16:** `714c006` published six direct papers and four author-linked artifacts, bringing the reviewed expansion to 731 sources and the curated collection to 84 entries, including 41 papers and 49 bibliography entries. One IndexNow POST for the eight substantively changed canonical pages returned **HTTP 200** after deployment. A separate read-only Search Console check still showed `/sitemap.xml` as **Unknown / Couldn't fetch / 0 discovered pages**, with no last-read value. No further sitemap or manual indexing submission was made during that check; the earlier homepage indexing confirmation and the unresolved sitemap report remain separate observations.

**置信度与工具核验更新（2026-10-16）：** `714c006` 已发布6篇直接论文和4项作者配套资源，累计731项新增来源、84项精选（41篇论文、49条书目）。部署后八个实质变化页面通过一次 IndexNow 通知返回 **HTTP 200**。另行只读复查 Search Console 时，sitemap 仍为 **Unknown／Couldn't fetch／发现0页**，最后读取时间为空；该次复查没有重复提交 sitemap 或手动索引请求，不能把之前首页已收录的确认解释为 sitemap 已处理成功。

**Domain-study release, 2026-10-16:** `ca36ed7` added eight papers and six whole companion resources, reaching 745 discoveries, 92 curated entries, 49 selected direct papers and 57 bibliography entries. After successful deployment and live bilingual checks, one IndexNow POST for all eight substantively changed canonical pages returned **HTTP 200**. Updates include domain studies, their release limitations, the proposed confidence-transfer protocol and the newly verified model-note date. This receipt does not establish indexing, ranking or AI-answer inclusion; the previously recorded Search Console sitemap status was not rechecked or replaced in this release.

**领域研究更新（2026-10-16）：** `ca36ed7` 新增8篇论文与6项完整配套资源，达到745项新增、92项精选、49篇直接论文和57条书目。部署与双语线上核对通过后，八个实质变化页面通过一次 IndexNow 通知返回 **HTTP 200**。新增领域研究、发布范围说明和建议的置信度迁移流程，模型说明核验日期也已更新。通知回执不等于收录、排名或AI引用；本次没有重查或改写此前的 Search Console sitemap 状态。

**Ordinal-scale and visual research release, 2026-10-16:** `6cfb02d` added three direct preprints and two whole author artifacts, reaching 750 discoveries, 95 curated resources, 52 selected direct papers and 60 bibliography entries. Both repositories passed CI and the website deployment succeeded; one live check confirmed all eight HTML pages and seven supporting artifacts matched the published commit. After that check, one IndexNow POST for the eight substantively changed pages returned **HTTP 200**. The bilingual guide gained an ordinal-label diagnostic and the repository survey distinguishes three efficiency denominators. This records publication and notification receipt, not new search indexing, ranking or AI citations. No Google or Bing account action was attempted for this release.

**有序量表与视觉研究更新（2026-10-16）：** `6cfb02d` 新增3篇直接论文和2项完整作者资源，累计750项新增来源、95项精选、52篇直接论文及60条书目。两个仓库CI与网站部署成功，线上八个HTML页面和七项配套文件均与提交字节一致。核对后，对八个实质变化页面发送一次 IndexNow 通知，返回 **HTTP 200**。双语指南补充有序标签诊断，仓库综述新增三类效率指标的分母对照。此处确认发布与通知，不新增收录、排名或AI引用主张；本轮未操作 Google 或 Bing 账号。

**Companion and reproduction-guide release, 2026-10-16:** `225dc54` published two distinct companion resources, reaching 752 discoveries and 97 curated entries; the 52 selected direct papers and 60 bibliography entries were unchanged. Thirteen existing companion links and one navigation-only author site were added to the README without increasing source counts. Both guides gained a reproduction-scope section. After both repository checks, Pages deployment and one 15-target live parity check succeeded, one IndexNow POST for the six substantively changed pages (`/`, `/zh/`, `/guide/`, `/zh/guide/`, `/discoveries/`, `/zh/discoveries/`) returned **HTTP 200**. The unchanged paper pages were not submitted. This is receipt of a change notification, not evidence of new indexing or AI citations; no Google or Bing account action was performed.

**配套材料与复现指南更新（2026-10-16）：** `225dc54` 发布两项独立配套资源，累计752项新增来源、97项精选；直接论文52篇、书目60条保持不变。README补齐13个既有配套链接及一个仅用于导航的作者论文站，未重复计数；双语指南新增复现范围说明。双仓检查、部署及15项线上一致性核验通过后，仅对首页、指南、新增目录的中英文六页发送一次 IndexNow 通知，返回 **HTTP 200**。内容未变的论文页没有再次提交；此回执不证明新收录或AI引用，本轮未操作 Google 或 Bing 账号。

**Security-measurement release, 2026-10-16:** `bb24adb` added one JevAdvBench implementation, reaching 753 discoveries, and promoted the already-known Just Ask Jev paper into the curated selection without counting it as a new source. The collection now has 99 curated resources, 53 selected papers and 61 bibliography entries. Both guides gained a comparison of attack outcomes and denominators. Both repository checks and Pages deployment succeeded; one 15-target live check matched all eight HTML pages and seven supporting artifacts to the exact commit. A single IndexNow POST for the eight substantively changed canonical pages returned **HTTP 200**. This confirms notification receipt, not new index inclusion, ranking or AI citations. No Google or Bing account operation was attempted.

**安全评测指标更新（2026-10-16）：** `bb24adb` 新增一个JevAdvBench代码项目，扩展资源达到753项；将原已收录的Just Ask Jev补入精选，不重复计作新来源。当前为99项精选、53篇精选论文、61条书目，双语指南新增攻击结果与分母对照。双仓检查、Pages部署和15项目标的线上字节核对均通过；八个实质变化页面经一次 IndexNow 通知返回 **HTTP 200**。此处只确认接收通知，不证明新增收录、排名或AI引用；本轮未操作 Google 或 Bing 账号。

**Classifier and language comparison release, 2026-10-16:** `9f81b37` promoted three already-known papers and added one distinct Turkish decision checkpoint, reaching 103 curated resources, 56 selected papers, 64 bibliography entries and 754 discoveries. The bilingual guide now separates task-label access, readout/fine-tuning conditions and language-label provenance. Five display annotations preserve the underlying source evidence. After successful deployment, one 17-target live check matched all eight HTML pages and supporting data/modules to the exact commit. One IndexNow POST for the eight substantively changed canonical pages returned **HTTP 200**. This is notification receipt, not indexing or AI-answer inclusion; no Google or Bing account action was performed.

**分类器与语言比较更新（2026-10-16）：** `9f81b37` 将三篇既有论文补入精选，并新增一个独立土耳其语决策检查点，累计103项精选、56篇论文、64条书目及754项新增来源。双语指南区分任务标签、读出／微调与语言标签来源；五项展示注释保留原证据。成功部署后17项目标的线上字节核对通过，八个实质变化页面经一次 IndexNow 通知返回 **HTTP 200**。此回执不代表收录或AI引用，本轮未操作 Google 或 Bing 账号。

### Pages artifact names during retries

The original [deployment run](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/38907985608) uploaded its artifact, but the deployment step reported no matching artifact. A same-run retry uploaded a second artifact with the same name and failed on multiple matches. A [fresh manual run](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/38908553219) successfully deployed the same `9f81b37` commit; the site content was unchanged during recovery.

The single-job workflow now supplies the same `github-pages-${{ github.run_id }}-${{ github.run_attempt }}` value to the upload action’s `name` and the deployment action’s `artifact_name`. The run identifier remains stable on a retry while the attempt increases, so the deployment step selects only that attempt’s upload. This addresses the observed naming collision; it does not guarantee immediate artifact metadata visibility. If upload and deployment are later split into separately retried jobs, pass the upload’s chosen name through a job output. [Pinned action inputs and context evidence](../data/pages-artifact-name-review-2026-10-16.json).

**中文：** 原部署先因未找到已上传文件失败，同一运行重试又上传了同名文件，随后因匹配到两份而失败；新建运行已成功部署同一提交。现将上传与部署的文件名统一包含运行编号和重试次数，避免旧尝试的文件重名。此改动处理重名问题，不承诺消除平台元数据延迟；若以后拆分上传和部署作业，应传递实际上传名称。

**Retry verification, 2026-10-17 UTC:** the [same Pages run](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/38909381634) for `55fec92` succeeded on attempts 1 and 2. The observed artifact names ended in `-1` and `-2`, respectively. This deliberate rerun verifies separation of retry uploads; no site-content change or extra IndexNow notification was involved.

**重试验证（2026-10-17 UTC）：** 同一部署运行的两次尝试均成功，文件名称分别以 `-1`、`-2` 结尾，实际验证了重试上传的名称隔离。该验证没有改变网站内容，也没有再次提交搜索通知。

**Read-only Search Console follow-up, 2026-10-17 UTC:** the Sitemaps report still displayed `/sitemap.xml` as **Unknown / Couldn't fetch / 0 discovered pages**. This check did not submit a sitemap or request indexing. The earlier homepage-indexing confirmation remains a separate historical observation; no new index inclusion is claimed from a successful site deployment.

**只读复查（2026-10-17 UTC）：** sitemap 报表仍为 **Unknown／Couldn't fetch／发现0页**。本次没有重新提交 sitemap 或申请索引；之前的首页收录确认仍单独保留，网站成功部署不等于新增页面已被收录。

**Scheduled-source selection release, 2026-10-17 UTC:** `8de8603` added six inspected whole projects, promoted three known workflow papers, refreshed the four Decision Index documents and corrected the renamed Space’s logical identity. The result is 110 curated resources, 59 direct arXiv papers, 68 bibliography entries and 760 reviewed expansion sources. The automatic scan PR remains open; its other proposed records are not counted as accepted by this release. All 17 live targets matched that commit. Follow-up `d8c7841` made publisher badges explicit; its four changed site files and both languages’ community/official labels were checked against the new commit, while other site bytes remained unchanged. Both repositories passed CI and the deployments succeeded. One IndexNow POST for the eight substantively changed canonical pages returned **HTTP 200** after these checks. This receipt does not establish indexing or AI-answer inclusion.

**扫描资源精选发布（2026-10-17 UTC）：** `8de8603` 新增六个已查项目、将三篇既有工作流论文补入精选，更新四份Decision Index文档并修复旧名称导致的重复身份。当前110项精选、59篇直接arXiv论文、68条书目、760项已接受扩展来源；自动PR其余提议仍待审。17项线上字节核对通过，随后 `d8c7841` 修正发布者标记，四项改变的站点文件及中英文标记均核对一致。双仓CI与部署成功，八个实质变化页面经一次 IndexNow 通知返回 **HTTP 200**，不代表收录或AI引用。

**Multilingual runtimes and evaluation release, 2026-10-17 UTC:** `dd22269` added 12 inspected whole projects, with eight curated selections, bringing the collection to 118 curated resources and 772 reviewed expansion sources. The 59 direct arXiv papers and 68 bibliography entries are unchanged. Both repositories passed CI, including 115 tests, and Pages deployed successfully. All 17 live targets matched the published commit; a browser check confirmed the new FRIDA entry, its community-source label and the restored 118-item list. One IndexNow POST notified only the six substantively changed home, guide and discovery pages in English and Chinese, returning **HTTP 200**. The paper pages were unchanged and were not resubmitted. This receipt confirms notification acceptance, not indexing, ranking or AI citations; no Google or Bing account action was performed.

**多语言运行库与评测更新（2026-10-17 UTC）：** `dd22269` 新增12个已检查的完整项目，其中8项进入精选，累计118项精选与772项已接受扩展来源；59篇直接arXiv论文和68条书目保持不变。双仓CI（含115项测试）、Pages部署及17项线上文件核对全部通过；浏览器确认新增FRIDA条目、社区资源标记与118项完整列表。仅对首页、指南和新增目录的中英文六个实质变化页面发送一次 IndexNow 通知，返回 **HTTP 200**；论文页未变，未重复提交。回执表示通知已接收，不代表收录、排名或AI引用；本轮未操作 Google 或 Bing 账号。

**Label, graph and audio release, 2026-10-17 UTC:** `b09e4fd` curated three already-known papers and one new audio checkpoint, reaching 122 curated resources, 62 selected direct papers, 71 bibliography entries and 773 reviewed expansion sources. The bilingual guide distinguishes option rendering from model mechanism and order consistency from correctness calibration. The homepage footer now retains the independent-project statement separately from evaluation badges. Both repository checks and Pages deployment succeeded; all 17 live targets matched the commit, and browser search showed the AudioJev paper and model card as separate entries with their respective evidence labels. One IndexNow POST for the eight substantively changed canonical pages returned **HTTP 200**. No Google or Bing account action or manual Google indexing request was performed; this notification receipt adds no indexing or AI-citation claim.

**标签、图任务与音频更新（2026-10-17 UTC）：** `b09e4fd` 将三篇既有论文及一个新音频检查点纳入精选，累计122项精选、62篇直接论文、71条书目和773项扩展来源。双语指南区分选项渲染与模型机制、顺序稳定与正确率校准；页脚恢复独立项目声明，与评测标记分开。双仓检查、部署和17项线上文件核对通过，浏览器检索确认AudioJev论文与模型卡分别展示并标注来源。八个实质变化页面通过一次 IndexNow 通知返回 **HTTP 200**。本轮未操作Google／Bing账号或申请Google手动索引，通知回执不新增收录或AI引用主张。

## Focused research routes

**Research-topics release, 2026-10-17 UTC:** `c98ec22` added three substantive research notes in both languages: option-label bias, AudioJev and graph decision evaluation. Each page contains a direct answer, named primary sources, a proposed diagnostic and explicit review limits. The two topic directories, ordinary homepage links, paper-directory links and guide links provide discovery paths without JavaScript. That release expanded the sitemap to 16 canonical pages, with reciprocal language alternatives; the current page count is stated at the top of this document. Article headlines, dates and citations match visible page content; nested breadcrumbs identify the topic directory. These are new reading routes, not new counted research sources.

The implementation follows Google's guidance on [AI features](https://developers.google.com/search/docs/appearance/ai-features) and [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap): prioritize accessible, useful text and internal links, keep structured data faithful to the page, and use accurate modification dates. There is no special AI schema or required AI text file. The existing optional `llms.txt` remains a reading aid, not an indexing mechanism. No FAQ rich-result eligibility, ranking improvement or AI citation is asserted.

A read-only Search Console check before this release still showed the old sitemap report as **Unknown / Couldn't fetch / 0 discovered pages**. The site-generation and offline crawl tests do not replace that external observation. Once the changed sitemap is deployed, a new submission may be recorded separately; unchanged sitemap files and quota-limited manual indexing requests must not be repeatedly submitted.

**专题发布（2026-10-17 UTC）：** `c98ec22` 新增三个有实质内容的双语专题，分别讨论标签偏置、AudioJev与图决策评测；提供简明回答、原始引用、建议诊断和核查局限。专题目录及首页、论文页、指南的普通链接均可在不运行脚本时发现；该版本将sitemap扩为16个规范页面（当前页面数见本文开头），双语对应、文章引用和面包屑与可见正文一致。这些页面不增加研究来源计数，也不承诺排名或AI引用。发布前只读复查的Google旧sitemap报表仍为“无法抓取／0页”；部署后实际提交与外部处理结果另行记录。

**Publication and submission receipt, 2026-10-17 UTC:** `c98ec22` passed both repository checks and Pages deployment. The 117-test suite passed, and one 28-target live check matched all 16 HTML pages, the sitemap and supporting assets to the exact commit. Browser navigation verified the English topic index, AudioJev detail page and its corresponding Chinese page. One submission of the changed `/sitemap.xml` received Search Console's **Sitemap submitted successfully** acknowledgement; the existing report still showed **Unknown / Couldn't fetch** immediately afterward. A separate single IndexNow POST for the 16 new or changed canonical pages returned **HTTP 200**. Neither receipt confirms crawling, indexing, ranking or AI-answer inclusion. No quota-limited Google manual indexing request or Bing account verification was attempted.

**发布与提交回执（2026-10-17 UTC）：** `c98ec22` 双仓检查和部署成功，117项测试通过；16个HTML页面、sitemap及配套文件共28项线上核对均与提交一致。浏览器验证英文专题目录、AudioJev详情和对应中文页。对实际已更新的站点地图提交一次，Google明确确认“提交成功”，但提交后的旧报表仍显示“Unknown／Couldn't fetch”。另一次 IndexNow POST 提交16个新增或变化的规范页面，返回 **HTTP 200**。两个回执都不等于已抓取、收录、获得排名或AI引用；没有重试受配额限制的Google手动索引，也未完成Bing账号验证。

**Domain and transfer release, 2026-10-17 UTC:** `261023b` added four original, fixed-v1 paper abstracts, reaching 126 curated resources, 66 direct papers, 75 bibliography entries and 777 reviewed expansion sources. The guide gained language-transfer and network-deadline distinctions, and the AudioJev note gained a scoped DuplexJev comparison. The source legend now includes directly checked arXiv abstracts without upgrading them to full-paper review. Both repositories passed CI, including 117 tests; Pages deployment and all 28 live parity targets passed. Browser inspection confirmed the new bilingual comparison section. One IndexNow POST for only the ten substantively changed home, guide, paper, discovery and AudioJev pages returned **HTTP 200**. The sitemap bytes were unchanged and were not submitted again. No Google or Bing account operation occurred; no new indexing or AI-citation result is claimed.

**领域与迁移更新（2026-10-17 UTC）：** `261023b` 新增四篇固定v1原始摘要，累计126项精选、66篇直接论文、75条书目及777项扩展来源。指南补充语言迁移和网络期限的区别，音频专题新增有适用范围的DuplexJev比较；来源图例明确原始arXiv摘要也仍属于摘要核查。双仓CI（含117项测试）、部署和28项线上核对通过，浏览器确认新增比较章节。仅对十个实质变化页面发送一次IndexNow通知，返回 **HTTP 200**；sitemap内容未变，没有再次提交。本轮未操作Google或Bing账号，不新增收录或AI引用主张。

**Model-card and alias release, 2026-10-17 UTC:** `6f6bcb6` added four model repositories with commit-verified documentation, reaching 130 curated resources and 781 reviewed expansion sources; the 66 direct papers and 75 bibliography entries are unchanged. A regression prevents Span-02's former Hub account from creating a second identity after card changes. The 118-test suite, both repository checks and Pages deployment passed; all 28 live targets matched the release. Browser filtering confirmed 15 curated model entries, publisher-card labels, Lychee's noncommercial declaration and Span-02's canonical link. One IndexNow POST for only the six changed home, guide and discovery pages returned **HTTP 200**. Unchanged paper/topic pages and the sitemap were not resubmitted. No search-account action or new indexing result is claimed.

**模型卡与别名更新（2026-10-17 UTC）：** `6f6bcb6` 新增四个模型仓库，文档均核对固定提交，累计130项精选与781项扩展；66篇直接论文和75条书目不变。回归测试防止Span-02旧账号在文档改变后形成第二个身份。118项测试、双仓检查、部署及28项线上核对通过；浏览器确认15项精选模型、发布者模型卡标记、Lychee非商业许可与Span新地址。仅对六个改变的首页、指南及扩展目录页面发送一次IndexNow通知，返回 **HTTP 200**；论文、专题和sitemap未变，未重复提交。本轮未操作搜索账号，不新增收录主张。

## Independent model directory

The English `/models/` and Chinese `/zh/models/` pages render all curated model entries directly as an HTML comparison table, using the same titles, summaries and publisher-card evidence as the homepage. Each page has its own canonical URL, reciprocal language links and an ItemList matching the visible rows. The `/models.json` export preserves the curated records, including explicit publisher and declared-license fields. Homepage, README and document navigation link to the directory; it is included in the existing sitemap URL. This adds two reading routes, not two research sources.

The introduction distinguishes publisher releases from hosted Jev, declared licenses from inferred rights, and model comparisons from rankings assembled under unmatched conditions. Tests check the export against the catalog and both language pages against the homepage, as well as the expanded sitemap and crawler rules. The project makes no new claim about external indexing from these local checks.

**中文：** 中英文模型目录直接输出全部精选模型的HTML比较表，标题、简介和发布者模型卡证据与首页一致，JSON导出保留发布者和声明许可。规范网址、双语对应与结构化列表匹配可见条目，首页、README、文档导航和sitemap均包含入口。两条页面不增加研究来源计数；许可与发布范围仍以已查材料为依据，不能由页面检查推断搜索引擎已经收录。

### Comparison and navigation refinement

The model table groups each release's name and publisher, declared license, and documented scope into three columns. Search and license filters progressively enhance the already-rendered table; without JavaScript every model remains readable. The comparison notes use native expandable HTML. On narrow screens rows stack without removing the full scope text. Both homepages show generated category counts and collection totals; these totals represent different subsets and must not be added together. README task paths connect research, model comparison, integrations and detailed topics. The homepage script now preserves the same title as the static HTML.

Browser checks exercised search plus license filtering, zero results, reset and both languages. A 390-pixel mobile check found no horizontal overflow. Source counts remain **134 curated entries, 66 direct papers, 15 curated models and 785 reviewed expansion sources**. These interface changes add no new source records or performance claims.

### Source scan alias repair

The [manual scan](https://github.com/reacher-z/Awesome-Jev/actions/runs/39006523362) finished discovery but failed repository validation before packaging or PR publication. It proposed 263 records and 166 changes; those proposals are not accepted source additions. A weaker legacy Decision Index record had been selected instead of the earlier editorial record because both shared one logical identity. Updating its stored URL then created an exact duplicate.

The merge now chooses the strongest protected owner, prefers canonical spelling for a tie and preserves historical URL fields when multiple aliases remain in one ledger. Two regression cases failed before the repair and pass afterward; an offline replay on the real ledger preserves all existing bytes and queues the synthetic change for review. The [repair record](../data/scan-alias-merge-review-2026-10-17.json) separates these checks from the subsequent real workflow result. No validation gate was removed and the six-file publication allowlist is unchanged.

**中文：** 手动扫描完成发现后，因同一来源的旧新地址处理错误而在校验阶段停止，尚未打包或更新PR。现按证据强度与规范地址选择更新对象，并保留历史记录网址；两项回归与真实台账的离线合并检查通过。没有移除校验或扩大自动发布范围，运行恢复情况另行记录。模型比较表、筛选、分类计数与README任务入口提升了可读性，未改变研究来源计数。

**Comparison release and discovery receipts, 2026-10-17 UTC:** `017f526` added four reviewed code projects and the two model-directory routes. `3fd6187` published the denser comparison table, search/license filters, generated category counts, README task paths and alias merge repair. Both repositories passed CI, including 121 tests, and Pages deployed successfully. All 32 live targets matched `3fd6187`, including 18 HTML pages, the model metadata and filtering module. The changed 18-page sitemap received Google's **Sitemap submitted successfully** acknowledgement; afterward its report still read **Unknown / Couldn't fetch / 0 discovered pages**. One IndexNow POST for the 18 new or changed pages returned **HTTP 200**. These receipts do not establish indexing or AI citations. The homepage footer subsequently uses the same source-controlled content date as the page build; this small date-display repair does not trigger another search notification.

**Scan recovery result:** [run 39014659959](https://github.com/reacher-z/Awesome-Jev/actions/runs/39014659959) passed collection, validation, artifact packaging and validation after restoration. The old duplicate-URL error did not recur. It proposed 263 additions and 175 changes in a partial scan with 167 reported errors; none were accepted into main by this run. Publication stopped at the separate pending-evidence continuity gate, preserving [PR 4](https://github.com/reacher-z/Awesome-Jev/pull/4). Forty paper proposals remain only in the older PR; three revision-path comparisons and four maintainer-accepted primary abstracts also need explicit reconciliation. The verified six-file artifact is retained by the run, and its hashes were checked locally. No repeat scan or guard removal was used to force publication. [Diagnostic record](../data/scan-alias-merge-review-2026-10-17.json).

**中文：** 新模型目录和四个运行库已发布，随后比较表、搜索／许可筛选、分类计数及README任务入口上线；121项测试、部署与32项线上核对通过。Google接收18页站点地图，但报表仍为“无法抓取／0页”；IndexNow一次提交18页返回HTTP 200，均不等于收录。扫描重复网址故障已通过真实运行验证修复，发现、校验、打包和恢复后校验均成功；另一个证据连续性检查阻止覆盖旧PR，40篇旧候选与版本／证据类型差异仍待协调。新扫描的263条提议和175项变化没有自动进入主分支；未取消保护，也未盲目重跑。
