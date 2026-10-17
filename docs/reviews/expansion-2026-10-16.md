# Review of the resource expansion

The expansion is measured against [commit 3519c15](https://github.com/reacher-z/Awesome-Jev/tree/3519c15d7e00686a8dbf9b1e184c68726327ab1e), not against zero. The baseline contained 3,495 unique indexed sources and 67 curated entries. The [frozen baseline](../../data/expansion-baseline-2026-10-16.json) records known identities and evidence; an [exclusion-only supplement](../../data/expansion-baseline-supplement-2026-10-16.json), derived entirely from that same commit, adds older citations and title variants initially missed by extraction. It does not change the baseline or admit new resources.

## First published intake

| Batch | Accepted into the ledgers | Evidence depth |
| --- | ---: | --- |
| GitHub projects | 130 | Public README content screening; original short relevance summaries. |
| Hugging Face artifacts | 146 | Public model, dataset, evaluation-archive or Space card screening. |
| Primary guides and evaluations | 34 | Substantive official documentation and primary evaluation/report pages. |
| Research papers | 345 | Original-abstract checks via Hugging Face or reconstruction from OpenAlex metadata. |
| **Total** | **655** | **310 content-screened resources and 345 abstract-checked papers.** |

All accepted identities are listed in the [intake](../../data/expansion-intake-2026-10-16.json). The [generated progress report](../../data/expansion-progress-2026-10-16.json) independently excludes prior URLs, repository/README aliases, arXiv DOI aliases, duplicate evidence hashes, duplicate paper titles, unreviewed additions and metadata-only records. For the first published intake, the count was 655 after the baseline supplement and alias checks. Source artifacts are not necessarily independent models, test sets or studies.

That first batch comprises 290 directly related resources, 24 adjacent resources and 341 background-method papers. The relationship labels distinguish relevance to Jev from evidence about TypeSafe's proprietary implementation. The expanded directory and its Chinese counterpart display every accepted source, its relationship, and its evidence tier directly in HTML.

## Scope and corrections

The independent [batch-review record](../../data/expansion-review-2026-10-16.json) retains exclusion reasons, primary evidence URLs, metadata corrections and review limits. This is assisted maintenance review, not a claim that every full paper or every codebase was manually examined.

- The final GitHub review removed six of 136 proposed projects: prospective-only integration, a chat-routing false positive, a fork/port counted separately, a connectivity-only example and a changed README whose remaining work included Jev. Seventeen ambiguous primary READMEs were refetched; sixteen matched their input hashes, and the changed case was excluded. Accepted descriptions were rewritten as original short summaries.
- The Hugging Face review removed two sampled/repackaged datasets from 148 proposals. Fifteen selected public cards were refetched and matched the retained hashes. Two model-namespace repositories contain experiment code and are categorized as projects, not model weights. Separate metadata annotations correct JEVal and Granite titles and identify the Tetris artifact as a simulation using measured constants. A soft-label dataset annotation avoids treating edited teacher probabilities as independently established calibration.
- The paper review removed 22 of 367 proposals: five conference recordings, one project record, six thesis records and ten scope mismatches. All input abstract hashes were checked against the retained provider snapshots; 45 targeted abstracts and 11 official registration/institutional pages received focused inspection. The remaining papers retain `abstract_checked`, with no claim that their canonical publisher pages or full papers were separately read.
- The 34 primary web resources favor substantive concepts, worked cookbooks, SDK usage and evaluation methodology. Individual auto-generated API type pages, legal pages, corporate pages and translated duplicates were not used to inflate the count. Release and case-study statements remain provider-reported; benchmark results were not reproduced.

No source was newly granted `editorial_reviewed`. No model weights or datasets were downloaded, no model/API benchmark was run, and no remote source instructions or code were executed. All repositories remain public; verification artifacts do not contain account emails, sign-in state or credentials.

## Publication and continued maintenance

The main curated collection also gained four versioned preprints: REFLEX with Jev, Mnemon, Bongard and VideoJev. Those four source identities are counted once in the 655 additions, not again because they appear in the curated list. The initial expanded curated collection had 71 resources, including 32 direct papers and 40 BibTeX entries.

The separate twice-daily public-source workflow remains enabled. Its data-only PR and human merge/publication boundaries are unchanged. Future exploration can add another reviewed intake batch and rebuild the report; a clock change alone or a repeated source does not count as progress.

## 中文说明

本轮相对固定版本3519c15新增655项资源，包含310项正文筛查资源和345篇摘要检查论文；不是把原有3,495项重新计数。补充清单只补齐旧引用的排除依据，不修改原基线。仓库README、模型卡、数据卡、论文摘要及原始评测页面均保留来源、抓取时间和哈希；关系标签区分290项直接相关、24项邻近领域和341项背景研究。

复核剔除了尚未实现的集成、移植副本、格式/抽样数据、被误当论文的会议录像与项目记录，以及范围偏离材料。没有新增编辑审阅等级，不代表全文精读、科学同行评审或实验复现。四篇新精选论文只在655项中计数一次；持续扫描继续保留，后续新增仍须经过相同的去重、范围与证据检查。


## Follow-up intake: reproducibility and robustness

A second reviewed release adds **58 distinct resources**: 32 additional projects from the reserve, 12 paper-linked reproducibility artifacts, and 14 robustness tools or result archives. One project appeared in both candidate batches; its richer robustness record was retained once, not counted twice. The cumulative expansion is **713 new sources**, including 368 content-screened artifacts and 345 abstract-checked papers. The full index contains 4,208 unique sources, with 4,161 checked at their explicit tiers and 47 metadata-only entries.

Eight selected project READMEs and six selected reproducibility cards were independently refetched; every fetched body matched the input hash. Five selected robustness cards were separately refetched and matched. File inventories were inspected for the reproducibility artifacts, without downloading dataset rows or model weights, executing software, or reproducing results.

Material limits are visible in the directory descriptions. SecurityEval distributes saved observations without original input or response text; Bongard omits part of its training recipe; Chinese-Jev model weights remain pending; some agent datasets omit question texts or raw trajectories. JEV-Contrast stores the gold answer first in both candidate arrays, so evaluation requires shuffling with label remapping. Mock demonstrations, synthetic policy-author fixtures and partially reviewed LLM-assisted annotations remain labeled as such. A neutral display title keeps a small zero-shot Laya diagnostic from reading as a universal model verdict.

Four sources already included in the first intake were promoted to the main curated collection: the Artificial Analysis Decision Index, Entagl's dated workflow evaluation, and the official SDE cascade and Structure recovery cookbooks. This brings the curated collection to 75 entries; these promotions add **zero** to the distinct expansion count. Artificial Analysis includes private questions, Entagl's private customer replays limit reproduction, and the cookbook walkthroughs are not independently reproduced experiments.

**后续批次：** 本次新增58项，跨批次重复项目只保留一次，累计净新增713项。其中368项为正文筛查、345篇为摘要检查；全文精读、模型运行和实验复现均未被声称。关键复现限制、正确选项位置泄漏、模拟或合成标签等信息已直接写入展示简介。四项既有来源提升为精选条目不增加净新增计数，精选目录现有75项。

## Direct-paper follow-up and Chinese descriptions

Six further preprints add direct research on table rewrites, selective reasoning, multi-agent coordination, citation verification, StarCraft control and mobile GUI execution. All six fixed-version arXiv abstracts were read and independently refetched; their abstract hashes matched the collector records. The [paper review record](../../data/expansion-paper-review-2026-10-16.json) retains the evidence URLs, hashes and limitations. These entries are **abstract checked**, with no claim of full-paper review or reproduced results.

- [Typed Decision Models on Tabular Data](https://arxiv.org/abs/2610.19536v1): content-preserving table and question rewrites; low decision probability may indicate instability, without establishing correctness.
- [Selective Reasoning for Typed Decision Models](https://arxiv.org/abs/2610.19644v1): candidate-answer reads during interruptible reasoning; results depend on the fixed backbone and three task families.
- [System One-guided multi-agent collaboration](https://arxiv.org/abs/2610.08155v1): bounded coordination decisions and LLM workers; reported efficiency concerns the entire collaboration framework.
- [Same-Number Citation Swaps](https://arxiv.org/abs/2610.08675v1): a controlled financial-evidence test, not a population estimate of verifier quality.
- [JEV-Star](https://arxiv.org/abs/2609.27331v1): simultaneous interface changes prevent isolating the effect of planning.
- [Jev-Mobile](https://arxiv.org/abs/2609.30186v1): efficiency comparisons are conditioned on successful trajectories.

The expansion now contains **719 distinct additions**, comprising 368 content-screened sources and 351 abstract-checked papers. The complete index has 4,214 unique sources, including 4,167 checked at their stated tiers. The curated homepage remains at 75 selections; the six new papers appear in the discovery directory, not as additional curated-paper or bibliography entries.

The Chinese directory now translates every resource description, including qualifications about evidence, model-derived labels, private tests and reproduction limits. Translations share the original titles, URLs and evidence grades; they add no resources to the count. The build binds each translation to the exact English description and stops when a new or changed summary lacks a corresponding translation.

**中文：** 另新增6篇直接相关预印本，逐篇核对固定版本的原始摘要，并独立重取核对摘要哈希；累计净新增719项。六篇仍标为摘要检查，未宣称全文审阅或实验复现。中文新增目录同步提供全部资源的中文简介，保留关键限定、原始题名和来源链接；翻译不增加资源数。精选首页仍为75项，精选论文与书目仍为32篇和40条。

## Implementation follow-up

Two author-linked repositories add independently inspectable code resources: [Selective Reasoning](https://github.com/binzheng-joey/selective-reasoning) and [JEV-Star](https://github.com/sc2musa/jev_star). Both primary READMEs were independently refetched with matching hashes, and public file/release inventories were inspected. The [implementation review](../../data/expansion-implementation-review-2026-10-16.json) records those checks. Software/data archives, selected replays and videos remain components of their repositories, not additional resources or independent studies.

The expansion reaches **721 distinct additions**: 370 content-screened resources and 351 abstract-checked papers. The complete index has 4,216 unique sources, including 4,169 checked at their stated tiers and 47 metadata-only discoveries. Selective Reasoning's measurement recomputation does not rerun model inference; external weights, benchmarks and feature caches remain necessary. JEV-Star omits full original logs, and implementation/service timing differences confound causal claims about planning. Neither repository was executed.

The Chinese directory provides corresponding summaries for both additions. Four existing paper descriptions were made more specific without changing evidence hashes or verification levels. The three curated-paper promotions recorded in the [selection review](papers-2026-10-16.md) are already counted sources, adding zero to the expansion.

**中文：** 本次新增两个论文配套代码仓库，累计净新增721项；同仓压缩包、胜局回放与视频不拆开凑数。两个README均独立重取并核对哈希，文件及发布清单已检查，但未下载归档内容、运行模型或游戏、复现实验。中文简介保留外部依赖、日志不完整与版本混杂等限制；三篇论文提升为精选及四条简介细化均不增加来源数。

## Tools, confidence and memory intake

This intake adds **10 distinct resources**: six direct preprints, three author-linked implementation repositories and one separately published annotated evaluation dataset. The expansion reaches **731 additions**: 374 content-screened resources and 357 abstract-checked papers. The full index has 4,226 unique sources, including 4,179 checked at their stated tiers and 47 metadata-only discoveries.

Every new paper's fixed-version primary abstract was independently retrieved with a matching hash, and its bibliographic metadata was checked. Every new implementation README or dataset card was also independently retrieved with a matching hash; public file inventories were inspected without executing code or downloading data rows. The [intake review](../../data/expansion-tools-memory-review-2026-10-16.json) preserves the evidence and limitations.

Two display-only annotations make important boundaries explicit: the option-channel study tests open-weight models, not hosted Jev, while the memory-retirement study's labels, shared errors and development-set selection constrain cascade claims. Original abstract hashes and evidence grades remain unchanged. All ten additions have corresponding Chinese descriptions. Six papers receive curated entries and citations without being counted a second time.

DeRef's separate dataset adds argument correctness/path labels and a controlled source-relocation set to existing benchmark material. It is one inspectable dataset artifact, not four separate configuration discoveries or a new independent task population. The companion code does not include model outputs or result caches. The confidence-audit repository fetches datasets separately under mixed source licenses, including noncommercial conditions; the guardrail repository's generated policy cases do not establish real-world attack prevalence.

**中文：** 本批净新增10项：6篇直接论文、3个作者代码仓库与1个独立发布的标注数据资源，累计731项。原始摘要及README／数据卡均有独立重取与哈希核对；未执行代码、下载模型权重或数据行、复现实验。所有新条目同步提供中文简介；六篇提升为精选不再加数，DeRef四个配置合计只算一个数据集。

## Reference-derived studies and companion artifacts

This release adds **14 distinct resources**: eight direct preprints, five repositories and one author supplementary deposit. The expansion reaches **745 additions**, comprising 380 content-screened resources and 365 abstract-checked papers. The complete index contains 4,240 unique sources: 4,193 checked at their stated tiers and 47 metadata-only discoveries. Thirteen additions are directly related; the social-science upstream benchmark is explicitly adjacent.

The [reference review](../../data/expansion-reference-review-2026-10-16.json) records the two four-paper inputs, normalized accepted records, independent source hashes and six-artifact review. Normalization maps initial submission dates and reviewed-version dates to separate fields and uses the scanner's fixed-version primary-abstract schema. It does not change hashes, retrieval times or evidence grades. A display-only annotation carries the medical manuscript's preliminary status into both discovery pages without altering the raw record.

Companion materials count as whole resources. The medical manuscript PDF is not another resource beside its supplement; KITE's mirrors, forecast files, scripts and aggregates remain one repository; the legal package's records and plots remain one package. JevOut's already known implementation adds zero. The upstream social-science repository is cited for its task materials, not as a separate Jev experiment, and no top-level license was confirmed.

All six primary artifact documents were independently refetched with matching hashes, including the medical deposit landing page. Two legal release-scope documents were checked separately. Readable-character counts were recomputed without changing original document hashes; the legal translation was corrected to describe a field-allowlisted export, not sample filtering. No archived contents, data rows, model weights or experiments were executed or independently reproduced. Every addition has a corresponding Chinese description.

**中文：** 本批净新增14项（8篇论文、5个仓库、1个作者补充材料档案），累计745项。论文修订版、精选展示、镜像、脚本、结果子集及同项目PDF均不重复计数。新论文使用固定版本字段，初始与修订日期分开；原始哈希、抓取时间和等级不变。六个材料主页／README均独立重取核对哈希，法律发布范围另行复核；医学档案只查发布页与目录，未检查包内内容。全部新增条目已配中文简介。

## Ordinal, visual and report-evaluation follow-up

Five distinct additions—three primary-abstract paper records and two whole code projects—bring the expansion to **750 sources**, with 382 content-screened artifacts and 368 abstract-checked papers. The complete index has 4,245 unique sources: 4,198 checked at their stated tiers and 47 metadata-only discoveries. Curated promotion of the three papers adds zero further resources.

The [review](../../data/expansion-ordinal-visual-review-2026-10-16.json) retains fixed versions, original hashes and review limits. Paper abstracts were independently refetched. Artifact checks instead used matching cached README, reproduction and selected-directory evidence; a parent batch refetch ended with HTTP 403 and is not represented as a fresh successful check. Original retrieval dates remain unchanged. The anonymous repository is categorized as a code project, with its file-revision and missing-material limits visible. Adapters, asset pieces, result subsets and project-page mirrors are not separate discoveries.

The next bounded reference pass inspected 138 citations from these three fixed-version manuscripts and found no additional uncollected direct papers: two relevant papers and four non-paper direct references were already known, while the remaining citations were background. No ordinary background was added to fill a numerical quota. This is a statement about that inspected reference set, not a claim that no other relevant work exists.

**中文：** 本批净新增5项（3篇论文、2个完整代码项目），累计750项；精选提升、适配器、分片和镜像不重复计数。论文原始摘要独立重取通过；代码资料按原缓存正文和目录哈希复核，不把HTTP403的新取失败写成成功，也不更新原抓取时间。后续检查三篇论文的138条引用，没有找到未收录的直接论文，未扩收普通背景凑数。

## Author companions and reproduction scope

Two distinct resources bring this expansion to **752**: the Jeva-4B author checkpoint package and the Reading Right, Acting Wrong diagnostic dashboard. The former is separate material from its already-known code repository; shards, adapters and heads count once. The latter contains a substantive evolving report, not just the paper abstract. The current 22-system report, its 18-system consistency subset and the fixed paper’s 18-system cohort must not be conflated.

Independent checks reviewed original model-card/report text, author links and public file metadata; the parent refetched both primary documents with matching hashes. No weights were loaded, source scripts executed or reported experiments reproduced. The checkpoint card declares no model license, and report aggregates do not establish a complete downloadable reproduction package. [Evidence record](../../data/expansion-companion-review-2026-10-16.json).

Thirteen links to already-known companion resources were added to eight paper entries; these add zero resources. A further author paper-site link is navigation only, not a verified analysis supplement. The bilingual [reproduction-scope review](reproducibility-2026-10-16.md) explains what different material releases can support without claiming that any route was executed.

**中文：** 本轮新增Jeva检查点包和作者诊断报告两项，累计752项新增来源。模型分片与网页资产不拆分计数；检查点许可未声明，看板的22系统、分析子集18系统与固定论文18系统保持区分。八篇论文补齐13个既有配套资源链接，另加一个仅用于导航的作者论文站，均不增加来源计数。双语复现说明区分可重算范围与实际执行状态；本轮未运行来源代码、加载模型或复现实验。

## Security implementation and measurement definitions

One new author implementation brings the reviewed expansion to **753**. JevAdvBench’s fixed-commit README and three selected directory listings support a documented offline-analysis route and API evaluation runners. The independent review checked cached hashes and filenames; the parent refetched the README with a matching hash. No archive restoration, script execution, prediction-record inspection or statistical reproduction was performed. Code and data have separately declared licenses, and model-derived labels are not independent human ground truth. [Evidence record](../../data/expansion-security-companion-review-2026-10-16.json).

The existing JevAdvBench dataset and system-one-security-eval repository gained paper navigation links with zero new identities. Just Ask Jev and its author code also remain known identities despite the paper’s curated promotion. A bounded check of two remaining judging papers found no verified author release entry; upstream benchmarks were not relabeled as companion releases, and absence in those snapshots is not proof of global unavailability.

The bilingual survey and guide now distinguish decision flips, target-selection frequency, case-level majority success and conditional routing metrics. Three fixed-version sources and 18 targeted anchors support this comparison; their results remain author-reported, and the proposed evaluation protocol is not a performed experiment. [Metric review](../../data/attack-metric-review-2026-10-16.json).

**中文：** 本轮只新增JevAdvBench完整代码项目，累计753项；既有数据集、系统安全评测项目、Just Ask Jev论文与作者代码均不重复计数。固定README和部分目录已核查，未运行脚本、还原归档或重算结果。双语综述与指南区分翻转率、目标频率、案例多数成功及条件路由指标，引用三篇固定稿的定向段落，不将作者结果写成本项目复现。

## Turkish checkpoint and comparison conditions

One distinct ufakzeka-karar checkpoint brings the expansion to **754**. The paper and already-known implementation identify the separate Hub weight release. The fixed model card, metadata and file inventory were independently checked; the parent refetched the card with a matching hash. No weight, loader, calibration file, dataset row or prediction archive was downloaded or executed. The card declares Apache-2.0 for weights and loader while retaining upstream data terms, and explicitly flags test-informed training and worsening calibration on support questions. Its released-run comparison is not an unseen-question test. [Review and provenance](../../data/baseline-selection-review-2026-10-16.json).

Three existing papers were promoted without adding raw source rows or upgrading evidence. Two known code-project links and a same-release benchmark mirror also add zero. Five display-only annotations clarify titles, first-submission dates and scope: one 2025 routing paper moves to background, while NeoHorse v2 retains its directly relevant typed-decision adaptation with the wider family results kept separate. All original ledger bytes, hashes, retrieval times and grades remain intact apart from appending the one new checkpoint row.

**中文：** 本轮只新增一个独立模型检查点，累计754项；三篇论文精选提升、已知代码与基准镜像均不重复计数。模型卡、元数据及目录已核查，未下载或执行权重、加载器、校准文件和数据记录；测试反馈影响训练及客服校准的限制保留。五项展示注释修正题名、日期与范围，早期路由研究归入背景，NeoHorse的决策适配与整体家族结果分开，原台账证据不改。

## Selected scheduled-scan sources — 17 October 2026 (UTC)

Six whole projects bring the reviewed expansion to **760**: a Protobuf client generator, a shadow-routing example, Weiche routing research, complaint-classification analysis, Chinese RAG reranking evaluation and a community survey package. Their public READMEs were freshly fetched and all six hashes matched the scheduled scan. Descriptions distinguish experimental interfaces, synthetic fixtures, author-reported measurements, saved-output analysis and fresh execution. No source code was executed and no paid model API was called. Complaint/customer records, model weights and prediction archives were not downloaded.

The automatic [scan PR](https://github.com/reacher-z/Awesome-Jev/pull/4) remains open. It reported 323 new records and a partial scan, including provider failures; this release accepts only the six individually inspected projects. The remaining candidates are not automatically added to this reviewed expansion. [Selection and scope](../../data/scan-review-2026-10-17.json).

The four existing Decision Index documents were separately refreshed to commit `0ddf675`. The edition is still 0.3.2, but its reference now names Jev 1.14 while frozen inputs retain 1.13. Public/private weights and scoring rules remain unchanged. The Hub’s old tracker name redirects to this same Space; canonicalizing that alias prevents a content update from creating an extra counted source. Raw historical alias evidence remains in the ledger. These document refreshes, three paper promotions and the alias correction add zero expansion identities.

**中文：** 本轮从自动扫描中单独核查并接受六个完整项目，累计760项；说明文件哈希全部匹配，但没有执行源码或重放实验。自动PR仍待继续审阅，323条提议不能直接当作已接受成果。四份Decision Index文档更新至新提交，区分1.14参考运行与1.13冻结输入；旧Space名称按官方跳转合并，不因正文变化虚增来源。原证据仍保留，文档刷新和论文精选提升均不重复计数。

## Multilingual runtimes and evaluation tools — 17 October 2026 (UTC)

Twelve documentation-backed projects bring the expansion to **772**. All fresh README hashes match the retained scheduled-scan observations, and no canonical URL or body hash duplicates were found in the current/frozen collection. Linked weights, size variants, example notebooks, data mirrors and component files are not additional sources. [Review record](../../data/multilingual-tools-review-2026-10-17.json).

The language implementations have different operating limits: FRIDA describes Russian–English inputs and Russian suffixes; OpenThai documents a Thai/English training pipeline; Quyet varies by checkpoint and caps option counts; Jev-AR reports synthetic Arabic data without native-speaker validation, approximate confidence on custom routes, and gated noncommercial weights. No gated access was requested or model downloaded.

Evaluation scope is equally important. CITY-Jev identifies its content as preliminary with partial human review and evaluates decisions rather than complete agents. The browser comparison uses native request formats, ambiguous GUI labels and nonidentical browser/timing environments. English RAG gating is exploratory, while the guardrail benchmark withholds part of its test set. The measurement project separates response-shape fixtures from accuracy data and records corrected baselines. The game-training project separates a selected seed, retention checks and later joint training. We did not execute any of these workflows or inspect raw predictions, customer data or model weights.

Eight projects were selected for the main catalog; all twelve have parallel Chinese discovery descriptions. The guide adds two documentation-based language-transfer examples without asserting that confidence thresholds transfer. The remaining scan proposal stays open for further review.

**中文：** 本轮十二个项目使扩展资源达到772项，说明文件哈希均与扫描一致，镜像、权重变体和组件文件不拆分计数。多语言实现的语言／长度／选项限制、阿拉伯语标签未由母语者验证、社区评测的初步状态、不同浏览器与计时环境、探索性门控和未公开测试切片均保留。八项进入精选，十二项都有中文简介；未执行代码、调用模型或检查原始数据，剩余候选继续待审。

## Audio checkpoint follow-up — 17 October 2026 UTC

One complete AudioJev checkpoint repository was accepted from its inspected public model card, bringing the expansion to **773 sources**. Three associated paper selections were already in the frozen baseline and add zero source counts; the inference-code navigation link is not an accepted ledger addition. The model card identifies a single seed and Qwen Research license, discloses audio-source overlap and distinguishes order stability from correctness calibration. No weights or audio were downloaded. [Evidence and preserved provider records](../../data/label-graph-audio-review-2026-10-17.json).

**中文：** 新增一个已查模型卡的完整AudioJev检查点，累计773项扩展来源；三篇精选论文均为既有来源，推理代码链接只作导航，均不重复计数。保留单种子、许可、音频来源重叠及顺序稳定与正确率校准的区别，未下载权重或音频。

## Four primary domain and transfer studies — 17 October 2026 UTC

Four distinct papers were accepted from fixed-v1 arXiv abstract pages, bringing the expansion to **777 sources**. Candidate identities came from the open scan proposal; the acceptance uses fresh, version-protected primary evidence. No old ledger rows were altered, no companion links were counted, and remaining scan records are still pending. English and Chinese descriptions retain medical, hardware, event-model and language-transfer limitations. [Review record](../../data/domain-transfer-review-2026-10-17.json).

**中文：** 四篇固定v1原始摘要使扩展达到777项；采用新抓取并固定版本的证据，不改写旧台账，不计入配套链接，扫描其余候选仍待审。中英文简介均保留医学、硬件、事件模型及语言迁移限制。

## Four model-card releases — 17 October 2026 UTC

Four distinct model repositories bring the expansion to **781 sources** and the main catalog to **130 curated resources**. All inspected card bytes match explicit Hub commits; three match the earlier scan, while Span-02 has changed and moved from `lihe07` to `respanai`. The old and new addresses are one identity, including in subsequent scanner matching. A regression test distinguishes the real alias from a similarly prefixed model. [Pinned evidence and review limits](../../data/model-card-review-2026-10-17.json).

Amos separates zero-shot and benchmark-train-prior settings. KnowLine discloses public-score checkpoint selection, related task/source exposure and approximate self-run calibration comparisons. Lychee declares CC BY-NC 4.0; an Apache-2.0 base does not replace that model license. Span-02 documents a dedicated engine, optional reasoning and separate index/default settings. These descriptions are publisher evidence, not reproduced performance. Sibling sizes, release variants and component files were not counted separately.

**中文：** 四个模型仓库使扩展达到781项、精选达到130项，模型卡均与固定Hub提交的字节一致。Span-02迁移且文档改变，旧新地址只算一个来源，并以回归测试保护扫描身份匹配。保留Amos先验拟合条件、KnowLine公开评测选点与来源重叠、Lychee非商业许可、Span专用引擎与推理配置区别；没有执行模型或拆分尺寸、版本、组件来增加计数。

## Browser and search runtimes — 17 October 2026 UTC

Four whole implementation repositories bring the expansion to **785 sources** and the main collection to **134 curated resources**. Source README hashes match the existing scan proposal. Browser output parity, synthetic form coverage, training-set overlap, unfinished modalities, calibration inputs and cache memory tradeoffs are retained in the summaries. Model mirrors, bundle variants, demos and the embedded SearchJev PDF are not separate additions. The mJev display title is protected from an unrelated example heading. [Evidence and scope](../../data/runtime-search-review-2026-10-17.json).

**中文：** 四个完整实现仓库使扩展达到785项、精选达到134项，README哈希与扫描一致。保留移植一致性与泛化的区别、合成表单范围、训练重叠、未完成模态、校准输入和缓存显存取舍；镜像、不同大小的包、演示及内嵌PDF不拆分计数。另修正mJev由代码示例标题引起的展示风险，未执行项目代码或下载模型数据。

## Unavailable and withdrawn papers — 17 October 2026 UTC

Five background papers were removed, leaving the expansion at **780 sources**. Four arXiv papers had been withdrawn by their authors before the 16 October intake: each current version is a withdrawal notice, and two notices state that the results are invalid. Their OpenAlex-reconstructed abstracts did not show the withdrawal. The fifth paper's DOI resolves only to `subscholar.org`, which no longer exists in DNS. *Classification with a Reject Option using a Hinge Loss* stays listed and now links its JMLR page, because its ACM `10.5555/` DOI is not registered with doi.org. Each removed or replaced URL has an exact-URL exclusion with its evidence and observation time in [source curation](../../data/source-curation.json), so a later scan cannot re-add it. The research-paper intake batch now lists 340 accepted URLs. ChenstarMr/jev-chat-windows was public again when rechecked, so its record is unchanged.

**中文：** 删除五篇背景论文后，扩展为780项。四篇arXiv论文在10月16日收录前已被作者撤回，当前版本均为撤稿说明，其中两篇指出结果无效；OpenAlex重建的摘要未反映撤回。另一篇的DOI只指向已无域名解析的`subscholar.org`。《Classification with a Reject Option using a Hinge Loss》保留，因其ACM `10.5555/` DOI未在doi.org注册，改为链接JMLR页面。每个删除或替换的URL都在来源策展文件中记录精确URL排除、证据与观察时间，防止后续扫描重新加入；论文收录批次现列340个URL。ChenstarMr/jev-chat-windows复查时已恢复公开，记录不变。
