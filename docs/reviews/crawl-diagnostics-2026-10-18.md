# Sitemap fetch diagnostics — 18 October 2026 UTC

The submitted sitemap still has an unresolved Search Console report error. Current evidence does **not** identify a website defect to repair, and successful live inspection does not prove successful sitemap processing.

| Check | Observed result | Scope |
| --- | --- | --- |
| Anonymous HTTPS GET | HTTP 200, `application/xml`, 8,868 bytes, final URL unchanged; 22 canonical URLs | Two direct requests from the same environment, using the diagnostic user agent and a `Googlebot` user-agent string. Changing that string does not make this an actual Google crawl. |
| Published bytes | Match the committed sitemap; SHA-256 `ce00c8883b2eb1fc9f60d6d4bf9f21ffcef1641e7d24571fa08620dac7126f71` | XML parses; this is byte/format evidence, not an indexing test. |
| Robots policy | Allows crawling and names the canonical HTTPS sitemap | The existing publication checks also verify all canonical page routes and language pairs. |
| Google Manual actions | **No issues detected** | Read-only inspection of this property; no account or permission changes. |
| Sitemap report detail | **Sitemap could not be read**, 0 discovered pages; displayed last read **10/18/26** | The detail screen also shows **An error occurred / Please try again later**, without a specific fetch error. One reload returned the same state. The report's displayed fields are preserved without inferring a root cause. |
| Google live URL inspection | **URL is available to Google**, **Crawl allowed: Yes**, **Page fetch: Successful**, **Indexing allowed: Yes** | Google Inspection Tool smartphone; displayed test time **18 October 2026, 2:01 AM**, timezone not inferred. This tests access to the XML URL, not whether the sitemap report processed its entries. |

Google's [Sitemaps report documentation](https://support.google.com/webmasters/answer/7451001) distinguishes fetch errors from parsing errors and recommends checking the report details and live URL fetch. The [sitemap construction guide](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) documents accepted formats and submission as a discovery hint. The current sitemap already follows those format and URL conventions.

No sitemap was deleted, renamed, duplicated or resubmitted during this diagnostic. No XML indexing request was made. Page discovery remains supported by the ordinary internal navigation and the already-submitted sitemap; the earlier page crawl requests retain their separate status. Review the report again when it exposes a specific error or new processing result instead of treating repeated submissions as a fix.

Only public URLs, observed statuses and document fingerprints are recorded here. Account identifiers, console screenshots, credentials, cookies and private data are not published.

**中文：** 当前地图匿名访问为200、XML可解析且与发布文件一致；人工处置报告无问题，Google实时抓取也成功。地图报表仍报读取失败，详情页同时发生加载错误，未给出可定位的原因。两种结果不能相互替代；本轮未重复提交或改变正常地图，也未将实时抓取成功写成地图处理或收录成功。
