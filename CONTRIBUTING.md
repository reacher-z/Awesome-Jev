# Contributing to Awesome Jev

Thank you for helping keep this field guide useful and inspectable. English and Chinese contributions are welcome.

Maintained by [reacher-z](https://github.com/reacher-z).

The canonical collection is [reacher-z/Awesome-Jev](https://github.com/reacher-z/Awesome-Jev). Please open [issues](https://github.com/reacher-z/Awesome-Jev/issues) and [pull requests](https://github.com/reacher-z/Awesome-Jev/pulls) there. [AwesomeJev/AwesomeJev.github.io](https://github.com/AwesomeJev/AwesomeJev.github.io) mirrors the tested source for the [website](https://awesomejev.github.io); maintainers synchronize the two repositories when publishing.

For collector refreshes, evidence tiers, bilingual updates and deployment, see the [maintenance guide](docs/maintenance.md).

## Add a resource

Open an issue or pull request with:

- A canonical public URL, title, author or organization, and publication date.
- Its resource type, one of the website categories: paper, model, tool, dataset, guide, evaluation, or foundation.
- Its relationship to Jev: a direct Jev or TypeSafe source, an adjacent implementation or evaluation, or a research foundation.
- A short explanation of its relevance to typed decisions.
- What you checked: metadata, abstract, documentation, code, or an executed experiment.
- The model, paper, dataset, or code version when it changes the claim.
- A material limitation, and a code or data link if available.

Prefer the original paper, model card, author repository, or provider documentation. Use secondary indexes to discover those sources. Distinguish Jev-inspired implementations from official TypeSafe artifacts. Identify preprints, provider-reported results, and independently run experiments.

### Where entries live

A pull request that adds or edits a curated entry updates every place it appears:

- `README.md` and `README.zh-CN.md`: the entry in the matching section of both READMEs.
- `site/catalog.mjs`: the website entry, with its `category` and its `en` and `zh` descriptions.
- `references.bib`: the scholarly metadata, for papers.

Then run `node scripts/build_site.mjs` and commit the regenerated files under `site/`. English and Chinese text change together: every entry has both descriptions, and a pull request that edits one language updates the other. The larger searchable source corpus comes from the scheduled scan's ledgers in `data/`; see [Source ledgers](data/README.md).

Credit a paper's authors the same way in both README paper tables and its catalog `by` field: name every author by surname when there are up to four (`Rao & Callison-Burch`, `Deng, Fan, Zhang & Xie`), and write the first author's surname followed by `et al.` when there are five or more.

A paper's links in the README Artifacts column also go in its catalog `artifacts` field, grouped by kind: `code`, `data`, `model`, `demo` or `page`. A link to both code and data is listed under both kinds. Where the README says an artifact was not verified, record its kind as `unverified` instead of a link. The website shows these as link chips, and the tests require the README and catalog links to match. Text the README cell gives beside its links ("README inspected, not executed.") goes in `artifact_note` in both languages, and `theme` names the README section the paper sits in, one of `paperThemes`.

## Evidence quality

Keep schema validity, task quality, calibration, and system efficiency separate. Numerical comparisons need a workload, denominator, baseline configuration, and date. A leaderboard using private tests is not fully reproducible merely because its results are public.

Do not count search results, mirror URLs, different versions of the same paper, or failed requests as independently reviewed sources. The research corpus includes automated content screening; use the recorded review level rather than describing every entry as editorially reviewed.

## Local development

Use Python 3.13 and Node 24, the versions CI uses, and run every command from the repository root.

Most files under `site/` are generated. `node scripts/build_site.mjs` writes the HTML pages, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `papers.json`, `models.json`, and `references.bib` in `site/` from `site/catalog.mjs`, `templates/`, `data/search-guide.json`, `data/research-topics.json`, `data/discovery-translations.zh-CN.json`, and `references.bib`. It also draws the papers-per-week chart into `assets/papers-by-week*.svg` and rewrites the block between the `papers-by-week` markers in both READMEs. Edit those inputs, not the generated files, which the next build overwrites. Rebuild after changing any input or the site scripts and stylesheet (`site/*.js`, `site/*.mjs`, `site/styles.css`), because the pages embed their content hashes. After editing a source ledger (`data/*.jsonl`), run `python3 scripts/build_source_index.py` to regenerate `data/source-counts.json` and the source index in `site/data/`.

Preview the website:

```sh
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`. Check both languages, search, category filters, the source corpus, narrow-screen layout, and keyboard navigation after UI changes.

Before a pull request, run the checks CI enforces:

```sh
python3 -m unittest discover -s tests
python3 scripts/validate.py
node scripts/build_site.mjs --check
python3 scripts/build_source_index.py --check
```

CI runs the tests and the validator; the tests include the site `--check` and the validator includes the source-index `--check`, so running those two separately shows which generated output is stale. If a `--check` fails, run the same command without `--check` and commit the regenerated files.

## Publication hygiene

Submit only public source material and original summaries. Keep API keys, `.env` files, local caches, account configuration, private URLs, and proprietary packages outside the repository. Third-party assets must carry the appropriate license and attribution. Font Awesome Pro assets must not be committed to this public repository.

## 中文说明

感谢帮助这份指南保持实用、可核查。欢迎中英文贡献。

维护者：[reacher-z](https://github.com/reacher-z)。

请统一向[资源主仓库 reacher-z/Awesome-Jev](https://github.com/reacher-z/Awesome-Jev)提交 issue 与 PR；组织仓库负责部署网站。两边保留同一份通过校验的源码，由维护者发布时同步，并非自动同步。

来源刷新、核查等级、双语更新与发布流程见[维护指南](docs/maintenance.md)。

### 补充资源

欢迎补充论文、模型、工具、数据与负面结果。提交 issue 或 PR 时请提供：

- 规范的公开链接、标题、作者或机构，以及发布日期。
- 资源类型，即网站的分类之一：论文、模型、工具、数据集、指南、评测或基础研究。
- 与 Jev 的关系：Jev 或 TypeSafe 的直接来源、相邻实现或评测，或研究基础。
- 与类型化决策的关系的简短说明。
- 实际核查的内容：元数据、摘要、文档、代码，或亲自运行的实验。
- 版本会影响结论时，注明模型、论文、数据集或代码的版本。
- 一项实质性局限；如有，附上代码或数据链接。

优先引用原始论文、模型卡、作者仓库或提供方文档；二级索引只用于发现这些来源。区分受 Jev 启发的实现与 TypeSafe 官方产物，并标明预印本、提供方自报结果与独立运行的实验。

#### 条目位置

新增或修改精选条目的 PR 须同步更新条目出现的每一处：

- `README.md` 与 `README.zh-CN.md`：两份 README 对应章节中的条目。
- `site/catalog.mjs`：网站条目，包括 `category` 以及 `en`、`zh` 两种描述。
- `references.bib`：论文的文献元数据。

随后运行 `node scripts/build_site.mjs`，并提交 `site/` 下重新生成的文件。中英文同步修改：每个条目都有两种语言的描述，修改其中一种语言的 PR 须同时更新另一种。规模更大的可检索来源语料来自定时扫描的 `data/` 台账，见[来源台账](data/README.md)。

论文作者在两份 README 的论文表格与 catalog 的 `by` 字段中以同一方式署名：作者不超过四人时列出全部作者的姓（如 `Rao & Callison-Burch`、`Deng, Fan, Zhang & Xie`），五人及以上时写第一作者的姓加 `et al.`。

论文在 README「材料」列中的链接也要按类型写入 catalog 的 `artifacts` 字段：`code`、`data`、`model`、`demo` 或 `page`。同时提供代码与数据的链接在两种类型下各列一次。README 注明某项材料未核验时，用 `unverified` 记录其类型，不写链接。网站据此显示链接标签，测试要求 README 与 catalog 的链接一致。README 单元格中链接旁的说明文字（如“仅检查 README，未执行。”）以中英文写入 `artifact_note`；`theme` 注明论文所在的 README 章节，取值为 `paperThemes` 之一。

### 证据质量

分别看待 schema 有效性、任务质量、校准与系统效率。数值比较须说明工作负载、分母、基线配置与日期。使用私有测试集的排行榜，不会因为结果公开就能完全复现。

不要把搜索结果、镜像链接、同一论文的不同版本或失败的请求算作独立核查的来源。研究语料包含自动正文筛查；请使用记录的核查等级，不要把每个条目都描述为经过编辑复核。

### 本地开发

使用与 CI 相同的 Python 3.13 与 Node 24，并在仓库根目录运行所有命令。

`site/` 下的大部分文件是生成的。`node scripts/build_site.mjs` 根据 `site/catalog.mjs`、`templates/`、`data/search-guide.json`、`data/research-topics.json`、`data/discovery-translations.zh-CN.json` 与 `references.bib`，在 `site/` 中写入 HTML 页面、`sitemap.xml`、`llms.txt`、`llms-full.txt`、`papers.json`、`models.json` 与 `references.bib`，并把每周论文图写入 `assets/papers-by-week*.svg`、重写两份 README 中 `papers-by-week` 标记之间的内容。请修改这些输入文件，不要手改生成文件，下次构建会覆盖它们。修改任一输入或网站脚本与样式表（`site/*.js`、`site/*.mjs`、`site/styles.css`）后都要重新构建，因为页面嵌入了它们的内容哈希。修改来源台账（`data/*.jsonl`）后，运行 `python3 scripts/build_source_index.py`，重新生成 `data/source-counts.json` 与 `site/data/` 中的来源索引。

预览网站：

```sh
python3 -m http.server 8000 --directory site
```

打开 `http://localhost:8000`。修改界面后，检查双语页面、搜索、分类筛选、来源语料、窄屏布局与键盘导航。

提交 PR 前运行 CI 强制执行的检查：

```sh
python3 -m unittest discover -s tests
python3 scripts/validate.py
node scripts/build_site.mjs --check
python3 scripts/build_source_index.py --check
```

CI 运行测试与校验脚本；测试已包含网站的 `--check`，校验脚本已包含来源索引的 `--check`，单独运行这两条可以看出哪一项生成结果已过期。若某个 `--check` 失败，去掉 `--check` 重新运行同一命令，并提交重新生成的文件。

### 发布规范

只提交公开来源材料与原创摘要。API 密钥、`.env` 文件、本地缓存、账户配置、私有 URL 与专有软件包不得进入仓库。第三方素材须附相应的许可与署名。Font Awesome Pro 素材不得提交到本公开仓库。
