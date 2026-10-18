"""Shareable views keep filter state, language navigation and static content aligned."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SearchRows(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr" and "data-search" in attrs:
            self.rows.append(attrs["data-search"])


class DirectoryViewTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required for view state checks")
    def test_view_state_round_trips_and_browser_navigation(self):
        source = r'''
import assert from 'node:assert/strict';
import {decodeView, encodeView, defaultView, bindDirectoryView} from './site/directory-view.mjs';
const schema={q:{default:''},theme:{default:'',values:['','robustness','calibration']},code:{default:'',values:['','1']},sort:{default:'newest',values:['newest','oldest','title']}};
const state={q:'标签 & probability #1 + <choice>',theme:'robustness',code:'1',sort:'oldest'};
assert.deepEqual(decodeView(encodeView(state,schema),schema),state);
assert.equal(encodeView(defaultView(schema),schema),'');
assert.deepEqual(decodeView('#paper-list',schema),defaultView(schema));
assert.deepEqual(decodeView('#view?theme=unknown&code=true&sort=bad&q=Jev&next=https://example.org',schema),{q:'Jev',theme:'',code:'',sort:'newest'});
assert.equal(encodeView({...state,next:'https://example.org'},schema).includes('next='),false);

function fixture(hash='') {
  const events=new Map(), clicks=new Map(), copies=[];
  const browser={location:new URL('https://awesomejev.github.io/papers/?utm_source=fixture'+hash),history:{state:{retained:true},calls:[]},navigator:{clipboard:{writeText:async value=>copies.push(value)}},addEventListener:(name,fn)=>events.set(name,fn)};
  browser.history.replaceState=(state,_,url)=>{browser.history.calls.push(url);assert.deepEqual(state,{retained:true});browser.location=new URL(url);};
  const links=[{href:'https://awesomejev.github.io/papers/'},{href:'https://awesomejev.github.io/zh/papers/'}];
  const status={textContent:''};let controls={...defaultView(schema)};
  const view=bindDirectoryView({schema,read:()=>controls,apply:value=>controls={...value},languageLinks:links,copyButton:{addEventListener:(name,fn)=>clicks.set(name,fn)},status,messages:{copied:'copied',failed:'failed'}},browser);
  return {browser,links,status,events,copies,view,click:()=>clicks.get('click')(),get:()=>controls,set:value=>controls={...value}};
}
const page=fixture(encodeView(state,schema));
assert.deepEqual(page.get(),state);
assert.equal(new URL(page.links[1].href).pathname,'/zh/papers/');
assert.deepEqual(decodeView(new URL(page.links[1].href).hash,schema),state);
assert.equal(page.browser.history.calls.length,0,'Opening a link must not add history entries');
await page.click();
assert.equal(page.status.textContent,'copied');
const copied=new URL(page.copies[0]);
assert.equal(copied.search,'','Shared links omit unrelated query parameters');
assert.deepEqual(decodeView(copied.hash,schema),state);

page.set({...state,q:'AudioJev',theme:'',code:'',sort:'title'});
page.view.commit();
assert.equal(page.browser.history.calls.length,1);
assert.deepEqual(decodeView(page.browser.location.hash,schema),page.get());
assert.equal(page.status.textContent,'');
page.browser.location.hash=encodeView(state,schema);
page.events.get('popstate')();
assert.deepEqual(page.get(),state);
page.set(defaultView(schema));
page.events.get('pageshow')();
assert.deepEqual(page.get(),state,'BFCache restoration follows the saved URL');
page.browser.location.hash='';
page.events.get('hashchange')();
assert.deepEqual(page.get(),defaultView(schema));
assert.equal(new URL(page.links[1].href).hash,'');
page.set(state);page.view.commit();
page.set(defaultView(schema));page.view.commit();
assert.equal(page.browser.location.hash,'','Reset removes the view fragment');

const anchored=fixture('#paper-list');
assert.equal(new URL(anchored.links[1].href).hash,'#paper-list');
assert.deepEqual(anchored.get(),defaultView(schema));
anchored.browser.navigator.clipboard.writeText=async()=>{throw new Error('fixture-denied');};
await anchored.click();
assert.equal(anchored.status.textContent,'failed');
assert.equal(anchored.copies.length,0);
'''
        result = subprocess.run([shutil.which("node"), "--input-type=module", "-e", source], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bilingual_directories_use_identical_search_text(self):
        for section in ("papers", "models", "tools"):
            with self.subTest(section=section):
                english = SearchRows((ROOT / f"site/{section}/index.html").read_text()).rows
                chinese = SearchRows((ROOT / f"site/zh/{section}/index.html").read_text()).rows
                self.assertTrue(english)
                self.assertEqual(english, chinese)
                for text in english:
                    self.assertRegex(text, r"[\u3400-\u9fff]", "Search must retain the Chinese explanation on both routes")
                    self.assertRegex(text, r"[A-Za-z]", "Search must retain the English metadata on both routes")


if __name__ == "__main__":
    unittest.main()
