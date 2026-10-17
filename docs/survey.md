# Jev and typed decision models

**A compact research survey · Evidence snapshot: 17 October 2026 (UTC)**

[English](survey.md) · [简体中文](survey.zh-CN.md) · [Resource index](../README.md) · [BibTeX](../references.bib)

Jev makes an interesting research question concrete: what changes when a model returns a decision that software can consume directly? This survey separates the interface, the evidence about a hosted model, and the systems that use its answers. It is a curated starting point, not an exhaustive review. We have checked sources, but have not reproduced their experiments.

## 1. The decision interface

TypeSafe introduced Jev on **15 September 2026**, describing a model architecture, parallel sampler, and Reinforcement Learning for Calibrated Decisions (RLCD). These are vendor descriptions; the launch article does not disclose enough to reconstruct the training method or architecture. “System One” is the product’s framing, not a demonstrated correspondence with human cognition. [Launch article](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

A request pairs shared state with questions and caller-defined criteria. **Choice** returns an option and its distribution; **Score** returns an assessment over ordered rubric levels; **Noul** returns a yes-probability. The surrounding program determines how those answers affect routing, review, or execution. This puts the decision contract, its alternatives, and uncertainty directly in the application. [Question primitives](https://docs.typesafe.ai/primitives)

Version boundaries matter. On this snapshot, `jev-latest` resolves to stable **1.13.0**; `jev-preview` resolves to **1.14.0**, released **14 October**. Log the returned model ID and pin versions for comparisons. The studies below mainly concern 1.13; they cannot establish 1.14 performance. [Models](https://docs.typesafe.ai/models)

The current interface is also broader than the original text-oriented evaluations: images require explicit experimental opt-in, and **Box** localization requires 1.14. These capabilities need their own evidence. [Images](https://docs.typesafe.ai/images) · [Box](https://docs.typesafe.ai/primitives/box)

## 2. Reading the evidence

Different sources answer different questions:

| Evidence | What it can establish | What remains separate |
| --- | --- | --- |
| Official documentation | Supported contracts, version names, operational limits | Measured reliability on a new workload |
| Vendor evaluations | Performance under the vendor’s published design | Generalization beyond its references and tasks |
| External empirical papers | Observations under specified prompts, data, and comparators | Our own reproduction; causal explanations of internals |
| Surveys and open implementations | Research connections and inspectable alternative designs | Proof that Jev uses the same mechanisms |

Official **WorkflowEvals** now has public [workflow code](https://github.com/typesafe-ai/WorkflowEvals) and a [dataset collection](https://huggingface.co/collections/typesafeAI/workflowevals). Its references use model consensus, so agreement with them measures agreement with that reference procedure. Human-label accuracy is a different claim. Public artifacts make inspection possible; availability alone does not certify a result. [Evaluation design](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

The community [**Jev Decision Index**](https://huggingface.co/spaces/multimodalart/jev-decision-index) is a central discovery resource for benchmarks and independent Jev-inspired implementations, not TypeSafe weights. Edition **0.3.2**, inspected at commit `0ddf675`, combines public and unreleased private tests. The current reference is a Jev 1.14 lab run dated 14 October; the frozen request files still name Jev 1.13. Its full ranking therefore cannot be independently recomputed from public material alone, and model-run provenance must be kept separate from archived request labels. [Versioned methodology](https://huggingface.co/spaces/multimodalart/jev-decision-index/blob/0ddf6758073eb77ae449a3541f57286d7f39d93f/data/methodology.json)

The six selected works below are **arXiv preprints**. Dates distinguish first publication from the version reviewed. Findings are author-reported; the audit paper maps evidence rather than adding another empirical replication.

| Work and reviewed version | Method, finding, and limitation |
| --- | --- |
| [Deußer et al. — broad benchmark](https://arxiv.org/abs/2609.37647v1) · 29 Sep · v1 | Tests 37 datasets against label-probability baselines; reports useful Choice calibration and task-dependent Noul thresholds. Single prompts, disabled baseline reasoning, and possible contamination limit interpretation. |
| [Tang & Zheng — evidence audit](https://arxiv.org/abs/2609.32160v1) · 26 Sep · v1 | Audits 28 early papers and proposes an evaluation checklist. Evidence does not isolate a general accuracy gain from typed readout; the corpus is an early snapshot. |
| [Li et al. — adversarial comparison](https://arxiv.org/abs/2610.17820v1) · 13 Oct · v1 | Compares judges under matched attacks across four tasks; robustness varies by task. English, single-turn experiments and one phishing corpus constrain generalization. |
| [Denney & DiGiuseppe — political science](https://arxiv.org/abs/2610.06625v2) · 5 Oct → 6 Oct · v2 | Replicates seven studies; accuracy is often competitive, while calibration and cost advantages depend on baselines. Historical comparisons and reconstructed prompts need separate interpretation. |
| [Li et al. — JEV-as-a-Judge](https://arxiv.org/abs/2609.26550v5) · 22 Sep → 9 Oct · v5 | Tests confidence-based escalation with frozen policies; some workloads support cheaper judging at comparable accuracy. Reference-free prose, adversarial style, and limited adjudication qualify the result. |
| [Rao & Callison-Burch — rubric judges](https://arxiv.org/abs/2609.29769v3) · 24 Sep → 13 Oct · v3 | Compares Jev, Decider, and LLM judges across nine panels; correlated errors restrict cascade gains. Default configurations and partly exploratory analyses leave room for different outcomes. |

These are different estimands, not entries in one leaderboard. A classification score, agreement with a rubric, resistance to a particular attack, and savings from a cascade should not be averaged into “Jev quality.”

## 3. Valid output, correct decision, useful uncertainty

**Schema validity** asks whether an answer belongs to the declared output space. **Accuracy** asks whether the selected answer is correct under the task’s labels. **Calibration** asks whether predicted probabilities match observed frequencies. A valid answer can be wrong; a calibrated model can still be insufficiently accurate for a particular decision.

TypeSafe’s Choice `confidence` is a derived statistic:

```text
confidence = (p_max − 1/n) / (1 − 1/n)
```

Here `n` is the number of options. It is not the selected option’s probability: with four options, `p_max = 0.7` gives confidence `0.6`. Noul has no separate returned confidence. Consequently, a confidence threshold is not automatically a promised accuracy. [Confidence documentation](https://docs.typesafe.ai/confidence)

For a policy that abstains, **coverage** is the fraction of cases accepted; **selective risk** is the average loss on those cases. Plotting risk against coverage exposes the tradeoff hidden by one threshold. A fallback must also correct the first model’s mistakes: confidence ranking alone cannot guarantee a good cascade. The reject-option literature supplies the relevant framework. [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html)

Three recent studies sharpen different parts of this distinction. These are interpretations of the inspected abstracts, not reproduced experiments.

| Study | Distinction to retain |
| --- | --- |
| [Labels Override Definitions, v1](https://arxiv.org/abs/2610.02586v1) | Changing prompt rendering with fixed weights probes an interface mechanism; label sensitivity alone does not identify a decision-head limitation. |
| [GraphDecisionBench, v3](https://arxiv.org/abs/2610.06354v3) | Recognizing local edges, combining graph and text evidence, and constructing a high-quality solution require separate measurements. |
| [AudioJev, v1](https://arxiv.org/abs/2610.01293v1) | Stability under option permutations is different from agreement between probabilities and observed correctness. |

## 4. Connections worth studying

**Probabilistic prediction.** Proper scoring rules evaluate whole predictive distributions, providing a foundation for Brier score and log loss. Calibration work shows why a highly accurate network still needs probability evaluation; language-model self-evaluation adds a relevant comparator. None establishes Jev’s training objective. [Gneiting & Raftery](https://doi.org/10.1198/016214506000001437) · [Guo et al.](https://proceedings.mlr.press/v70/guo17a.html) · [Kadavath et al.](https://arxiv.org/abs/2207.05221)

**Constrained generation.** LMQL and XGrammar show how generative systems can impose output constraints. They motivate comparisons that distinguish a typed API from the model producing its answers. [LMQL](https://www.sri.inf.ethz.ch/publications/beurerkellner2023prompting) · [XGrammar](https://arxiv.org/abs/2411.15100)

**Programmable inference.** DSPy studies optimization of model pipelines; SGLang studies their efficient execution. Both motivate controlling orchestration, caching, and serving conditions before attributing end-to-end improvements to one decision model. [DSPy](https://arxiv.org/abs/2310.03714) · [SGLang](https://papers.nips.cc/paper_files/paper/2024/file/724be4472168f31ba1c9ac630f15dec8-Paper-Conference.pdf)

## 5. A proposed reproducible evaluation

**This is a research protocol, not an experiment executed by this project.**

1. **Define the decision.** Specify labels, ambiguity rules, error costs, and the acceptable human-review load. Separate human judgments, programmatically verifiable answers, and model-consensus references.
2. **Freeze the comparison.** Pin model versions, datasets, prompts, option descriptions, and preprocessing. Include label-logprob, constrained-generation, and task-specialist baselines where available. Report reasoning settings and unequal capabilities explicitly.
3. **Separate development from testing.** Select prompts, calibrators, and routing thresholds on development data. Preserve a held-out test set; group related examples to prevent leakage. Repeat a sample to measure response variability.
4. **Measure decisions and probabilities.** Report task-appropriate accuracy or F1, Brier score, log loss, calibration plots, and risk–coverage curves with uncertainty intervals. Break results down by language, label frequency, and task difficulty.
5. **Test the surrounding system.** Separate batch throughput, successful-call latency and success-conditioned workflow cost. State every denominator and exclusion; retain attempts, retries, completion/validity rates, all-attempt spend and fallback accuracy, alongside region, concurrency, cache state and price date. Evaluate attacks and input perturbations separately.
6. **Publish the trail.** State whether you regenerate tables or figures from scored summaries, recompute metrics from released per-example answers, obtain fresh predictions, or retrain a checkpoint. Release permitted inputs, versioned templates, raw responses, manifests and analysis scripts. Repeat after version changes before reusing thresholds.

### Compare supervision, readout and language conditions

A useful comparison names what information and computation each system receives. These three fixed-version studies illustrate supervision, readout and language conditions. Only their fixed-version original abstracts and metadata were checked; the right-hand column is a proposed comparison protocol, not an account of experiments reproduced here.

| Comparison axis | What the fixed abstract reports | Proposed matched check |
| --- | --- | --- |
| **Task-label access** | The abstract compares typed decision models, generative readouts and classifiers under a common request harness. It reports strong trained-classifier results when task labels are available, with different trade-offs when task-specific labels are unavailable. [v2](https://arxiv.org/abs/2610.00346v2) | Separate settings with and without task-specific training labels. Record training-label access, dataset exposure, splits, prompt/output contracts and format failures before comparing accuracy, selective coverage or cost. |
| **Readout, fine-tuning and reasoning** | The abstract evaluates frozen decision recipes and KL-anchored fine-tuning on Qwen3.5-4B and Qwen3-0.6B, with budgeted reasoning as another intervention. It describes an independent framework and does not disclose hosted Jev’s architecture. [v3](https://arxiv.org/abs/2610.02076v3) | Use a frozen comparator with the same backbone and keep option sets, data split and reasoning budget explicit. Attribute changes to readout, training or extra inference only where matched comparisons isolate them; report general-generation checks separately. |
| **Language and reference-label provenance** | HakemBench reports Turkish decision, probability and risk–coverage metrics plus perturbation probes. Its abstract explicitly identifies mostly AI-derived labels and test-informed training of the lab’s own model on flagged tracks. [v1](https://arxiv.org/abs/2610.02293v1) | Show metric components and per-track results, reference-label provenance and prior test exposure. Keep translation probes separate from independent validation in another language; disclose any tracks influenced by earlier test feedback and evaluate untouched data before claiming transfer. |

Keep these axes separate: a classifier trained on task labels, a frozen readout with additional reasoning, and a benchmark for a particular language with model-generated references answer different questions. These reported measures do not form one general capability ranking. A claimed risk bound requires its own protocol and assumptions; the abstract alone does not validate it for deployment.

### Attack success and repeated calls

These fixed-version studies define different endpoints and denominators. Compare those definitions and repeat controls before comparing reported rates; the examples below are author-reported, not a cross-paper ranking or our reproduced results.

| Study | Endpoint and denominator | Repeat control and reported example |
| --- | --- | --- |
| **JevAdvBench, v1** | Flip rate counts Noul crossing 0.5, Choice changing option, or Score changing its most-likely level—not every change in the expected score. It measures change from the same question’s clean decision, not necessarily a label error or target hit. | An identical clean re-run provides a paired baseline, with scenario-cluster intervals for the excess. The authors report 12.1% flips for observer opinion versus 1.0% on re-run. Most labels are model-derived and the benchmark conditions on clean stability; this is not a population error rate. [protocol](https://arxiv.org/html/2609.31142v1#S3.SS3) · [label scope](https://arxiv.org/html/2609.31142v1#S3.SS1.p2.1) · [result](https://arxiv.org/html/2609.31142v1#S4.SS2.p3.1) |
| **Decision Hijacking, v1** | Targeted attack success rate (ASR) averages target-selection frequency over cases qualified by safe clean decisions and target eligibility. Call-level ASR differs from any-action flips and case-level majority success. | Repeated conditions are interleaved; adaptive candidates are frozen before five fresh validation calls, requiring at least three target selections. The unmodified attacker-request condition has 51 / 2,550 target-selecting calls (2.0%) but 11 / 510 majority-success cases. Neither measure establishes completed harmful workflows or guaranteed future success. [definitions](https://arxiv.org/html/2609.28613v1#S3.SS2) · [fresh validation](https://arxiv.org/html/2609.28613v1#S4.SS4) · [call/case counts](https://arxiv.org/html/2609.28613v1#A1.SS4.p2.1) |
| **Same Attack, Different Judge, v1** | ASR counts pass-after-attack among malicious cases each judge flagged when clean, so denominators can differ. Separate Jev-only gate bypass requires a less restrictive action and severity-Score confidence ≥0.7; review can qualify, while low-confidence pass need not. | Clean moderation and phishing cases receive two additional unchanged calls. The control compares routed actions: Jev’s raw severity changes on 75% of repeated moderation calls, but its routed action on 1%. A pass is a routing result, not observed downstream harm. [metrics](https://arxiv.org/html/2610.17820v1#S4.SS5) · [repeat protocol](https://arxiv.org/html/2610.17820v1#S5.SS2) · [raw vs routed](https://arxiv.org/html/2610.17820v1#A2) |

For a new evaluation, freeze case eligibility, editable fields, decision rules, targets, thresholds and query budgets; keep search calls separate from fresh validation. Check that edits preserve the intended answer and reach the model. Equal token counts alone do not prove non-delivery. Compare matched unchanged calls with uncertainty; exceeding a repeat baseline is not by itself causal proof of harm. [Delivery caveat](https://arxiv.org/html/2609.31142v1#S3.SS3.p3.1)

### Efficiency denominators

These fixed-version studies use different accounting scopes. The table compares their denominators, not model rankings. The recording fields are a proposed evaluation protocol. Only selected methods/results passages and table notes were inspected; no full-paper review or experiments were performed.

| Reported quantity | Denominator and limits | Suggested recording fields |
| --- | --- | --- |
| **Visual Jev, v1 — Warm amortized batch execution** | Warm group completion time / N co-available questions about one image; N / group time gives throughput. The reported 5.7 ms at N=32 corresponds to about 182 ms for the group. Includes tokenization, transfers and model execution; excludes decoding the image, building records, disk, network and queues. This is not independent-request latency. [timing scope](https://arxiv.org/html/2609.25845v1#S4.SS0.SSS0.Px4.p1) · [Table 3](https://arxiv.org/html/2609.25845v1#S5.T3) · [batch completion](https://arxiv.org/html/2609.25845v1#S5.SS2.SSS0.Px2.p1) | Group/image ID, N, batch/reuse mode, warm-ups and repetitions, synchronized start/end, hardware/precision, peak memory; record queue delay separately. |
| **Agent Trace Security, v1 — Successful-call latency and valid-judgment cost** | Latency statistics use available successful single calls; USD/valid averages recorded token charges for valid judgments. Timed and valid sample counts are separate. Latency excludes failed attempts, repairs and retry waiting. Cost excludes failed requests but includes logged repair tokens attached to valid results and reasoning-token usage; prices are configured estimates. [coverage definition](https://arxiv.org/html/2609.34862v1#S4.SS3.p1) · [timing scope](https://arxiv.org/html/2609.34862v1#S4.SS4.p1) · [Table 4](https://arxiv.org/html/2609.34862v1#S5.T4) · [cost accounting](https://arxiv.org/html/2609.34862v1#A3.p1) | Trace ID, attempted/valid/timed counts, validity and failure reason, call/repair/retry times, input/output/reasoning usage, repair attribution, price configuration and coverage. |
| **Jev-Mobile, v1 — Efficiency conditional on successful trajectories** | Time and mean all-model API cost average only successful episodes. Executor cost is instead a sum over that successful cohort; success rate uses all evaluated tasks. Successful-episode wall time includes planning, execution, device interaction, waits and retries; executor time isolates action-model APIs. Failed episodes are outside those efficiency summaries, and systems may succeed on different tasks. [time accounting](https://arxiv.org/html/2609.30186v1#S5.SS2.p1) · [cost accounting](https://arxiv.org/html/2609.30186v1#S5.SS2.p2) · [Table 1](https://arxiv.org/html/2609.30186v1#S6.T1) · [limitations](https://arxiv.org/html/2609.30186v1#S8.p1) | Task/episode ID, terminal success, attempted/successful counts, stage times, all model-role charges, waits/retries and task budget; retain successful IDs to support matched comparisons. |

For deployment budgeting, separately report total model charges across all attempted episodes divided by the number of successful episodes; report it as undefined when there are no successes. This proposed measure includes failed-episode spend and differs from Jev-Mobile’s successful-cohort average. Always retain success/coverage rates beside conditional efficiency.

### Reproduction boundaries

The four operations named in step 6 of the protocol above cover different pipeline stages. The examples below describe documented availability in the inspected snapshots; we did not execute the procedures or exhaustively audit the artifacts.

- Name the target: a specific table or figure regenerated from scored summaries, metrics recomputed from released per-example answers, fresh predictions, or a retrained checkpoint.
- Map the target to required inputs and their versions/hashes. Distinguish files present from files merely documented, upstream restricted material, and missing artifacts. Use a body hash plus retrieval time where a provider revision is not an immutable commit.
- List dependencies separately: analysis environment; source data and reconstruction rules; model/adapter versions or hosted-service access; compute and charges. Preserve failed hash checks and missing inputs instead of silently replacing them with current data.
- Report the actual outcome: documented only, inputs inspected, command executed, or outputs matched. For executed work, retain commands, environment, output hashes and deviations; partial table regeneration is not a reproduced inference or training run.

| Example | Documented analysis route | What remains separate |
| --- | --- | --- |
| [Visual Jev](https://github.com/guanxuyu-sv/Visual-Jev/blob/a392eaedfa41adae348f9767b55c0f54b3a13b57/REPRODUCE.md) | Committed scored JSON supports specified tables and two result plots without a GPU. | Other figures need omitted per-example predictions and intervention analyses. Fresh predictions need upstream corpora, backbone weights and a GPU; source images are not redistributed. |
| [Ordinal-scale artifact](https://anonymous.4open.science/api/repo/jev_ordinal_scale_bia/file/README.md?v=3ed72968) | The described analysis route recomputes metrics from released per-example answers, not new model calls. | Source text, weights and post-trained checkpoints are omitted. Missing historical revisions can prevent reconstruction of inputs matching the recorded hashes; hosted results may change. The provider file revision is opaque, not a verified immutable commit. |
| [Radiology report judging, v1](https://arxiv.org/html/2609.27607v1#Sx1.p1) | The fixed-v1 availability statement says analysis scripts and aggregates are being prepared for release. | Third-party dataset links and question details do not supply those missing author outputs. The inspected version does not establish an available analysis-replay route. |

The most useful next evidence would isolate model, interface, and workflow effects while tracking deployment shift. That requires matched comparisons and inspectable records, especially for new modalities and releases. The collection’s 87 research bibliography entries are maintained in [references.bib](../references.bib).
