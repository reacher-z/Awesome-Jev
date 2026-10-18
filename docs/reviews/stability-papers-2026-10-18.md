# Stability, fallback, security and recalibration — 18 October 2026 UTC

Five paper identities were selected from scan PR 4 at `5fa0e40ae7a483cc2fca81ec4128ca7220048562`. Fresh fixed-version abstracts match the raw scan evidence, with complete citation metadata retained. The source-index view consolidates hashes, so equality was checked against the raw ledgers rather than a missing abstract-specific field in the index. This is abstract and targeted-section review, not full-paper reading, independent proof verification or experimental reproduction.

| Study | Fixed version / first submission | Scope and limitations |
| --- | --- | --- |
| [Prism-1: Position- and Rival-Independent Scoring for System One Models](https://arxiv.org/abs/2610.22066v1) | v1 · 2026-10-15; first 2026-10-15 | Two open backbones and benchmark sets with at most 20 options; one to three seeds per configuration. The readout needs fine-tuning and gives up within-model option comparison. None-of-the-above and odd-one-out tasks fall outside its preferred assumptions. State injection is not addressed; numerical rounding can affect near-ties and normalized top probabilities can change when candidates are added. [Section 1](https://arxiv.org/html/2610.22066v1#S5.SS6) · [Section 2](https://arxiv.org/html/2610.22066v1#S7) |
| [Lost in the Fallback: How Reliably Do Typed Decision Models Use Fallback Options?](https://arxiv.org/abs/2610.19856v1) | v1 · 2026-10-14; first 2026-10-14 | Controlled tests use CLINC, BANKING and TREC with fixed parameters, paired reassignment and equivalent definitions. These diagnose rule execution in the tested open models, not production fallback reliability or a validated mitigation. A correct supplied category does not guarantee correct reassignment; a confidence threshold is a separate policy. [Section 1](https://arxiv.org/html/2610.19856v1#S2.SS0.SSS0.Px2) · [Section 2](https://arxiv.org/html/2610.19856v1#S3.SS1.SSS0.Px1) · [Section 3](https://arxiv.org/html/2610.19856v1#S3.SS1.SSS0.Px2) · [Section 4](https://arxiv.org/html/2610.19856v1#A1.SS0.SSS0.Px1) · [Section 5](https://arxiv.org/html/2610.19856v1#Sx1) |
| [SecJev: Bringing Security Expertise to System One Decision Models](https://arxiv.org/abs/2610.03073v2) | v2 · 2026-10-14; first 2026-10-02 | Source annotations may depend on facts absent from an individual input, whereas policy tasks use the displayed rule. Task-macro averaging gives equally weighted tasks of uneven difficulty. A 280-question human audit reveals evidence/annotation disagreements; broader transfer and residual overlap remain open. Public release metadata was inspected, not model/data packages; a custom agreement and source-specific upstream terms apply. [Section 1](https://arxiv.org/html/2610.03073v2#Sx1) · [Section 2](https://arxiv.org/html/2610.03073v2#A2) |
| [BLADE: Auditing Information Use for Failure Attribution in LLM Multi-Agent Systems](https://arxiv.org/abs/2610.18780v1) | v1 · 2026-10-13; first 2026-10-13 | Eight strategies are compared under one shared Jev interface, not as a ranking of their original complete systems. Agent/step accuracy measures agreement with annotations; DyLAN uses an agent-round criterion. Input shortening may omit useful evidence, and broader workflows or other judge backbones were not established. The linked TRIAGE repository is an upstream baseline, not verified BLADE code. [Section 1](https://arxiv.org/html/2610.18780v1#S4.SS1.SSS0.Px3) · [Section 2](https://arxiv.org/html/2610.18780v1#Sx1) |
| [Recalibrating Many Questions with Few Labels: Minimax Rates and Identification Limits](https://arxiv.org/abs/2610.18488v1) | v1 · 2026-10-13; first 2026-10-13 | A theoretical study motivated by typed-decision probabilities, not a Jev experiment or deployment guarantee. Fixed-effects rates assume a shared non-atomic output law and monotone maps; coarse grids can have different rates. The loss is average excess Brier risk, not worst-question performance. The random-effects upper bound uses a population idealization; a finite-question empirical-Bayes procedure remains open. Formal proofs and numerical illustrations were not independently checked. [Section 1](https://arxiv.org/html/2610.18488v1#A1.SS2.SSS0.Px1) |

## Document fingerprints

| Study | Fixed abstract-page SHA-256 | Original abstract SHA-256 | Manuscript HTML SHA-256 |
| --- | --- | --- | --- |
| arxiv:2610.22066 | `d80fbef0da16e0c0a0da9b71081f28764dba623f8dbec0c2967fb70b48906df0` | `42fb228ac2f90cf10f8d36d9a1f91910799883260f9fba72d76137ffbd46cbcb` | `1dd60c29a9564225d666cd9316123cac061c86c6cc51d950eca62def98608526` |
| arxiv:2610.19856 | `9cfc15ab4dd7353c391166da6f15852c0408b792c1fd9e350b5bcc2bacee30fe` | `1501bea0917b26ff46d630b2eab84803c098a05a4640d0895ad0e8d1d0c75854` | `e86d09f8feb721445c457da94061d66a9b515363d2d9e15b10862743553e0b51` |
| arxiv:2610.03073 | `9aae6dd7e02231e848bf15f9adeaedde0eb7bd51fb31d32dabbdb0aa6a837673` | `3475324b78c1bc087406f26aa6fbb024f0e57a395d9fcfba9c244cfa73b6929c` | `0d06bc52bde3276067ae3fae880ccdb933963a12936ca1fc7fbb228690a31af5` |
| arxiv:2610.18780 | `1707fde04c53f19dae900fd1e411b6c63dfd747b985678759ecd8b237adcc706` | `77c44fd250d2b23b96c7298da687c01bab5f478191ccfc57b8c5f7de91e7d6b0` | `baaf13220c52b089b9edc533f61084e6feca98275e37b25d09b2c10529bf913f` |
| arxiv:2610.18488 | `a298f058115b60e6f2023b3e1677fba662e0b5d8c175cb9764da57af3ac0a690` | `6784e8ab881e2b02eff1a8bb0333b88590c61f47915c78ef56970686be6ccac4` | `ab517b55ba624ddd947a4d4cf8a0a7ac0dc51407f328a1a04541d1098960b3fa` |

## SecJev release navigation

The repository README, custom distribution agreement and release-status document were read at one fixed commit. Release metadata confirms named model/code assets in v1.3.0 and a corpus asset in v1.0.0; asset contents and checksums were not independently verified. No model, training corpus, attack trace, raw security log, package or executable was downloaded or run. The source-specific terms are preserved as a release constraint rather than relabeled as blanket MIT/Apache licensing.

- [README.md](https://raw.githubusercontent.com/UESTC1010/SecJev/2499c2704adcb918e503c287b4920e159f32b278/README.md): SHA-256 `6671550bbbebbddf01f5864990035c90e3217087b35c29fa97b5df64776c2d9b`.
- [LICENSE](https://raw.githubusercontent.com/UESTC1010/SecJev/2499c2704adcb918e503c287b4920e159f32b278/LICENSE): SHA-256 `b6a588f3a9a4da1cab13af0aeda2e580865748bbb989bb58bebb1b89bc2834ba`.
- [RELEASE-STATUS.json](https://raw.githubusercontent.com/UESTC1010/SecJev/2499c2704adcb918e503c287b4920e159f32b278/RELEASE-STATUS.json): SHA-256 `e4afd6bfe1b9b00f90d744f4207512677c6a3a968a12a0844459b7ea6dbbd7a0`.
- [v1.0.0](https://github.com/UESTC1010/SecJev/releases/tag/v1.0.0): API metadata SHA-256 `c980f5ff5324b285849e89cfb79acc54dba8a9ceb924432583abfa0478d10890`, observed 2026-10-18T06:18:31.935436+00:00.
- [v1.3.0](https://github.com/UESTC1010/SecJev/releases/tag/v1.3.0): API metadata SHA-256 `08687eed142bf364dd1bb461acf25208ced7e6ce8c953fb05465321b47f9432d`, observed 2026-10-18T06:18:31.809065+00:00.

Prism-1 and the fallback paper link upstream models and benchmarks, but no dedicated author implementation was verified. BLADE’s GitHub reference identifies a TRIAGE baseline; it is not presented as BLADE code. The theory paper is listed without a code claim. These are bounded availability checks, not proof that no release exists elsewhere.

Intake SHA-256: `2afb96f643b0fea8d5aa935ce9c48e5982411fa9f5d9a0e3d32d83c18e14992c` over the five sorted-key UTF-8 ledger JSON lines. Only the five papers increase source counts; versions, code links and release variants add zero. Existing ledger bytes and the frozen baseline remain unchanged. The remaining scan candidates stay pending. No raw pages, contacts, private paths or credentials are published.

The bilingual guide now separates a model-selected fallback option from an application confidence gate. The option-label topic distinguishes stable original-option probability ratios from unchanged normalized probabilities, and notes the limits of option-independent scoring for menu-dependent rules. Proposed diagnostic steps are identified as our evaluation suggestions; no experiment is implied.

**中文：** 本轮核查五篇固定版本论文的摘要、引用信息及指定方法／限制段落。SecJev保留v2与首次提交日期，区分已查发布元数据和未加载的权重／数据包；理论论文明确其风险目标与假设，不把定理写成Jev实测结果。指南区分兜底选项与应用门控，专题区分概率比稳定和归一化概率不变；所有结果仍为作者报告，配套链接不重复计数。

## Local validation

All 452 repository tests pass. The bibliography/README/catalog checks agree on 87 direct papers, 96 bibliography entries and 169 curated resources; the expansion audit reports 793 sources. Previous research-ledger bytes are unchanged, with five rows appended. Static build verification, publication validation (199 files and 4,313 ledger records) and whitespace checks pass.

Browser checks verified the SecJev v2 date, separate first-submission date, three release links and bilingual material-scope note. The new fallback section is reachable from its ordinary table-of-contents link and is readable at 390 px without horizontal overflow. The guidance and topic comparison remain ordinary static HTML with primary citations.

## Publication and search checks

Commit `cdb23233bcf0c52ade0ab59dd93f404e650f2fb0` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39104107725), [website repository checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39104110078) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39104110050). All 38 live targets matched committed bytes. The live directory shows 87 papers and 46 with linked code; release metadata and unverified-code markers retain their separate meanings.

One IndexNow POST for the ten substantively changed home, paper, discovery, guide and option-bias pages (English/Chinese pairs) returned HTTP 200. No unchanged model/tool page was submitted.

Google Search Console's inspection of `https://awesomejev.github.io/papers/` showed **URL is on Google** and **Page is indexed**. Fetching and indexing were allowed, Googlebot smartphone had fetched it successfully, the user canonical was the inspected URL and Google's selected canonical was “Inspected URL.” Its displayed last crawl was **16 October 2026, 01:17:39**; no timezone conversion is inferred. This verifies indexing of the directory, not Google's capture of this five-paper update or any ranking. After live deployment verification, one request for updated indexing completed the live check and received **Indexing requested**, placing the URL in a crawl queue.

The sitemap screen separately still showed the earlier Unknown / Couldn't fetch / zero discovered pages record. That issue remains unresolved; page indexing is not evidence that sitemap processing has recovered. No account identifiers or Search Console screenshots are committed. Bing verification is unchanged.
