# Maintaining Awesome Jev

[Contributing](../CONTRIBUTING.md) · [Source audit](source-audit.md) · [Source ledgers](../data/README.md)

The site has two layers: an editorial selection in [site/catalog.mjs](../site/catalog.mjs), and a searchable source index generated from the public ledgers. A new scanned source does not automatically belong in the editorial selection.

The HTML pages are generated with `node scripts/build_site.mjs` from the shared catalog, the homepage template, and the source-backed guide. See [Search discovery](search-discovery.md) for canonical language routes, verification, and submission procedures.

## Repository roles

| Destination | Purpose |
| --- | --- |
| [reacher-z/Awesome-Jev](https://github.com/reacher-z/Awesome-Jev) | Main resource collection and the destination for issues and pull requests. |
| [awesomejev.github.io](https://awesomejev.github.io) | Published website. |
| [AwesomeJev/AwesomeJev.github.io](https://github.com/AwesomeJev/AwesomeJev.github.io) | Deployment mirror serving GitHub Pages. |

Keep both repositories on the same tested source snapshot. Synchronization is a maintainer action; there is no automatic repository-mirroring workflow.

## Twice-daily source scans

The [Scan public sources workflow](../.github/workflows/scan-sources.yml) is configured for **09:17 and 21:17, America/Los_Angeles**, every day (`17 9,21 * * *`). The named timezone follows daylight saving time. It runs only in `reacher-z/Awesome-Jev`, from `main`; the deployment mirror does not run another copy.

The scan proposes resource-data updates through a pull request. It does **not** merge that request, promote discoveries into the curated README, or synchronize the website mirror. Maintainers review the evidence and merge useful changes, then use the publication process below.

### Operation and results

1. The read-only scan job reads the current Decision Index and linked news/artifacts, includes primary arXiv URLs from the generated [curated paper catalog](../site/papers.json), refreshes existing sources, follows one level of dependency links, and runs the configured scholarly discovery queries. Scheduled runs do not impose a new-candidate count cap; this is bounded discovery, not a scan of the entire web. The job rebuilds the index and validates the resulting data.
2. A separate publication job checks the permitted output files before receiving its publication token. Material changes are proposed on `automation/source-scan` with the title `chore: refresh public source index`; subsequent updates reuse the open PR.
3. Unchanged source content keeps its existing evidence and retrieval timestamps. A clock change alone should not create a new data update. Fetch failures are reported, with previous successful evidence retained rather than dropped or relabeled as a new successful fetch.
4. Automated collection never grants `editorial_reviewed`. If a previously reviewed source changes, the old reviewed record remains distinguishable from the new material awaiting review.

Catalog entries supply discovery URLs, not evidence grades or source hashes. The scanner validates the entire local catalog before making network requests, accepts only primary arXiv paper URLs, deduplicates versions, and respects curated exclusions before fetching. A malformed catalog stops with a bounded diagnostic. A successful primary landing-page check is still not a full-paper review; unavailable content retains only the evidence actually obtained.

Canonical paper identities are shared across both ledgers, while a curated version URL remains the actual fetch target. A paper already held in the research ledger is not counted again when the ecosystem or scholarly discovery path encounters it. Historical duplicate rows are retained; new observations go to an existing owner rather than creating another copy.

Fixed-version primary-abstract records retain their original evidence, dates and `abstract_checked` grade. The scanner also observes the current public arXiv version; a changed abstract or newly observed version becomes a review candidate instead of silently replacing the pinned record. A new version with an unchanged abstract still remains distinguishable. Repeated identical observations preserve the pending record, and later fetch failures do not erase it. These items use the existing `editorial_refresh_candidates` report field for compatibility; that field does not grant an editorial-review grade.

The PR publisher checks this version continuity too: a pending v3 cannot be replaced by an unknown-version or v2 candidate from a later scan. Accepting a pending revision requires both its version and evidence hash to match the retained record. Publication stays limited to the seven-file data allowlist, with read-only collection and write publication in separate jobs. When a scan accepts a source that the ecosystem screen had excluded, it removes that source's row from the exclusion ledger, so a source is never in both. The validation of this continuity check is recorded in the [scan review](reviews/scan-2026-10-16.md#pinned-version-continuity-2026-10-16).

The scan report records `error_code_counts` across **all** issues before limiting `errors` to 100 examples. `error_count`, `error_examples_count`, and `error_examples_truncated` distinguish the total from the displayed sample. Fetch diagnostics retain only fixed, allowlisted codes such as `http_429` or `network_failure`; arbitrary exception messages and response bodies are not published. These fields describe observed failures, not an inferred provider outage or cause.

Rate limits are bounded so that a throttled scan ends with a partial result instead of hitting the job timeout. The fetcher retries a `429` or `5xx` response twice and honours a `Retry-After` of at most 60 seconds; a longer requested delay ends that request as `retry_after_exceeded`. A `429` or a `Retry-After` delay applies to the whole host: all workers share the host's not-before time and send it nothing earlier. The plain backoff after a `5xx` without `Retry-After` delays only that request. The scan also has an 18-minute deadline (`SCAN_TIME_BUDGET_SECONDS` in `scripts/refresh_sources.py`), counted from the start of fetching, which leaves the 25-minute job time to merge, rebuild and validate. It is split into guaranteed shares per phase (`PHASE_TIME_BUDGET_SECONDS`): 14 minutes for the ecosystem phase and 4 minutes for the research queries that follow it. Time that the ecosystem phase leaves unused passes to research, and a slow ecosystem phase cannot use up the research share. A wait that would end after the current phase's deadline is not started, and that phase sends no new request. The run is then reported as `partial` with `retry_budget_exhausted: true`, `retry_budget_exhausted_phases` naming the phase or phases, `retry_budget_seconds` and `phase_budget_seconds` in `data/scan-latest.json` and the job summary. Unscanned sources keep their earlier evidence.

Use **Actions → Scan public sources → Run workflow**, selecting `main`, to trigger the same process manually. A successful scan is not proof that a PR was merged or the website was deployed; inspect the run summary and the proposed diff separately.

Manual runs can select all new candidates or a cap of 100 or 300. The `smoke` option performs a small public-network dry-run: it does not rewrite the ledgers or scan report, package an update, or publish a PR. It checks connectivity and the small scan path, not the completeness of a full scheduled run.

The same collector can be inspected locally without a GitHub token:

```sh
python3 scripts/refresh_sources.py --smoke
```

GitHub may place CI for a PR created or updated with `GITHUB_TOKEN` in an approval-required state. A maintainer with write access can select **Approve workflows to run** on the PR. The scan's own validation still runs before publication. See [GitHub's token-trigger rules](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs); do not assume a proposed PR already has successful independent checks.

GitHub schedules are best-effort: runs may be delayed, and public-repository schedules can be disabled after 60 days without repository activity. See [GitHub's schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). If the schedule is disabled, re-enable it in Actions and inspect a manual run before relying on later scans.

**Operational check, 2026-10-16:** the [full manual scan and publication run](https://github.com/reacher-z/Awesome-Jev/actions/runs/38848656459) succeeded. A temporary, read-only five-minute UTC probe produced no `event=schedule` runs during **06:50:35–07:05:33 UTC** and was removed. A later [genuine scheduled run](https://github.com/reacher-z/Awesome-Jev/actions/runs/38877935151), recorded as `event=schedule` at **09:04:22 UTC**, completed successfully and opened [PR #3](https://github.com/reacher-z/Awesome-Jev/pull/3). Its source-retrieval report was partial, with 103 issues; workflow success does not mean every source was fetched. This establishes automatic triggering, but does not establish execution exactly at the configured local times or explain the earlier missing events.

### Trust and publication boundaries

Fetched pages, model cards, metadata, and repository descriptions are **untrusted data**. The scanner does not execute their code, follow instructions embedded in them, or install packages they recommend. Requests are public and unauthenticated; credential-bearing URLs and private network addresses are outside the scan scope. Provider failures and retry exhaustion must remain visible without destroying prior evidence.

The collection job has read-only repository permissions and no publication-token environment variable. The separate publication job receives write permissions only for proposing the bounded data update. Its token is injected into the GitHub-only pending-reconciliation step and the final publication step, and is removed from the index-builder subprocess environment. Reconciliation reads only data from the existing bot-owned PR, retains absent candidates with their original provenance, rebuilds the source index using trusted base-branch code, and updates the six-file manifest. Full validation runs again before retaining the reconciled artifact or publishing. A changed pending-branch head stops publication. It must not execute downloaded source code or interpret source text as a shell command. Keep credentials, private URLs, raw caches, and full copyrighted documents out of the proposed commit.

The evidence tiers below still apply. An automatically discovered source is not an endorsed recommendation, an abstract check is not a full-paper review, and a published result is not an experiment reproduced by this project.

## Refresh the evidence

Run these commands from the repository root. These are the legacy full-refresh commands, separate from the scheduled incremental scan above. They make public network requests and replace the default output ledgers wholesale; inspect the resulting changes before committing. A rebuilt ledger holds only what these collectors regenerate, so records written only by the incremental scan, such as fixed-version primary abstracts (`abstract_provider: arxiv_primary_abstract_page`), are dropped. To refresh sources without discarding earlier evidence, run the scan's collector, `python3 scripts/refresh_sources.py`, instead.

```sh
python3 scripts/collect_ecosystem.py --workers 12 --max-depth 1
python3 scripts/collect_research.py --target 0 --with-openalex --workers 3
python3 scripts/build_source_index.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The ecosystem collector writes `data/ecosystem-sources.jsonl` and a separate exclusion ledger, and prints a run summary without committing it; current counts are in the generated `data/source-counts.json`. Like the scan, it records the Decision Index files as `content_screened` with evidence parsed from the fetched revision and never grants `editorial_reviewed`. An earlier `editorial_reviewed` row, with its evidence, is kept unchanged only while its URL, resolved revision and content hash match the new fetch; changed content falls back to `content_screened` until it is reviewed and documented again. `--resume` reuses previously retrieved dependency records and rechecks their relevance; it is not a fresh network retrieval of every dependency. Use the normal command for a new retrieval snapshot.

The research collector writes `data/research-sources.jsonl`. `--target 0` keeps all qualifying distinct results rather than imposing a numerical target. `--with-openalex` supplements Hugging Face discovery with older scholarly work. Every online run fetches fresh API responses and stores the raw responses in a private per-user cache outside this repository, `~/.cache/awesome-jev/research-api` (or `$XDG_CACHE_HOME/awesome-jev/research-api` when that variable is set), created with mode `0700`. The collector refuses a cache directory that another account owns or that its group or other users can write to. Online runs never read the cache. To repeat screening against the cache from an earlier online run on the same machine:

```sh
python3 scripts/collect_research.py --offline --target 0 --with-openalex
```

`--offline` makes no network requests, so it needs that warm cache; a fresh clone, another machine, or a cleared cache directory has none. If any query has no cached response, or no record qualifies, the collector exits with an error and leaves `data/research-sources.jsonl` unchanged. A successful re-screen still replaces the ledger wholesale, as described above. Re-screened records keep the `retrieved_at` of the original response, and the audit output reports `cached_queries`, the number of queries answered from the cache.

The index builder deduplicates the ledgers and regenerates `site/data/source-index.json`, `data/source-counts.json`, and `site/data/source-badge.json`. Do not edit their counts by hand. To check that the generated index is current without rewriting it:

```sh
python3 scripts/build_source_index.py --check
```

Retain document identifiers when normalizing URLs: OpenReview's `id` and CiteSeer's `doi` are content identifiers, not tracking parameters. Preserve retrieval dates and hashes; reusing cached content must not become a claim that it was fetched again.

## Keep the verification tiers precise

| Recorded tier | What it means |
| --- | --- |
| `metadata_only` | Discovered or identified, without a successful substantive content check. Excluded from checked counts. |
| `abstract_checked` | Original abstract screened through Hugging Face Papers, reconstructed from OpenAlex metadata, or read from a fixed-version arXiv abstract page (`abstract_provider: arxiv_primary_abstract_page`). Only the arXiv route fetches the primary page itself, recorded as `canonical_page_separately_fetched: true`. None of these is a full-paper review. |
| `content_screened` | Retrieved README, model card, dataset card or web-page text passed explicit automated relevance rules. An abstract landing page is not a full paper. |
| `editorial_reviewed` | A documented, focused editorial review of the source. It does not by itself mean experimental reproduction. |

Checked-source totals measure distinct documents under these rules. They do not measure independent studies or manually read papers. Preserve the distinction between provider claims, paper-reported results, and experiments actually run by this project. Record direct, adjacent and background relationships separately.

## Preserve curation decisions

[Source curation](../data/source-curation.json) records exact-URL exclusions and evidence-backed display corrections. Exclusions prevent rejected material from being reintroduced by a later scan. An excluded record still present in an accepted ledger fails validation; removing an existing record requires an explicit reviewed change.

Annotations may correct a displayed title, first-submission date, topic, relationship, or relevance note. They include a primary-source URL and review date. Raw provider metadata, retrieval timestamps, hashes, and verification levels remain unchanged. The website exposes each correction's source under its corpus entry.

When an update PR is still open, the publisher refuses to replace it with data that drops or downgrades previously gathered evidence or loses an outstanding editorial-review candidate. An explicit trusted exclusion can authorize a scope removal. A blocked update leaves the existing PR available for review.

## Maintain the editorial collection

For a promoted resource, read the original source, pin the relevant version, state its purpose and a material limitation, and verify any license or access label. Synchronize its English and Chinese descriptions across `README.md`, `README.zh-CN.md`, and `site/catalog.mjs`. Add scholarly metadata to `references.bib`; update survey or audit prose only when the new evidence changes it. When adding a paper, refresh *What's new* in both READMEs so it keeps only the ten most recent studies by linked-version date.

Anonymous review mirrors expire. **Before 2027-04-10**, recheck the anonymous.4open.science mirror `jev_ordinal_scale_bia`, the code artifact of the Ordinal-Scale Bias paper (arXiv 2609.38827). It is linked from both READMEs, both survey pages, `data/search-guide.json` and the [expansion directory](expansion-2026-10-16.md), and the service reports an `expirationDate` of 2027-04-10T10:02:50Z. Replace it with the de-anonymized repository if the authors have released one; otherwise remove or mark the expired link. A plain link check is not enough: the mirror URL redirects to a page that returns HTTP 401 without a session cookie. Read the status from `https://anonymous.4open.science/api/repo/jev_ordinal_scale_bia/options` instead.

Review the site locally after interface changes:

```sh
python3 -m http.server 8000 --directory site
```

Check both languages, search, category filters, source-tier labels, keyboard focus and a narrow viewport. The curated cards and large source browser serve different purposes; do not silently promote the entire scanned corpus into an endorsed reading list.

## Review and publish

[Repository CI](../.github/workflows/ci.yml) checks repository integrity in both repositories. Send proposed changes to the [main collection](https://github.com/reacher-z/Awesome-Jev). The [automated PR review](../.github/workflows/pr-review.yml) comments on bounded patches and provenance fields. It is deterministic assistance, not human scholarly review, verification of linked claims, or approval to merge. Keep its privileged workflow restricted to trusted base-branch logic: it must not check out or execute pull-request code.

After merging and testing `main`, maintainers publish the same commit to both remotes. In the maintainer checkout, `origin` points to `reacher-z/Awesome-Jev` and `awesomejev` points to `AwesomeJev/AwesomeJev.github.io`; confirm those destinations before using these commands:

```sh
git push origin main
git push awesomejev main
```

Configure Pages in the deployment repository to use GitHub Actions. The [Pages workflow](../.github/workflows/pages.yml) responds to a push to `main` or a manual dispatch, but its deployment job explicitly runs only when `github.repository` is `AwesomeJev/AwesomeJev.github.io`. It validates the publication and uploads only `site/`. Verify that both remote `main` branches identify the same commit, inspect CI in both repositories, and inspect the deployment result and live bilingual views. A local preview or a successful validation run is not evidence that deployment completed.

## Public-source and license boundaries

Collect only public resources with public, unauthenticated requests. Keep private transcripts, credentials, local account configuration, machine-specific paths and raw response caches out of commits. Before publication, inspect the staged files and commit author identity; use the maintainer's public GitHub identity and GitHub-provided noreply address rather than a private email address. Preserve historical authorship instead of attributing every past commit to the current maintainer. Do not copy full copyrighted articles or abstracts into the ledger.

Preserve the individual licenses of third-party resources. A repository license does not relicense linked papers, datasets or models. The bundled fonts carry SIL Open Font License notices; the icon subset is Font Awesome **Free**, with its included license. Keep those notices and source versions with the assets. Do not add Font Awesome Pro files or proprietary font packages to this public repository.

## Reviewed resource expansion

The [expansion directory](expansion-2026-10-16.md) and its [frozen baseline](../data/expansion-baseline-2026-10-16.json) distinguish new resources from previously known URLs and evidence. Only accepted URLs listed in the [reviewed intake](../data/expansion-intake-2026-10-16.json) may count toward the expansion target; ordinary scan discoveries do not automatically enter this audited count.

For a reviewed expansion release, update the ledgers and accepted intake, then run:

```sh
python3 scripts/build_source_index.py
python3 scripts/build_expansion_report.py
node scripts/build_site.mjs
python3 scripts/validate.py
python3 -m unittest discover -s tests
```

The generated discoveries pages are snapshots of the reviewed intake, separate from the live searchable corpus. The recurring scanner retains its existing data-only PR boundary and does not silently rewrite the expansion report or directory. Continue to inspect proposed resources, verification scope, duplicates, and any licensed or experimental limitations before publication.

The Chinese directory uses [discovery-translations.zh-CN.json](../data/discovery-translations.zh-CN.json) for its resource descriptions. Each translation is keyed by the exact reviewed English description, so a changed qualification cannot silently retain an older translation. Add or review the Chinese wording whenever an accepted description changes, preserving private-data, label-provenance, license and reproduction limits. The build stops if a current description lacks Chinese text. Original source titles and links remain unchanged; translating a summary does not add another source or upgrade its evidence tier.

## 中文说明

### 每日两次扫描

[Scan public sources](../.github/workflows/scan-sources.yml) 配置为每天洛杉矶时间 **09:17 和 21:17** 运行，时区为 `America/Los_Angeles`，会随夏令时调整。只在主仓库 `reacher-z/Awesome-Jev` 的 `main` 上运行，网站部署镜像不会重复执行。

扫描通过 `automation/source-scan` 分支创建或更新同一个待审 PR，标题为 `chore: refresh public source index`。**不会自动合并、自动把发现项加入精选 README，也不会自动同步网站镜像。** 维护者核对来源与差异、合并后，再按发布流程同步。

定时扫描覆盖当前 Decision Index、其动态与链接材料、`site/papers.json` 精选论文目录中的 arXiv 原始来源、已有来源、一层依赖链接和已配置的学术查询；不设新增候选数量上限，但不代表扫描整个互联网。手动运行可选择全部候选或 100／300 项上限。`smoke` 只进行小规模公开网络试运行，不写入台账或报告、不打包更新、不发布 PR，也不证明完整扫描已经通过。

精选目录只提供发现入口，不直接提供证据等级或正文哈希。扫描前先完整检查本地目录格式与 arXiv URL，按论文身份去重，并在抓取前应用排除规则；格式有误即停止，不把任意地址送入网络请求。实际页面筛查仍不等于阅读全文或编辑审阅。报告的 `error_code_counts` 统计全部问题，`errors` 最多保存 100 个示例，并用总数、示例数及截断标记明确区分；仅记录白名单中的固定错误码，不发布任意异常消息或响应正文。

两份台账共享规范论文身份，但实际抓取保留精选链接中的固定版本。已在研究台账中的论文不会因生态或学术发现路径再次出现而重复报新增；已有历史重复行不静默删除。固定版本的原始摘要保留原证据、日期和摘要核查等级，同时观察当前公开版本；新版本或摘要变化进入待审记录，不直接混入旧版本字段。即使摘要未变，新版本也可进入待审；重复观察不重写待审时间，抓取失败不清除未解决记录。为兼容现有流程，这些条目沿用 `editorial_refresh_candidates` 字段，但不代表授予编辑审阅等级。

扫描 job 只读且不接收发布 token。独立发布 job 在核验文件后，仅向GitHub待审证据协调步骤及最终发布步骤注入 token，重建索引的子进程不接收该 token。协调步骤只读取旧bot PR的数据，按原时间与证据保留本轮缺失的候选，用可信主分支代码重建索引并更新六文件清单，重新完整校验后才保存和发布；若待审分支期间发生变化，则停止写入。扫描接受此前被生态筛查排除的来源时，会从排除台账中删除该行，同一来源不会同时被接受和排除。远程网页、README 和模型卡中的内容一律作为不可信数据处理，不执行其代码或指令，不使用其推荐安装命令；仅请求公开来源，拒绝携带凭据的 URL 与私有网络地址。

内容未变时保留原有证据和抓取时间，避免仅更新时间戳的 PR。抓取失败或重试耗尽时保留既有成功记录并报告失败，不能把失败伪装为新的成功核查。自动扫描不授予 `editorial_reviewed`；已有编辑审阅的来源发生变化时，应区分旧已审版本与待复核的新内容。

手动运行：**Actions → Scan public sources → Run workflow**，选择 `main`。GitHub 定时运行可能延迟，公开仓库长期无活动时也可能停用；以 Actions 状态和运行摘要为准。扫描成功不等于 PR 已合并或网站已发布。

**2026-10-16 运行核查：**[完整手动扫描及发布流程](https://github.com/reacher-z/Awesome-Jev/actions/runs/38848656459)已成功。临时只读的五分钟 UTC 探针在 **06:50:35–07:05:33 UTC** 窗口内没有产生定时运行，随后已移除。之后的[真实定时运行](https://github.com/reacher-z/Awesome-Jev/actions/runs/38877935151)于 **09:04:22 UTC** 记录为 `event=schedule`，成功完成并创建 [PR #3](https://github.com/reacher-z/Awesome-Jev/pull/3)；来源抓取报告为部分成功，共 103 个问题，工作流成功不代表全部来源均已抓取。自动触发现已有实证，但尚不能据此确认每日按配置时间准点运行，也不能解释此前缺失事件的原因。

由 `GITHUB_TOKEN` 创建或更新的 PR，其 CI 可能处于等待批准状态；有写权限的维护者可在 PR 上选择 **Approve workflows to run**。扫描本身会在发布 PR 之前校验，但不能因此假定 PR 已取得全部独立检查结果。

### 人工维护与发布

维护顺序是：刷新公开来源清单 → 生成网站索引与计数 → 运行校验和回归测试 → 同步中英文精选内容 → 检查暂存区后发布。`--resume` 与 `--offline` 会复用已有材料，不能写成全部来源重新抓取。旧版全量收集脚本会整体替换默认台账，只保留它们能重新生成的记录；固定版本原始摘要（`arxiv_primary_abstract_page`）等仅由增量扫描写入的记录会被丢弃，需要保留既有证据时改用 `python3 scripts/refresh_sources.py`。生态收集脚本不授予 `editorial_reviewed`；只有 URL、解析版本和内容哈希都与新抓取一致时，才原样保留既有的 `editorial_reviewed` 行及其证据，内容变化后回到 `content_screened`，需重新审阅并记录。联网运行总是重新抓取 API 响应，不读取缓存；原始响应存放在仓库外每个用户私有的缓存目录 `~/.cache/awesome-jev/research-api`（设置了 `XDG_CACHE_HOME` 时为 `$XDG_CACHE_HOME/awesome-jev/research-api`，权限 `0700`），目录属于其他账户或任何用户可写时脚本拒绝使用。`--offline` 不发网络请求，只能复用同一台机器上此前联网运行留下的缓存，重新筛选的记录保留原响应的 `retrieved_at`，审计输出的 `cached_queries` 给出来自缓存的查询数；任一查询缺少缓存或没有记录通过筛选时，脚本报错退出，不改动 `data/research-sources.jsonl`。

新增论文时，同步更新两份 README 的“最近更新”，只保留按所链接版本日期排列的最新十项研究。

匿名评审镜像会过期。**请在 2027-04-10 之前**复查有序量表偏差论文（arXiv 2609.38827）的代码材料，即 anonymous.4open.science 镜像 `jev_ordinal_scale_bia`。两份 README、两份综述页面、`data/search-guide.json` 与[扩展目录](expansion-2026-10-16.md)都链接了它，服务端报告的 `expirationDate` 为 2027-04-10T10:02:50Z。作者若已发布去匿名化仓库，改用该仓库；否则删除或标注失效链接。普通链接检查不够：镜像地址会跳转到一个未带会话 cookie 时返回 HTTP 401 的页面，应改为读取 `https://anonymous.4open.science/api/repo/jev_ordinal_scale_bia/options` 中的状态。

[reacher-z/Awesome-Jev](https://github.com/reacher-z/Awesome-Jev) 是资源主仓库，也是 issue 和 PR 的统一入口；[组织仓库](https://github.com/AwesomeJev/AwesomeJev.github.io) 是网站部署镜像。维护者将验证通过的同一个 `main` 提交推送到 `origin` 与 `awesomejev`，并核对两边提交一致；当前没有自动镜像同步。

自动内容筛查、摘要核查、编辑审阅和亲自复现是不同层级。PR 自动评论不等于学术审查，也不批准合并。CI 在两个仓库运行，Pages 部署 job 仅允许组织部署仓库执行、只发布 `site/`；完成后检查两边 Actions 与线上双语页面。

只使用公开来源，不提交密钥、私人对话、个人路径或原始缓存。保留第三方字体、图标、模型与数据的许可边界，不将商业受限资源描述为可任意使用的开源资源。

### 资源扩展审阅

[扩展目录](expansion-2026-10-16.md)及其[冻结基线](../data/expansion-baseline-2026-10-16.json)区分新资源与此前已知的 URL 和证据。只有列入[审阅后接收清单](../data/expansion-intake-2026-10-16.json)的 URL 才能计入扩展目标；普通扫描发现不会自动进入这一审计计数。

发布一次审阅后的资源扩展时，先更新台账和接收清单，再运行：

```sh
python3 scripts/build_source_index.py
python3 scripts/build_expansion_report.py
node scripts/build_site.mjs
python3 scripts/validate.py
python3 -m unittest discover -s tests
```

生成的新增来源页面是审阅接收清单的快照，与可搜索的完整来源库分开。定期扫描仍只提交数据 PR，不会静默改写扩展报告或目录。发布前继续检查拟新增资源的核查范围、重复情况以及许可或实验限制。

中文资源简介保存在独立翻译文件中，以完整英文简介对应。新增或修改来源简介时同步校对译文，保留数据私有性、标签来源、许可和复现限制；缺少对应中文时，构建会停止。翻译不改变来源数量、原始标题、链接或证据等级。
