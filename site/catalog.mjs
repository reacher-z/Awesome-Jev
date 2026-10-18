const translations = {
  en: {
    skip: "Skip to the collection",
    navLabel: "Main navigation",
    homeLabel: "AwesomeJev home",
    navIndex: "Resources",
    navStart: "Get started",
    metaDescription:
      "Explore Jev and System One decision models through research papers, benchmarks, models and tools, with primary sources and English–Chinese guides.",
    socialImageAlt:
      "AwesomeJev — an independent field guide to typed decision models. Research, models, tools, and evidence.",
    heroLine1: "Awesome Jev",
    heroLine2: "by design.",
    heroDescription:
      "Research, models and tools for Jev and System One decision models.",
    explore: "Explore the collection",
    figureInput: "“I was charged twice.<br>Could you help?”",
    figureCaption: "Illustrative output. Not a live call or a benchmark.",
    figureAria:
      "Illustrative probabilities: billing 84 percent, technical 11 percent, other 5 percent",
    pathsLabel: "Reading paths",
    pathResearch: "Read the research",
    pathResearchSub: "Early evidence, open questions",
    pathBuild: "Build with intention",
    pathBuildSub: "SDKs, patterns, working examples",
    pathEvaluate: "Inspect the evidence",
    pathEvaluateSub: "Methods, datasets, reproducibility",
    versionNote:
      "Stable: Jev 1.13 · Preview: Jev 1.14.",
    modelNotes: "Model notes ↗",
    collectionTitle: "Resource index",
    collectionIntro:
      "Filter by type or search titles and descriptions.",
    filterLabel: "Filter resources",
    filterAll: "All",
    filterPapers: "Papers",
    filterModels: "Models",
    filterTools: "Tools",
    filterDatasets: "Datasets",
    filterGuides: "Guides",
    filterEvaluations: "Evaluations",
    filterFoundations: "Foundations",
    filterHasCode: "Papers with code",
    artifactCode: "Code",
    artifactData: "Data",
    artifactModel: "Model",
    artifactDemo: "Demo",
    artifactPage: "Project page",
    artifactFor: (label, title) => `${label} for ${title}`,
    artifactUnverified: (label) => `${label} not verified`,
    searchLabel: "Search resources",
    searchPlaceholder: "Find something useful…",
    emptyTitle: "No matches, yet.",
    emptyDescription: "Try a broader term, or explore the full collection.",
    resetFilters: "Clear search & filters",
    editorialNote:
      "Preprints report their authors’ findings; listing is not independent validation. Foundations provide context, not evidence of Jev’s internal architecture.",
    startTitle: "One call.<br><em>Typed decisions.</em>",
    startDescription:
      "Give Jev the context and a bounded question. Keep the next action in your code.",
    fullQuickstart: "Read the official quickstart",
    startFootnote:
      "Requires your own API key. This page makes no model calls. Confidence is a routing signal, not a correctness guarantee.",
    copyCode: "Copy code",
    copied: "Copied",
    copyFailed: "Select code to copy",
    keyNote: "Set TYPESAFE_API_KEY in your environment, then run:",
    contributeTitle: "Good work belongs here.",
    contributeDescription:
      "Found a thoughtful paper, a useful tool, or a result worth reproducing? Help make the collection better.",
    contributeLink: "Contribute on GitHub",
    affiliation: "Independent project. Not affiliated with TypeSafe AI.",
    lastCurated: "Last curated",
    backTop: "Back to top",
    sourceLink: "Website source",
    // Evidence markers: who published a source, then how far its claims were checked here.
    // docs/source-audit.md#evidence-markers defines the same terms.
    sourceOfficial: "Official",
    sourcePreprint: "Preprint",
    sourceCommunity: "Community",
    sourceBackground: "Background",
    evidenceAuthorReported: "author-reported",
    evidenceScreened: "screened",
    evidenceReproduced: "reproduced",
    evidenceAuthorReportedNote: "not re-run here",
    evidenceScreenedNote: "page checked",
    evidenceReproducedNote: "none so far",
    evidenceLegendLabel: "Evidence markers",
    evidenceSeparator: ": ",
    evidenceMethod: "How we check",
    readFurther: "Project links",
    readmeLink: "README",
    surveyLink: "Research guide",
    bibtexLink: "BibTeX",
    modelEvidence:
      "Model capabilities and licenses follow publisher cards. API compatibility does not establish equivalent behavior or accuracy.",
    // Announced by the #result-count live region: plain words, no padding or capitals.
    resourceCount: (n, total) =>
      n ? `${n} of ${total} resources` : "No resources match",
    indexTitle: "Decision Index",
    indexDescription:
      "Explore decision models and community evaluations, including open Jev-inspired alternatives.",
    indexLink: "Open the Decision Index",
    indexCaveat:
      "Community-maintained. Full scores include private tests; public materials do not reproduce the entire ranking.",
    corpusTitle: "Follow the connections.",
    corpusIntro:
      "Mixed screening levels: editorial review, automated content screening, abstract checks, and metadata-only discovery. Inspect each entry’s label; inclusion is a research lead, not an endorsement.",
    corpusAudit: "Screening methodology",
    metadataCorrection: "Metadata checked against the primary source",
    primaryMetadata: "View the source used for this correction",
    verificationDepth: "Verification depth",
    verificationHint: "How to read the labels",
    levelEditorial: "Editorially reviewed",
    levelContent: "Content screened",
    levelAbstract: "Abstract checked",
    levelMetadata: "Metadata only",
    editorialDefinition:
      "Focused editorial inspection of core Decision Index sources. This label does not imply experimental reproduction.",
    contentDefinition:
      "A public README, model card, or page passed automated relevance and substance checks. An arXiv landing page is an abstract, not a full-paper review.",
    abstractDefinition:
      "An abstract was checked on a versioned arXiv page, through Hugging Face Papers, or from OpenAlex metadata. Inspect the provider record: this tier is not full-paper review.",
    metadataDefinition:
      "A source was discovered, but its content check did not pass. These entries are excluded from the checked-source total.",
    sourceCount: (n) =>
      `${n.toLocaleString("en-US")} ${n === 1 ? "source" : "sources"}`,
    corpusAuditCounts: (checked, metadata) =>
      `${checked.toLocaleString("en-US")} checked · ${metadata.toLocaleString("en-US")} metadata-only`,
    corpusSummary: "Browse the research corpus",
    corpusSearch: "Search the research corpus",
    corpusPlaceholder: "Search titles, topics, or sources…",
    corpusLoading: "Loading the source index…",
    corpusLoadFailed: "The source index could not be loaded. Retry or open the source files below.",
    corpusRetry: "Retry loading",
    corpusJSON: "Open source index (JSON)",
    corpusLedger: "Browse source ledgers",
    corpusUnavailable: "The source index contains no available entries.",
    corpusEmpty: "No sources match this search.",
    corpusMore: "Show more sources",
    corpusCount: (n) => `${n.toLocaleString("en-US")} indexed sources`,
    corpusResults: (n, total) =>
      `${n.toLocaleString("en-US")} of ${total.toLocaleString("en-US")} sources`,
  },
  zh: {
    skip: "跳转至资源索引",
    navLabel: "主导航",
    homeLabel: "AwesomeJev 首页",
    navIndex: "资源索引",
    navStart: "开始使用",
    metaDescription:
      "探索 Jev 与 System One 决策模型的论文、基准、模型和工具，提供原始来源、中英文研究指南与证据局限。",
    socialImageAlt:
      "AwesomeJev：类型化决策模型的独立研究指南，汇集研究、模型、工具与证据。",
    heroLine1: "Awesome Jev",
    heroLine2: "始于设计。",
    heroDescription:
      "Jev 与 System One 决策模型的论文、模型和工具。",
    explore: "探索精选资源",
    figureInput: "“我被重复扣费了，<br>可以帮忙处理吗？”",
    figureCaption: "示意输出。并非实时调用或评测结果。",
    figureAria: "示意概率：账单问题 84%，技术问题 11%，其他 5%",
    pathsLabel: "阅读路径",
    pathResearch: "阅读研究",
    pathResearchSub: "早期证据与开放问题",
    pathBuild: "动手构建",
    pathBuildSub: "SDK、设计模式与代码示例",
    pathEvaluate: "检查证据",
    pathEvaluateSub: "方法、数据集与可复现性",
    versionNote:
      "稳定版：Jev 1.13 · 预览版：Jev 1.14。",
    modelNotes: "模型说明 ↗",
    collectionTitle: "资源索引",
    collectionIntro:
      "按类型筛选，或搜索标题与简介。",
    filterLabel: "筛选资源",
    filterAll: "全部",
    filterPapers: "论文",
    filterModels: "模型",
    filterTools: "工具",
    filterDatasets: "数据集",
    filterGuides: "指南",
    filterEvaluations: "评测",
    filterFoundations: "基础研究",
    filterHasCode: "有代码的论文",
    artifactCode: "代码",
    artifactData: "数据",
    artifactModel: "模型",
    artifactDemo: "演示",
    artifactPage: "项目页面",
    artifactFor: (label, title) => `${title} 的${label}`,
    artifactUnverified: (label) => `${label}未核验`,
    searchLabel: "搜索资源",
    searchPlaceholder: "搜索论文、工具或主题…",
    emptyTitle: "暂时没有匹配项。",
    emptyDescription: "试试更宽泛的关键词，或浏览完整资源库。",
    resetFilters: "清除搜索与筛选",
    editorialNote:
      "预印本呈现作者报告的结果，收录不代表我们已独立验证。基础文献提供研究背景，不代表 Jev 内部架构的证据。",
    startTitle: "一次调用。<br><em>类型化决策。</em>",
    startDescription: "给出上下文与边界清晰的问题。让代码决定下一步行动。",
    fullQuickstart: "阅读官方快速入门",
    startFootnote:
      "需要你自己的 API key。本页面不会调用模型。置信度用于路由判断，并不保证答案正确。",
    copyCode: "复制代码",
    copied: "已复制",
    copyFailed: "请选择代码后复制",
    keyNote: "先在环境变量中设置 TYPESAFE_API_KEY，然后运行：",
    contributeTitle: "让好工作被更多人看见。",
    contributeDescription:
      "发现了值得读的论文、实用的工具，或值得复现的结果？欢迎一起完善这份资源库。",
    contributeLink: "在 GitHub 上参与贡献",
    affiliation: "独立社区项目，与 TypeSafe AI 无隶属关系。",
    lastCurated: "最近整理",
    backTop: "返回顶部",
    sourceLink: "网站源码",
    sourceOfficial: "官方",
    sourcePreprint: "预印本",
    sourceCommunity: "社区",
    sourceBackground: "背景文献",
    evidenceAuthorReported: "作者报告",
    evidenceScreened: "已筛查",
    evidenceReproduced: "已复现",
    evidenceAuthorReportedNote: "本项目未重跑",
    evidenceScreenedNote: "已查页面内容",
    evidenceReproducedNote: "暂无",
    evidenceLegendLabel: "证据标记",
    evidenceSeparator: "：",
    evidenceMethod: "核查方法",
    readFurther: "项目链接",
    readmeLink: "项目说明",
    surveyLink: "研究指南",
    bibtexLink: "BibTeX 文献",
    modelEvidence:
      "模型能力和许可依据发布者模型卡。API 兼容并不证明行为或准确率等同。",
    resourceCount: (n, total) =>
      n ? `${total} 项资源中匹配 ${n} 项` : "没有匹配的资源",
    indexTitle: "Decision Index",
    indexDescription: "查看决策模型与社区评测，包括受 Jev 启发的开放模型。",
    indexLink: "打开 Decision Index",
    indexCaveat: "社区维护。完整分数包含私有测试，公开材料无法复现全部排名。",
    corpusTitle: "沿着线索，继续探索。",
    corpusIntro:
      "各来源核查深度不同：编辑审阅、自动内容筛查、摘要核查或仅元数据发现。请查看条目标注；收录代表研究线索，而非质量背书。",
    corpusAudit: "核查方法与范围",
    metadataCorrection: "元数据已按原始来源核对",
    primaryMetadata: "查看此次修正依据",
    verificationDepth: "核查深度",
    verificationHint: "如何理解来源标签",
    levelEditorial: "编辑审阅",
    levelContent: "内容筛查",
    levelAbstract: "摘要核查",
    levelMetadata: "仅元数据",
    editorialDefinition:
      "对 Decision Index 核心来源进行聚焦编辑审查，不代表已复现实验。",
    contentDefinition:
      "公开 README、模型卡或网页通过自动相关性与实质内容检查。arXiv 简介页仍只是摘要，不代表阅读全文。",
    abstractDefinition:
      "核查固定版本 arXiv 页的原始摘要、Hugging Face Papers 摘要，或 OpenAlex 重建摘要。具体途径见来源记录；此等级不代表全文评审。",
    metadataDefinition:
      "发现了来源，但内容检查未通过；这些条目不计入已核查来源总数。",
    sourceCount: (n) => `${n.toLocaleString("zh-CN")} 项来源`,
    corpusAuditCounts: (checked, metadata) =>
      `${checked.toLocaleString("zh-CN")} 项已核查 · ${metadata.toLocaleString("zh-CN")} 项仅元数据`,
    corpusSummary: "浏览研究来源库",
    corpusSearch: "搜索研究来源库",
    corpusPlaceholder: "搜索标题、主题或来源…",
    corpusLoading: "正在加载来源索引…",
    corpusLoadFailed: "来源索引加载失败。请重试，或打开下方原始文件。",
    corpusRetry: "重新加载",
    corpusJSON: "打开来源索引（JSON）",
    corpusLedger: "浏览来源记录",
    corpusUnavailable: "来源索引中暂无可用条目。",
    corpusEmpty: "没有匹配的来源。",
    corpusMore: "显示更多来源",
    corpusCount: (n) => `${n.toLocaleString("zh-CN")} 项索引来源`,
    corpusResults: (n, total) =>
      `${total.toLocaleString("zh-CN")} 项中匹配 ${n.toLocaleString("zh-CN")} 项`,
  },
};

// Descriptions are editorial summaries. Paper findings remain author-reported.
// `artifacts` repeats a paper's README Artifacts links by kind (code, data, model, demo, page);
// a link to code and data is listed under both, and `unverified` names a kind the README could not verify.
// Tool purposes describe reviewed project scope; multi-purpose projects occur once.
const toolTasks = [
  {
    "id": "integration",
    "en": "API integration",
    "zh": "API 接入"
  },
  {
    "id": "workflow",
    "en": "Workflow control",
    "zh": "工作流控制"
  },
  {
    "id": "runtime",
    "en": "Inference runtimes",
    "zh": "推理运行时"
  },
  {
    "id": "training",
    "en": "Training & evaluation",
    "zh": "训练与评测"
  }
];

const resources = [
  {
    "category": "Papers",
    "title": "Where Can a Decision Model Diagnose HVAC Faults? Reasoning Demand, Physical Representation, and Robustness Under Shift",
    "by": "Jung · 2026-10-07 · v1",
    "date": "2026-10-07",
    "first_submitted": "2026-10-07",
    "url": "https://arxiv.org/abs/2610.09937v1",
    "theme": "applications",
    "en": "Tests fault diagnosis across equipment, representations and operating shifts. Physical features enable selected diagnoses, while context-dependent faults remain difficult; shared-day training conditions, small fault-day counts and dataset-specific option sets limit general claims of robustness.",
    "zh": "跨设备、表示和运行变化测试故障诊断。物理特征支持部分诊断，但依赖运行上下文的故障仍困难；共享日条件、少量故障日与各数据集不同的选项集，限制通用鲁棒性结论。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "HydroJEV: A one-second, training-free screen for cyber-attack and fault attribution in water distribution networks",
    "by": "Mu et al. · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02048v1",
    "theme": "applications",
    "en": "Simulated water-network triage combines Jev, rule agreement and an LLM reviewer. Fewer reviewer calls coexist with accepted attacks, event-selection constraints and a transfer endpoint that misses multiplicity correction; reported timing and non-inferiority margins do not establish field reliability.",
    "zh": "仿真水网分诊结合 Jev、规则一致与语言模型复核。减少复核调用的同时仍会接纳部分攻击，受事件选择条件限制，且一个迁移端点未通过多重比较校正；所报耗时和非劣效界不证明现场可靠性。",
    "artifacts": {
      "code": "https://github.com/mutianwei521/hydrojev"
    },
    "artifact_note": {
      "en": "README and inventory checked; paper/script round numbers differ and datasets remain separate.",
      "zh": "已查说明和目录；论文与脚本轮次编号不同，数据集另行取得。"
    }
  },
  {
    "category": "Papers",
    "title": "System One Models for Wireless Decision-Making:Applications and Performance Evaluation",
    "by": "Rahimi et al. · 2026-10-03 · v1",
    "date": "2026-10-03",
    "first_submitted": "2026-10-03",
    "url": "https://arxiv.org/abs/2610.04345v1",
    "theme": "applications",
    "en": "Compares bounded wireless action selection with LLMs and task-specific baselines. Lower successful-request latency trades off against decision quality; a separately reported orchestration study shows that faster interpretation need not improve end-to-end completion. Local and hosted timing boundaries differ.",
    "zh": "比较有限无线动作选择、语言模型与任务专用基线。较低的成功请求耗时需与决策质量权衡；另引的编排研究表明，更快解释不一定改善端到端完成率。本地与托管计时边界也不同。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Type-Safe Decision Frameworks for Agentic 5G Control: A Theory-Driven Testbed Characterization of Where They Can Be Applied",
    "by": "Kourtis & Xilouris · 2026-09-27 · v1",
    "date": "2026-09-27",
    "first_submitted": "2026-09-27",
    "url": "https://arxiv.org/abs/2609.33689v1",
    "theme": "applications",
    "en": "Maps typed frameworks to timing, label-budget and decision-schema conditions on a 5G testbed. Changed-question probes expose failures hidden by output validity and paraphrase stability; simulator labels, open RAN-loop scope and conditional risk assumptions constrain deployment conclusions.",
    "zh": "在 5G 测试床上按时限、标签预算和决策模式评估类型化框架。改变问题的探针揭示了输出合法性与改写稳定性掩盖的失效；仿真标签、未闭合的 RAN 回路及有条件风险假设限制部署结论。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "A First Glance at Jev for Network Traffic Classification: Accuracy, Processing Time, and Cost",
    "by": "Xu & Mei · 2026-09-30 · v1",
    "date": "2026-09-30",
    "first_submitted": "2026-09-30",
    "url": "https://arxiv.org/abs/2610.00376v1",
    "theme": "applications",
    "en": "Classifies ten application labels from early packet features over 26 later collection weeks. Labeled examples improve Jev but the tested tree ensembles remain more accurate; unequal supervision and service configurations prevent attributing the gap to architecture or intrinsic label efficiency.",
    "zh": "利用早期数据包特征，在后续 26 个采集周识别十类应用标签。带标签示例改善 Jev，但所测树集成仍更准确；监督预算和服务配置不同，不能把差距归因于架构或固有标签效率。",
    "artifacts": {
      "data": "https://arxiv.org/src/2610.00376v1/anc"
    },
    "artifact_note": {
      "en": "Figure/table aggregates only; not a full flow-level prediction archive.",
      "zh": "仅图表汇总数据，并非完整逐流预测归档。"
    }
  },
  {
    "category": "Papers",
    "title": "Jev-IDS: System One Models for Network Intrusion Detection",
    "by": "Severo, Quincozes & Dias · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.01079v1",
    "theme": "applications",
    "en": "Studies typed intrusion decisions, but v1 mixes configurations: its abstract and pinned code describe a 300-flow GPT-5.6 Luna pilot, while its body describes 2,000 flows and Gemini. These cohorts and comparators must remain separate; benchmark-withheld attack types are not operational zero-day validation.",
    "zh": "研究类型化入侵判断，但 v1 混用了配置：摘要和固定代码描述 300 条流、GPT-5.6 Luna 试验，正文却描述 2,000 条流与 Gemini。两组样本及对照必须分开；基准内留出的攻击类型不等于真实零日攻击验证。",
    "artifacts": {
      "code": "https://github.com/jev-sec/jev-ids/tree/286a310fea249a7b4a5a8c45377049e914f8b9c9"
    },
    "artifact_note": {
      "en": "v1 abstract/body mismatch; linked code is the paper-cited pilot revision.",
      "zh": "v1 摘要与正文配置不一致；链接指向论文引用的试验代码版本。"
    }
  },
  {
    "category": "Papers",
    "title": "Can Decision Models Understand Stance? Evaluating Jev Against General-Purpose LLMs",
    "by": "Li et al. · 2026-10-08 · v1",
    "date": "2026-10-08",
    "first_submitted": "2026-10-08",
    "url": "https://arxiv.org/abs/2610.11901v1",
    "theme": "applications",
    "en": "Compares Jev on English single-text stance and Chinese conversational stance. Support/opposition errors grow in the conversational task, but language, dataset and input structure change together; differing batching and prompt formats also limit a general language-capability ranking.",
    "zh": "比较 Jev 的英语单文本立场与中文对话立场识别；对话任务中支持／反对混淆更明显，但语言、数据集和输入结构同时变化，批处理及提示格式也不同，不能据此形成通用语言能力排名。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Benchmarking System One Models in Online Moderation",
    "by": "Mazzoni & Failla · 2026-10-06 · v1",
    "date": "2026-10-06",
    "first_submitted": "2026-10-06",
    "url": "https://arxiv.org/abs/2610.07953v1",
    "theme": "evaluation",
    "en": "Separates written rules, retrieved precedents and candidate restrictions across five moderation benchmarks. Retrieval can improve discrimination or merely change flagging rates; using labeled evaluation examples as precedents and representing media through generated captions limits deployment claims.",
    "zh": "在五个审核基准中区分书面规则、检索先例和候选限制。检索可改善区分能力，也可能只是改变被标记内容的比例；使用带标签评测样本作先例、用生成描述表示媒体，会限制部署结论。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "To Jev or Not? Evaluating the Accuracy and Efficiency of Structured Decision Models for Hate-Speech Moderation",
    "by": "Paschalides, Pallis & Dikaiakos · 2026-10-02 · v1",
    "date": "2026-10-02",
    "first_submitted": "2026-10-02",
    "url": "https://arxiv.org/abs/2610.03324v1",
    "theme": "evaluation",
    "en": "HATEDECIDE tests definitions and decomposed judgments across four English datasets. More explicit criteria change predictions without reliably improving annotation agreement; component outputs are not verified explanations, and diagnostic-set cost comparisons do not establish production moderation quality.",
    "zh": "HATEDECIDE 在四个英语数据集上测试定义与分解判断。更明确的标准会改变预测，却不稳定提高标注一致率；组件输出不是已核验的解释，诊断集成本比较也不能证明生产审核质量。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Emo-Jev: Probabilistic Reasoning for Emotion Classification with Jev",
    "by": "Zhang & Yu · 2026-09-27 · v1",
    "date": "2026-09-27",
    "first_submitted": "2026-09-27",
    "url": "https://arxiv.org/abs/2610.08829v1",
    "theme": "applications",
    "en": "Adds atomic-question decomposition or multiple judgment paths for eight text-classification benchmarks. Neither extension improves average macro-F1 over direct Jev in the reported setup; extra questions increase cost, and fixed aggregation rules do not establish calibrated uncertainty.",
    "zh": "在八个文本分类基准上加入原子问题分解或多条判断路径；所报设置中，两种扩展的平均宏 F1 均未超过直接 Jev。额外问题增加成本，固定聚合规则也不能证明不确定性已校准。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Decide, Don't Generate: Competitive Dimensional ABSA with Jev's Typed Decisions",
    "by": "Zhang et al. · 2026-09-28 · v1",
    "date": "2026-09-28",
    "first_submitted": "2026-09-28",
    "url": "https://arxiv.org/abs/2609.35293v1",
    "theme": "applications",
    "en": "Uses frozen Jev decisions plus 488 coefficients fitted to labels for multilingual sentiment regression and extraction. Supervised calibration and span selection drive the gains; reconstructed aggregate rankings, reused development data and incomplete overlap removal qualify the comparisons.",
    "zh": "将冻结的 Jev 决策与 488 个由标签拟合的系数结合，用于多语言情感回归和抽取。监督校准与片段选择贡献主要收益；重建的汇总排名、重复使用的开发数据及未完全排除的重叠，限制比较结论。",
    "artifacts": {
      "code": "https://github.com/ZhangYiqun018/jev-dimabsa"
    },
    "artifact_note": {
      "en": "Code, fitted parameters and summaries; dataset text and prediction caches are not distributed.",
      "zh": "代码、拟合参数与汇总结果；未分发数据文本及预测缓存。"
    }
  },
  {
    "category": "Papers",
    "title": "From Probabilities to Decisions: Search and Multi-Teacher Distillation with Jev",
    "by": "Sadoun, Sharif & Banad · 2026-10-06 · v1",
    "date": "2026-10-06",
    "first_submitted": "2026-10-06",
    "url": "https://arxiv.org/abs/2610.09188v1",
    "theme": "applications",
    "en": "Distills Jev and LLM judgments into compact search evaluators and rerankers; matched-label-budget gains in chess do not generalize to every tested game. The deployed bot also uses Stockfish, opening books and tablebases, and API wall time differs from GPU labeling time.",
    "zh": "将 Jev 与语言模型判断蒸馏为紧凑搜索评估器和重排器；相同标签预算下的棋类收益并未推广到所有测试游戏。部署机器人还依赖 Stockfish、开局库与残局库，API 墙钟时间也不同于 GPU 标注耗时。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "SharedKV-BT: Node-Local Typed Decisions for Behavior-Tree Agents",
    "by": "Wake & Wagle · 2026-10-05 · v1",
    "date": "2026-10-05",
    "first_submitted": "2026-10-05",
    "url": "https://arxiv.org/abs/2610.07327v1",
    "theme": "applications",
    "en": "Combines shared-prefix candidate scoring with behavior-tree node interfaces and external execution checks. The experiments separate scoring speed, stage restrictions and postcondition authority; predefined trees, simulated tasks and order-sensitive choices limit broader closed-loop reliability claims.",
    "zh": "把共享前缀候选评分、行为树节点接口与外部执行检查结合，区分评分速度、阶段限制和后置条件的权限。预定义树、仿真任务及对顺序敏感的选择，限制了更广泛的闭环可靠性结论。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Student-Guided Teacher Distillation for Efficient LLM Task Routing: Positioning Against Jev-Style System-1 Classifiers",
    "by": "Wu et al. · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02516v1",
    "theme": "architectures",
    "en": "Preliminary distillation for a fixed 60-label task taxonomy uses a student shortlist to reduce teacher scoring. Teacher agreement is not human accuracy; complete held-out controls remain pending, and the best checkpoint differs from the version used for serving measurements. No Jev head-to-head result is established.",
    "zh": "面向固定 60 标签任务分类的初步蒸馏研究，用学生候选表减少教师评分。与教师一致不等于人工准确率，完整留出对照仍待完成；最佳检查点与服务测量版本不同，未建立与 Jev 的直接对照结果。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Prune First, Decide Fast: Scalable Semantic Query Processing with JEVDB",
    "by": "Wang, Yan, Zhao & Liu · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02046v1",
    "theme": "applications",
    "en": "Combines semantic SQL with relational pruning, semantic conditions and an optional decision-to-LLM cascade. Lossless pruning requires sound conditions and key extraction; empirically learned filters may lose recall. Imported SemBench baselines and separately amortized index preparation qualify efficiency comparisons.",
    "zh": "将语义 SQL、关系剪枝、语义条件与可选的决策模型—语言模型级联结合。无损剪枝依赖可靠的必要条件与键提取，经验学习的过滤器可能损失召回；引用的 SemBench 基线和单独摊销的索引准备成本限制效率比较。",
    "artifacts": {
      "code": "https://github.com/PDAIS/JEVDB"
    },
    "artifact_note": {
      "en": "Implementation README and inventory checked; package and benchmarks not executed.",
      "zh": "已查实现说明和目录，未执行软件包或基准。"
    }
  },
  {
    "category": "Papers",
    "title": "OpenJev-RLCD: A Working RLCD Implementation",
    "by": "Gao & Wang · 2026-09-30 · v1",
    "date": "2026-09-30",
    "first_submitted": "2026-09-30",
    "url": "https://arxiv.org/abs/2609.38850v1",
    "theme": "calibration",
    "en": "An independent two-stage RLCD recipe calibrates a reasoning model's answer readout, then reinforces rationales with a proper-score reward. Three-seed results on a 1.7B model show task-dependent gains; the implementation explicitly makes no claim to recover TypeSafe's internal training algorithm.",
    "zh": "独立的两阶段 RLCD 方法先校准推理模型的答案读出，再用适当评分奖励强化推理。1.7B 模型上的三种子结果显示收益随任务变化；实现明确不声称还原 TypeSafe 内部训练算法。",
    "artifacts": {
      "code": "https://github.com/ZimmyGao/openjev-rlcd"
    },
    "artifact_note": {
      "en": "Independent implementation; released result files were not replayed.",
      "zh": "独立实现，未回放公开结果文件。"
    }
  },
  {
    "category": "Papers",
    "title": "NumericJev: Jev-like LLM Numerical Decoding with Multiway Decision Trees",
    "by": "Ye, Liu & Jiang · 2026-09-23 · v1",
    "date": "2026-09-23",
    "first_submitted": "2026-09-23",
    "url": "https://arxiv.org/abs/2609.28587v1",
    "theme": "architectures",
    "en": "Uses repeated Choice calls to refine a known numerical interval without retraining. Resolution is not accuracy or calibrated uncertainty, and early wrong branches are irreversible. Arithmetic variants share 64 base families; historical-index recall and later controller demonstrations are separate evidence.",
    "zh": "无需重训，通过重复 Choice 调用缩小已知数值区间。分辨率不等于准确性或已校准不确定性，早期错误分支不可逆。算术变体共享 64 个基础问题族；历史指数回忆与后续控制演示属于不同证据。",
    "artifacts": {
      "code": "https://github.com/Bring-AI/JevNext"
    },
    "artifact_note": {
      "en": "Renamed JevNext repository; current release declares PolyForm Noncommercial 1.0.0.",
      "zh": "仓库已更名 JevNext，当前版本声明 PolyForm Noncommercial 1.0.0。"
    }
  },
  {
    "category": "Papers",
    "title": "Benchmarking candidate coverage and rejection policy transfer in typed decision models",
    "by": "Lu & Wu · 2026-10-06 · v2",
    "date": "2026-10-06",
    "first_submitted": "2026-10-02",
    "url": "https://arxiv.org/abs/2610.03387v2",
    "theme": "calibration",
    "en": "Separates artificial omissions, retrieval misses and out-of-scope queries under matched calibration budgets; a source-task threshold can reject covered target inputs or miss absent answers. Candidate membership, label ambiguity and small natural-miss samples limit transfer claims.",
    "zh": "在相同校准预算下区分人为移除、检索遗漏与范围外查询；源任务阈值可能误拒目标任务中已有答案的输入，或漏检缺失答案。候选成员、标签歧义及自然遗漏的小样本限制迁移结论。",
    "artifacts": {
      "code": "https://github.com/luckykevvv/Decision_Model_Benchmark"
    },
    "artifact_note": {
      "en": "Recorded-output scoring is separate from reconstructing source text and fresh inference.",
      "zh": "已记录输出评分与源文本重建、重新推理分开。"
    }
  },
  {
    "category": "Papers",
    "title": "Probability Contracts: Accuracy, Coherence, and Decisions Across LLM Interfaces",
    "by": "Chen & Li · 2026-10-05 · v2",
    "date": "2026-10-05",
    "first_submitted": "2026-09-27",
    "url": "https://arxiv.org/abs/2609.37470v2",
    "theme": "calibration",
    "en": "Known-posterior finite worlds separate probability accuracy, interface coherence and decision loss. Averaging can improve expected Brier score without improving a policy at every deferral cost; valid-report coverage and each comparison's reference policy remain essential.",
    "zh": "用已知后验的有限世界区分概率准确性、接口一致性和决策损失。取平均可改善期望 Brier 分数，却不保证每个转交成本下的策略更好；有效输出覆盖率与具体对照策略不可省略。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Fast Models, Slow Evidence: A Paired and Self-Audited Evaluation of System-1 Decision Models for LLM Agent Harnesses",
    "by": "Li · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02267v1",
    "theme": "evaluation",
    "en": "Paired Laya/Jev evaluation of 11 agent decision points includes a self-audit: pre-screen cost, end-to-end quality, threshold leakage and unnatural channel content change deployment conclusions. Public English-dominant labels and zero-shot configurations limit generalization.",
    "zh": "成对评测 Laya／Jev 的 11 类 agent 决策并自查流程：前置筛查成本、端到端质量、阈值泄漏及不自然的通道内容都会改变部署结论。公开、英语为主的标签和零样本配置限制泛化。",
    "artifacts": {
      "code": "https://github.com/David-DL-Space/sys1-eval"
    },
    "artifact_note": {
      "en": "README and inventory checked; raw responses and analyses not replayed.",
      "zh": "已查说明和目录，未回放原始响应或分析。"
    }
  },
  {
    "category": "Papers",
    "title": "Jev-as-a-Judge for RAG Claim Verification: Confidence-Gated Cascading Between a Non-Generative Verifier and a Frontier LLM",
    "by": "Do Rosario & Atef · 2026-09-30 · v1",
    "date": "2026-09-30",
    "first_submitted": "2026-09-30",
    "url": "https://arxiv.org/abs/2610.20634v1",
    "theme": "judging",
    "en": "Paired verification of 495 RAG claims finds different false-verification rates despite similar aggregate scores. One threshold is cross-fitted, but design choices and matched random-escalation controls remain exploratory; simulated savings do not establish equivalence or a better production gate.",
    "zh": "对 495 条 RAG 声明的成对核验显示，汇总分数相近仍可有不同的误放率。一个阈值经过交叉拟合，但设计选择与同预算随机升级对照仍属探索；模拟节省不证明等效性或生产门控更优。",
    "artifacts": {
      "code": "https://github.com/adorosario/jev-rag-claim-verification"
    },
    "artifact_note": {
      "en": "Gold labels require upstream dataset access; offline replay is not a deployed cascade.",
      "zh": "参考标签需取得上游数据访问权限；离线回放并非已部署级联。"
    }
  },
  {
    "category": "Papers",
    "title": "When the Right Answer Is Missing: An Arithmetic-Dependent Rejection Bottleneck in Jev",
    "by": "Zhong, Li & Lai · 2026-09-30 · v1",
    "date": "2026-09-30",
    "first_submitted": "2026-09-30",
    "url": "https://arxiv.org/abs/2609.39496v1",
    "theme": "robustness",
    "en": "Paired numerical menus expose strong answer-present selection but weak none-of-the-above rejection. Separate development thresholds recover much of the tested rejection performance, while Boolean verification behaves differently; this diagnoses an interface-dependent failure, not hidden model mechanisms or universal threshold transfer.",
    "zh": "成对数值候选集揭示：答案存在时选择较强，缺失时却难以选中“以上皆非”。独立开发集阈值改善了所测拒答表现，布尔核验则呈现不同结果；这是接口相关失效诊断，不揭示内部机制或普遍阈值迁移。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Laya as a Typed Probabilistic Assessor: An Independent Reproduction and a Preregistered Study of Calibration and Selective Escalation",
    "by": "Nandakishore · 2026-09-27 · v1",
    "date": "2026-09-27",
    "first_submitted": "2026-09-27",
    "url": "https://arxiv.org/abs/2609.33843v1",
    "theme": "calibration",
    "en": "A pinned Laya checkpoint is underconfident on synthetic teacher labels. Temperature fitting improves probability metrics, but the frozen calibrator-selection rule and escalation gate fail held-out targets; reported Jev comparisons are indirect, and the initial reproduction predates preregistration.",
    "zh": "固定版本 Laya 检查点在合成教师标签上信心不足。温度拟合改善概率指标，但冻结的校准器选择规则与升级门控未达到留出目标；Jev 对照来自间接引用，初始复现早于预注册。",
    "artifacts": {
      "code": "https://arxiv.org/src/2609.33843v1/anc/metrics.py",
      "data": "https://arxiv.org/src/2609.33843v1/anc"
    },
    "artifact_note": {
      "en": "Metric code and ancillary records; full training/collection source is not included.",
      "zh": "指标代码与附属记录；不包含完整训练／采集源码。"
    }
  },
  {
    "category": "Papers",
    "title": "PRISM: Calibrating Black-Box Judges with Counterfactual Probes",
    "by": "Yamamoto & Kuroki · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18389v1",
    "theme": "judging",
    "en": "Learns a score correction from counterfactual probes and human labels; improved ranking agreement on two text tasks is distinct from probability calibration, and probe cost and cross-task transfer remain relevant limits.",
    "zh": "利用反事实评分探针和人类标签学习校正；两个文本任务上的排序一致性提升不同于概率校准，额外探针成本与跨任务迁移仍是重要限制。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Cheap, Consistent, Calibrated, but Biased? Typed Decision Models as Judges",
    "by": "Lukassen, Weisser & Silbersdorff · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18122v1",
    "theme": "judging",
    "en": "CALM pairwise challenges expose position and rewrite sensitivity despite consistency and calibration; inherited reference labels and rewrites that change more than tone limit causal interpretation and transfer to other judging tasks.",
    "zh": "CALM 成对挑战显示，一致性和校准并不能消除位置与改写敏感性；沿用的参考标签，以及不只改变语气的改写，限制了因果解释和对其他评判任务的推广。",
    "artifacts": {
      "code": "https://github.com/fabian-lu/TDM_as_a_Judge"
    },
    "artifact_note": {
      "en": "Declared MIT code; benchmark and results CC BY-NC-SA 4.0.",
      "zh": "声明代码为 MIT；基准与结果为 CC BY-NC-SA 4.0。"
    }
  },
  {
    "category": "Papers",
    "title": "FunDM: Cheap & Label-Free Decision Models from Frozen Language Models",
    "by": "Panchal · 2026-10-12 · v1",
    "date": "2026-10-12",
    "first_submitted": "2026-10-12",
    "url": "https://arxiv.org/abs/2610.17175v1",
    "theme": "architectures",
    "en": "Distills teacher probabilities into small heads using fewer layers of a frozen Qwen3-8B; label-free means no correct-answer training labels, and efficiency measurements cover one GPU and engine workload rather than production serving.",
    "zh": "把教师概率蒸馏到较浅的冻结 Qwen3-8B 计算路径上的小型决策头；无标签指不使用正确答案训练标签，效率测量只覆盖一个 GPU 和引擎任务，而非生产服务。",
    "artifacts": {
      "code": "https://github.com/Ujjawal-K-Panchal/FunDM"
    }
  },
  {
    "category": "Papers",
    "title": "Poisoned into Action: Context Attacks on Typed Decision Workflows",
    "by": "Wu, Chang & Yan · 2026-10-11 · v1",
    "date": "2026-10-11",
    "first_submitted": "2026-10-11",
    "url": "https://arxiv.org/abs/2610.15537v1",
    "theme": "robustness",
    "en": "Traces context poisoning through retrieval, typed choices and persisted execution while measuring retained clean utility; two synthetic development workflows and nonsignificant prespecified contrasts make the findings exploratory.",
    "zh": "追踪上下文投毒经检索、类型化选择到持久化执行的路径，并衡量保留的正常任务效用；仅覆盖两个合成开发工作流，预设比较未达显著，结论仍属探索性。",
    "artifacts": {
      "code": "https://github.com/WuXixiong/jev-poisoning-bench"
    },
    "artifact_note": {
      "en": "Public subset; full call archives and private attestations are omitted.",
      "zh": "公开子集；完整调用归档与私有证明材料未包含。"
    }
  },
  {
    "category": "Papers",
    "title": "Koa-decision: Fast and Consistent Structured Decision Making with Generative LLMs",
    "by": "Dai et al. · 2026-10-10 · v2",
    "date": "2026-10-10",
    "first_submitted": "2026-09-28",
    "url": "https://arxiv.org/abs/2609.36115v2",
    "theme": "architectures",
    "en": "Uses atomic label tokens and supervised fine-tuning for single-step constrained decisions; latency follows a specified sequential serving protocol, adaptation differs across baselines, and the production intent data cannot be released.",
    "zh": "通过原子标签 token 和监督微调实现单步受约束决策；延迟采用指定的顺序服务测量协议，不同基线的适配程度不同，生产意图数据无法公开。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "DICE: Tilting the Odds through Interface Attackson System One Model",
    "by": "Dong, Lu, Guo & Wang · 2026-10-09 · v1",
    "date": "2026-10-09",
    "first_submitted": "2026-10-09",
    "url": "https://arxiv.org/abs/2610.14404v1",
    "theme": "robustness",
    "en": "Tests bounded substitutions at state-extraction, question-generation and output-interpretation adapters while leaving authentic Jev responses intact; three synthetic pilots locate decision-integrity failures without estimating deployed attack prevalence.",
    "zh": "在状态抽取、问题生成和输出解释适配层测试有界替换，保持 Jev 原始响应不变；三个合成试验定位决策完整性失效，不估计实际部署中的攻击发生率。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "PACT: Pairwise-Anchored Calibrated Tuning for Single-Token Typed Decisions",
    "by": "Lin · 2026-09-26 · v1",
    "date": "2026-09-26",
    "first_submitted": "2026-09-26",
    "url": "https://arxiv.org/abs/2609.35865v1",
    "theme": "calibration",
    "en": "Uses certified contrastive pairs, permutation consistency and contextual temperature fitting to improve decision stability and ordinal error; a 324-item synthetic holdout, one model scale and certificate dependence limit generalization.",
    "zh": "利用带证书的对比样本对、排列一致性和上下文温度拟合改善决策稳定性与序数误差；留出集仅324条合成样本，模型尺度单一，且依赖证书正确性，推广范围有限。",
    "artifacts": {
      "code": "https://github.com/BennyLinntu/PACT-Pairwise-Anchored-Calibrated-Tuning-for-Single-Token-Typed-Decisions"
    },
    "artifact_note": {
      "en": "Paper results are separate from the repository’s later single-run Tetris demo.",
      "zh": "论文结果与仓库中后续的单次 Tetris 演示应分开解读。"
    }
  },
  {
    "category": "Papers",
    "title": "Dyad: Extending Large Language Models with Native Typed Decision-Making",
    "by": "Zhan et al. · 2026-09-28 · v1",
    "date": "2026-09-28",
    "first_submitted": "2026-09-28",
    "url": "https://arxiv.org/abs/2609.36116v1",
    "theme": "architectures",
    "en": "Adds an environment-conditioned action encoder to an LLM for typed actions; frozen-LLM adaptation and joint reinforcement learning are separate settings, and the Jev latency comparison uses previously published API measurements.",
    "zh": "为 LLM 加入环境条件化行动编码器以选择类型化动作；冻结 LLM 仅适配编码器与联合强化学习是不同设置，Jev 延迟比较引用既有 API 测量。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Prism-1: Position- and Rival-Independent Scoring for System One Models",
    "by": "Teng et al. · 2026-10-15 · v1",
    "date": "2026-10-15",
    "first_submitted": "2026-10-15",
    "url": "https://arxiv.org/abs/2610.22066v1",
    "theme": "robustness",
    "en": "An option-isolated readout targets order invariance and stable relative odds when candidates change; it requires fine-tuning, limits within-model comparison, and fits independently judged options better than menu-dependent fallback rules.",
    "zh": "通过隔离选项读出，使排列和候选变化时原有选项间的概率比保持稳定；需要微调并限制模型内选项比较，更适合可独立判断的选项，而非依赖整个候选集的兜底规则。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Lost in the Fallback: How Reliably Do Typed Decision Models Use Fallback Options?",
    "by": "Xie et al. · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.19856v1",
    "theme": "robustness",
    "en": "Paired tests on three text datasets separate category recognition from executing fallback rules; tested open models can disagree under equivalent definitions even when supplied the correct category, and the study diagnoses failures without establishing a fix.",
    "zh": "三个文本数据集的成对测试将类别识别与兜底规则执行分开；即使给出正确类别，所测开放模型在等价定义下仍可能产生分歧。研究诊断失效，未确立修复方法。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "SecJev: Bringing Security Expertise to System One Decision Models",
    "by": "Chen et al. · 2026-10-14 · v2",
    "date": "2026-10-14",
    "first_submitted": "2026-10-02",
    "url": "https://arxiv.org/abs/2610.03073v2",
    "theme": "applications",
    "en": "Adapts decision scorers to 14 security tasks; source-label prediction and displayed-policy execution are distinct targets, task difficulty is uneven, and benchmark accuracy does not establish end-to-end attack prevention.",
    "zh": "将决策评分器适配到14项安全任务；来源标签预测与显式策略执行是不同目标，任务难度不均，基准准确率不证明端到端攻击防护能力。",
    "artifacts": {
      "code": "https://github.com/UESTC1010/SecJev",
      "data": "https://github.com/UESTC1010/SecJev/releases/tag/v1.0.0",
      "model": "https://github.com/UESTC1010/SecJev/releases/tag/v1.3.0"
    },
    "artifact_note": {
      "en": "Release metadata checked; packages not loaded. Custom agreement and upstream terms apply.",
      "zh": "已查发布元数据，未加载包；适用自定义协议及上游条款。"
    }
  },
  {
    "category": "Papers",
    "title": "BLADE: Auditing Information Use for Failure Attribution in LLM Multi-Agent Systems",
    "by": "Guo, Long & Zhang · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18780v1",
    "theme": "judging",
    "en": "Uses Jev to audit information use at agent handoffs and localize failures; comparisons share one decision model on five benchmark subsets, and attribution depends on the completeness of retained traces.",
    "zh": "用 Jev 审查 agent 交接时如何使用信息并定位失效；比较在五个基准子集上共用一个决策模型，归因质量受所保留轨迹证据完整性限制。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Recalibrating Many Questions with Few Labels: Minimax Rates and Identification Limits",
    "by": "Li & Yang · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18488v1",
    "theme": "calibration",
    "en": "Derives excess-Brier risk bounds for pooling recalibration across questions under shared-distribution and monotonicity assumptions; fixed-effects and empirical-Bayes results have different targets, and risk lower bounds do not directly become calibration-error lower bounds.",
    "zh": "在共享输出分布与单调性假设下，推导跨问题合并重校准的超额 Brier 风险界；固定效应与经验贝叶斯结果的目标不同，风险下界不能直接视为校准误差下界。"
  },
  {
    "category": "Papers",
    "title": "Jev-LiteMAS: Separating Decisions from Generation in Multi-Agent Workflows",
    "by": "Wang, Zhou, Lou & Li · 2026-10-15 · v1",
    "date": "2026-10-15",
    "first_submitted": "2026-10-15",
    "url": "https://arxiv.org/abs/2610.21411v1",
    "theme": "judging",
    "en": "Routes expert handoffs and screens artifacts before generative re-review; lower generative-token use depends on the workload, with fixed expert pools and savings that shrink as more artifacts need repair.",
    "zh": "在生成式复审前进行专家交接路由和产物筛查；生成模型的 token 节省取决于任务，专家池固定，需要修复的产物越多，节省可能越少。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Papers",
    "title": "Verdict: Encode Once, Decide Many",
    "by": "Chouhan & Perry · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.20778v1",
    "theme": "architectures",
    "en": "Encodes shared state once for multiple typed questions; invariance requires identical retained state tokens, while teacher-derived labels, adaptive testing and unstable BoolQ training constrain the reported gains.",
    "zh": "一次编码共享状态，回答多个类型化问题；不变性要求保留的状态 token 一致，教师模型标签、适应性测试过程及 BoolQ 训练不稳定限制了所报收益的解读。",
    "artifacts": {
      "code": "https://github.com/LEC-AI/verdict"
    },
    "artifact_note": {
      "en": "Code and saved results; trained checkpoints are not included.",
      "zh": "提供代码与已保存结果，未发布训练后的检查点。"
    }
  },
  {
    "category": "Papers",
    "title": "Prune the Summary, Not the History: Source-Judged Compaction for Long-Horizon Agents",
    "by": "Min & Chen · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.20927v1",
    "theme": "architectures",
    "en": "Uses Jev to prune summary entries lacking source support; reported gains concern success in all three runs on two benchmarks, while useful constraints can be discarded and sourced errors retained.",
    "zh": "用 Jev 删除缺少来源支持的摘要条目；所报收益衡量两个基准上三次独立运行均成功的比例，但有用约束可能被删去，有来源的错误也可能保留。",
    "artifacts": {
      "code": "https://github.com/GuanghuiMin/sjc"
    },
    "artifact_note": {
      "en": "Requires separate benchmark environments and model API access; not run here.",
      "zh": "需另行配置基准环境和模型 API，本项目未运行。"
    }
  },
  {
    "category": "Papers",
    "title": "Consider, Then Choose: Order-Invariant Decisions in System One Models",
    "by": "Huang, Teng, Deng & An · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18233v1",
    "theme": "robustness",
    "en": "Runoff scores options individually, then balances finalist positions; order invariance assumes deterministic responses and a unique ranking, and does not resolve option-name bias or guarantee more accurate decisions.",
    "zh": "Runoff 先逐个评分选项，再平衡入围候选的位置；顺序不变性假设响应确定且排序唯一，不能解决选项名称偏置，也不保证决策更准确。",
    "artifacts": {
      "unverified": "code"
    }
  },
  {
    "category": "Tools",
    "title": "Abide",
    "by": "coldteadotai · rule checks · MIT",
    "url": "https://github.com/coldteadotai/abide",
    "tool_tasks": ["workflow"],
    "en": "Jev checks edits and turns against compiled project rules and requests repairs; missing credentials or network let edits pass unchecked, and replay findings depend on the chosen rubric.",
    "zh": "用 Jev 按编译后的项目规则检查编辑和轮次，并请求修复；缺少凭据或网络时会放行未检查编辑，回放结果也取决于规则设计。"
  },
  {
    "category": "Tools",
    "title": "jev-fabric",
    "by": "fabric-runtime · process orchestration · MIT",
    "url": "https://github.com/fabric-runtime/jev-fabric",
    "tool_tasks": ["workflow"],
    "en": "Native process orchestration with bounded logs, deadlines and explicit typed decisions; commands run with caller privileges, exit status needs outcome checks, and selected policy proofs do not verify the whole runtime.",
    "zh": "原生进程编排，提供有界日志、截止时间与显式类型化决策；命令使用调用者权限，退出状态仍需结果核验，部分策略证明不等于整个运行时已验证。"
  },
  {
    "category": "Tools",
    "title": "atoma",
    "by": "atoma-run · agent workflows · AGPL-3.0-only",
    "url": "https://github.com/atoma-run/atoma",
    "tool_tasks": ["workflow"],
    "en": "Multi-agent planning, execution and evidence review with Jev routing; shared agent/skill learning can expose document-derived material across organizations, and tenant isolation is not independently audited.",
    "zh": "结合 Jev 路由的多 agent 规划、执行与证据审查；共享 agent／技能学习可能使文档衍生内容跨组织可读，租户隔离尚未经过独立审计。"
  },
  {
    "category": "Tools",
    "title": "circuit",
    "by": "Barneyjm · training code · Apache-2.0",
    "url": "https://github.com/Barneyjm/circuit",
    "tool_tasks": ["training", "runtime"],
    "en": "LoRA and pointer-head training, evaluation and serving for text, image and audio decisions; publisher tests cover selected task sets and do not establish universal calibration or option-order invariance.",
    "zh": "面向文本、图像与音频决策的 LoRA、指针头训练、评测和服务工具；发布者测试只覆盖选定任务集，不能证明普遍校准或选项顺序不变性。"
  },
  {
    "category": "Tools",
    "title": "cua-s1.js",
    "by": "ai-ecoverse · browser port · MIT",
    "url": "https://github.com/ai-ecoverse/cua-s1.js",
    "tool_tasks": ["runtime"],
    "en": "Browser ports of Cua form and next-action models; output-parity checks do not establish generalization, and the small form model can confidently skip unfamiliar fields.",
    "zh": "Cua 表单与下一步动作模型的浏览器移植；输出一致性检查不证明泛化，小型表单模型可能高置信度跳过陌生字段。"
  },
  {
    "category": "Tools",
    "title": "jev-omni.js",
    "by": "ai-ecoverse · WebGPU port · Apache-2.0",
    "url": "https://github.com/ai-ecoverse/jev-omni.js",
    "tool_tasks": ["runtime"],
    "en": "Work-in-progress WebGPU port for Jev-Omni text and image decisions; audio/video are unfinished, model downloads are large, and reported parity is limited to selected fixtures and hardware.",
    "zh": "开发中的 Jev-Omni 文本与图像决策 WebGPU 移植；音视频未完成、模型下载体积较大，一致性结果仅覆盖指定样本与硬件。"
  },
  {
    "category": "Tools",
    "title": "SearchJev training pipeline",
    "by": "EvoScientist · training code · Apache-2.0",
    "url": "https://github.com/EvoScientist/SearchJev",
    "tool_tasks": ["training"],
    "en": "Search-agent decision training with soft-label and Brier losses, reliability weights and per-question-type temperature fitting; the documented pipeline and split controls were not reproduced.",
    "zh": "面向搜索 agent 决策的训练流程，包含软标签与 Brier 损失、可靠性权重及按问题类型拟合温度；文档中的流程与切分控制尚未复现。"
  },
  {
    "category": "Tools",
    "title": "mJev",
    "by": "SoMarkAI · multimodal runtime · Apache-2.0",
    "url": "https://github.com/SoMarkAI/mJev",
    "tool_tasks": ["runtime"],
    "en": "Shared-context candidate scoring with HF/vLLM routes; normalized option probabilities are not calibrated confidence, and the reported cache speedup trades higher memory in one controlled video setup.",
    "zh": "通过 HF/vLLM 路径进行共享上下文候选评分；选项归一化概率不是已校准置信度，所报缓存加速在一个受控视频设置中需要更多显存。"
  },
  {
    "publisher": "OmniJev",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "OneJev1.5-27B",
    "by": "OmniJev · Apache-2.0",
    "url": "https://huggingface.co/OmniJev/OneJev1.5-27B",
    "en": "27B full fine-tune for text, image and video decisions, served through qev. Training includes public benchmark training splits; reported scores cover the public suite, and Jev comparison numbers are imported rather than a matched multimodal rerun.",
    "zh": "面向文本、图像和视频决策的 27B 全量微调模型，通过 qev 提供服务。训练包含公开基准的训练切分；所报分数覆盖公共评测，Jev 对照数字来自已发表结果，并非同条件的多模态重测。",
    "provenance": "modelcard"
  },
  {
    "publisher": "Liquid AI",
    "license": "LFM Open License v1.0",
    "category": "Models",
    "title": "d1-omni-600M",
    "by": "Liquid AI · LFM Open License v1.0",
    "url": "https://huggingface.co/LiquidAI/d1-omni-600M",
    "en": "587M encoder for text with images or up to 30 seconds of English speech; one request cannot mix both media. Only text uses fitted temperatures. Image requests cap text at 896 tokens; custom code and the LFM Open License apply.",
    "zh": "587M 编码器，支持文本配合图像或最长 30 秒的英语语音，单次请求不能同时使用两种媒体。仅文本使用拟合温度；图像请求的文本上限为 896 个 token，需使用自定义代码并遵循 LFM Open License。",
    "provenance": "modelcard"
  },
  {
    "publisher": "Torchcast AI",
    "license": "CC BY-NC 4.0",
    "category": "Models",
    "title": "Torchcast Decision 27B",
    "by": "Torchcast AI · CC BY-NC 4.0",
    "url": "https://huggingface.co/torchcast-ai/torchcast-decision-27b",
    "en": "Merged LoRA decision model with a CUDA serving package; weights are noncommercial, serving code Apache-2.0. Text-only, checkpoint-selected results use Decision Index 0.2.1; long states and more than 26 options change the inference path.",
    "zh": "合并 LoRA 权重的决策模型，附 CUDA 服务包；权重限非商业用途，服务代码为 Apache-2.0。文本评测使用 Decision Index 0.2.1 且参与检查点选择；长状态或超过 26 个选项会改变推理路径。",
    "provenance": "modelcard"
  },
  {
    "publisher": "tasksource",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "tasksource-decider-nano",
    "by": "tasksource · Apache-2.0",
    "url": "https://huggingface.co/tasksource/tasksource-decider-nano",
    "en": "150M joint cross-encoder with shared-state tree attention and choice/noul outputs. Rejects pairs above 8,192 tokens; training includes public benchmark training splits. Reported speed and public-suite scores use the documented A10 setup.",
    "zh": "150M 联合交叉编码器，通过树形注意力共享状态，输出 choice／noul。超过 8,192 个 token 的配对会被拒绝；训练包含公开基准的训练切分，所报速度和公共评测分数使用文档所述 A10 配置。",
    "provenance": "modelcard"
  },
  {
    "publisher": "Felhen",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "Saracura PT-BR 4B",
    "by": "Felhen · Apache-2.0",
    "url": "https://huggingface.co/felhen-ai/saracura-ptbr-4b",
    "en": "Brazilian Portuguese Kev adapter and pointer head. Source-matched tests and two-fold human-set calibration do not establish general Portuguese performance; private email-tuned results belong to an unreleased model. Use the documented 2,048-token state setting for comparisons.",
    "zh": "面向巴西葡萄牙语的 Kev 适配器和指针头。同源测试及人工标注集上的两折校准不能证明通用葡语能力；私有邮件微调结果属于未发布模型。比较时需使用文档所述 2,048-token 状态设置。",
    "provenance": "modelcard"
  },
  {
    "publisher": "Perplexity",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "Perplexity Decider v1.2 27B",
    "by": "Perplexity · Apache-2.0",
    "url": "https://huggingface.co/perplexity-ai/pplx-decider-v1.2",
    "en": "27B text/image model with joint question readouts: questions can affect one another. Public-suite training exposure and grouping affect comparisons. Anonymous Hub metadata and a weight HEAD were accessible on 18 Oct; the card still instructs private access.",
    "zh": "27B 文本／图像模型，联合读取多个问题，问题间可相互影响。公开评测训练数据的使用与问题分组会影响比较。10 月 18 日匿名元数据与权重 HEAD 请求可访问，但模型卡仍写着需私有访问权限。",
    "provenance": "modelcard"
  },
  {
    "publisher": "mukaddamzaid",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "Amos 1 large",
    "by": "mukaddamzaid · Apache-2.0",
    "url": "https://huggingface.co/mukaddamzaid/amos-1-large",
    "en": "English typed decisions with image inputs; distinguish zero-shot results from train-split prior fitting, and public-only Decision Index results from the full evaluation.",
    "zh": "支持图像输入的英文类型化决策模型；应区分零样本结果与按训练切分拟合先验的结果，以及 Decision Index 公共部分与完整评测。",
    "provenance": "modelcard"
  },
  {
    "publisher": "PelaAI",
    "license": "Apache-2.0 weights; MIT server",
    "category": "Models",
    "title": "KnowLine-35B-A3B-Gen1",
    "by": "PelaAI · Apache-2.0 weights; MIT server",
    "url": "https://huggingface.co/PelaAI/KnowLine-35B-A3B-Gen1",
    "en": "English/Chinese MoE decision checkpoint; public-suite checkpoint selection, disclosed task/source overlap and self-run calibration ranges constrain comparisons with independent held-out evaluations.",
    "zh": "英中文 MoE 决策检查点；公开评测选点、披露的任务／来源重叠与自行计算的校准区间，限制了它与独立留出评测的比较。",
    "provenance": "modelcard"
  },
  {
    "publisher": "LycheeAI",
    "license": "CC BY-NC 4.0",
    "category": "Models",
    "title": "Lychee-27B",
    "by": "LycheeAI · CC BY-NC 4.0",
    "url": "https://huggingface.co/LycheeAI/Lychee-27B",
    "en": "Noncommercial Qwen-derived typed-decision model with publisher-reported public-suite results; requests exceeding context or GPU-memory limits are documented as rejected rather than truncated.",
    "zh": "按非商业许可发布的 Qwen 派生决策模型，公共评测结果由发布者报告；文档说明超出上下文或显存限制时拒绝请求，而非截断。",
    "provenance": "modelcard"
  },
  {
    "publisher": "Respan",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "Span-02",
    "by": "Respan · Apache-2.0",
    "url": "https://huggingface.co/respanai/span-02",
    "en": "Multimodal decision model with a dedicated Blackwell Rust/CUDA runtime and optional reasoning; distinguish default serving from deterministic index settings and output-specific confidence semantics.",
    "zh": "使用专用 Blackwell Rust/CUDA 运行库、可选择生成推理的多模态决策模型；需区分默认服务与确定性榜单配置，以及不同输出类型的置信度语义。",
    "provenance": "modelcard"
  },
  {
    "category": "Papers",
    "title": "TypedBench: A Benchmark for Calibration, Framing Sensitivity, and Cost in System One Decision Models",
    "by": "Sharma, Duncan, Caron & Vollmer · 2026-10-09 · v2",
    "date": "2026-10-09",
    "first_submitted": "2026-10-08",
    "url": "https://arxiv.org/abs/2610.11392v2",
    "theme": "evaluation",
    "en": "The hosted model is wording-sensitive and underconfident, and under asymmetric costs acting on its probabilities can cost more than taking its top answer; synthetic policy-labelled suites also report paraphrase ranges and calibration against a finite-sample noise floor.",
    "zh": "托管模型对措辞敏感且系统性信心不足，在非对称成本下按其概率行动的代价可能高于直接采用最高答案；基于带策略标签的合成测试集，还报告不同改写下的准确率范围及相对有限样本噪声下限的校准误差。"
  },
  {
    "category": "Papers",
    "title": "Does a Hosted Decision Model Respect Irrelevant Alternatives? A Pre-Registered Test of Option-Set Dependence in Jev",
    "by": "Rajput, Chauhan & Kosaraju · 2026-10-12 · v1",
    "date": "2026-10-12",
    "first_submitted": "2026-10-12",
    "url": "https://arxiv.org/abs/2610.16655v1",
    "theme": "calibration",
    "en": "Adding an irrelevant option shifts jev-1.13.0’s gold-versus-rival log-odds, more so as options grow, so its probabilities are relative to the option list; independent yes/no scoring removes this but is less accurate (pre-registered, 299,463 calls, three datasets).",
    "zh": "加入无关选项会改变 jev-1.13.0 对正确标签与最强错误标签的对数几率，选项越多偏移越大，因此其概率只相对于所给选项列表成立；逐项独立的是非评分可消除这种依赖，但准确率更低（预注册，299,463 次调用，三个数据集）。"
  },
  {
    "category": "Papers",
    "title": "Nudge the Judge: Uncovering Program Decision Hijacking in Real-World Jev Applications",
    "by": "Luo et al. · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "artifacts": {"code": "https://github.com/xiaoxiaohg8d/JevProbe-", "data": "https://github.com/xiaoxiaohg8d/JevProbe-"},
    "url": "https://arxiv.org/abs/2610.18612v1",
    "theme": "robustness",
    "artifact_note": {"en": "README inspected, not executed.", "zh": "仅检查 README，未执行。"},
    "en": "JevProbe traces attacker-controlled context into the decisions that 228 popular Jev applications act on; in 2,273 curated cases (at most ten per app, flips selected first, so not an unbiased sample) 81.5% flip, 98.6% of flips with potential downstream security impact, and existing defenses offer limited protection.",
    "zh": "JevProbe 追踪攻击者可控的上下文如何影响 228 个热门 Jev 应用据以执行的决策；在 2,273 个精选用例中（每个应用至多十条、优先选取翻转案例，并非无偏样本），81.5% 出现决策翻转，其中 98.6% 可能造成下游安全影响，现有防御作用有限。"
  },
  {
    "category": "Papers",
    "title": "From Detection to Decision: Calibration and Deferral for Prompt-Injection Detection",
    "by": "Lan, Kaul, Pandurangan & Sanyal · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.20907v1",
    "theme": "robustness",
    "en": "On 47,611 held-out prompt-injection examples, Jev ranks second in AUROC after an LLM judge, its native probabilities do not consistently beat post-hoc calibrated classifiers, and a 1% false-negative target forces over 91.8% escalation in every gate-reviewer system.",
    "zh": "在 47,611 条留出的提示注入样本上，Jev 的 AUROC 仅次于 LLM 评审，其原生概率并不总优于事后校准的分类器分数；若把漏报率目标定为 1%，所有门控—复核系统都需升级处理超过 91.8% 的输入。"
  },
  {
    "category": "Papers",
    "title": "How Reliable Are System-One Decisions in Medicine? A Comparative Study of Jev, Jev-like Models, and LLMs",
    "by": "Du et al. · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "url": "https://arxiv.org/abs/2610.18529v1",
    "theme": "applications",
    "en": "Across 15 medical datasets (8,742 instances), Jev rivals leading models on text-driven tasks, is weaker on numerical ones and is the most stable under question-format changes; most models miss absent correct answers. A benchmark study, not clinical validation.",
    "zh": "在 15 个医学数据集（8,742 个实例）上，Jev 在文本主导任务上可比肩领先模型、数值任务较弱，题目格式变化下最稳定；多数模型难以识别正确答案缺失。这是基准研究，不是临床验证。"
  },
  {
    "category": "Papers",
    "title": "Jev-ToM: Evaluating Theory of Mind in Typed Decision Models",
    "by": "Chung et al. · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "artifacts": {"data": "https://github.com/HKUST-KnowComp/Jev-ToM"},
    "url": "https://arxiv.org/abs/2610.18610v1",
    "theme": "evaluation",
    "artifact_note": {"en": "source-benchmark terms apply.", "zh": "各来源基准的使用条款仍然适用。"},
    "en": "On 11,117 English Theory of Mind questions from nine benchmarks, Jev reaches 73.2% source-balanced accuracy and ranks first or second in all six capability groups among twelve typed and generative models; confidence-based selection is benchmark-dependent, and supplied reasons repair or overturn answers depending on how they are attached.",
    "zh": "在来自九个基准的 11,117 道英文心智理论题上，Jev 的来源均衡准确率为 73.2%，在十二个类型化与生成式模型中六类能力均列前二；基于置信度的选择效果因基准而异，附加理由则视其附加方式，可能纠错，也可能推翻正确答案。"
  },
  {
    "category": "Papers",
    "title": "When Faster Decisions Do Not Make Better Agents: An Empirical Study of Jev in Agent Workflows",
    "by": "Ling, Yu, Chen & Fang · 2026-10-09 · v1",
    "date": "2026-10-09",
    "first_submitted": "2026-10-09",
    "url": "https://arxiv.org/abs/2610.13092v1",
    "theme": "evaluation",
    "en": "Jev cut decision cost and latency for five agents in ALFWorld and AndroidWorld (4,500 runs), but two mobile agents lost more success, extra reasoning and interactions absorbed the savings, and cost per success rose for one agent.",
    "zh": "Jev 让 ALFWorld 与 AndroidWorld 中五个 agent 的决策成本和时延下降（共 4,500 次运行），但两个移动端 agent 成功率降幅较大，辅助推理与额外交互抵消了节省，其中一个 agent 的单次成功成本反而上升。"
  },
  {
    "category": "Papers",
    "title": "Qwen-Audio-Jev: A Unified Interface for Audio Decisions",
    "by": "Fang et al. · 2026-10-15 · v1",
    "date": "2026-10-15",
    "first_submitted": "2026-10-15",
    "url": "https://arxiv.org/abs/2610.21614v1",
    "theme": "architectures",
    "en": "An independent Jev-style decision head on Qwen-Audio-3.1-ASR-Flash-Next gives Choice, Noul and Score readouts over audio, reporting 84.06% on MMSU, a 6.50% speaker-verification equal error rate and about 20× faster inference than its own base model.",
    "zh": "在 Qwen-Audio-3.1-ASR-Flash-Next 上加入独立实现的 Jev 式决策头，对音频给出 Choice、Noul 与 Score 读出；报告 MMSU 准确率 84.06%、说话人验证等错误率 6.50%，推理速度约为其基础模型的 20 倍。"
  },
  {
    "category": "Papers",
    "title": "Are AI Decision Models Biased? A Case Study of Jev",
    "by": "Imperatrice, Kameneva, Greenberg & Romano · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.19619v1",
    "theme": "calibration",
    "en": "In 41,500 responses Jev's selected answers look largely unbiased, but its judgments shift with irrelevant numbers and option order, and several bias manipulations move its probabilities even when the answer stays the same; on 30 adapted conjunction tasks it violates the conjunction rule in 54% of 15,000 responses.",
    "zh": "在 41,500 次回答中，Jev 选出的答案大体未显示偏差，但其判断会受无关数字和选项顺序影响，部分认知偏差操纵即使不改变所选答案也会明显改变返回的概率；在 30 个改编的合取任务上，15,000 次回答中有 54% 违反合取规则。"
  },
  {
    "category": "Papers",
    "title": "Hidden Risks of Jev: An Empirical Study of Security, Privacy, and Dual Use",
    "by": "Wang et al. · 2026-10-04 · v1",
    "date": "2026-10-04",
    "first_submitted": "2026-10-04",
    "artifacts": {"code": "https://github.com/shihe98/Security_Privacy_Jev"},
    "url": "https://arxiv.org/abs/2610.04985v1",
    "theme": "robustness",
    "artifact_note": {"en": "no license declared.", "zh": "未声明许可。"},
    "en": "Tests the official Jev API and the local NanoJev for prompt injection, data-poisoning backdoors, membership, attribute and knowledge inference, and dual use in four detection tasks; the authors report Jev remains vulnerable to the examined threats.",
    "zh": "以官方 Jev API 和本地模型 NanoJev 检验提示注入、数据投毒后门，成员、属性与内部知识推断，以及四项检测任务中的双重用途；作者报告 Jev 对所考察的威胁仍然脆弱。"
  },
  {
    "category": "Papers",
    "title": "Calibration and Risk-Budgeted Decisions with System One Models",
    "by": "Messoudi & Mansar · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "url": "https://arxiv.org/abs/2610.19811v1",
    "theme": "calibration",
    "en": "Jev and other System One models make binary allow/block or retain/discard decisions without human deferral; across six moderation, safety and reranking datasets, naive threshold selection exceeds the target risk in about half the settings, against 7.8% for Learn Then Test.",
    "zh": "Jev 等 System One 模型在无法转交人工时做二元放行／拦截或保留／丢弃决策；在六个审核、安全与重排序数据集上，朴素阈值选择约在一半设置中超出目标风险，Learn Then Test 仅为 7.8%。"
  },
  {
    "category": "Papers",
    "title": "ufakzeka-karar: An Open Turkish Typed-Decision Model with Order-Invariant Option Scoring",
    "by": "Teke · 2026-10-05 · v1",
    "date": "2026-10-05",
    "first_submitted": "2026-10-05",
    "artifacts": {"code": "https://github.com/ufakai/ufakzeka-karar", "model": "https://huggingface.co/ufakai/ufakzeka-karar"},
    "url": "https://arxiv.org/abs/2610.06744v1",
    "theme": "architectures",
    "artifact_note": {"en": "Apache-2.0.", "zh": "Apache-2.0。"},
    "en": "An open 182M-parameter Turkish model scores each option blind to the others, so answers ignore option order, and adds a “not sure” signal; its 7th-of-16 HakemBench rank is not blind, since later runs trained after full-test results were read.",
    "zh": "开源的 1.82 亿参数土耳其语模型对每个选项独立评分，答案不受选项顺序影响，并提供“不确定”信号；其在 HakemBench 16 行中排第 7 的结果并非盲测，因为后续训练是在读过完整测试结果后进行的。"
  },
  {
    "category": "Papers",
    "title": "OmniMed-Jev: Calibrating LVLM Confidence for Trustworthy Medical Multimodal Decisions via System One",
    "by": "Tang & Chen · 2026-09-30 · v1",
    "date": "2026-09-30",
    "first_submitted": "2026-09-30",
    "artifacts": {"code": "https://github.com/lytang63/OmniMed-Jev"},
    "url": "https://arxiv.org/abs/2610.00381v1",
    "theme": "applications",
    "en": "Medical candidate-conditioned decisions are compared with a matched generative baseline; calibration gains do not isolate interface effects from training differences or establish clinical readiness.",
    "zh": "将医学候选条件决策与匹配的生成式基线比较；校准收益未分离接口与训练差异的影响，也不能证明临床部署成熟度。"
  },
  {
    "category": "Papers",
    "title": "Batched Speech Decisions Without Decoding: Single-Token Supervision Lets a Frozen LLM Hear Beyond the Transcript",
    "by": "Jin et al. · 2026-10-02 · v1",
    "date": "2026-10-02",
    "first_submitted": "2026-10-02",
    "artifacts": {"code": "https://github.com/adventists-ai/duplexjev"},
    "url": "https://arxiv.org/abs/2610.02638v1",
    "theme": "architectures",
    "en": "DuplexJev connects ASR hidden states to a frozen LLM for batched answer-token readout; connector-specific speech tasks and eight-GPU timing do not establish single-device or live-agent latency.",
    "zh": "DuplexJev 将 ASR 隐藏状态接入冻结 LLM，通过答案 token 读出批量决策；连接器相关的语音任务结果与八 GPU 计时，不能证明单设备或实时 agent 延迟。"
  },
  {
    "category": "Papers",
    "title": "SoK: Semantic Decision Engines in Network Control Loops",
    "by": "Li et al. · 2026-10-05 · v1",
    "date": "2026-10-05",
    "first_submitted": "2026-10-05",
    "url": "https://arxiv.org/abs/2610.06425v1",
    "theme": "evaluation",
    "en": "Surveys semantic engines in network control loops; separates valid decisions, action feasibility, service checks and deadline attainment, with bounded event-model tests rather than production validation.",
    "zh": "综述网络控制环中的语义引擎，区分决策格式有效、动作可行、服务核查与期限达成；验证来自有界事件模型测试，而非生产部署。"
  },
  {
    "category": "Papers",
    "title": "Does System One Transfer? Calibrated Typed-Decision Models, Label Budgets, and Translation for Indonesian Regional Languages",
    "by": "Fadli, Rusdah, Utami & Amana · 2026-10-09 · v1",
    "date": "2026-10-09",
    "first_submitted": "2026-10-09",
    "artifacts": {"code": "https://github.com/tnromy/evaluating-system-one-models-for-indonesian-regional-languages"},
    "url": "https://arxiv.org/abs/2610.14112v1",
    "theme": "evaluation",
    "en": "Tests Jev and multilingual Laya on Indonesian regional-language tasks; stable expected calibration error can coexist with worse error ranking, while human translation, label budgets and cascade choices change comparisons.",
    "zh": "在印尼地方语言任务中测试 Jev 与多语言 Laya；预期校准误差稳定仍可伴随错误排序变差，人类翻译、标签预算与级联选择会改变比较条件。"
  },
  {
    "category": "Papers",
    "title": "Labels Override Definitions in Jev-Style Typed Decision Models",
    "by": "Azizi, Baghaei Potraghloo & Pedram · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02586v1",
    "theme": "robustness",
    "en": "Studies option-label bias in open-weight decision models; prompt-rendering changes with fixed weights implicate the label/definition interface, without testing hosted Jev.",
    "zh": "研究开放权重决策模型的选项标签偏置；固定权重后改变提示渲染，指向标签／定义接口的影响，未测试托管 Jev。"
  },
  {
    "category": "Papers",
    "title": "GraphDecisionBench: Benchmarking System One Models on Graph Tasks",
    "by": "Yang, Zhang & Zhao · 2026-10-12 · v3",
    "date": "2026-10-12",
    "first_submitted": "2026-10-05",
    "artifacts": {"code": "https://github.com/VictorYXL/GraphDecisionBench"},
    "url": "https://arxiv.org/abs/2610.06354v3",
    "theme": "evaluation",
    "en": "Compares graph decisions across fourteen model-interface configurations; local adjacency, graph-text evidence use and sequential solution quality are separate capabilities.",
    "zh": "比较十四种模型—接口配置的图决策；局部邻接识别、图文证据利用与序列构造解的质量是不同能力。"
  },
  {
    "category": "Papers",
    "title": "AudioJev: Direct Audio Decisions with Order-Calibrated Probabilities",
    "by": "Lv et al. · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "artifacts": {"code": "https://github.com/SihanLv/AudioJev-Inference", "model": "https://huggingface.co/shlv/AudioJev"},
    "url": "https://arxiv.org/abs/2610.01293v1",
    "theme": "architectures",
    "en": "Learns audio-conditioned candidate probabilities with aligned option-permutation training; order stability and empirical correctness calibration remain different properties.",
    "zh": "通过按候选身份对齐的选项重排训练学习音频条件概率；顺序稳定性与概率符合实际正确率仍是不同性质。"
  },
  {
    "publisher": "shlv",
    "license": "Qwen Research",
    "category": "Models",
    "title": "AudioJev checkpoint",
    "by": "shlv · Qwen2.5-Omni-3B derivative · Qwen Research",
    "url": "https://huggingface.co/shlv/AudioJev",
    "en": "One released AudioJev training seed with a Qwen Research license; original-order scores disclose audio-source overlap and are distinct from the paper’s three-seed averages.",
    "zh": "按 Qwen Research 许可发布的单训练种子 AudioJev 检查点；原始选项顺序得分披露了音频来源重叠，与论文三种子均值不同。",
    "provenance": "modelcard"
  },
  {
    "category": "Tools",
    "title": "FRIDA-Decisions",
    "by": "SberAI · independent runtime · MIT code",
    "url": "https://github.com/ai-forever/FRIDA-Decisions",
    "tool_tasks": ["runtime"],
    "en": "Packed Russian–English encoder runtime for typed questions and ranking; state truncation, Russian instruction suffixes and margin-versus-probability semantics remain explicit.",
    "zh": "面向类型化问题与排序的俄英双语编码器运行库；需注意状态截断、俄语指令后缀，以及边际分数与归一化概率的区别。"
  },
  {
    "category": "Tools",
    "title": "OpenThai-SystemOne",
    "by": "iapp-technology · Thai/English pipeline",
    "url": "https://github.com/iapp-technology/openthai-systemone",
    "tool_tasks": ["training", "runtime"],
    "en": "Thai/English text decision-model training and serving pipeline with a slot readout; the documented recipe does not establish independently validated calibration or interface equivalence.",
    "zh": "采用槽位读出的泰英文本决策模型训练与服务流程；文档中的配方不代表校准或接口等价性已获独立验证。"
  },
  {
    "category": "Tools",
    "title": "Quyet runtime",
    "by": "ncchinh · runtime · Apache-2.0",
    "url": "https://github.com/ncchinh/quyet",
    "tool_tasks": ["runtime"],
    "en": "Runtime for Quyet decision models with checkpoint-dependent English/Vietnamese coverage; it documents ten-option limits and state truncation, without evaluated adversarial robustness.",
    "zh": "Quyet 决策模型运行库，英越语言覆盖依检查点而异；文档说明最多十个选项及状态截断，尚未确立对抗鲁棒性。"
  },
  {
    "category": "Evaluations",
    "title": "Browser decision-vision benchmark",
    "by": "ai-ecoverse · browser comparison",
    "url": "https://github.com/ai-ecoverse/decision-vision-bench",
    "en": "Mixed visual/text comparison of browser decision models using native formats; ambiguous GUI labels, shared hardware and different browsers limit broad ranking and latency claims.",
    "zh": "以各模型原生格式比较浏览器视觉／文本决策；GUI 标签歧义、共享硬件及不同浏览器限制了通用排名和时延结论。"
  },
  {
    "category": "Evaluations",
    "title": "English Jev RAG Benchmark",
    "by": "emretheus · RAG evaluation",
    "url": "https://github.com/emretheus/jev-rag-benchmark",
    "en": "English RAG study separates frozen-pool reranking from frozen-context answer generation; gating analyses are exploratory, and free-tier gateway pacing is not isolated model latency.",
    "zh": "英文 RAG 研究区分固定候选池重排与固定上下文回答生成；门控分析属探索性，免费通道限速下的时延不等于模型推理耗时。"
  },
  {
    "category": "Tools",
    "title": "JevLang",
    "by": "TimMikeladze · policy and replay",
    "url": "https://github.com/TimMikeladze/JevLang",
    "tool_tasks": ["workflow"],
    "en": "TypeScript/Python policy layer separates typed model answers from routing and action dispatch, with documented journals and replay; a trace does not establish truthful inputs or calibrated thresholds.",
    "zh": "TypeScript／Python 策略层将类型化模型答案与路由、动作分发分开，提供日志与重放说明；可追溯记录不证明输入真实或阈值已校准。"
  },
  {
    "category": "Tools",
    "title": "sysone decision-learning library",
    "by": "sgaseretto · decision learning",
    "url": "https://github.com/sgaseretto/sysonelib",
    "tool_tasks": ["training"],
    "en": "Training, calibration and interpretation tools for several text, image and protein backends; documented compatibility checks and small experiments do not validate every backend or workload.",
    "zh": "提供多种文本、图像及蛋白质后端的训练、校准和解释工具；文档中的兼容检查与小实验不代表所有后端和任务已获验证。"
  },
  {
    "category": "Evaluations",
    "title": "Decision models as guardrails",
    "by": "raxIT Labs · partial public split",
    "url": "https://github.com/raxITlabs/decision-models-as-guardrails",
    "en": "Common policy benchmark compares decision models and managed guardrails with fixed scoring; an unpublished test slice prevents exact full-board reproduction from the public clone.",
    "zh": "用固定评分规则比较决策模型与托管护栏的共同策略基准；未发布的测试切片使公开克隆无法精确复现完整榜单。"
  },
  {
    "category": "Papers",
    "title": "Jev-Mobile: Jev as an Executor for Mobile GUI Agents",
    "by": "Zhang · 2026-09-24 · v1",
    "date": "2026-09-24",
    "first_submitted": "2026-09-24",
    "url": "https://arxiv.org/abs/2609.30186v1",
    "theme": "applications",
    "en": "Uses VLM local-goal planning with Jev action selection over Android accessibility-tree candidates; reported time and API-cost savings are conditional on successful trajectories and the tested controller configurations.",
    "zh": "用 VLM 规划局部目标，再由 Jev 从 Android 无障碍树候选中选动作；报告的时延和 API 成本节省仅针对成功轨迹及所测控制器配置。"
  },
  {
    "category": "Papers",
    "title": "JEV-Star: Fast, Low-Cost StarCraft II Control with Language-Model Planning",
    "by": "Ma, Zhao, Zeng & Zhao · 2026-09-23 · v1",
    "date": "2026-09-23",
    "first_submitted": "2026-09-23",
    "artifacts": {"code": "https://github.com/sc2musa/Jev_Star"},
    "url": "https://arxiv.org/abs/2609.27331v1",
    "theme": "applications",
    "en": "Combines Jev action selection with persistent language-model planning for StarCraft II; limited full-game evidence and simultaneous interface changes prevent isolating the planning contribution.",
    "zh": "在星际争霸 II 中结合 Jev 动作选择与持续的语言模型规划；完整对局证据有限，同时发生的接口变化使规划贡献无法单独归因。"
  },
  {
    "category": "Papers",
    "title": "Token-Efficient Multi-Agent Collaboration via System One-Guided Computational Division of Labor",
    "by": "Zhou et al. · 2026-10-06 · v1",
    "date": "2026-10-06",
    "first_submitted": "2026-10-06",
    "url": "https://arxiv.org/abs/2610.08155v1",
    "theme": "applications",
    "en": "Separates bounded multi-agent coordination from LLM reasoning through a controller–reader loop; reported GPT-4o-token and end-to-end latency reductions concern complete framework comparisons on seven benchmarks.",
    "zh": "通过控制器—读取器循环分离多智能体的有界协调与 LLM 推理；报告的 GPT-4o token 用量和端到端时延下降来自七个基准上的完整框架比较。"
  },
  {
    "category": "Tools",
    "title": "protoc-gen-jev",
    "by": "Buf · experimental generator · MIT",
    "url": "https://github.com/bufbuild/protoc-gen-jev",
    "tool_tasks": ["integration"],
    "en": "Generates typed Go, TypeScript and Python clients from annotated Protobuf schemas. Generator and runtime releases must be matched; backend behavior was not tested here.",
    "zh": "从带注释的 Protobuf 定义生成 Go、TypeScript 和 Python 类型化客户端；生成器与运行库需匹配版本，本项目未测试后端行为。"
  },
  {
    "category": "Evaluations",
    "title": "113-class complaint classification benchmark",
    "by": "Ariño de la Rubia · recorded-output analysis",
    "url": "https://github.com/earino/zero-shot-complaint-benchmark",
    "en": "Compares zero-shot, retrieval and trained classifiers using released predictions. Numeral tracing and analysis replay differ from retraining or new model calls.",
    "zh": "使用发布的预测比较零样本、检索及已训练分类器；数字溯源与分析重算不同于重新训练或调用模型。"
  },
  {
    "category": "Evaluations",
    "title": "Jev RAG Chinese Benchmark",
    "by": "Community evaluation · 100 queries · single run",
    "url": "https://github.com/vicfei/jev-rag-zh-benchmark",
    "en": "Chinese reranking comparison with fixed candidate pools and a pinned OpenRouter-served Jev version. Small single-run results and concurrent latency remain workload-specific.",
    "zh": "使用固定候选池和固定 OpenRouter 服务版本的 Jev 进行中文重排比较；小规模单次运行结果及并发时延限于该工作负载。"
  },
  {
    "category": "Guides",
    "title": "A Survey on Jev: Prior Research, Adaptation Costs, and Evidence of System One Models",
    "by": "Chen et al. · community survey v0.5",
    "url": "https://github.com/evan-py-chen/jev-survey",
    "en": "Survey manuscript connecting routing, label-probability readout and adaptation costs. The README abstract was inspected; this listing is not a full-manuscript review or empirical replication.",
    "zh": "综述手稿联系路由、标签概率读出与适配成本；本次检查了 README 摘要，收录不代表全文审阅或实证复现。"
  },
  {
    "category": "Guides",
    "title": "Jev Cookbook (Chinese)",
    "by": "Datawhale · CC BY-NC-SA 4.0",
    "url": "https://github.com/datawhalechina/jev-cookbook",
    "en": "Community Chinese course of eleven notebook chapters, from the three primitives and design patterns to 18 walkthroughs of official cookbook recipes, a smart-home experiment, a 231-question evaluation, agent integration and RLCD fine-tuning of the open Laya model; offline examples need no API key. Noncommercial license; documentation translations are unofficial.",
    "zh": "社区维护的中文课程，共十一章 Notebook：从三种原语与架构模式，到 18 篇官方配方复刻、智能家居实验、231 题评测、Agent 集成，以及用 RLCD 微调开源 Laya 模型；离线示例无需 API Key。采用非商业许可，文档中译为非官方翻译。"
  },
  {
    "category": "Papers",
    "title": "Benchmarking System One decision models against trained classifiers and language models for automated decision gates",
    "by": "Rafe & Das · 2026-10-06 · v2",
    "date": "2026-10-06",
    "first_submitted": "2026-09-29",
    "url": "https://arxiv.org/abs/2610.00346v2",
    "theme": "evaluation",
    "en": "A common-request harness compares typed decision models, generative readouts and trained classifiers; accuracy, selective coverage and out-of-scope acceptance depend on label access and task.",
    "zh": "用共同请求框架比较类型化决策模型、生成模型读出与训练分类器；准确率、选择性覆盖率和域外接纳取决于是否有任务标签及具体任务。"
  },
  {
    "category": "Papers",
    "title": "LLM-as-Jev: LLMs Are Already Jev-Style Decision Models -- When and How to Fine-Tune Them",
    "by": "Li & Wagle · 2026-10-13 · v3",
    "date": "2026-10-13",
    "first_submitted": "2026-10-01",
    "url": "https://arxiv.org/abs/2610.02076v3",
    "theme": "architectures",
    "en": "Compares frozen Qwen decision readouts with optional KL-anchored fine-tuning and budgeted reasoning; reported gains depend on backbone size and routing workload, not disclosure of hosted Jev internals.",
    "zh": "比较冻结 Qwen 的决策读出、带 KL 锚定的可选微调与限预算推理；所报收益依赖骨干规模和路由任务，并不揭示托管 Jev 内部实现。"
  },
  {
    "category": "Papers",
    "title": "HakemBench: A Turkish Benchmark of Typed Decisions",
    "by": "Teke · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "artifacts": {"code": ["https://github.com/ufakai/hakembench", "https://github.com/ufakai/ufakzeka-karar"], "data": "https://github.com/ufakai/hakembench", "model": "https://huggingface.co/ufakai/ufakzeka-karar"},
    "url": "https://arxiv.org/abs/2610.02293v1",
    "theme": "evaluation",
    "en": "Turkish typed-decision evaluation reports decision quality, Brier-based probability quality and risk–coverage alongside input probes; most labels are AI-derived, and the lab’s model used feedback from earlier test results.",
    "zh": "土耳其语类型化决策评测同时报告决策质量、基于 Brier 的概率质量、风险—覆盖及输入探查；多数标签由 AI 产生，实验室自身模型还使用过先前测试结果的反馈。"
  },
  {
    "publisher": "ufak AI",
    "license": "Apache-2.0",
    "category": "Models",
    "title": "ufakzeka-karar",
    "by": "ufak AI · Apache-2.0",
    "provenance": "modelcard",
    "url": "https://huggingface.co/ufakai/ufakzeka-karar",
    "en": "Turkish typed-decision checkpoint with shipped temperature scaling. Its card flags test-informed training and worsening support-task calibration; benchmark results are not blind.",
    "zh": "土耳其语类型化决策检查点，附温度缩放参数；模型卡标注训练参考了测试结果，并报告客服任务的校准恶化，基准结果并非盲测。"
  },
  {
    "category": "Papers",
    "title": "Just Ask Jev: Reinforcement Learning for Calibrated Decisions as a Zero-Shot Detector of AI Alignment Failures",
    "by": "Guo et al. · 2026-09-24 · v1",
    "date": "2026-09-24",
    "first_submitted": "2026-09-24",
    "artifacts": {"code": "https://github.com/sumleo/RLCDAlignBench", "data": "https://github.com/sumleo/RLCDAlignBench"},
    "url": "https://arxiv.org/abs/2609.29429v1",
    "theme": "robustness",
    "en": "Benchmarks Jev alignment-failure detection while separating question wording from input context; benchmark-scorer labels dominate, and context gains often depend on fields encoding the label.",
    "zh": "评测 Jev 对 AI 对齐失效的检测，分别改变提问与输入上下文；参考标签主要来自基准评分器，上下文收益常依赖编码标签的字段。"
  },
  {
    "category": "Evaluations",
    "title": "JevAdvBench analysis and evaluation code",
    "by": "MIT code · CC BY-NC 4.0 data",
    "url": "https://github.com/JevAdvBench/JevAdvBench",
    "en": "Recorded-response analysis and new API evaluations use identical-input reruns as a control. Most labels are model-derived; this project has not executed the analyses.",
    "zh": "提供已记录响应分析与新的 API 评测，以相同输入重跑作为对照。多数标签来自模型；本项目未运行这些分析。"
  },
  {
    "publisher": "Jeva authors",
    "license": "Not declared",
    "category": "Models",
    "title": "Jeva-4B",
    "by": "Jeva authors · license not declared",
    "provenance": "modelcard",
    "url": "https://huggingface.co/LIQIIIII/Jeva-4B",
    "en": "Author checkpoint with backbone, adapter and decision-head files. The inspected card declares no model license; weights have not been loaded or tested by this project.",
    "zh": "作者发布的检查点包，含骨干、适配器和决策头文件；所查模型卡未声明模型许可，本项目未加载或测试权重。"
  },
  {
    "category": "Evaluations",
    "title": "Reading Right, Acting Wrong — diagnostic dashboard",
    "by": "Li, Krishnan & Padman · author report",
    "url": "https://yubol-bobo.github.io/System_one_model_evaluation/",
    "en": "Interactive factual-probe and action-decision diagnostics. The current report covers 22 systems, distinct from the fixed paper’s 18; it is not a verified code or data release.",
    "zh": "交互式事实探查与动作决策诊断；当前报告覆盖22个系统，与固定论文的18个不同，不是经过核验的代码或数据发布。"
  },
  {
    "category": "Papers",
    "title": "Can Jev Judge Radiology Reports? Evaluating a System One Model for Clinical Factuality",
    "by": "Huang et al. · 2026-09-23 · v1",
    "date": "2026-09-23",
    "first_submitted": "2026-09-23",
    "url": "https://arxiv.org/abs/2609.27607v1",
    "theme": "applications",
    "en": "Jev checks support between generated and reference radiology reports in both directions; expert agreement depends on report size and error definitions and does not establish prospective clinical effectiveness.",
    "zh": "Jev 双向检查生成与参考放射学报告之间的陈述支持关系；与专家的一致性受报告长度和错误定义影响，并不证明前瞻性临床效果。"
  },
  {
    "category": "Papers",
    "title": "More Choices, Fewer Decisions: Ordinal-Scale Bias in JEV-like Direct-Decision Models",
    "by": "Gao et al. · 2026-10-14 · v2",
    "date": "2026-10-14",
    "first_submitted": "2026-09-30",
    "artifacts": {"code": "https://anonymous.4open.science/r/jev_ordinal_scale_bia/"},
    "url": "https://arxiv.org/abs/2609.38827v2",
    "theme": "calibration",
    "artifact_note": {"en": "anonymous mirror, expires 2027-04-10.", "zh": "匿名镜像，2027-04-10 到期。"},
    "en": "Audits ordinal label underuse across selected decision models; finer scales increase compression, while accuracy, final-label utilization and averaged candidate probabilities remain distinct measures.",
    "zh": "审查所选决策模型对有序标签的使用不足；细化量表会加重压缩，准确率、最终标签利用率和平均候选概率仍是不同测量。"
  },
  {
    "category": "Papers",
    "title": "Visual Jev: Accurate and Efficient Decisions from Shared Visual Context",
    "by": "Yu & Yao · 2026-09-22 · v1",
    "date": "2026-09-22",
    "first_submitted": "2026-09-22",
    "artifacts": {"code": "https://github.com/guanxuyu-sv/Visual-Jev"},
    "url": "https://arxiv.org/abs/2609.25845v1",
    "theme": "architectures",
    "en": "An independent visual decision architecture shares image context across batched questions using an LM-head readout; warm amortized speedups trade higher peak memory, while accuracy gains concentrate on trained task families.",
    "zh": "独立的视觉决策架构以语言模型头读出，让批处理问题共享图像上下文；预热后的摊销加速伴随更高峰值内存，准确率收益集中于训练覆盖的任务家族。"
  },
  {
    "category": "Papers",
    "title": "Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions",
    "by": "Wu & Lim · 2026-09-23 · v1",
    "date": "2026-09-23",
    "first_submitted": "2026-09-23",
    "url": "https://arxiv.org/abs/2609.28613v1",
    "theme": "robustness",
    "en": "Audits Jev injection on reconstructed InjecAgent cases, separating probability shifts from attacker-target selections; optimization results are checked on fresh calls, within this benchmark setting.",
    "zh": "在重构的 InjecAgent 案例中审查 Jev 提示注入，区分概率偏移与攻击目标选择；优化结果通过新调用验证，结论限于该基准设置。"
  },
  {
    "category": "Papers",
    "title": "JevOut: Natural Context Can Flip Decision Models",
    "by": "Xu et al. · 2026-10-08 · v2",
    "date": "2026-10-08",
    "first_submitted": "2026-09-24",
    "artifacts": {"code": "https://github.com/xzx34/JevOut"},
    "url": "https://arxiv.org/abs/2609.30243v2",
    "theme": "robustness",
    "en": "Optimizes context additions around unchanged questions and options in four decision systems; results concern initially correct decisions, and human validity checks cover a sampled subset of successful attacks.",
    "zh": "在四种决策系统中围绕不变的题目和选项优化上下文补充；结果针对原本答对的决策，人工有效性检查仅覆盖成功攻击的抽样子集。"
  },
  {
    "category": "Papers",
    "title": "JEV as a Judge for Agent Trace Security: An Empirical Comparison with Generative LLM Judges",
    "by": "Wang & Gao · 2026-09-28 · v1",
    "date": "2026-09-28",
    "first_submitted": "2026-09-28",
    "url": "https://arxiv.org/abs/2609.34862v1",
    "theme": "judging",
    "en": "Compares Jev and generative judges on retrospective agent-trace risk classification; dataset rankings vary, and successful-call latency and valid-judgment cost must be read with coverage.",
    "zh": "比较 Jev 与生成式评判模型对历史 agent 轨迹的风险分类；排名因数据集而异，成功调用耗时和有效判断成本需结合覆盖率解读。"
  },
  {
    "category": "Papers",
    "title": "Evaluating Decision Models for Text Annotation in Computational Social Science",
    "by": "Ibrahim & Zaki · 2026-09-23 · v2",
    "date": "2026-09-23",
    "first_submitted": "2026-09-21",
    "artifacts": {"code": "https://github.com/hazemibrahim97/decision-models-css"},
    "url": "https://arxiv.org/abs/2609.24574v2",
    "theme": "applications",
    "en": "Evaluates zero-shot social-science annotation and confidence-routed LLM cascades; lower costs coexist with task-dependent errors and overconfidence, so confidence cannot substitute for label validation.",
    "zh": "评估零样本社会科学标注与按置信度分流的 LLM 级联；低成本仍伴随任务相关误差和过度自信，置信度不能替代标签验证。"
  },
  {
    "category": "Papers",
    "title": "Jev for Scientific Decisions: Evaluating Semantic Choices and Their Consequences",
    "by": "Deng, Fan, Zhang & Xie · 2026-10-15 · v3",
    "date": "2026-10-15",
    "first_submitted": "2026-09-21",
    "artifacts": {"code": "https://github.com/bydeng01/scientific-decision-eval"},
    "url": "https://arxiv.org/abs/2609.24965v3",
    "theme": "applications",
    "en": "In ten prepared scientific cases, the authors separate semantic selections, computed quantities and final labels; comparison-model errors can be hidden by unchanged final labels.",
    "zh": "作者在十个预设科学案例中分别评估语义选择、计算得到的数值与最终标签；对比模型的错误可能被不变的最终标签掩盖。"
  },
  {
    "category": "Papers",
    "title": "Same Scores, Different Decisions: Evaluating JEV and Language Models for Legal Document Understanding",
    "by": "Zhang et al. · 2026-10-10 · v2",
    "date": "2026-10-10",
    "first_submitted": "2026-09-23",
    "artifacts": {"code": "https://github.com/ZF-Utokyo/Jev-Benchmark"},
    "url": "https://arxiv.org/abs/2609.27678v2",
    "theme": "applications",
    "en": "ContractNLI request variations can change which answers are wrong while aggregate accuracy stays unchanged; stable answers may preserve errors. This benchmark does not validate real legal deployment.",
    "zh": "ContractNLI 请求变化可能改变具体错误答案，而总体准确率保持不变；稳定答案也可能保留错误。该基准不能验证真实法律场景的部署有效性。"
  },
  {
    "category": "Papers",
    "title": "Jev in Medicine: A Benchmark Evaluation",
    "by": "Madrid-García & Merino-Barbancho · 2026-10-10 · v4",
    "date": "2026-10-10",
    "first_submitted": "2026-09-27",
    "artifacts": {"data": "https://zenodo.org/records/23008156"},
    "url": "https://arxiv.org/abs/2609.34024v4",
    "theme": "applications",
    "en": "Preliminary medical-benchmark evaluation of Jev 1.13 reports task-dependent accuracy, calibration and weak unanswerable-question detection; it does not establish clinical deployment validity.",
    "zh": "Jev 1.13 的初步医学基准评测报告了随任务变化的准确率、校准表现及较弱的不可回答问题识别能力；这不能证明临床部署有效性。"
  },
  {
    "category": "Papers",
    "title": "KITE: Scaling Jev Population Experiments with Sparse Flagship Calibration",
    "by": "Li · 2026-09-23 · v1",
    "date": "2026-09-23",
    "first_submitted": "2026-09-23",
    "artifacts": {"code": "https://github.com/HengyuLi-Ozaki-lab/kite_population_simulator"},
    "url": "https://arxiv.org/abs/2609.27535v1",
    "theme": "applications",
    "en": "Jev state tables and sparse flagship-model anchors support population simulations with shared human–model discrepancy estimates; larger simulations do not add human evidence or establish prospective intervention effects.",
    "zh": "Jev 状态表与少量强模型锚点支持纳入共享人—模型差异估计的群体模拟；扩大模拟规模不会增加人类证据，也不能确立前瞻性干预效果。"
  },
  {
    "category": "Papers",
    "title": "Beyond Answer Confidence: A Controlled Audit of Self-Knowledge in a Black-Box Decision Model",
    "by": "Shankaranarayana, Runje & Jannink · 2026-10-01 · v1",
    "date": "2026-10-01",
    "first_submitted": "2026-10-01",
    "artifacts": {"code": "https://github.com/Syntheme/beyond-answer-confidence"},
    "url": "https://arxiv.org/abs/2610.01006v1",
    "theme": "calibration",
    "en": "Controls information and surface cues to distinguish Jev answer confidence from self-knowledge; black-box behavior does not establish access to an internal knowledge state.",
    "zh": "通过控制信息与表面线索，区分 Jev 的答案置信度与是否知道答案的自评；黑盒表现并不证明能读取内部知识状态。"
  },
  {
    "category": "Papers",
    "title": "Specialized Decision Models vs. General-Purpose LLMs: Benchmarking Jev Across Knowledge, Reasoning, and Multilingual Tasks",
    "by": "Li et al. · 2026-10-08 · v1",
    "date": "2026-10-08",
    "first_submitted": "2026-10-08",
    "url": "https://arxiv.org/abs/2610.11978v1",
    "theme": "evaluation",
    "en": "Knowledge, reasoning and multilingual multiple-choice evaluation of Jev; reported rankings and mathematical weaknesses apply to the selected models and benchmarks.",
    "zh": "在知识、推理和多语言选择题中评测 Jev；报告的排名及数学弱点仅适用于所选模型与基准。"
  },
  {
    "category": "Papers",
    "title": "One Word Opens the Gate: The Option-Channel Attack on Typed Decision Models as Agent Guardrails",
    "by": "Azizi, Baghaei Potraghloo & Pedram · 2026-10-08 · v1",
    "date": "2026-10-08",
    "first_submitted": "2026-10-08",
    "artifacts": {"code": "https://github.com/ArminAzizi98/option-channel-attack"},
    "url": "https://arxiv.org/abs/2610.12292v1",
    "theme": "robustness",
    "en": "Tests option-channel attacks on seven open-weight models; reversed decisions can remain confident. The reported experiments do not test hosted Jev.",
    "zh": "测试七个开放权重模型的选项通道攻击；决策翻转后仍可能高置信。报告中的实验未测试托管 Jev。"
  },
  {
    "category": "Papers",
    "title": "Calibrated to Whom? Persona and Language Effects on Cultural Values in JEV",
    "by": "Asseri & Asseri · 2026-10-03 · v2",
    "date": "2026-10-03",
    "first_submitted": "2026-09-28",
    "url": "https://arxiv.org/abs/2609.36399v2",
    "theme": "evaluation",
    "en": "English/Arabic persona-conditioned Jev survey audit; the effects concern simulated respondents in one model, not measurements of real populations.",
    "zh": "对 Jev 进行英语和阿拉伯语人物设定条件下的问卷审查；观察的是单一模型的模拟受访者，并非对真实人群的测量。"
  },
  {
    "category": "Papers",
    "title": "Suggested Is Not Superseded: A Pre-Registered Evaluation of a System-One Model as a Memory-Retirement Gate",
    "by": "Chen & Le · 2026-10-11 · v1",
    "date": "2026-10-11",
    "first_submitted": "2026-10-11",
    "url": "https://arxiv.org/abs/2610.15710v1",
    "theme": "judging",
    "en": "Jev memory-retirement evaluation separates confirmed updates from suggestions; mixed LLM/human labels, shared errors and selection on a small development set constrain cascade claims.",
    "zh": "Jev 旧记忆停用评测区分已确认更新与变化暗示；LLM／人工混合标注、共享错误及小型开发集上的选择限制了级联收益主张。"
  },
  {
    "category": "Papers",
    "title": "Judges Follow the Reference: The Derivation Gap in Verifying Tool-Call Arguments",
    "by": "Ma et al. · 2026-10-13 · v1",
    "date": "2026-10-13",
    "first_submitted": "2026-10-13",
    "artifacts": {"code": "https://github.com/SarielMa/DeRef_release", "data": "https://huggingface.co/datasets/lm2445/DeRef"},
    "url": "https://arxiv.org/abs/2610.18497v1",
    "theme": "judging",
    "artifact_note": {"en": "model outputs are not included.", "zh": "不包含模型输出。"},
    "en": "Tool-argument judges including Jev reject some correct derived values without visible references; model-generated references are evaluated on three benchmarks.",
    "zh": "包括 Jev 在内的工具参数评判模型，在缺少可见参考时会拒绝部分正确推导值；模型生成的参考在三个基准上接受评测。"
  },
  {
    "category": "Papers",
    "title": "Typed Decision Models on Tabular Data",
    "by": "Zhang, Ye & Zha · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "artifacts": {"unverified": "code"},
    "url": "https://arxiv.org/abs/2610.19536v1",
    "theme": "evaluation",
    "en": "Tests classification and verification under content-preserving table rewrites across three task families; confidence can flag instability without proving correctness.",
    "zh": "在三类表格任务中检验保持内容不变的改写对分类与验证的影响；置信度可提示不稳定，但不证明正确性。"
  },
  {
    "category": "Papers",
    "title": "Selective Reasoning for Typed Decision Models: When to Start, Read, and Stop",
    "by": "Zheng & Chen · 2026-10-14 · v1",
    "date": "2026-10-14",
    "first_submitted": "2026-10-14",
    "artifacts": {"code": "https://github.com/binzheng-joey/selective-reasoning"},
    "url": "https://arxiv.org/abs/2610.19644v1",
    "theme": "judging",
    "artifact_note": {"en": "README inspected, not executed.", "zh": "仅检查 README，未执行。"},
    "en": "Gates reasoning start, candidate-answer reading and generation stopping; evidence is limited to a frozen Qwen backbone and three task families.",
    "zh": "控制推理启动、候选答案读取与生成停止的时机；证据限于冻结的 Qwen 骨干及三类任务。"
  },
  {
    "category": "Papers",
    "title": "Same-Number Citation Swaps: Stress-Testing Jev as a Financial Evidence Judge",
    "by": "Xu et al. · 2026-10-06 · v1",
    "date": "2026-10-06",
    "first_submitted": "2026-10-06",
    "url": "https://arxiv.org/abs/2610.08675v1",
    "theme": "robustness",
    "en": "Same-number citation swaps probe financial-evidence verification; rejecting wrong roles trades off with accepting equivalent support in a constructed test.",
    "zh": "以同数值引用替换检验金融证据验证；在构造测试中，识别财务项目错配与接受等价证据之间存在权衡。"
  },
  {
    category: "Papers",
    title: "REFLEX with Jev for Efficient Selective Control in LLM Agents",
    by: "Wu & Lim · 2026-09-22 · v1",
    date: "2026-09-22",
    first_submitted: "2026-09-22",
    url: "https://arxiv.org/abs/2609.26532v1",
    theme: "judging",
    en: "Confidence-gated Jev control with LLM fallback; gains depend on action alternatives and baseline routing.",
    zh: "以置信度控制 Jev 与 LLM 回退；收益取决于候选动作与基线路由。",
  },
  {
    category: "Papers",
    title: "Mnemon: Raw Records, Fast Judgments, Slow Thoughts",
    by: "Wang · 2026-09-28 · v1",
    date: "2026-09-28",
    first_submitted: "2026-09-28",
    artifacts: { code: "https://github.com/Grivn/mnemon-memory-agent" },
    url: "https://arxiv.org/abs/2609.36059v1",
    theme: "architectures",
    en: "Keeps raw memory records, separating Jev relevance judgments from LLM search planning and answer generation.",
    zh: "保留原始记忆记录，将 Jev 相关性判断与 LLM 检索规划、回答生成分开。",
  },
  {
    category: "Papers",
    title: "Bongard: Training Machine Intuition",
    by: "Ding, Jin & Ji · 2026-09-30 · v1",
    date: "2026-09-30",
    first_submitted: "2026-09-30",
    artifacts: { model: "https://huggingface.co/AgentBull/bongard-mini" },
    url: "https://arxiv.org/abs/2609.39111v1",
    theme: "architectures",
    en: "Shared evidence encoding and candidate-probability readout, trained with representation and action-outcome feedback.",
    zh: "共享证据编码与候选概率读出，结合表征学习和行动结果反馈训练。",
  },
  {
    category: "Papers",
    title: "VideoJev: System One Model for Video Understanding and Interaction",
    by: "Zhu et al. · 2026-10-13 · v1",
    date: "2026-10-13",
    first_submitted: "2026-10-13",
    artifacts: { page: "https://mcg-nju.github.io/VideoJev/" },
    url: "https://arxiv.org/abs/2610.18615v1",
    theme: "architectures",
    en: "Structured video decisions with temporal spans and candidate scores; cached and joint inference reuse visual computation.",
    zh: "以时间区间和候选分数表达视频决策，通过缓存与联合推理复用视觉计算。",
  },
  {
    category: "Papers",
    title: "Releasing the Inner Jev: A Simple Recipe for Open Decision Models",
    by: "Geuter, Cheng & Alvarez-Melis · 2026-10-12 · v1",
    date: "2026-10-12",
    first_submitted: "2026-10-12",
    artifacts: { code: "https://github.com/j-geuter/jeff-serve", data: "https://huggingface.co/datasets/jgeuter/OpenDecisions" },
    url: "https://arxiv.org/abs/2610.17205v1",
    theme: "architectures",
    en: "Answer-letter readout and supervised LoRA baselines; evaluation includes model-generated labels.",
    zh: "答案字母概率读出与监督式 LoRA 基线；评测包含模型生成的标签。",
  },
  {
    category: "Papers",
    title: "SanSi: A Looped Typed Decision Model for System 1.5 Thinking",
    by: "Gan, Lee & Kang · 2026-10-10 · v2",
    date: "2026-10-10",
    first_submitted: "2026-10-06",
    artifacts: { code: "https://github.com/minnesotanlp/Sansi" },
    url: "https://arxiv.org/abs/2610.07730v2",
    theme: "architectures",
    artifact_note: {en: "covering part of the paper's experiments.", zh: "覆盖论文的部分实验。"},
    en: "Looped hidden-state computation for typed decisions; additional loops trade compute for accuracy.",
    zh: "通过隐状态循环计算输出类型化决策；额外循环以计算成本换取准确率。",
  },
  {
    category: "Papers",
    title: "JevCascade: Readout Stability and Inference-Time Compute Allocation for Prefill-Only Decision Models",
    by: "Li & Chen · 2026-10-10 · v2",
    date: "2026-10-10",
    first_submitted: "2026-10-06",
    artifacts: { code: "https://github.com/rlisml/jev-cascade", data: "https://github.com/rlisml/jev-cascade" },
    url: "https://arxiv.org/abs/2610.07716v2",
    theme: "judging",
    en: "Candidate-menu interventions and confidence cascades; ranking stability does not establish probability calibration.",
    zh: "研究候选集合干预与置信度级联；排序稳定性并不等同概率校准。",
  },
  {
    category: "Papers",
    title: "JevSpawn: Adaptive Agentic Inference through Compositional Action Spaces",
    by: "Su & Huang · 2026-09-30 · v1",
    date: "2026-09-30",
    first_submitted: "2026-09-30",
    artifacts: { code: "https://github.com/Hoyant-Su/JevSpawn" },
    url: "https://arxiv.org/abs/2610.00437v1",
    theme: "architectures",
    en: "Composes finite action fields and explores alternatives using interaction feedback.",
    zh: "组合有限行动字段，利用交互反馈探索候选路径。",
  },
  {
    category: "Papers",
    title: "MetaEncoder: Exploring the Limit of Bi-Encoders for Multimodal System One Decision Making with Natural Language Interface",
    by: "Cheng et al. · 2026-10-08 · v1",
    date: "2026-10-08",
    first_submitted: "2026-10-08",
    artifacts: { code: "https://github.com/facebook/meta-encoder-eval" },
    url: "https://arxiv.org/abs/2610.11316v1",
    theme: "architectures",
    en: "Bi-encoder approach to multimodal decisions and retrieval through natural-language interfaces.",
    zh: "通过自然语言接口实现多模态决策与检索的双编码器方法。",
  },
  {
    category: "Papers",
    title: "Reading Right, Acting Wrong: Diagnosing Decision Failures of System One Models in Agent Loops",
    by: "Li, Krishnan & Padman · 2026-10-13 · v1",
    date: "2026-10-13",
    first_submitted: "2026-10-13",
    artifacts: { page: "https://yubol-bobo.github.io/System_one_model_evaluation/" },
    url: "https://arxiv.org/abs/2610.18579v1",
    theme: "evaluation",
    en: "Pairs factual probes with action choices to diagnose decision failures.",
    zh: "将事实探针与行动选择配对，诊断决策失败。",
  },
  {
    category: "Papers",
    title: "DecisionRobust: Benchmarking Robustness for JEV Style Decision Models Across Text and Vision",
    by: "Lan et al. · 2026-10-13 · v1",
    date: "2026-10-13",
    first_submitted: "2026-10-13",
    artifacts: { code: "https://github.com/Yifan-Lan/DecisionRobust", page: "https://yifan-lan.github.io/DecisionRobust/" },
    url: "https://arxiv.org/abs/2610.19118v1",
    theme: "robustness",
    en: "Text and vision attacks with label-validity checks and held-out evaluation models.",
    zh: "结合标签有效性检查与留出评测模型，考察文本和视觉攻击。",
  },
  {
    category: "Papers",
    title: "Type-Safe Is Not Error-Free: Typed Decision Models Follow the Option Name, Not the Definition Bound to It",
    by: "Sun, Xu, Shi & Yang · 2026-10-08 · v3",
    date: "2026-10-08",
    first_submitted: "2026-09-22",
    url: "https://arxiv.org/abs/2609.26758v3",
    theme: "robustness",
    en: "Tests conflicts between option names and definitions despite structurally valid outputs.",
    zh: "检验输出结构合法时，选项名称与定义之间的冲突。",
  },
  {
    category: "Papers",
    title: "AnyJev Technical Report",
    by: "Zhang et al. · 2026-09-30 · v1",
    date: "2026-09-30",
    first_submitted: "2026-09-30",
    artifacts: { code: "https://github.com/nokia-applied-research/AnyJev" },
    url: "https://arxiv.org/abs/2610.00831v1",
    theme: "calibration",
    en: "Training-free decision readout with label-prior and option-order correction.",
    zh: "无需训练的决策读出，修正标签先验与选项顺序偏差。",
  },
  {
    category: "Papers",
    title: "LAVOIR: Teaching a Single-Pass Decision Encoder When and What to Ask with Amortized Value of Information",
    by: "Yilmaz, Tasdemir & Gozay · 2026-09-25 · v1",
    date: "2026-09-25",
    first_submitted: "2026-09-25",
    artifacts: { code: "https://github.com/moganai/lavoir", model: "https://huggingface.co/moganai/lavoir" },
    url: "https://arxiv.org/abs/2609.30706v1",
    theme: "judging",
    en: "Estimates whether asking for missing information would improve a typed decision.",
    zh: "估计追问缺失信息是否有助于改进类型化决策。",
  },
  {
    category: "Papers",
    title: "General Decision Models: Benchmarking and Insights Beyond Jev",
    by: "Duan et al. · 2026-10-12 · v2",
    date: "2026-10-12",
    first_submitted: "2026-10-02",
    artifacts: { code: "https://github.com/amazingljy1206/SII-Decision", data: "https://huggingface.co/datasets/carlosxiang/JEVal" },
    url: "https://arxiv.org/abs/2610.03935v2",
    theme: "evaluation",
    en: "Bilingual decision evaluation and reliability when local decisions compose into larger systems.",
    zh: "双语决策评估，以及局部决策组合成更大系统时的可靠性。",
  },
  {
    category: "Papers",
    title: "JevAgentHarness: Benchmarking, Deploying and Training Decision Models That Share Control with LLMs",
    by: "Zhu et al. · 2026-10-15 · v1",
    date: "2026-10-15",
    first_submitted: "2026-10-15",
    artifacts: { code: "https://github.com/JevAgentHarness/JevAgentHarness" },
    url: "https://arxiv.org/abs/2610.21412v1",
    theme: "judging",
    en: "Studies fitted confidence thresholds for sharing agent control with decision models.",
    zh: "研究通过拟合置信度阈值，让决策模型参与 agent 控制。",
  },
  {
    "category": "Datasets",
    "title": "evalsafe-invoice-processing",
    "by": "TypeSafe · WorkflowEvals",
    "provenance": "official",
    "url": "https://huggingface.co/datasets/typesafeAI/evalsafe-invoice-processing",
    "en": "Official dataset for the invoice-processing workflow evaluation.",
    "zh": "官方发票处理工作流评测数据集。"
  },
  {
    "category": "Datasets",
    "title": "evalsafe-customer-service",
    "by": "TypeSafe · WorkflowEvals",
    "provenance": "official",
    "url": "https://huggingface.co/datasets/typesafeAI/evalsafe-customer-service",
    "en": "Official dataset for the customer-service workflow evaluation.",
    "zh": "官方客户服务工作流评测数据集。"
  },
  {
    "category": "Datasets",
    "title": "evalsafe-security-incidents",
    "by": "TypeSafe · WorkflowEvals",
    "provenance": "official",
    "url": "https://huggingface.co/datasets/typesafeAI/evalsafe-security-incidents",
    "en": "Official dataset for the security-incident workflow evaluation.",
    "zh": "官方安全事件工作流评测数据集。"
  },
  {
    "category": "Datasets",
    "title": "evalsafe-agent-trace-observability",
    "by": "TypeSafe · WorkflowEvals",
    "provenance": "official",
    "url": "https://huggingface.co/datasets/typesafeAI/evalsafe-agent-trace-observability",
    "en": "Official evaluation dataset for the agent-trace observability workflow.",
    "zh": "官方 agent 轨迹观测工作流评测数据集。"
  },
  {
    "category": "Datasets",
    "title": "Bekko System One Dataset v0",
    "by": "hotchpotch · Training mixture",
    "provenance": "community",
    "url": "https://huggingface.co/datasets/hotchpotch/bekko-system-one-dataset-v0",
    "en": "A community training mixture for System One-style decision models. Read the card for its composition and usage conditions.",
    "zh": "面向 System One 风格决策模型的社区训练混合数据；组成与使用条件见数据卡。"
  },
  {
    "category": "Datasets",
    "title": "Bespoke Nimble 9B v3 — Decision Index runs",
    "by": "Bespoke Labs · Evaluation archive",
    "provenance": "community",
    "url": "https://huggingface.co/datasets/bespokelabs/bespoke-nimble-9b-v3-decision-index",
    "en": "An archive of Decision Index evaluation runs for Bespoke Nimble 9B v3.",
    "zh": "Bespoke Nimble 9B v3 在 Decision Index 上的评测运行归档。"
  },
  {
    category: "Papers",
    title:
      "this-that-model-1.0: A typed decision model that decides in 30 ms, for a millionth of a cent",
    by: "Cheng, Dai & Sun · 2026-09-20 · v1",
    date: "2026-09-20",
    first_submitted: "2026-09-20",
    artifacts: { code: "https://github.com/FLock-io/this-that-model", data: "https://huggingface.co/datasets/limberc/this-that-spatial-bench", model: "https://huggingface.co/flock-io/this-that-model-1.0" },
    url: "https://arxiv.org/abs/2609.23886v1",
    theme: "architectures",
    en: "An open typed-decision model using hidden-state readout. The abstract reports a small external comparison.",
    zh: "采用隐藏状态读出的开放类型化决策模型。摘要报告了一项小规模外部比较。",
  },
  {
    category: "Papers",
    title: "Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents",
    by: "Jiang, Li & Li · 2026-09-21 · v1",
    date: "2026-09-21",
    first_submitted: "2026-09-21",
    artifacts: { code: "https://github.com/libingzheren/Jev-Mem" },
    url: "https://arxiv.org/abs/2609.23986v1",
    theme: "architectures",
    en: "Studies Jev as a controller for agent memory. Reported outcomes concern the complete memory workflow.",
    zh: "研究以 Jev 控制 agent 记忆；报告结果衡量完整记忆工作流。",
  },
  {
    category: "Papers",
    title:
      "From Text Decisions to Pixels: An Study of Jev-Style Visual Choice Model",
    by: "Zhou, Yang & Zhao · 2026-09-24 · v1",
    date: "2026-09-24",
    first_submitted: "2026-09-24",
    url: "https://arxiv.org/abs/2609.29283v1",
    theme: "architectures",
    en: "A Jev-style visual-choice study separating adaptation gains, candidate-readout validity, and calibration limits.",
    zh: "Jev 风格视觉选择模型研究，区分适配收益、候选读出有效性与校准局限。",
  },
  {
    category: "Papers",
    title:
      "JevAdvBench: A Benchmark and Black-Box Attacks for Reinforcement Learning for Calibrated Decisions Models",
    by: "Hu et al. · 2026-09-25 · v1",
    date: "2026-09-25",
    first_submitted: "2026-09-25",
    artifacts: { code: "https://github.com/JevAdvBench/JevAdvBench", data: "https://huggingface.co/datasets/Hangtao/JevAdvBench" },
    url: "https://arxiv.org/abs/2609.31142v1",
    theme: "robustness",
    en: "A black-box adversarial benchmark. A changed decision is not necessarily an incorrect decision.",
    zh: "黑盒对抗评测基准。决策发生变化，并不必然代表决策错误。",
  },
  {
    category: "Papers",
    title:
      "Beyond Calibration: Do a Typed-Decision Model's Probabilities Obey the Probability Axioms?",
    by: "Li, He & Li · 2026-09-27 · v1",
    date: "2026-09-27",
    first_submitted: "2026-09-27",
    artifacts: { code: "https://github.com/bro789/typed-decision-coherence" },
    url: "https://arxiv.org/abs/2609.33209v1",
    theme: "calibration",
    en: "Tests coherence between logically related probabilities, separately from accuracy and calibration.",
    zh: "检验逻辑相关命题的概率一致性，与准确率和校准分别考察。",
  },
  {
    category: "Papers",
    title:
      "Evaluating System One Models for Agent Security Decisions: Reliability, Calibration, and Selective Automation",
    by: "Liu · 2026-10-03 · v3",
    date: "2026-10-03",
    first_submitted: "2026-09-27",
    artifacts: { code: "https://github.com/yxsec/system-one-security-eval" },
    url: "https://arxiv.org/abs/2609.33401v3",
    theme: "robustness",
    en: "Examines reliability, group-specific confident errors, and selective automation in security decisions.",
    zh: "研究安全决策中的可靠性、不同群体的高置信错误与选择性自动化。",
  },
  {
    category: "Papers",
    title:
      "Jev thinks “I don't know”, but doesn't say it: Introducing Sys1Cal-v1 Dataset for Probability Calibration",
    by: "Porcedda · 2026-09-28 · v1",
    date: "2026-09-28",
    first_submitted: "2026-09-28",
    artifacts: { code: "https://github.com/little-g-ai/Sys1Cal-v1", data: "https://github.com/little-g-ai/Sys1Cal-v1" },
    url: "https://arxiv.org/abs/2609.35342v1",
    theme: "calibration",
    en: "A controlled calibration study using constructed probabilities. Interpretations of latent uncertainty remain hypotheses.",
    zh: "使用构造概率进行受控校准测试；对潜在不确定性的解释仍属研究假说。",
  },
  {
    category: "Papers",
    title: "Chinese-Jev: Bringing System One Model to Chinese-Language Tasks",
    by: "Wang et al. · 2026-09-29 · v1",
    date: "2026-09-29",
    first_submitted: "2026-09-29",
    artifacts: { code: "https://github.com/gulucaptain/Chinese-Jev", data: ["https://huggingface.co/datasets/bbldCVer-hf/CJ-Bench", "https://huggingface.co/datasets/bbldCVer-hf/CJ-Dataset"] },
    url: "https://arxiv.org/abs/2609.36965v1",
    theme: "architectures",
    en: "A Chinese typed-decision model and proposed benchmark; domain-specific training calls for independent validation.",
    zh: "面向中文的类型化决策模型与新基准；领域专用训练的效果仍需独立验证。",
  },
  {
    category: "Papers",
    title: "Jeva: System One Models from First Principles",
    by: "Li & Wang · 2026-10-13 · v1",
    date: "2026-10-13",
    first_submitted: "2026-10-13",
    artifacts: { code: "https://github.com/LiQiiiii/Jeva", model: "https://huggingface.co/LIQIIIII/Jeva-4B" },
    url: "https://arxiv.org/abs/2610.18773v1",
    theme: "architectures",
    en: "A decision-model architecture exploring null handling, option permutations, scaling, and caching. Its design is Jeva’s, not Jev’s disclosed internals.",
    zh: "探索空答案、选项排列、规模扩展与缓存的决策架构。这是 Jeva 的设计，并非 Jev 已披露的内部实现。",
  },
  {
    category: "Papers",
    title: "System1-Arena: Which Decisions Can Be Left to System 1?",
    by: "Chen et al. · 2026-10-15 · v1",
    date: "2026-10-15",
    first_submitted: "2026-10-15",
    artifacts: { code: "https://github.com/TianyuCodings/S1-Arena", data: "https://huggingface.co/datasets/C-Tianyu/S1-Arena" },
    url: "https://arxiv.org/abs/2610.21244v1",
    theme: "evaluation",
    en: "A benchmark spanning matched requests and closed-loop tasks. Experiments have not been reproduced here.",
    zh: "涵盖匹配请求与闭环任务的基准；本项目尚未复现其实验。",
  },
  {
    "publisher": "convaiinnovations",
    "license": "Apache-2.0",
    category: "Models",
    title: "Laya",
    by: "convaiinnovations · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/convaiinnovations/laya",
    en: "An encoder-based decision family with English, multilingual, and workflow-specific checkpoints.",
    zh: "基于编码器的决策模型家族，包含英语、多语言与工作流专用检查点。",
  },
  {
    "publisher": "Jared Palmer",
    "license": "Apache-2.0",
    category: "Models",
    title: "Kev-4B",
    by: "Jared Palmer · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/jaredpalmer/kev-4b",
    en: "A Qwen3.5-4B-Base LoRA adapter and pointer head for decisions over documents and typed questions.",
    zh: "基于 Qwen3.5-4B-Base 的 LoRA 适配器与指针头，面向文档与类型化问题的决策。",
  },
  {
    "publisher": "Bespoke Labs",
    "license": "CC BY-NC 4.0",
    category: "Models",
    title: "Bespoke Nimble 9B v3",
    by: "Bespoke Labs · CC BY-NC 4.0",
    provenance: "modelcard",
    url: "https://huggingface.co/bespokelabs/Bespoke-Nimble-9B-v3",
    en: "A Qwen3.5-9B LoRA adapter returning candidate probabilities. Released under a noncommercial license.",
    zh: "返回候选项概率的 Qwen3.5-9B LoRA 适配器；采用非商业用途许可。",
  },
  {
    "publisher": "InternLM",
    "license": "Apache-2.0",
    category: "Models",
    title: "Intern-Decision-4B",
    by: "InternLM · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/internlm/Intern-Decision-4B",
    en: "A decision-tuned Qwen checkpoint with a structured inference wrapper and image support.",
    zh: "经过决策微调的 Qwen 检查点，提供结构化推理封装并支持图片输入。",
  },

  {
    "publisher": "Fastino",
    "license": "Apache-2.0",
    category: "Models",
    title: "GLiNER2.5-Decide",
    by: "Fastino · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/fastino/GLiNER2.5-Decide",
    en: "A 340M English classifier with runtime label sets and single-label or multi-label decisions.",
    zh: "340M 英语分类模型，支持调用时指定标签集合，以及单标签和多标签决策。",
  },
  {
    "publisher": "vLLM Semantic Router",
    "license": "Apache-2.0",
    category: "Models",
    title: "d3",
    by: "vLLM Semantic Router · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/vllm-sr/d3",
    en: "A text, image, and video decision model with Choice, Yes/No, and Score outputs.",
    zh: "支持文本、图片与视频的决策模型，提供 Choice、Yes/No 与 Score 输出。",
  },
  {
    "publisher": "Cloudflare",
    "license": "Apache-2.0",
    category: "Models",
    title: "Clef",
    by: "Cloudflare · Apache-2.0",
    provenance: "modelcard",
    url: "https://huggingface.co/Cloudflare/clef",
    en: "A multimodal model with a joint schema head, returning probabilities over allowed answers.",
    zh: "使用联合 schema 预测头的多模态模型，返回允许答案集合上的概率。",
  },
  {
    category: "Papers",
    title: "Evaluating and Benchmarking the System One Model Jev",
    by: "Deußer, Sparrenberg & Sifa · 2026-09-29 · v1",
    date: "2026-09-29",
    first_submitted: "2026-09-29",
    artifacts: { code: "https://github.com/AppliedMachineLearning-Lab/jev-benchmarking" },
    url: "https://arxiv.org/abs/2609.37647v1",
    theme: "evaluation",
    en: "An early benchmark study of Jev. Read the task selection and evaluation setup alongside its reported results.",
    zh: "Jev 的早期基准研究。阅读报告结果时，同时检查任务选择与评测设置。",
  },
  {
    category: "Papers",
    title:
      "Typed Decision Models: An Early Evidence Audit and Evaluation Checklist",
    by: "Tang & Zheng · 2026-09-26 · v1",
    date: "2026-09-26",
    first_submitted: "2026-09-26",
    url: "https://arxiv.org/abs/2609.32160v1",
    theme: "evaluation",
    en: "An evidence audit and a checklist for evaluating typed decision models.",
    zh: "围绕类型化决策模型的证据审查与评估清单。",
  },
  {
    category: "Papers",
    title:
      "Same Attack, Different Judge: A First Controlled Adversarial Comparison of Jev, LLM Judges, and Purpose-Built Safety Classifiers",
    by: "Li, Huang, Zhang & Liu · 2026-10-13 · v1",
    date: "2026-10-13",
    first_submitted: "2026-10-13",
    url: "https://arxiv.org/abs/2610.17820v1",
    theme: "robustness",
    en: "A controlled adversarial comparison of Jev, LLM judges, and purpose-built safety classifiers.",
    zh: "对 Jev、LLM 评判模型与专用安全分类器进行受控对抗比较。",
  },
  {
    category: "Papers",
    title:
      "JEV versus LLMs: Accuracy, Cost and Calibration on Seven Political Science Replications",
    by: "Denney & DiGiuseppe · 2026-10-06 · v2",
    date: "2026-10-06",
    first_submitted: "2026-10-05",
    url: "https://arxiv.org/abs/2610.06625v2",
    theme: "evaluation",
    en: "Studies accuracy, cost, and calibration in seven political-science replication tasks.",
    zh: "在七项政治学复现任务中考察准确率、成本与校准。",
  },
  {
    category: "Papers",
    title: "JEV-as-a-Judge: Accept When Confident, Escalate When Unsure",
    by: "Li, Miao, Krishnan & Padman · 2026-10-09 · v5",
    date: "2026-10-09",
    first_submitted: "2026-09-22",
    artifacts: { page: "https://yubol-bobo.github.io/jev-as-a-judge/" },
    url: "https://arxiv.org/abs/2609.26550v5",
    theme: "judging",
    en: "Studies confidence-based escalation from Jev to a reasoning judge, including limits under distribution shift.",
    zh: "研究基于置信度从 Jev 升级到推理评判模型的方法，以及分布变化下的局限。",
  },
  {
    category: "Papers",
    title:
      "Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places",
    by: "Rao & Callison-Burch · 2026-10-13 · v3",
    date: "2026-10-13",
    first_submitted: "2026-09-24",
    url: "https://arxiv.org/abs/2609.29769v3",
    theme: "judging",
    en: "Compares rubric judges and examines correlated errors that can limit cascade improvements.",
    zh: "比较评分准则评判模型，考察相关错误如何限制级联系统的收益。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "TypeSafe Python SDK",
    by: "Python · MIT",
    url: "https://github.com/typesafe-ai/typesafe-sdk-python",
    "tool_tasks": ["integration"],
    en: "The official sync and async client for typed Jev questions and answers.",
    zh: "官方 Python 同步与异步客户端，支持类型化问题和答案。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "TypeSafe JavaScript SDK",
    by: "TypeScript / JavaScript · MIT",
    url: "https://github.com/typesafe-ai/typesafe-sdk-js",
    "tool_tasks": ["integration"],
    en: "The official JavaScript client with answer types inferred from your questions.",
    zh: "官方 JavaScript 客户端，可根据问题推导答案类型。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "System One Adapter",
    by: "Python · MIT",
    url: "https://github.com/typesafe-ai/system-one-adapter-python",
    "tool_tasks": ["training"],
    en: "Compare LLMs through the same question interface, with probability outputs and request diagnostics.",
    zh: "用相同问题接口比较 LLM，支持概率输出与请求诊断。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "TypeSafe Agent Skills",
    by: "Coding agents · MIT",
    url: "https://github.com/typesafe-ai/skills",
    "tool_tasks": ["integration"],
    en: "Official guidance for coding agents building with the System One API.",
    zh: "帮助编码 agent 使用 System One API 的官方技能。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "TypeSafe Public Examples",
    by: "Cookbooks & demos · MIT",
    url: "https://github.com/typesafe-ai/typesafe-public-examples",
    "tool_tasks": ["integration", "workflow"],
    en: "Source code accompanying official documentation, demos, and cookbooks.",
    zh: "官方文档、演示与实践教程配套源代码。",
  },
  {
    provenance: "official",
    category: "Tools",
    title: "TypeSafe for n8n",
    by: "Workflow integration · MIT",
    url: "https://github.com/typesafe-ai/n8n-nodes-typesafe-ai",
    "tool_tasks": ["workflow"],
    en: "TypeSafe-maintained nodes for adding typed decisions to n8n workflows.",
    zh: "由 TypeSafe 维护的 n8n 节点，用于将类型化决策加入工作流。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Introducing System One Models & Jev",
    by: "TypeSafe · September 15, 2026",
    url: "https://typesafe.ai/blog/introducing-system-one-models-and-jev",
    en: "The launch article. A primary source for the provider’s design claims and their stated caveats.",
    zh: "发布文章：了解厂商设计主张及其限定条件的一手来源。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Jev: For the builders AND dreamers",
    by: "TypeSafe · 2026-10-14 · jev-1.14.0",
    url: "https://typesafe.ai/blog/jev-1-14",
    en: "Release notes for jev-1.14.0 under jev-preview: opt-in header flags for images (also on jev-1.13.0) and long context, Box for 1.14 only, and the deprecation-notice plan. Its intelligence chart is provider-run and, by its own account, likely biased toward TypeSafe’s models.",
    zh: "jev-1.14.0 的官方发布说明（经 jev-preview 提供）：图像（jev-1.13.0 同样可用）与长上下文须通过请求头开关启用，Box 仅限 1.14，并说明弃用前的通知安排。文中的能力对比由厂商自行测得，且自称可能偏向自家模型。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Primitives: Choice, Score, Noul",
    by: "API concepts",
    url: "https://docs.typesafe.ai/primitives",
    en: "Choose between categorical decisions, ordered ratings, and yes/no probabilities.",
    zh: "了解闭集选择、有序评分与是非概率三类决策原语。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Confidence",
    by: "Probability & routing",
    url: "https://docs.typesafe.ai/confidence",
    en: "How confidence is derived from a distribution, and how it differs from probability.",
    zh: "解释置信度的计算方式，以及它与概率的区别。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Jev 1.13 Jaggedness",
    by: "Limitations · reviewed October 2, 2026",
    url: "https://docs.typesafe.ai/model-jaggedness/jev-1.13",
    en: "Documented limitations: numeric precision, long irrelevant context, adversarial inputs, and option-order sensitivity.",
    zh: "已知局限：数值精度、无关长上下文、对抗输入与选项顺序敏感性。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Guardrails for LLMs",
    by: "Official cookbook",
    url: "https://docs.typesafe.ai/cookbooks/llm_guardrails",
    en: "Combine narrow risk questions with application rules for passing, reviewing, or blocking content.",
    zh: "用多个风险问题配合应用规则，对内容放行、复核或拦截。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Double-checking Citations",
    by: "Official cookbook",
    url: "https://docs.typesafe.ai/cookbooks/citation_check",
    en: "Check whether a citation’s source context supports a claim.",
    zh: "检查引文的来源上下文是否支持相关主张。",
  },
  {
    provenance: "official",
    category: "Guides",
    title: "Hierarchical Classification",
    by: "Official cookbook",
    url: "https://docs.typesafe.ai/cookbooks/hierarchical_classification",
    en: "Use Choice probabilities to explore deep classification trees.",
    zh: "使用 Choice 概率探索多层分类树。",
  },
  {
    category: "Evaluations",
    title: "Jev Decision Index",
    by: "Hugging Face · community",
    provenance: "community",
    url: "https://huggingface.co/spaces/multimodalart/jev-decision-index",
    en: "A community index of decision models and evaluations. Full rankings include private tests.",
    zh: "决策模型与评测的社区索引；完整排名包含私有测试。",
  },
  {
    provenance: "official",
    category: "Evaluations",
    title: "Workflow Evals",
    by: "Interactive evaluation explorer",
    url: "https://evals.typesafe.ai/",
    en: "Inspect four structured workflows. Scores measure agreement with model-generated references.",
    zh: "查看四类结构化工作流。分数衡量与模型生成参考结果的一致性。",
  },
  {
    provenance: "official",
    category: "Evaluations",
    title: "WorkflowEvals — Code",
    by: "Python · Apache-2.0",
    url: "https://github.com/typesafe-ai/WorkflowEvals",
    en: "The official evaluation runner, workflow definitions, scoring, and plotting tools.",
    zh: "官方评测运行器、工作流定义、评分与绘图工具。",
  },
  {
    category: "Evaluations",
    title: "WorkflowEvals — Datasets",
    by: "Hugging Face · four datasets",
    url: "https://huggingface.co/collections/typesafeAI/workflowevals",
    en: "Published cases, model-generated references, and recorded runs for inspecting reproducibility.",
    zh: "公开案例、模型生成的参考标签与运行记录，便于检查可复现性。",
    provenance: "official",
  },
  {
    category: "Foundations",
    title: "Strictly Proper Scoring Rules, Prediction, and Estimation",
    by: "Gneiting & Raftery · JASA 2007 · Author PDF",
    url: "https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf",
    en: "A foundation for evaluating and incentivizing honest probabilistic predictions.",
    zh: "评估概率预测与鼓励诚实概率表达的理论基础。",
  },
  {
    category: "Foundations",
    title: "On Calibration of Modern Neural Networks",
    by: "Guo et al. · ICML 2017",
    url: "https://proceedings.mlr.press/v70/guo17a.html",
    en: "A practical reference for calibration and temperature scaling.",
    zh: "概率校准与温度缩放的经典参考。",
  },
  {
    category: "Foundations",
    title: "SelectiveNet",
    by: "Geifman & El-Yaniv · ICML 2019",
    url: "https://proceedings.mlr.press/v97/geifman19a.html",
    en: "Studies prediction with a reject option and the trade-off between coverage and risk.",
    zh: "研究带拒绝选项的预测，以及覆盖率与风险之间的关系。",
  },
  {
    category: "Foundations",
    title: "Language Models (Mostly) Know What They Know",
    by: "Kadavath et al. · 2022",
    url: "https://arxiv.org/abs/2207.05221",
    en: "An investigation of language models’ self-evaluation and uncertainty.",
    zh: "研究语言模型的自我评估与不确定性。",
  },
  {
    category: "Foundations",
    title: "LMQL — Prompting Is Programming",
    by: "Beurer-Kellner et al. · PLDI 2023",
    url: "https://www.sri.inf.ethz.ch/publications/beurerkellner2023prompting",
    en: "A programming-language approach to constrained language-model interaction.",
    zh: "以编程语言方式组织受约束的语言模型交互。",
  },
  {
    category: "Foundations",
    title: "XGrammar",
    by: "Dong et al. · MLSys 2025",
    url: "https://arxiv.org/abs/2411.15100",
    en: "Efficient grammar-constrained generation: a useful comparison point for typed outputs.",
    zh: "高效语法约束生成，为理解类型化输出提供比较背景。",
  },
  {
    category: "Foundations",
    title: "DSPy",
    by: "Khattab et al. · ICLR 2024",
    url: "https://arxiv.org/abs/2310.03714",
    en: "Declarative language-model programs and pipeline optimization.",
    zh: "声明式语言模型程序与流水线优化。",
  },
  {
    category: "Foundations",
    title: "SGLang",
    by: "Zheng et al. · NeurIPS 2024",
    url: "https://papers.nips.cc/paper_files/paper/2024/file/724be4472168f31ba1c9ac630f15dec8-Paper-Conference.pdf",
    en: "Efficient execution of structured language-model programs.",
    zh: "结构化语言模型程序的高效执行。",
  },
  {
    "category": "Evaluations",
    "title": "Artificial Analysis Decision Index",
    "by": "Artificial Analysis · Methodology v1.0",
    "provenance": "independent",
    "url": "https://artificialanalysis.ai/evaluations/artificial-analysis-decision-index",
    "en": "External evaluation of classification, tool calling, knowledge and reasoning. The suite includes private questions.",
    "zh": "第三方分类、工具调用、知识与推理评测；测试集包含私有问题。"
  },
  {
    "category": "Evaluations",
    "title": "Entagl: Jev vs Gemini workflow evaluation",
    "by": "Entagl Research · 2026-09-23",
    "provenance": "reportedEvaluation",
    "url": "https://www.entagl.com/blog/typesafe-jev-benchmark-ai-decision-models",
    "en": "Author-run labeled decisions and workflow replays. Private customer cases limit public reproducibility.",
    "zh": "作者开展的标注决策与工作流重放评测；私有客户案例限制公开复现。"
  },
  {
    "category": "Evaluations",
    "title": "jev-benchmarking",
    "by": "AppliedMachineLearning-Lab · paper code · MIT",
    "url": "https://github.com/AppliedMachineLearning-Lab/jev-benchmarking",
    "en": "Code accompanying Deußer et al.'s 37-dataset study.",
    "zh": "Deußer 等人 37 数据集研究的配套代码。"
  },
  {
    "category": "Evaluations",
    "title": "jev-bench",
    "by": "PavelRavvich · benchmark code",
    "url": "https://github.com/PavelRavvich/jev-bench",
    "en": "Classification, raw predictions, calibration, latency, cost, and cascades. Check sampling and confidence definitions before comparing results.",
    "zh": "分类、原始预测、校准、延迟、成本与级联分析；比较前需核对采样和置信度定义。"
  },
  {
    "category": "Evaluations",
    "title": "AY Automate benchmark",
    "by": "AY Automate · benchmark write-up",
    "provenance": "reportedEvaluation",
    "url": "https://www.ayautomate.com/blog/jev-vs-llm-benchmark",
    "en": "Routing and injection-detection experiments with linked code and raw calls. Reported by the benchmark author.",
    "zh": "路由与注入检测实验，附代码和原始调用；结果由评测作者报告。"
  },
  {
    "category": "Guides",
    "title": "SDE cascade",
    "by": "TypeSafe · Official cookbook",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/cookbooks/sde_cascade",
    "en": "Check inexpensive extraction with per-field Jev questions before escalation; the walkthrough uses cached and illustrative outputs.",
    "zh": "先用逐字段 Jev 问题核查低成本抽取，再决定是否升级；教程使用缓存及示意输出。"
  },
  {
    "category": "Guides",
    "title": "Structure recovery",
    "by": "TypeSafe · Official cookbook",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/cookbooks/autoformat",
    "en": "Restore Markdown structure through line-continuation and block-type decisions while code retains the original wording.",
    "zh": "通过续行和块类型判断恢复 Markdown 结构，由代码保留原始措辞。"
  },
  {
    "category": "Guides",
    "title": "Confidence-gated routing",
    "by": "TypeSafe · Official pattern",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/patterns/confidence-routing",
    "en": "Route uncertain cases to another system or a person.",
    "zh": "将不确定案例转交其他系统或人工。"
  },
  {
    "category": "Guides",
    "title": "Composite scoring",
    "by": "TypeSafe · Official pattern",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/patterns/composite-scoring",
    "en": "Combine separate judgments with weights controlled by code.",
    "zh": "在代码中按权重组合独立判断。"
  },
  {
    "category": "Guides",
    "title": "RAG passage classification",
    "by": "TypeSafe · Official cookbook",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/cookbooks/classifying_rag_passages",
    "en": "Filter retrieved context: score each passage, then decide in code which ones reach the answering model.",
    "zh": "筛选检索上下文：逐段评分，再由代码决定哪些段落交给回答模型。"
  },
  {
    "category": "Guides",
    "title": "Pre-parsed value extraction",
    "by": "TypeSafe · Official cookbook",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook",
    "en": "Choose among bounded candidates found by patterns, then normalize the verbatim value in code.",
    "zh": "从规则匹配出的有限候选中选择，再在代码中规范化原文取值。"
  },
  {
    "category": "Guides",
    "title": "Date extraction",
    "by": "TypeSafe · Official cookbook",
    "provenance": "official",
    "url": "https://docs.typesafe.ai/cookbooks/date_extraction_cookbook",
    "en": "Ask for the date parts a document names; resolve, calculate and validate them in code.",
    "zh": "询问文档中提到的日期组成部分，在代码中解析、计算并校验。"
  },
];

const categoryOrder = ["Papers", "Models", "Tools", "Datasets", "Evaluations", "Guides", "Foundations"];
resources.sort((a, b) => {
  const categoryDifference = categoryOrder.indexOf(a.category) - categoryOrder.indexOf(b.category);
  if (categoryDifference) return categoryDifference;
  if (a.category !== "Papers") return 0;
  const dateDifference = (b.date || "").localeCompare(a.date || "");
  if (dateDifference) return dateDifference;
  const paperId = resource => resource.url.match(/\d{4}\.\d{4,5}/)?.[0] || "";
  return paperId(b).localeCompare(paperId(a), "en", { numeric: true });
});

// The six paper sections of the READMEs, in README order. Every paper names one in `theme`, and
// `artifact_note` repeats the caveat its README Artifacts cell gives beside the links, if any.
// tests/test_bibliography_consistency.py keeps both equal to the READMEs.
const paperThemes = [
  { id: "evaluation", en: "Evaluation and benchmarking", zh: "评测与基准", short: { en: "Evaluation", zh: "评测" } },
  { id: "calibration", en: "Probability calibration and coherence", zh: "概率校准与一致性", short: { en: "Calibration", zh: "校准" } },
  { id: "judging", en: "Judging and selective automation", zh: "评判与选择性自动化", short: { en: "Judging", zh: "评判" } },
  { id: "robustness", en: "Robustness and security", zh: "鲁棒性与安全", short: { en: "Robustness", zh: "鲁棒性" } },
  { id: "architectures", en: "Architectures, memory, and multimodality", zh: "架构、记忆与多模态", short: { en: "Architectures", zh: "架构" } },
  { id: "applications", en: "Applications and domain studies", zh: "应用与领域研究", short: { en: "Applications", zh: "应用" } },
];

export { resources, translations, paperThemes, toolTasks };
