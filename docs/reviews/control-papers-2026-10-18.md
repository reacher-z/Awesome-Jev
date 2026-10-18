# Control, compaction and invariance — 18 October 2026 UTC

Four distinct papers were absent from both accepted ledgers and the supplemented frozen baseline. Three came from focused web discovery followed by primary arXiv checks; Runoff also appeared in scan PR 4 at `656c0e8be89e0ac757d3d5e53b2c24b1d935841f`. All fixed-v1 abstracts match separately fetched current canonical abstracts. This review covers abstracts, citation metadata, selected method/limitation paragraphs and linked README documentation, not full-paper reading or experimental reproduction.

| Paper | Reviewed primary evidence | Interpretation limit |
| --- | --- | --- |
| [Jev-LiteMAS: Separating Decisions from Generation in Multi-Agent Workflows](https://arxiv.org/abs/2610.21411v1) | 2026-10-15 · v1 · [Section 1](https://arxiv.org/html/2610.21411v1#A1.p1) · [Section 2](https://arxiv.org/html/2610.21411v1#A2.p1) | Four benchmarks and two generative backbones; token reductions concern generative-LLM usage, with decision-layer overhead reported separately. Expert roles are predefined and review savings depend on artifact quality. The paper-linked anonymous archive remained at 0% preparation in two browser observations; implementation contents were not verified. |
| [Verdict: Encode Once, Decide Many](https://arxiv.org/abs/2610.20778v1) | 2026-10-14 · v1 · [Section 1](https://arxiv.org/html/2610.20778v1#S7.p1) · [Section 2](https://arxiv.org/html/2610.20778v1#Sx1.SS0.SSS0.Px6.p1) | The headline comparison is a specialist experiment on a small synthetic teacher-labeled benchmark. Research decisions were adaptive rather than test-blind; standard benchmarks show mixed results and unstable BoolQ training. Guarantees assume identical retained state tokens. Jev uses an unpinned gateway alias, and trained checkpoints are not released. |
| [Prune the Summary, Not the History: Source-Judged Compaction for Long-Horizon Agents](https://arxiv.org/abs/2610.20927v1) | 2026-10-14 · v1 · [Section 1](https://arxiv.org/html/2610.20927v1#S5.SS1.SSS0.Px2.p1) · [Section 2](https://arxiv.org/html/2610.20927v1#Sx1.p2) | Pass^3 is the share of tasks solved in all three runs, distinct from mean accuracy. Agent/compressor token totals exclude separately reported Jev calls. The study uses two benchmarks, two agent models and one compressor with the original instruction always visible; multi-turn user history is not evaluated. Source support does not imply correctness, and the judge can prune useful constraints. |
| [Consider, Then Choose: Order-Invariant Decisions in System One Models](https://arxiv.org/abs/2610.18233v1) | 2026-10-13 · v1 · [Section 1](https://arxiv.org/html/2610.18233v1#Sx1.p1) · [Section 2](https://arxiv.org/html/2610.18233v1#A5.SS0.SSS0.Px2.p1) | The invariance argument assumes identical-request determinism and a unique canonical ranking. Nondeterministic APIs may still flip answers; option-name bias is outside its target. Accuracy and latency claims are limited to the tested models, benchmarks and batching conditions. No dedicated author code release was verified; cited upstream repositories are not treated as this paper’s artifact. |

## Retained document fingerprints

| Paper | Fixed abstract page SHA-256 | Abstract text SHA-256 | Manuscript HTML SHA-256 |
| --- | --- | --- | --- |
| arxiv:2610.21411 | `12537851a46a9e18fa75c03ab52934a6836431a9aef637fba989ed61eabdf988` | `097a055e166e2bee05e94fa0cd5e1d716b7e2432adb8f992d42286d519ae4313` | `bedb8f307d442ea8a9e9743da60c428dfaab829a439b0a4f8fbfabcd1e73a883` |
| arxiv:2610.20778 | `245087981c4d1a4a546d67ab2dd024cb332602fd4610f45ab94c9f15a7dea600` | `65263bfedd1bdb73b48d746c584396645bfb272631680ae79fb7e3b6957633de` | `e42d588516b0cd003c07499c333a47a6211dc499ccb980ab50c259e0c41e44c4` |
| arxiv:2610.20927 | `cdb424ddfc6b3504cf74806b0ffb0cf24aaf00a735d11ad295bd6f822afd9e6c` | `9325f151ce56a69bbca9597e75cf7d2739bc3f0b874cf9a08a0d2021d057c11a` | `105ddeb75485114bce882face5d04c96a1b262d57e5d839e44dfd2bc97b40e98` |
| arxiv:2610.18233 | `a0ba971b15eaab0d656f3df393b7592db4ea0d46113fb43785885ebca378ad71` | `ffeb41a70208c2cef04fdc84afde97556ffe7aaf2e094d5e1ea49ffadc36dddb` | `9f5b7309c7a46a743d9c974b085c5fcde9e9c63d5c126604c6f9219138aeee02` |

Abstract normalization uses the scanner’s joined-text whitespace normalization. The ledger keeps full public author names in Given Surname order; BibTeX retains citation names. LiteMAS metadata spells its second author Zhaijiacheng Zhou while the manuscript spells Zhaojiacheng Zhou. We preserve the arXiv citation spelling rather than silently choosing a correction. Placeholder conference metadata in that manuscript is not treated as a publication venue.

## Companion documentation

- [LEC-AI/verdict](https://github.com/LEC-AI/verdict): [fixed README](https://raw.githubusercontent.com/LEC-AI/verdict/eaaba56bf0bf47ac14d39bc4bca4e73f4ce970d3/README.md), SHA-256 `768dceeb7aae76248efca6f22d899d90bf2b9a9410746d38cdfb374fc599a083`, fetched 2026-10-18T05:27:39.985998+00:00. README scope and reproduction requirements were inspected; no code, results archive, training data or checkpoint was executed/downloaded.
- [GuanghuiMin/sjc](https://github.com/GuanghuiMin/sjc): [fixed README](https://raw.githubusercontent.com/GuanghuiMin/sjc/771517bebf49b9d45aa7bd48c7f5daec883c6282/README.md), SHA-256 `7d710996b90f8fbc00416491c0cfed39b9d6058b2c001b59c49d1eb9a406a75f`, fetched 2026-10-18T05:27:40.002562+00:00. README scope and reproduction requirements were inspected; no code, results archive, training data or checkpoint was executed/downloaded.

The [LiteMAS anonymous archive status](https://anonymous.4open.science/status/jevlite-mas-2312) stayed at 0% preparation in two browser observations. Its content was not available for this review, so the catalog marks code unverified. Runoff’s inspected manuscript links upstream implementations and datasets but no dedicated author release; those references are not relabeled as its code. This bounded check is not proof that no release exists elsewhere.

Intake SHA-256: `799d5587028e64b29a59aac735b8bd309681821fac5d035c7a7dbe8b7fb962e4` over the four sorted-key UTF-8 ledger JSON lines. Only these four papers increase source counts; manuscript sections, fixed-version URLs and companion links add zero. Original source bytes, versions and evidence grades remain untouched. No model calls, benchmark execution, account access, dataset or weight downloads were performed. Raw pages, contact addresses and private paths are not committed.

The bilingual option-label topic adds a comparison of order invariance and label meaning, with explicit determinism, ranking and retained-input assumptions. The proposed diagnostic separates option permutations, identical-request repeats and label substitutions; it is advice derived from inspected sources, not a performed experiment.

**中文：** 本轮新增四篇论文，固定v1摘要、当前摘要与引用信息均已核查，并定向阅读方法／限制段落。两项作者仓库只核查说明文档；匿名档案仍未就绪，Runoff未核实专用作者代码。来源支持、语义正确、跨次运行成功、顺序不变性和校准不能混为一谈；没有运行任何模型或实验，配套链接不另计来源。

## Validation

The collection now has 82 direct papers, 91 bibliography entries, 164 curated resources and 788 expansion sources. The previous research-ledger bytes are unchanged, with four rows appended; the intake hash was recomputed after clarifying that Pass^3 requires success in all three independent runs.

All 434 repository tests passed, including bibliography/README/catalog consistency and static bilingual page checks. The final wording also passes targeted bibliography checks, the deterministic build check, source/expansion validation and publication hygiene. Browser checks found the Runoff and SJC entries through their descriptions, retained the code-unverified and release-scope notes, and showed no horizontal overflow at 390 px. The expanded Chinese option-bias topic renders its new comparison, references and diagnostic steps.

## Publication receipts and discovery follow-up

Commit `aa855025ce6d2ac3804efe21ffea3fbc12ebca47` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39101027257), [website repository checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39101029909) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39101029812). All 38 live targets matched committed bytes, including 82-paper lists, 788-source discovery lists, the updated topic, exports and versioned modules. The live paper directory shows 45 papers with linked code; the two newly unverified releases do not enter that filter.

One IndexNow POST for the ten substantively changed home, paper, discovery, topic-directory and option-bias pages (English/Chinese pairs) returned HTTP 200. No Google or Bing account action was taken and no unchanged tool/model page was notified. The receipt does not establish indexing or ranking.

Discovery follow-up: the latest scan proposal at `656c0e8` did not contain Jev-LiteMAS, Verdict or SJC, although their primary pages were available. Inspection of `Scan.scan_research` showed discovery queries to Hugging Face and OpenAlex, while primary arXiv pages are refreshed for already seeded papers. A bounded primary arXiv discovery path is worth evaluating next; this release does not claim that change has been implemented or that automated coverage is exhaustive.
