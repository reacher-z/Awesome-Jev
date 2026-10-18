# Filtered bibliography export and paper density — 18 October 2026 UTC

The paper directory now exports only its visible rows, in their current display order. Entries are copied from the maintained `references.bib`, preserving citation keys, full authors, nested braces, Unicode and exact reviewed-version URLs. The full bibliography remains a normal link and includes background and survey entries outside the paper table. The static build requires every curated paper to have an exact citation match.

The parser handles the repository's self-contained, brace-delimited entries with literal fields, numeric values or standard month abbreviations. Macro definitions, concatenations and cross-entry dependencies are rejected rather than dropped from the filtered file. Missing versions, ambiguous keys/URLs and malformed content stop the filtered export rather than producing an incomplete file. Background entries without URLs remain valid in the full bibliography. Zero matches disable export. Failed preparation provides retry/reload guidance and a full-bibliography link.

The browser requests only the same-origin, content-hashed bibliography after an export click, with credentials and referrer omitted. Search terms appear in neither the request nor filename. Parsing is cached for the page session; no citation provider, model API, local storage or analytics is involved. The clicked view is captured before loading, so later filter changes do not change an in-progress selection. A Save .bib link remains available for the prepared file.

The header combines date/scope notes and the existing publication-activity figure in a native disclosure. Its chart still covers the full collection. The redundant visible list heading is removed while preserving a screen-reader heading. At a 1728 px desktop viewport, the first paper moved from 660 px to 496 px without reducing table text size. Narrow layouts use a native theme selector tied to the desktop chips and shareable URL state; Chinese layouts at 390 px and 320 px have no horizontal overflow.

## Validation

Five new offline checks cover nested and quoted values, Unicode, exact version matching, malformed/ambiguous sources, source-entry parity for all 87 papers, content-hashed export URLs and mobile/desktop theme parity. The complete 457-test suite passed, alongside static generation and publication validation.

A real browser export selected eight v2 papers with code, sorted oldest first. The saved file contained exactly those eight entries in the observed order. An independent check matched every entry to the original bibliography, including SecJev's v2 and first-submission note. The file SHA-256 is `73154001c93fdf6181b2e61504f6832fc1bd7db08957189e1bf1f6436ee79a94`. No local download path is recorded here.

Browser checks also verified the native theme selector, empty-result disabling, reset, cross-language preservation of a robustness/code view, and expanding/collapsing reading notes. The collection remains at 87 papers, 169 curated resources and 793 expansion sources. No source ledger, reviewed version, evidence grade or bibliography entry changed.

**中文：** 论文目录支持按可见结果及其排序导出BibTeX，保留引用键、完整作者、原始格式与固定版本。实际保存的八条v2论文引用已逐条对照源书目；缺项或版本不匹配会拒绝导出。桌面首条论文上移164px，手机改用原生主题下拉框，阅读说明和全目录趋势仍可展开查看。筛选和导出不向外部文献服务发送查询，资源计数与证据等级不变。

The final narrow-layout checks also cover English at 320 px: sort, reset and copy-link controls remain within the page gutters without overlap. The Chinese theme selector correctly restores the same eight robustness/code results on the English desktop layout. Reading notes explicitly distinguish the full-collection activity chart from the filtered citation export.

## Deployed verification

Release `92f2e3d8763afe7592f57d9577bfee5126e70c2d` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39107491050), [website checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39107495088) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39107495049). All 40 live targets matched committed bytes, including the new bibliography module and the exact versioned bibliography URL requested by the export control. The live filtered view shows eight papers and Download BibTeX (8).

One IndexNow POST for the two substantively changed paper-directory routes returned HTTP 200. Other routes only received the updated stylesheet reference and were not resubmitted. No Google indexing request was repeated, and no source, paper or evidence counts changed.
