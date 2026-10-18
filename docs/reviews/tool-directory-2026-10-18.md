# Developer tool directory — 18 October 2026 UTC

The new English and Chinese `/tools/` routes organize the existing 20 curated Tools entries by four purposes: API integration (5), workflow control (6), inference runtimes (7), and training/evaluation (5). Categories overlap; each project appears once in the table, JSON export and structured ItemList. The 160-resource curated total, 784-source expansion, source-ledger bytes and evidence grades are unchanged.

Purpose labels describe the scope already retained in reviewed catalog summaries. They do not assert compatibility, production readiness, model execution, a universal ranking or independent reproduction. TypeSafe official versus community filtering follows existing publisher provenance. SDKs, independent-model runtimes and training code remain different implementation roles. Longer evaluation and operating limits are retained in full.

The static pages, their reciprocal language links, canonical URLs, sitemap entries, catalog JSON and navigation are generated from shared catalog data. The generated sitemap now contains 20 canonical pages; 404 remains noindex. Both READMEs and homepages link the tool directory. The README curation date now matches the completed 18 October content review.

Search and filters use a URL fragment and the existing directory-view module. Both languages search the same English/Chinese metadata. Purpose, publisher and search state survive refresh and language navigation; resetting removes the fragment. Filtering makes no network request and uses no local storage or analytics. Projects with multiple purposes, such as circuit, are available under either purpose without duplicated rows.

Local checks covered a Python / API integration / official compound filter; reload and Chinese navigation; the Chinese keyword 共享 across both languages; an empty result and reset; and training/runtime membership. Chinese layouts at 390 px and 320 px have no horizontal overflow. A concise title, complete scope text and combined metadata keep the first Chinese tool row at about 668 px in a 390 × 844 viewport.

The 434-test suite passed. Extended static checks verify complete bilingual rows, distinct identities, export parity, exact ItemList order, canonical/hreflang coverage, current module hashes and bilingual search text. The final layout-only adjustment also passes the targeted site/view tests, deterministic build check, publication validator and whitespace check. Publication and search receipts are recorded after deployment.

**中文：** 新增中英文工具目录，按四种用途筛选既有20个项目，支持官方／社区来源和双语关键词组合检索。一个项目可属于多个用途，但静态表格、JSON和结构化数据均只计一次；来源数量和证据等级不变。所有说明直接存在于HTML中，筛选链接支持刷新和语言切换恢复。手机端保持白底黑字和完整范围说明，没有横向溢出；本目录没有运行这些项目或增加复现声明。

## Publication receipts

Commit `0e8564e237da77c51cfd59fd451d2b8d226d4719` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39100157106), [website repository checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39100158953) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39100158982). All 38 live HTTP targets matched committed bytes, including both new pages, their 20-row static tables, the JSON export and the versioned filtering module. A live workflow/community filter returned four distinct projects and copying the view showed success feedback.

A single IndexNow POST for the two new tool routes returned HTTP 200. The updated 20-page sitemap was submitted once through the already-verified Google Search Console property, which displayed “Sitemap submitted successfully.” After dismissal, its table still showed the earlier Unknown / Couldn't fetch / 0 discovered pages record. Submission acceptance therefore does not establish restored fetching, indexing, ranking or AI citation. No account data or Search Console screenshots were committed; Bing authentication remains outside this release.
