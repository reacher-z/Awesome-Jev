# Model directory review — 18 October 2026

Five existing source records become curated model entries: OneJev1.5-27B, Liquid d1-omni-600M, Torchcast Decision 27B, tasksource-decider-nano and Saracura PT-BR 4B. Perplexity Decider v1.2 replaces the v1.1 representative. The curated collection now has **20 models and 182 resources**. This is a selection for useful technical variety, not a performance ranking.

## Fixed evidence

Discovery source: [Decision Index snapshot](https://huggingface.co/spaces/multimodalart/jev-decision-index/raw/0ddf6758073eb77ae449a3541f57286d7f39d93f/data/index.json), generated 16 October 2026; inspected 18 October. Commit `0ddf6758073eb77ae449a3541f57286d7f39d93f`, SHA-256 `23496572ce8da74277208b5796060331b366b015a800f281e7df21960a9ef609`. Its 173 evaluated rows are not 173 independent families: revisions, sizes, serving modes and closed entries can be separate rows.

| Model card | Fixed commit | README SHA-256 | Declared release license |
| --- | --- | --- | --- |
| [OneJev1.5-27B](https://huggingface.co/OmniJev/OneJev1.5-27B/raw/0742f8d16dd42c97643eec095cfc252acc4db18f/README.md) | `0742f8d16dd42c97643eec095cfc252acc4db18f` | `bee8403b483efa2b282c94a29910d88588637e49ed5c796fa52971e334f0b753` | Apache-2.0 |
| [d1-omni-600M](https://huggingface.co/LiquidAI/d1-omni-600M/raw/02b55d7076f15129e59ab3f94783f32c4b088674/README.md) | `02b55d7076f15129e59ab3f94783f32c4b088674` | `6577bee7b8cb23b595a90e99aa82007f57214d447f0ebcdfb2e812a7123d57bf` | LFM Open License v1.0 |
| [Torchcast Decision 27B](https://huggingface.co/torchcast-ai/torchcast-decision-27b/raw/08645834899cb8e00d370b77a3f4e0baa3241dd1/README.md) | `08645834899cb8e00d370b77a3f4e0baa3241dd1` | `5ee1fa39ef6243d33e56ba20f2d88e4537720341caa6beec639f4269924e8081` | CC BY-NC 4.0 |
| [tasksource-decider-nano](https://huggingface.co/tasksource/tasksource-decider-nano/raw/46e88e08cc1a3122a348ce134f18865e93f8e1c8/README.md) | `46e88e08cc1a3122a348ce134f18865e93f8e1c8` | `2f9b6cae9e67a0f30a4c37c24f73944c7ceeba008c9de2c5163ba56d9cc69ef0` | Apache-2.0 |
| [Saracura PT-BR 4B](https://huggingface.co/felhen-ai/saracura-ptbr-4b/raw/9b27a7be153afee62b778b61eb5d664ce978d3b1/README.md) | `9b27a7be153afee62b778b61eb5d664ce978d3b1` | `6087eac0488cc8f4e236bb7037b1be66623c6f76e529acddb9847e1631982d33` | Apache-2.0 |
| [Perplexity Decider v1.2 27B](https://huggingface.co/perplexity-ai/pplx-decider-v1.2/raw/225c913ddc8761a8264f04f64548e1f97e443eb3/README.md) | `225c913ddc8761a8264f04f64548e1f97e443eb3` | `a5cb0c340a376543344571e28c335fa030b915699c9cd0a77959b1222944dace` | Apache-2.0 |

These six fixed model cards were read along with anonymous Hub metadata and file inventories. Current anonymous metadata was also checked for all 15 previously curated repositories. Jeva-4B still has no declared license in its inspected card or metadata at `50078fcff42bd63717105dc20bd4e55eccf8c83d`; README SHA-256 `82fa0fdc2d185a86d98f44da320d4c93ba8a5739f95f3f7704665ce80e0d31cd`. A metadata/card check does not establish correctness of every listed file.

## Scope notes

| Release | What the directory distinguishes |
| --- | --- |
| OneJev1.5-27B | 27B full fine-tune for text, image and video decisions, served through qev. Training includes public benchmark training splits; reported scores cover the public suite, and Jev comparison numbers are imported rather than a matched multimodal rerun. |
| d1-omni-600M | 587M encoder for text with images or up to 30 seconds of English speech; one request cannot mix both media. Only text uses fitted temperatures. Image requests cap text at 896 tokens; custom code and the LFM Open License apply. |
| Torchcast Decision 27B | Merged LoRA decision model with a CUDA serving package; weights are noncommercial, serving code Apache-2.0. Text-only, checkpoint-selected results use Decision Index 0.2.1; long states and more than 26 options change the inference path. |
| tasksource-decider-nano | 150M joint cross-encoder with shared-state tree attention and choice/noul outputs. Rejects pairs above 8,192 tokens; training includes public benchmark training splits. Reported speed and public-suite scores use the documented A10 setup. |
| Saracura PT-BR 4B | Brazilian Portuguese Kev adapter and pointer head. Source-matched tests and two-fold human-set calibration do not establish general Portuguese performance; private email-tuned results belong to an unreleased model. Use the documented 2,048-token state setting for comparisons. |
| Perplexity Decider v1.2 27B | 27B text/image model with joint question readouts: questions can affect one another. Public-suite training exposure and grouping affect comparisons. Anonymous Hub metadata and a weight HEAD were accessible on 18 Oct; the card still instructs private access. |

The guide explains how question grouping changes the inference protocol and how input limits and calibration differ by modality. Scores remain publisher-reported; no training run, decontamination audit, inference test or calibration reproduction was performed. Model cards can describe historical board snapshots even when the current index later includes the model.

## Access and licensing evidence

Anonymous metadata for the six reviewed releases reported `private=false` and `gated=false`. For each, one fixed-revision `.safetensors` or adapter URL returned HTTP 302 to an unauthenticated **HEAD** request on 18 October. Redirects were not followed, signed destination URLs were not retained, and no weight bodies were downloaded. This confirms an initial download response, not the integrity or complete availability of all shards. Saracura lists an adapter; it is not represented as a standalone full checkpoint.

Perplexity’s inspected README still instructs authentication to a private repository, conflicting with the observed public/ungated metadata and initial weight response. Both observations are retained instead of silently treating the README instruction or metadata as definitive. Its new joint request format also differs from v1.1; questions within a request may interact while separate requests remain isolated in the documented fast path.

The following license documents were inspected at the same revisions as their cards:

- [d1-omni-600M: LICENSE](https://huggingface.co/LiquidAI/d1-omni-600M/raw/02b55d7076f15129e59ab3f94783f32c4b088674/LICENSE), SHA-256 `9953509cbd8c1c6ce7b06ddf74fcc204a892692316201dd8f7400a84790d4120`.
- [Torchcast Decision 27B: LICENSE](https://huggingface.co/torchcast-ai/torchcast-decision-27b/raw/08645834899cb8e00d370b77a3f4e0baa3241dd1/LICENSE), SHA-256 `00a51d1af14594a85bf6e63789418358aa1473c4234af05444d389898cf95637`.
- [Perplexity Decider v1.2 27B: LICENSE](https://huggingface.co/perplexity-ai/pplx-decider-v1.2/raw/225c913ddc8761a8264f04f64548e1f97e443eb3/LICENSE), SHA-256 `bbedc3fda3305820b977265f01b8619d87570a6739de3a5582c3464840f1e57a`.

Liquid’s release declares the custom LFM Open License v1.0, including a commercial-use limitation; it is placed in the directory’s **Other / see card** filter. Torchcast’s weights and serving code have different declared licenses. Other rows use their inspected card declarations; no broader legal permission is inferred.

The index-linked Surogate Rune GGUF repository could not be retrieved anonymously in this review. It is not promoted from its existing metadata-only record, and no absence-of-weights claim is made.

## Counting and privacy

The five promotions already exist in the accepted source ledger, and each fresh fixed README hash matches its original record. Display annotations refine their scope without changing evidence grades or historical fields. Perplexity v1.2 adds one separate version record; v1.1 remains in source history, and the v1.2 replacement receives **zero expansion credit**. The accepted expansion count remains **801**. No sibling sizes, model files, license files or repeated snapshots count as additional families.

The frozen baseline and all previous accepted ledger bytes remain intact. Public identifiers, source URLs and document fingerprints support this review; personal paths, account details, contact addresses, raw card bodies, credential material, downloaded weights and private data are not published.

**中文：** 本轮将五条既有来源提升为精选模型，并用 Perplexity v1.2 替换精选目录中的 v1.1，共 20 项模型、182 项精选资源；扩展计数仍为 801。核查仅涉及公开模型卡、许可、元数据、目录及不跟随跳转的 HEAD 请求，未下载或运行权重。保留私有访问说明与匿名观测的矛盾，明确适配器、不同模态校准、问题分组及评测范围。

## Validation

All 457 repository tests passed. Generated-output, link/provenance, publication-hygiene and expansion checks agree on 20 models, 182 curated resources, 95 papers and 801 reviewed expansion sources. Existing accepted ledger bytes and frozen baseline files are preserved. Browser checks confirmed the custom-license filter returns Liquid d1, the noncommercial filter returns three models, filters survive the English/Chinese switch, and Chinese search finds Saracura. At 390 px, the Chinese directory has no horizontal overflow and the complete model note remains readable.

## Publication and discovery receipts

Commit `04bc15a0010f6073432d5f9592d90d23889f2c5c` passed [main repository checks](https://github.com/reacher-z/Awesome-Jev/actions/runs/39112062389), [website repository checks](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39112064665) and [Pages deployment](https://github.com/AwesomeJev/AwesomeJev.github.io/actions/runs/39112064666). Both repositories remain public. All 40 live targets matched that commit, including 20-model JSON, bilingual static model pages, source annotations and the updated guide. The live browser shows 20 models and the v1.2 Perplexity link.

One IndexNow submission for the six changed home, model-directory and guide pages (English/Chinese pairs) returned HTTP 200. The unchanged paper, topic and discovery pages were not resubmitted.

Google Search Console reported `https://awesomejev.github.io/models/` as **not indexed: URL is unknown to Google**. After the new release, one indexing request passed its live check and received **Indexing requested**, confirming admission to a priority crawl queue. The page still showed the earlier unindexed status after dismissal. This is a submission receipt, not proof of indexing, ranking or AI retrieval. The already-requested paper and guide pages were not submitted again. Console screenshots and account state remain outside the repository.
