"""Primary discovery must work without aggregators and obey transport/evidence boundaries."""
import concurrent.futures
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from html import escape

from scripts import arxiv_discovery as api
from scripts import refresh_sources as refresh
from scripts import validate

ABSTRACT = 'Jev is a TypeSafe typed decision model. ' + 'We evaluate probability calibration and finite option decisions with controlled benchmark comparisons. ' * 4
PID = '2610.21411'


def entry(pid=PID, version='v1', title='Jev decision fixture', abstract=ABSTRACT):
    return f'<entry><id>http://arxiv.org/abs/{pid}{version}</id><title>{escape(title)}</title><summary>{escape(abstract)}</summary><published>2026-10-15T07:00:00Z</published><updated>2026-10-16T07:00:00Z</updated><author><name>Example Fixture</name></author></entry>'


def feed(entries=None, total=None, start=0, size=200):
    entries = [entry()] if entries is None else entries
    total = len(entries) if total is None else total
    return (f'<feed xmlns="http://www.w3.org/2005/Atom" xmlns:o="http://a9.com/-/spec/opensearch/1.1/">'
            f'<o:totalResults>{total}</o:totalResults><o:startIndex>{start}</o:startIndex><o:itemsPerPage>{size}</o:itemsPerPage>'
            + ''.join(entries) + '</feed>').encode()


def page(pid=PID, version='v1', abstract=ABSTRACT):
    return (f'<meta name="citation_title" content="Jev decision fixture"><meta name="citation_author" content="Fixture, Example">'
            f'<meta name="citation_date" content="2026/10/15"><td class="arxividv"><a href="https://arxiv.org/abs/{pid}{version}">version</a></td>'
            f'<blockquote class="abstract">Abstract: {escape(abstract)}</blockquote>').encode()


class FakeFetcher:
    def __init__(self, responses):
        self.responses, self.urls = responses, []
    def fetch(self, url):
        self.urls.append(url)
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        return response, url, 'application/atom+xml' if api.api_host(url) else 'text/html'


class Clock:
    def __init__(self):
        self.time = 100.0
    def now(self):
        return self.time
    def sleep(self, seconds):
        self.time += seconds


class ArxivFeedTests(unittest.TestCase):
    def test_valid_atom_preserves_version_dates_and_unicode(self):
        papers, total = api.parse_feed(feed([entry(title='Jev 决策 fixture')]), 0, 200)
        self.assertEqual(total, 1)
        self.assertEqual(papers[0]['title'], 'Jev 决策 fixture')
        self.assertEqual(papers[0]['version_url'], 'https://arxiv.org/abs/' + PID + 'v1')
        self.assertEqual(papers[0]['published_at'], '2026-10-15')
        self.assertEqual(api.parse_feed(feed([]), 0, 200), ([], 0))

    def test_legacy_identifier_does_not_invalidate_a_modern_discovery_page(self):
        papers,total=api.parse_feed(feed([entry(),entry('cs/0607143',title='Historical study',abstract='An unrelated historical computer science paper.')]),0,200)
        self.assertEqual(total,2)
        self.assertEqual(papers[1]['id'],'cs/0607143')
        fetcher=FakeFetcher({api.query_url():feed([entry('cs/0607143')])})
        scan=refresh.Scan(fetcher)
        self.assertEqual(scan.scan_arxiv(),[])
        self.assertEqual(scan.errors[-1]['code'],'arxiv_discovery_unsupported_legacy_id')
        self.assertEqual(fetcher.urls,[api.query_url()])

    def test_error_unsafe_and_inconsistent_feeds_are_rejected(self):
        invalid = [b'<html>unavailable</html>', b'<feed',
            b'<!DOCTYPE feed [<!ENTITY x SYSTEM "file:///private/fixture">]>' + feed(),
            feed().replace(b'http://arxiv.org/abs/', b'http://example.org/abs/'),
            feed().replace(b'2026-10-15T07:00:00Z', b'not-a-date'),
            feed().replace(b'<author>', b'<not-author>').replace(b'</author>', b'</not-author>'),
            feed([entry(), entry()], total=2), feed([], total=1), feed(start=1),
            feed().replace(b'<o:totalResults>1', b'<o:totalResults>-1')]
        for raw in invalid:
            with self.subTest(raw=raw[:30]):
                with self.assertRaisesRegex(ValueError, '^invalid_arxiv_api_feed$'):
                    api.parse_feed(raw, 0, 200)


class ArxivDiscoveryTests(unittest.TestCase):
    def test_new_candidate_requires_primary_page_and_satisfies_schema(self):
        url='https://arxiv.org/abs/' + PID + 'v1'
        fetcher=FakeFetcher({api.query_url():feed(), url:page()})
        scan=refresh.Scan(fetcher)
        rows=scan.scan_arxiv()
        self.assertEqual(fetcher.urls, [api.query_url(), url])
        self.assertEqual(rows[0]['authors'], ['Example Fixture'])
        self.assertEqual(rows[0]['reviewed_version_url'], url)
        self.assertEqual(rows[0]['verification_level'], 'abstract_checked')
        self.assertFalse(rows[0]['full_text_reviewed'])
        self.assertNotIn('abstract', rows[0])
        self.assertNotIn('summary', rows[0])
        self.assertEqual(scan.arxiv_discovery['verified_new'], 1)
        self.assertTrue(scan.arxiv_discovery['query_complete'])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'research-sources.jsonl';path.write_text(json.dumps(rows[0])+'\n')
            with patch.object(validate,'ROOT',Path(directory)), patch.object(validate,'errors',[])as errors:
                validate.check_ledger(path);validate.check_record_ids_and_authors(path)
                self.assertEqual(errors, [])

    def test_new_primary_evidence_survives_other_provider_landing_pages(self):
        url='https://arxiv.org/abs/'+PID
        scan=refresh.Scan(FakeFetcher({api.query_url():feed(),url+'v1':page()}))
        primary=scan.scan_arxiv()[0]
        landing={'url':url,'title':'Jev decision fixture','verification_level':'content_screened','status':'screened',
                 'content_sha256':'a'*64,'retrieved_at':'2026-10-15T00:00:00Z','relation':'direct','relevance':'Landing-page fixture.'}
        for incoming in ([landing,primary],[primary,landing]):
            merged,changes=refresh.merge_records(refresh.Ledger([],[]),incoming)
            self.assertEqual(merged.rows[0]['abstract_provider'],'arxiv_primary_abstract_page')
            self.assertEqual(changes['added'],[url])
        prior=refresh.Ledger([landing],[json.dumps(landing)+'\n'])
        merged,_=refresh.merge_records(prior,[primary,landing])
        self.assertEqual(merged.lines,prior.lines)

    def test_failed_or_mismatched_page_cannot_promote_api_metadata(self):
        url='https://arxiv.org/abs/' + PID + 'v1'
        for result in [refresh.FetchError('http_503'), page(version='v2'), page(abstract='unrelated short text')]:
            with self.subTest(result=type(result).__name__):
                scan=refresh.Scan(FakeFetcher({api.query_url():feed(),url:result}))
                row=scan.scan_arxiv()[0]
                self.assertEqual(row['verification_level'],'metadata_only')
                self.assertEqual(row['status'],'unavailable')
                self.assertNotIn('abstract_sha256',row)
                self.assertEqual(scan.arxiv_discovery['unavailable_new'],1)
                self.assertTrue(scan.errors)

    def test_known_excluded_and_irrelevant_entries_do_not_fetch_papers(self):
        class Policy:
            def exclusion(self, url):return url.endswith('21412')
        entries=[entry(),entry('2610.21412'),entry('2610.21413',title='Japanese encephalitis virus',abstract='Japanese encephalitis virus uses the abbreviation JEV.')]
        fetcher=FakeFetcher({api.query_url():feed(entries)})
        scan=refresh.Scan(fetcher, known_keys={'https://arxiv.org/abs/'+PID},policy=Policy())
        self.assertEqual(scan.scan_arxiv(), [])
        self.assertEqual(fetcher.urls,[api.query_url()])
        self.assertEqual(scan.arxiv_discovery['known_skipped'],1)
        self.assertEqual(scan.curation_excluded,{'https://arxiv.org/abs/2610.21412'})

    def test_pagination_reaches_end_without_an_intake_count_cap(self):
        pids=[PID,'2610.21412','2610.21413']
        responses={api.query_url(0,2):feed([entry(p)for p in pids[:2]],total=3,size=2),api.query_url(2,2):feed([entry(pids[2])],total=3,start=2,size=2)}
        responses.update({'https://arxiv.org/abs/'+p+'v1':page(p)for p in pids})
        scan=refresh.Scan(FakeFetcher(responses))
        with patch.object(api,'PAGE_SIZE',2):rows=scan.scan_arxiv()
        self.assertEqual(len(rows),3)
        self.assertEqual(scan.arxiv_discovery['pages'],2)
        self.assertTrue(scan.arxiv_discovery['query_complete'])

    def test_changed_pagination_reports_partial_and_keeps_verified_records(self):
        responses={api.query_url(0,1):feed(total=2,size=1),api.query_url(1,1):feed(total=2,start=1,size=1),'https://arxiv.org/abs/'+PID+'v1':page()}
        scan=refresh.Scan(FakeFetcher(responses))
        with patch.object(api,'PAGE_SIZE',1):rows=scan.scan_arxiv()
        self.assertEqual(len(rows),1)
        self.assertFalse(scan.arxiv_discovery['query_complete'])
        self.assertEqual(scan.errors[-1]['code'],'arxiv_discovery_failed:arxiv_pagination_changed')

    def test_smoke_only_reads_one_small_feed_page(self):
        url=api.query_url(0,5)
        entries=[entry('2610.'+str(21411+i))for i in range(5)]
        scan=refresh.Scan(FakeFetcher({url:feed(entries,total=6,size=5)}),known_keys={'https://arxiv.org/abs/2610.'+str(21411+i)for i in range(5)})
        self.assertEqual(scan.scan_arxiv(smoke=True),[])
        self.assertTrue(scan.arxiv_discovery['smoke_limited'])
        self.assertFalse(scan.arxiv_discovery['query_complete'])

    def test_api_failure_is_diagnostic_and_never_a_successful_query(self):
        scan=refresh.Scan(FakeFetcher({api.query_url():refresh.FetchError('http_503')}))
        self.assertEqual(scan.scan_arxiv(),[])
        self.assertEqual(scan.successful_queries,0)
        self.assertEqual(scan.errors[-1]['code'],'arxiv_discovery_failed:http_503')

    def test_rlcd_acronym_collision_is_not_direct_decision_research(self):
        self.assertFalse(refresh.direct_paper("Rank of random matrices", "Our model studies probability bounds using a randomized least common denominator (RLCD)."))
        self.assertTrue(refresh.direct_paper("RLCD training", "Reinforcement learning produces calibrated decisions for language models."))

    def test_catalog_identity_is_already_known_even_without_a_ledger_row(self):
        url='https://arxiv.org/abs/'+PID
        fetcher=FakeFetcher({api.query_url():feed()})
        scan=refresh.Scan(fetcher,curated_seeds={url:{'url':url}})
        self.assertEqual(scan.scan_arxiv(),[])
        self.assertEqual(fetcher.urls,[api.query_url()])
        self.assertEqual(scan.arxiv_discovery['known_skipped'],1)

    def test_primary_discovery_is_wired_in_even_when_aggregators_fail(self):
        fetcher=FakeFetcher({api.query_url(0,5):feed(size=5),'https://arxiv.org/abs/'+PID+'v1':page()})
        scan=refresh.Scan(fetcher)
        with patch.object(scan,'query',side_effect=lambda topic,q,provider:(topic,q,{'data':[]})):
            _,direct=scan.scan_research(smoke=True)
        self.assertEqual(len(direct),1)
        self.assertEqual(direct[0]['abstract_provider'],'arxiv_primary_abstract_page')


class ArxivTransportTests(unittest.TestCase):
    def test_retry_is_spaced_three_seconds_after_each_attempt(self):
        clock=Clock();attempts=[]
        def request(url):
            attempts.append(clock.now())
            clock.time+=.5
            return (503,{},b'') if len(attempts)==1 else (200,{},feed())
        with patch.object(refresh.time,'monotonic',clock.now),patch.object(refresh.time,'sleep',clock.sleep):
            fetcher=refresh.PublicFetcher(retries=1)
            with patch.object(fetcher,'_request_public',side_effect=request):fetcher.fetch(api.query_url())
        self.assertEqual(len(attempts),2)
        self.assertGreaterEqual(attempts[1]-attempts[0],3.5)

    def test_redirect_between_api_hosts_uses_the_same_pacing_gate(self):
        clock=Clock();attempts=[]
        def request(url):
            attempts.append(clock.now());clock.time+=.5
            return (302,{'location':'https://arxiv.org/api/query?start=0'},b'') if len(attempts)==1 else (200,{},feed())
        with patch.object(refresh.time,'monotonic',clock.now),patch.object(refresh.time,'sleep',clock.sleep):
            fetcher=refresh.PublicFetcher(retries=0)
            with patch.object(fetcher,'_request_public',side_effect=request):fetcher.fetch(api.query_url())
        self.assertEqual(len(attempts),2)
        self.assertGreaterEqual(attempts[1]-attempts[0],3.5)

    def test_pacing_respects_deadline_without_issuing_extra_request(self):
        clock=Clock()
        with patch.object(refresh.time,'monotonic',clock.now),patch.object(refresh.time,'sleep',clock.sleep):
            fetcher=refresh.PublicFetcher(retries=0,budget=2)
            with patch.object(fetcher,'_request_public',return_value=(200,{},feed()))as request:
                fetcher.fetch(api.query_url())
                with self.assertRaisesRegex(refresh.FetchError,'retry_budget_exhausted'):
                    fetcher.fetch(api.query_url(200))
                self.assertEqual(request.call_count,1)
                self.assertTrue(fetcher.budget_exhausted)

    def test_api_connections_are_serial_across_threads(self):
        clock=Clock();entered=threading.Event();release=threading.Event();second=threading.Event();calls=[]
        def request(url):
            calls.append(url)
            if len(calls)==1:
                entered.set();self.assertTrue(release.wait(2))
            else:second.set()
            return 200,{},feed()
        with patch.object(refresh.time,'monotonic',clock.now),patch.object(refresh.time,'sleep',clock.sleep):
            fetcher=refresh.PublicFetcher(retries=0)
            with patch.object(fetcher,'_request_public',side_effect=request),concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
                first=pool.submit(fetcher.fetch,api.query_url());self.assertTrue(entered.wait(2))
                other=pool.submit(fetcher.fetch,api.query_url(200));self.assertFalse(second.wait(.05))
                release.set();first.result();other.result()
        self.assertTrue(second.is_set())
