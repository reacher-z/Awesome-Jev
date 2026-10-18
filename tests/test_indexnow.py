"""IndexNow submission boundaries; all HTTP calls are fixtures."""
import contextlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import submit_indexnow as indexnow


PAGES = [indexnow.SITE + path for path in ["/", "/zh/", "/papers/", "/zh/papers/", "/sources/", "/zh/sources/"]]
KEY = "fixture-public-key"


class Response(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(body)
        self.status = status


def sitemap(path):
    path.write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                    ''.join('<url><loc>' + url + '</loc></url>' for url in PAGES) + '</urlset>')


class IndexNowTests(unittest.TestCase):
    def test_sitemap_can_grow_but_duplicate_or_empty_pages_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sitemap.xml"
            expanded = PAGES + [indexnow.SITE + "/discoveries/", indexnow.SITE + "/zh/discoveries/"]
            def write(pages):
                path.write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + url + '</loc></url>' for url in pages) + '</urlset>')
            write(expanded)
            self.assertEqual(indexnow.changed_urls(path), expanded)
            self.assertEqual(indexnow.changed_urls(path, [expanded[-1]]), [expanded[-1]])
            for invalid in [[], expanded + [expanded[0]]]:
                write(invalid)
                with self.assertRaises(indexnow.SubmissionError):
                    indexnow.changed_urls(path)

    def test_default_dry_run_reads_no_key_and_sends_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'site').mkdir()
            sitemap(root / 'site/sitemap.xml')
            output = io.StringIO()
            with patch.object(indexnow, 'ROOT', root), patch.object(indexnow.urllib.request, 'build_opener') as opener, contextlib.redirect_stdout(output):
                self.assertEqual(indexnow.main([]), 0)
            opener.assert_not_called()
            report = json.loads(output.getvalue())
            self.assertEqual(report['changed_urls'], PAGES)
            self.assertNotIn('key', report)

    def test_only_site_https_urls_without_queries_or_credentials_are_allowed(self):
        credentials = 'https://' + 'fixture-user' + ':' + 'fixture-password' + '@' + indexnow.HOST + '/'
        for url in ['https://google.com/', 'https://github.com/AwesomeJev/AwesomeJev.github.io', 'http://' + indexnow.HOST + '/', PAGES[0] + '?lang=zh', PAGES[0] + '#papers', credentials]:
            with self.subTest(kind=url.split(':', 1)[0]), self.assertRaises(indexnow.SubmissionError):
                indexnow.site_url(url)

    def test_mismatched_live_key_or_canonical_prevents_post(self):
        opener = Mock()
        opener.open.return_value = Response(b'different-public-fixture')
        with self.assertRaises(indexnow.SubmissionError):
            indexnow.submit(PAGES, KEY, opener)
        self.assertEqual([c.args[0].get_method() for c in opener.open.call_args_list], ['GET'])
        opener = Mock()
        opener.open.side_effect = [Response(KEY.encode()), Response(b'<html><head></head></html>')]
        with self.assertRaises(indexnow.SubmissionError):
            indexnow.submit(PAGES, KEY, opener)
        self.assertTrue(all(c.args[0].get_method() == 'GET' for c in opener.open.call_args_list))

    def test_single_post_uses_fixed_endpoint_and_receipt_is_not_indexing(self):
        for status in [200, 202, 429]:
            with self.subTest(status=status):
                opener = Mock()
                responses = [Response(KEY.encode())]
                responses += [Response(('<html><head><link rel="canonical" href="' + url + '"></head></html>').encode()) for url in PAGES]
                responses += [Response(b'', status=status)]
                opener.open.side_effect = responses
                self.assertEqual(indexnow.submit(PAGES, KEY, opener), status)
                posts = [c.args[0] for c in opener.open.call_args_list if c.args[0].get_method() == 'POST']
                self.assertEqual(len(posts), 1)
                self.assertEqual(posts[0].full_url, indexnow.ENDPOINT)
                payload = json.loads(posts[0].data)
                self.assertEqual(payload, {'host': indexnow.HOST, 'key': KEY, 'keyLocation': indexnow.KEY_LOCATION, 'urlList': PAGES})
                if status in [200, 202]:
                    self.assertIn('does not mean', indexnow.status_message(status))
                else:
                    self.assertIn('No automatic retry', indexnow.status_message(status))


class ConnectionFailureTests(unittest.TestCase):
    """A dropped connection must map to the safe messages and exit 1, not a traceback."""

    def submit(self, side_effect):
        opener = Mock()
        opener.open.side_effect = side_effect
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'site').mkdir()
            sitemap(root / 'site/sitemap.xml')
            (root / 'site/indexnow-key.txt').write_text(KEY + '\n', encoding='utf-8')
            with patch.object(indexnow, 'ROOT', root), patch.object(indexnow.urllib.request, 'build_opener', return_value=opener), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                code = indexnow.main(['--submit', '--url', PAGES[0]])
        return code, stderr.getvalue(), [c.args[0].get_method() for c in opener.open.call_args_list]

    def failures(self):
        return [http.client.RemoteDisconnected('Remote end closed connection without response'),
                ConnectionResetError('Connection reset by peer')]

    def test_dropped_live_verification_sends_no_submission(self):
        for failure in self.failures():
            with self.subTest(failure=type(failure).__name__):
                code, stderr, methods = self.submit(failure)
                self.assertEqual(code, 1)
                self.assertEqual(stderr.strip(), 'Live verification failed; no submission was sent.')
                self.assertEqual(methods, ['GET'])

    def test_truncated_live_page_sends_no_submission(self):
        truncated = Mock(status=200)
        truncated.__enter__ = Mock(return_value=truncated)
        truncated.__exit__ = Mock(return_value=False)
        truncated.read.side_effect = http.client.IncompleteRead(b'fixture')
        code, stderr, methods = self.submit([Response(KEY.encode()), truncated])
        self.assertEqual(code, 1)
        self.assertEqual(stderr.strip(), 'Live verification failed; no submission was sent.')
        self.assertEqual(methods, ['GET', 'GET'])

    def test_dropped_single_post_is_unconfirmed_and_not_retried(self):
        page = ('<html><head><link rel="canonical" href="' + PAGES[0] + '"></head></html>').encode()
        for failure in self.failures():
            with self.subTest(failure=type(failure).__name__):
                code, stderr, methods = self.submit([Response(KEY.encode()), Response(page), failure])
                self.assertEqual(code, 1)
                self.assertIn('receipt is unconfirmed. No automatic retry was attempted.', stderr)
                self.assertEqual(methods, ['GET', 'GET', 'POST'])


if __name__ == '__main__':
    unittest.main()
