# Source audit

**Research snapshot: 15 October 2026 · Retrieval audit: 16 October 2026, 01:30 UTC**

[Resource index](../README.md) · [Machine-readable audit](../data/editorial-audit.json) · [Source counts](../data/source-counts.json)

## Current counts (as of 17 October 2026)

The source-check badge in the README shows `checked_sources` from [source-counts.json](../data/source-counts.json). This is the number of distinct source documents in the three checked tiers. `metadata_only` records are not included. The table shows the accepted registry as of 17 October 2026 (latest retrieval 12:16 UTC):

| Verification tier | Distinct records |
| --- | ---: |
| `editorial_reviewed` | 4 |
| `content_screened` | 2,392 |
| `abstract_checked` | 1,843 |
| **Checked sources (badge)** | **4,239** |
| `metadata_only` (not counted) | 47 |
| Unique records | 4,286 |

The ledgers hold 4,300 raw records. Deduplication by canonical URL, exact content hash and repeated paper title removes 14 of them. The tiers are defined in the initial snapshot table below. Scheduled source scans regenerate `source-counts.json` and the badge but not this page, so after a later accepted scan the JSON file holds the current figures.

## Initial snapshot (15 October 2026)

The figures in this section and the audit findings below describe the initial snapshot. The [subsequent source-update review](reviews/scan-2026-10-16.md) records exclusions, metadata corrections, and accepted changes.

At the initial snapshot, the collection contained **3,400 distinct source documents**, of which **3,352 passed a stated content or abstract check**. These are document counts, not independent studies, reproduced experiments, or papers read in full. The **1,929 records based on retrieved original source pages** are reported separately from the abstract-only layer.

| Verification tier | Distinct records | Meaning |
| --- | ---: | --- |
| `editorial_reviewed` | 4 | Core Decision Index sources received focused editorial inspection. |
| `content_screened` | 1,925 | A public README, card, or web page was retrieved and automatically screened for substantive, relevant content. An arXiv landing page is still an abstract page, not the full paper. |
| `abstract_checked` | 1,423 | An original abstract was screened through Hugging Face Papers or reconstructed from OpenAlex metadata. This does not establish retrieval of the original publisher page. |
| `metadata_only` | 48 | Discovery or metadata exists, but the content check did not pass. Excluded from checked-source totals. |

The input ledgers contain 3,408 records. Canonical URL and exact content-hash checks remove eight duplicates. The raw research ledger contains 897 Hugging Face abstract records and 527 OpenAlex abstract records before merging. Full downloaded source texts and reconstructed full abstracts are not published in these ledgers; they retain provenance, hashes, concise evidence and relevance notes.

Subsequent additions also include original abstracts read directly from fixed-version arXiv pages. These retain `abstract_checked`, with `abstract_provider: arxiv_primary_abstract_page`, a matching `reviewed_version_url`, separate page and abstract hashes, and explicit review scope. They are not full-paper reviews. Provider records distinguish direct arXiv retrieval from mirrored or reconstructed abstracts; the historical counts above are unchanged. See the [domain and transfer study review](../data/domain-transfer-review-2026-10-17.json) for examples.

**中文：** 后续来源也包含直接核查固定版本 arXiv 页面得到的原始摘要，仍标为 `abstract_checked`，记录来源类型、版本链接以及页面和摘要各自的哈希。具体途径可区分原始页面、镜像摘要与重建摘要，均不代表全文评审；上表保留初始快照计数。

## How sources entered the collection

The [Jev Decision Index](https://huggingface.co/spaces/multimodalart/jev-decision-index) is fixed at commit `5d09dd9cf226338c68fad22284c4982e6680af7d`. Its model metadata, news and methodology lead to model cards, evaluation sources and repositories. One substantial discovery path is:

```text
Decision Index news
  → hellogumbo/awesome-jev
  → each linked project's actual public README
  → recorded content hash and relevance check
```

The [community list](https://github.com/hellogumbo/awesome-jev) supplies discovery links; its descriptions alone do not count as checking the linked projects. The ecosystem collector retrieves those projects' own documents. It requires substantive readable text and explicit topic evidence; implementation pages reached on the dependency hop must discuss Jev, TypeSafe AI or typed decisions. Generic dependencies that fail this check remain in a separate exclusion ledger. No linked project code was executed.

The background layer searches calibration, selective prediction, scoring rules, constrained decoding, model programming, routing and judge reliability. It is deliberately broader than the recommended reading list. Its presence does not establish any mechanism inside Jev.

## What the 60-source audit checked

We inspected **60 selected sources**: 10 direct papers, 10 model cards, 15 application repositories, 10 dataset cards and 15 background abstracts. Papers and model cards were selected to span useful mechanisms; the other groups used a fixed sampling seed. This targeted audit is not a statistically representative precision estimate.

The review read abstracts or selected substantive README/card passages, checked topic fit and provenance, and compared response hashes. All 45 sampled ecosystem records were retrieved again with matching hashes. For the background sample, 12 original arXiv abstracts were readable; two DOI requests failed and one publisher returned an application shell. Those three were checked through their original OpenAlex-reconstructed abstracts and retain abstract-only status. **No sampled study was fully reproduced, and this audit does not imply full-paper review.** Per-source notes are in [editorial-audit.json](../data/editorial-audit.json).

The sampled applications describe concrete Jev integrations, including skill routing, command-line decisions, coding tools, Home Assistant and a Sudoku testbed. Their existence is relevant ecosystem evidence; their reliability, security and performance claims are not thereby validated.

## Findings and repairs

**Document identifiers must survive normalization.** The first merge stripped all URL queries, incorrectly merging four distinct CiteSeer works and two OpenReview works. The builder now retains nontracking identifiers such as `doi` and `id`. This corrected the unique count from 3,396 to 3,400. Genuine removals are seven exact-content duplicates and one duplicate canonical paper URL. Examples include renamed SemIf/OpenJev repositories and the renamed Decision Index Space.

**Titles need a display fallback.** Fourteen clear extraction failures selected headings such as “Citation”, “Installation” or code comments instead of an artifact title. The browser projection uses repository or dataset identifiers for these cases. Raw extraction values remain available in the ledgers. Matching titles alone do not establish duplicate projects: several unrelated repositories use names such as “Jev Router”.

**Some categories are coarse.** The Sieve-9B, Sieve-27B and crivo dataset cards in the sample are evaluation-result archives, although their raw topic says `training-dataset`. They remain useful sources, with this correction recorded. The Twitter financial sentiment card also lists a total inconsistent with the sum of its split counts; those numbers should not be reused without checking the dataset.

**Architectures and claims differ.** Tev1's card explicitly describes ordinary next-token generation of option letters. It should not be presented as a non-autoregressive implementation merely because it is Jev-inspired. Other cards make strong calibration or hallucination claims that remain publisher assertions. The selected papers distinguish probability coherence, marginal calibration, label accuracy, adversarial decision changes and closed-loop outcomes; these are different measurements.

**Background is not direct evidence.** Edge-NPU scheduling and personalized federated learning appear in the contextual sample. They belong in the broad research index, not automatically in a concise Jev reading list. Public and private Decision Index score components also remain distinct: a public leaderboard does not make its unreleased private tests reproducible.

## Publication privacy and remaining limits

The audit searched project scripts, ledgers, documentation, website and workflow files for personal filesystem paths, common real-token forms and private-key markers. It found no confirmed exposed credentials or personal machine paths. A path-pattern match in the validator is its detection expression. Collection used public unauthenticated requests; no inference keys or private user conversations were supplied, and external examples were not installed or run. Public author and project names remain as source attribution.

These checks do not certify external projects as private or secure. For example, one sampled integration explicitly sends selected conversation content to its inference provider. Inclusion is not an installation recommendation.

Exact hashes identify the retrieved bytes, not the truth of claims. Mutable pages may change, semantically equivalent mirrors may escape byte-level deduplication, and independently released model variants are separate artifacts rather than independent studies. A large checked-source count establishes breadth of discovery; the editorial shortlist and reproducible evaluation protocol provide the narrower basis for conclusions.

## 中文说明

### 当前数量（截至 2026 年 10 月 17 日）

README 中的来源核查徽章显示 [source-counts.json](../data/source-counts.json) 的 `checked_sources`，即属于三个已检查层级的去重来源文档数，不含 `metadata_only` 记录。截至 2026 年 10 月 17 日（最近一次抓取为 12:16 UTC），已收录来源中有 4 个经编辑审阅，2,392 个原始页面经自动内容筛查，1,843 个仅经摘要核查，合计 **4,239 个已检查来源**，即徽章数字。另有 47 个仅元数据记录，不计入该数字。去重后共 4,286 条记录：台账中的 4,300 条原始记录按规范 URL、内容哈希与重复论文标题去重，去除了 14 条。定期来源扫描会更新 `source-counts.json` 和徽章，但不会修改本页；此后如有新的扫描被接受，应以 JSON 文件中的数字为准。

### 初始快照（2026 年 10 月 15 日）

初始审计快照共有 **3,400 个来源文档**，其中 **3,352 个经过明确分级的检查**：4 个核心来源经编辑审阅、1,925 个原始页面经自动内容筛查、1,423 个仅经摘要核查；另有 48 个仅元数据记录，不计入已检查数量。前两类共 1,929 个，与摘要层单独统计。

我们进一步阅读了 60 条分层样本的摘要或关键正文段落，没有宣称逐篇精读全部论文，也没有运行实验。抽查发现并修复了 URL 文档 ID 被误删造成的错误去重；通用标题、结果档案分类及上游数据数量矛盾均已记录。来源的存在不等于其准确率、校准、隐私或安全承诺得到验证。

采集只访问公开资源，不使用推理密钥，不上传私人对话，不发布完整抓取正文。公开作者和项目名称作为来源归属保留；外部项目自身的数据处理行为仍需单独审查。

## Decision Index refresh — 17 October 2026 (UTC)

The current reviewed Space commit is `0ddf6758073eb77ae449a3541f57286d7f39d93f`. Its metadata and the four public documents match the scan’s pending hashes. The edition label remains 0.3.2; the scoreboard contains 173 engine records and the full-score file 174 records including the reference. The reference is a Jev 1.14 lab run dated 14 October, while the frozen request payloads still name Jev 1.13. The methodology’s older `generated_utc` value is not used as the review timestamp.

The 0.2/0.5/0.3 public/same-skills/new-domains weights and scoring-rule objects are unchanged. Private evaluations remain unavailable for complete independent reconstruction. This was a metadata, structure and changed-field review, not execution of the evaluator or validation of its model scores. Previous hashes and source metadata remain in the [refresh record](../data/scan-review-2026-10-17.json).

**中文：** 本次复核的 Space 提交为 `0ddf6758073eb77ae449a3541f57286d7f39d93f`，其元数据和四份公开文档与扫描待审记录中的哈希一致。版本标签仍为 0.3.2；记分板有 173 条引擎记录，完整分数文件连同参照项共 174 条。参照项是 10 月 14 日的 Jev 1.14 实验室运行，而冻结的请求载荷仍写 Jev 1.13。方法说明中较早的 `generated_utc` 不作为复核时间。公开题、同技能题、新领域题 0.2/0.5/0.3 的权重和评分规则对象未变；私有评测仍无法完整独立重建。本次只复核元数据、结构和变化字段，没有运行评测程序，也没有验证其模型分数。先前的哈希和来源元数据保留在[刷新记录](../data/scan-review-2026-10-17.json)中。

## Evidence markers

Each curated row on the website ends its metadata line with one marker: a small glyph, then two words. The first word says who published the source. The second says how far its claims were checked here. The glyph's fill repeats the first word, so the marker never relies on colour. A one-line legend under the homepage filters links to this section.

| Source | Glyph | Meaning |
| --- | --- | --- |
| Official | Filled square | Published by TypeSafe. TypeSafe's own entries carry this marker explicitly. |
| Preprint | Half-filled square | A research paper posted without peer review, linked at a fixed arXiv version. |
| Community | Outlined square | Published by anyone other than TypeSafe, including companies, model publishers and independent evaluators. |
| Background | Dotted square | Background literature. It gives context; it is not evidence about Jev's internal architecture. |

| Evidence | Meaning |
| --- | --- |
| author-reported | Findings are given as their authors or publisher state them, and nothing was re-run here. Papers, official pages, model cards, background literature and evaluation reports carry this word. |
| screened | The linked page passed a recorded relevance and substance check (`content_screened` or `editorial_reviewed` in the source ledgers). The source's claims were not tested. |
| reproduced | Results were re-run independently. No curated entry carries this word so far. |

The marker describes attribution and checking depth, not quality. It does not certify code behavior or reproduce a reported result. Several finer provenance values in `site/catalog.mjs` all display as "Community · author-reported": `modelcard`, `independent` and `reportedEvaluation`. The research corpus and the new-resources page keep the four verification tiers defined above. On a curated row, "screened" covers the editorially reviewed and content-screened tiers.

**中文：** 网站上每个精选条目的信息行末尾都有一个证据标记：一个小图形加两个词。第一个词说明来源由谁发布，第二个词说明本项目对其结论核查到什么程度。图形的填充方式与第一个词一一对应，因此不只依靠颜色区分。首页筛选栏下方的一行图例链接到本节。

- **官方**（实心方块）：TypeSafe 发布；TypeSafe 自身资源明确标注。
- **预印本**（半填充方块）：未经同行评审的论文，链接到固定的 arXiv 版本。
- **社区**（空心方块）：TypeSafe 以外的发布者，包括公司、模型发布者与独立评测方。
- **背景文献**（点线方块）：提供研究背景，不是 Jev 内部架构的证据。
- **作者报告**：按作者或发布者的说法转述，本项目未重跑。论文、官方页面、模型卡、背景文献和评测报告均属此类。
- **已筛查**：链接页面通过了有记录的相关性与实质内容检查（来源台账中的 `content_screened` 或 `editorial_reviewed`），其结论未经检验。
- **已复现**：结果经独立重跑。目前没有精选条目属于此类。

该标记说明出处与核查深度，不代表质量评价，也不证明代码行为或实验结果。`site/catalog.mjs` 中更细的出处值都显示为“社区 · 作者报告”，包括 `modelcard`、`independent` 与 `reportedEvaluation`。研究来源库与新增资源目录沿用上文的四个核查等级；精选条目上的“已筛查”对应其中的编辑审阅与内容筛查两级。
