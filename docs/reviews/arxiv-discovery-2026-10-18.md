# Primary arXiv discovery — 18 October 2026 UTC

The previous research release found three papers missing from scan PR 4: Jev-LiteMAS, Verdict and Source-Judged Compaction. The scanner refreshed primary pages for known papers, but discovery depended on Hugging Face and OpenAlex. A new independent arXiv search path now feeds the existing scheduled review pipeline.

The query covers Jev, typed decisions, System One models and RLCD in titles/abstracts, ordered by last update. Pages contain at most 200 entries; pagination continues until the feed ends or the existing research deadline is exhausted. There is no new intake cap. The [arXiv API manual](https://info.arxiv.org/help/api/user-manual.html) and [official rate limits](https://info.arxiv.org/help/api/tou.html) were checked for this change. One transport gate serializes API connections and waits at least three seconds after every attempt, including retries and redirects. All scholarly providers share at most three workers.

The Atom response is untrusted discovery metadata. XML with DTD/entity declarations, invalid identities, errors, missing metadata or inconsistent pagination is rejected without exposing its body in diagnostics. Valid legacy IDs do not invalidate modern results; a relevant legacy-format candidate is reported as unsupported. Duplicate/changing pages stop the query with a partial-result diagnostic. Known identities and explicit exclusions are skipped; existing refresh and pinned-evidence review rules remain in effect.

New candidates receive `abstract_checked` only after a separate fixed-version primary-page request verifies identity, version, date, author/title metadata and a substantive directly relevant abstract. Failed primary checks remain metadata-only. The feed body and full abstracts are not published. API discovery counters appear separately in the scan JSON and Actions summary; they are not accepted-resource or reproduction counts.

A real feed contained 194 entries and included all three previously missed papers. It also exposed two edge cases: a valid legacy `cs/` identifier, and RLCD meaning randomized least common denominator in a random-matrix paper. The parser now handles the first without rejecting the page; direct-paper screening requires decision/calibration context for the ambiguous acronym. Synthetic regressions cover both.

The final isolated real-network check completed at **2026-10-18T05:53:12Z**: one feed page, 194 entries, 122 direct candidates, 71 known identities skipped, and **51 new candidates with verified fixed-version abstracts**, with no unavailable pages or errors. It used 52 public requests (one API query and 51 primary pages). Candidate records passed ledger and author/identity validation. These 51 observations are pending review, not additions to the curated site or expansion totals; no source ledger was edited by this check. No code, model, benchmark or private data was executed or submitted.

Tests cover pagination, malformed/error feeds, version mismatches, failed page checks, exclusions, known catalog entries, source-schema validity, aggregator-independent operation, API retry/redirect spacing, single-connection behavior, and deadline exhaustion. Smoke mode uses the first five feed entries and retains its existing no-publication behavior. Publication and workflow receipts are recorded after running the deployed change.

**中文：** 新增独立的 arXiv 一手论文发现，并核查固定版本摘要；已知来源不重复计数，失败条目不提升为已查证据。真实查询覆盖194条结果，最终筛出122个直接候选，跳过71个已知身份，对51个台账外候选完成固定摘要核查。这是待审提议，不是51篇新精选或实验复现。限速、重试、分页、异常XML、旧式编号和缩写歧义均有测试；公开站点及来源数量保持不变。

Local validation passed all **451 tests**, including 17 new discovery/transport regressions, plus publication validation and whitespace checks. The change leaves the public site, source ledgers and their counts unchanged. The real-network candidate observations remain outside the accepted collection until reviewed through the existing workflow.

## Deployed smoke check and merge protection

Commit `db2c88b` passed both repository check workflows. The [GitHub smoke run](https://github.com/reacher-z/Awesome-Jev/actions/runs/39102259670) completed its scan/validation job; publication was skipped. Its arXiv counters show five feed entries, four known identities and one verified new candidate, with `smoke_limited: true`. The entire smoke report is partial because one other source was unavailable. It used 39 public requests and did not change scan PR 4, whose head remained `656c0e8be89e0ac757d3d5e53b2c24b1d935841f`.

A follow-up merge regression verifies that new fixed-version primary evidence wins over a same-run generic landing-page screen in either arrival order. The prior-record grade policy stays unchanged. This preserves the new discovery evidence when another provider finds the same new paper. The final suite contains 452 tests, including 18 new regressions.

## Full scheduled-path validation

The full [scan run 39102522027](https://github.com/reacher-z/Awesome-Jev/actions/runs/39102522027), dispatched from `9a62a6f8c9eeeccf5f27ca5eb8acece036704fea`, completed both scan and publish jobs. It updated [review PR 4](https://github.com/reacher-z/Awesome-Jev/pull/4) to `5fa0e40ae7a483cc2fca81ec4128ca7220048562`. Both repository checks and the code-only Pages deployment also passed.

The run made 3,837 public requests and reported 327 additions proposed against main, 224 changed records and two changes requiring editorial review. It remains **partial**, with 169 provider/document issues and no exhausted phase budget. Its arXiv path completed all 194 feed entries, skipped 71 known identities and verified 51 new fixed-version abstracts, with zero failed primary-page checks. These candidate counts do not increase the curated collection.

Reconciliation retained 40 absent candidates from the previous unmerged PR, with their original evidence and dates. Independent verification confirmed that all seven allowlisted artifact files match their manifest hashes/sizes and published PR bytes. Every one of the 51 primary candidates retained its version and abstract hash; all 40 carried records match prior-PR bytes. Six files differ in the PR because the seventh allowlisted file is unchanged. The PR remains open for review; nothing was automatically merged into the main collection.
