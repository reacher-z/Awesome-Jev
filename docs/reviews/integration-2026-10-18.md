# Release integration — 18 October 2026 UTC

The canonical repository advanced from `ef99a16` to `3425c16` while the website repository remained on the earlier release. The integration preserves the merged research, taxonomy, companion links, generated charts, validation and collector changes. Its current catalog has **156 curated resources, 78 direct arXiv papers and 87 bibliography entries**. The reviewed expansion is **780 sources**; this counts reviewed intake against the frozen baseline and is distinct from the full registry's **4,286 unique sources**. Lower expansion totals after exclusions must not be hidden by restoring removed entries or counting known sources again.

## Presentation and cross-platform validation

The website retains a white background and dark text regardless of the system color preference. The paper-activity figure and its numeric table remain available in a native disclosure, keeping the paper filters and table closer to the top. Theme, code-availability, search and reset were exercised together in the browser. The model directory, topic pages and companion links come from the shared catalog and build inputs.

Ten local link-check failures were caused by comparing resolved targets with an unresolved temporary-root spelling on macOS. The validator now resolves both containment boundaries and the target. It still rejects paths outside the repository or published `site/` root, and the independent publication rule still rejects symlinks inside the artifact. A directory-alias regression exercises both valid internal links and a forbidden escape. The complete local suite passed 424 tests after the repair.

The expansion report was regenerated after the merged source changes. Its accepted total stays 780; the global registry snapshot now matches the current source index. One previously accepted URL uses its inspected resolving host. No source-ledger record, frozen baseline or accepted-intake list is changed by this integration.

## Pending scan evidence

The scheduled [scan at `3425c16`](https://github.com/reacher-z/Awesome-Jev/actions/runs/39058580868) passed collection, validation and artifact restoration, then stopped at publication's continuity check. The artifact's six file hashes were verified locally against its same-run manifest. Comparison with [PR 4](https://github.com/reacher-z/Awesome-Jev/pull/4), head `bd0c9de6abd50644dfe803074aadf6d38340049a`, identified the remaining nonexcluded discrepancies:

- Three Decision Index documents were compared by revision-bearing paths even though the collector treats each as one logical document. Their old pending hashes match the already accepted current documents.
- An OpenAlex record retained the same record ID and abstract hash but had its HTML-escaped URL separators corrected. Its identifying query values remain intact.
- Four paper landing pages had previously received automatic `content_screened` labels. The maintainer-accepted main branch replaced these with fixed-version primary abstracts at `abstract_checked`, documented in the [domain-study review](../../data/domain-transfer-review-2026-10-17.json).

Publication now compares HTML-unescaped URL identities and normalizes only the Decision Index's revision-bearing document paths. A narrow exception recognizes a protected primary-abstract snapshot already present on the trusted workflow base: its paper identity, fixed version, provider, page hash and abstract hash must all match the fresh record. It does not accept a scan-only conversion, an editorial downgrade, missing primary-page evidence, a newer version recorded only in the previous PR, or removal of an unresolved versioned review candidate.

The old PR and the validated latest artifact pass this check with the current main snapshots and existing reviewed exclusions. Negative regressions continue to reject genuine evidence loss. The six-file publication allowlist, ref concurrency checks, bot ownership checks and no-automatic-merge behavior are unchanged. This offline reconciliation does not claim that any pending proposal has been accepted or that the subsequent workflow has succeeded; its observed result is recorded separately.

The first verification [run 39096728520](https://github.com/reacher-z/Awesome-Jev/actions/runs/39096728520) then reached publication with **0 downgraded records and 0 unresolved editorial changes**, confirming that those identity/acceptance mismatches were addressed. It correctly stopped on **40 absent older proposals**, reflecting variation in current scholarly discovery. The older PR remained unchanged.

The publication job now reads the existing bot-owned PR's data and carries forward only absent, nonexcluded source identities. It preserves their original row bytes, evidence tiers and retrieval times; fresh observations are not overwritten. The report labels these as retained pending sources, separately from newly fetched candidates. Trusted base-branch code rebuilds the browser index without a token in its environment, and the full validator and test suite run again before publication. The reconciled six-file bundle is retained as a separate same-run artifact. Its manifest records the prior PR head, and any intervening branch change stops the final write.

Seven regression tests cover exact row preservation, repeated reconciliation, aliases, exclusions, non-bot refusal, malformed evidence, token-free rebuilding and concurrent-head changes. The full suite passes **431 tests**. An isolated replay combining the actual older PR and the actual first verification artifact retained 40 rows and passed continuity and repository validation. No proposed row was accepted into main by that replay.

## 中文

主仓库已有新合并，而官网仍停留在旧版本。本次保留既有研究与功能，修正macOS路径校验，并按用户要求维持白底黑字。趋势图改为原生可展开区，论文筛选与列表更靠前；主题、代码过滤、关键词搜索和重置已经组合实测。当前156项精选、78篇直接论文、87条书目、780项审阅扩展来源；来源总库与扩展计数分开，删除不合格来源后不人为补回计数。

扫描发布的剩余差异来自三个文档修订路径、一个HTML转义网址，以及四篇已在主分支接受的固定原始摘要。新检查保留真实丢失、仅由扫描引入的降级及未处理更新版本的阻拦；只有与可信主分支的版本和两个哈希完全一致的原始摘要可按其真实证据类型保留。没有扩大自动写入范围、自动合并PR或把待审提议计入官网。运行恢复情况须以真实工作流结果为准。
