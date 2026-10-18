# Workflow and training runtime review — 18 October 2026 UTC

Four whole repositories were accepted from the open [scan proposal](https://github.com/reacher-z/Awesome-Jev/pull/4) at `656c0e8be89e0ac757d3d5e53b2c24b1d935841f`. Each public README was inspected for purpose, evaluation scope, operational boundaries and declared license. Fresh bytes match both the scan and a separately fetched fixed Git commit. This is documentation review, not code audit or experimental reproduction.

No canonical project identity or README hash overlaps the accepted ledgers or supplemented frozen baseline. Each project counts once. Weight variants, component files, linked documentation and demos add no source counts. The remaining scan proposal is still pending.

| Project | Fixed README | SHA-256 | Scope retained in the catalog |
| --- | --- | --- | --- |
| [Abide](https://github.com/coldteadotai/abide) | [21b7e74fa92c](https://raw.githubusercontent.com/coldteadotai/abide/21b7e74fa92cf96eb8bf525f5d1b612e6fcaa8dd/README.md) | `51d411ac3f315720a7180775f0b9bff05254848306a64d2c1d5d55d5c15faa5b` | Hooks have deadlines and exit zero; missing credentials or network leave edits unchecked. Edit checks send changed lines to TypeSafe or a configured gateway. Rule wording and thresholds affect results; the two-repository replay does not establish complete violation recall. |
| [jev-fabric](https://github.com/fabric-runtime/jev-fabric) | [618c53821ffb](https://raw.githubusercontent.com/fabric-runtime/jev-fabric/618c53821ffba3d972e0cd3f9ca2f09028f3d0d4/README.md) | `bc6db4b22ffdcad210b49d20adf2a230e209b5e537c9df3ca50d82551a71d5ca` | The runtime is not a sandbox and promises no reboot resume, exactly-once execution or rollback. Proofs cover selected pure policy modules with explicit FFI boundaries. Native decision probabilities, generated estimates and token-logprob readouts have different semantics. |
| [atoma](https://github.com/atoma-run/atoma) | [364465553d19](https://raw.githubusercontent.com/atoma-run/atoma/364465553d19394d5b8df90c65851e6bb5391472/README.md) | `6fa2a4f6abff93b62436e0294c0c8abbc74a4d2c7725ff619bdb7abba2708994` | The registry, skills and trust counters are shared across organizations; prompts or recipes derived from documents may be visible to other runs. Mutually untrusted tenants are unsupported. Local file containment is not shell isolation, and historical controlled rounds predate a platform-state reset. |
| [circuit](https://github.com/barneyjm/circuit) | [3580e3634de5](https://raw.githubusercontent.com/barneyjm/circuit/3580e3634de58e32fcba7580ccc31816c3ea2bd4/README.md) | `939968f324fd85f6c7409e5eeb6354e84301ca44e8d44f9ee93be2afa4563c16` | The README reports separate text, image and audio evaluations with differing data and execution conditions. Cross-entropy training alone does not guarantee calibration or absence of option-order bias. Code is Apache-2.0; base-model and dataset licenses remain separate. |

The intake hash is `7e6b6588c953c50a1f6265e804b9a3551e414b3a1c691aecebce9efc9b5842ab` (SHA-256 of the four new ledger records serialized as sorted-key, UTF-8 JSON lines). Retrieval and fixed-commit verification times are retained in the source ledger. Abide has a display-title annotation because the automatic Markdown parser selected a heading inside a code example. Original provider evidence is preserved.

The publication contains summaries and provenance only. No hooks were installed; no project code, model, dataset, hosted app, MCP service or API inference was run. Raw README files, illustrative contacts, account details and local paths are not published. The declared code licenses do not substitute for downstream model or data terms.

**中文：** 本轮核查四个完整实现项目，README 均与固定提交及扫描哈希一致；仅审阅文档，没有运行代码或复现实验。项目身份和正文哈希经过当前台账与冻结基线去重，权重变体、组件和文档链接不重复计数。简介保留未检查放行、调用者权限、共享学习范围及评测条件；原始说明文件和个人信息不进入公开仓库，其余扫描候选仍待审。

## Publication checks

The source ledger is append-only: all pre-existing bytes are unchanged and four records were appended. Generated output contains 160 curated resources, 78 papers and 784 reviewed additions; the full source index contains 4,290 unique identities, including 47 metadata-only entries. These counts describe different collections and are not additive.

Local browser checks verified the Tools filter (20 entries), an atoma search (one result), translated metadata, and white backgrounds with dark text. Reducing mobile heading/control gaps moved the first Chinese tool row from 924 px to 758 px at a 390 × 844 viewport without reducing resource text size. Both 320 px English and 390 px Chinese layouts have no horizontal page overflow. Exact publisher handles and the `AGPL-3.0-only` identifier remain untranslated; descriptive qualifiers are localized.

All 433 repository tests pass after the exact-name/license adjustment. The static build check, expansion audit, publication validator (189 files and 4,304 ledger records) and whitespace check pass. Browser checks are local observations; deployment receipts are recorded separately after publication.

## Deployed verification

Commit `1e0f4cb3de618a8b5ea94ff911ccd5e20ba48c99` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39099515079), [website repository checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39099518657) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39099518692). One public HTTP verification pass matched all 34 targets to committed bytes: 18 canonical pages, machine-readable exports and versioned browser assets. Chinese discovery descriptions and the new Abide title annotation also passed the targeted semantic checks. The live Tools filter shows 20 of 160 resources with all four new entries marked community / screened.

One IndexNow POST returned HTTP 200 for the English/Chinese home and discovery pages. These four URLs have substantive content additions; other routes were not resubmitted merely because the shared CSS or curation date changed. The receipt confirms notification, not indexing, search ranking or AI citation. No Google or Bing account action was taken for this release.
