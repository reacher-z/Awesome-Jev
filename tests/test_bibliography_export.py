"""Filtered citation exports preserve source entries and exact reviewed versions."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest
from urllib.parse import urlsplit, parse_qs

from scripts.validate import bib_fields

ROOT=Path(__file__).resolve().parents[1]


class ExportButton(HTMLParser):
    def __init__(self,text):
        super().__init__();self.button=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='button'and attrs.get('id')=='paper-export':self.button=attrs


class ThemeControls(HTMLParser):
    def __init__(self,text):
        super().__init__();self.options={};self.buttons=[];self.in_theme=False;self.option=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='select':self.in_theme=attrs.get('id')=='paper-theme'
        if tag=='option'and self.in_theme:self.option=attrs['value'];self.options[self.option]=''
        if tag=='button'and 'data-theme'in attrs:self.buttons.append(attrs['data-theme'])
    def handle_endtag(self,tag):
        if tag=='option':self.option=None
        if tag=='select':self.in_theme=False
    def handle_data(self,value):
        if self.option is not None:self.options[self.option]+=value


@unittest.skipUnless(shutil.which('node'),'Node is required for bibliography export checks')
class BibliographyExportTests(unittest.TestCase):
    def node(self,source):
        result=subprocess.run(['node','--input-type=module','-e',source],cwd=ROOT,text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return result.stdout

    def test_nested_text_unicode_quotes_and_selection_order_are_preserved(self):
        self.node(r'''
import assert from 'node:assert/strict';
import {parseBibliography,selectBibliography,bibliographyText} from './site/bibliography.mjs';
const first=String.raw`@misc{alpha,
 title = {Nested {Jev}, {α} and quoted "labels"},
 author = {Dörr, A and Li, B},
 url = {https://arxiv.org/abs/2610.12345v2},
 note = {Version 2, 2026-10-14; first posted 2026-10-02; preprint}
}`;
const second=`@article{beta,
 title = "A title, with a comma", author={B. Author}, year={2026},
 url="https://arxiv.org/abs/2610.12346v1"
}`;
const text=`% public fixture\n@comment{Ignored {nested} comment}\n@book{book,title={A book},author={A},year={2020},month=oct}\n${first}\n\n${second}\n`;
const entries=parseBibliography(text);
assert.equal(entries.length,3);
assert.equal(entries[1].text,first);
assert.equal(entries[2].text,second);
const chosen=selectBibliography(entries,[entries[2].url,entries[1].url]);
assert.deepEqual(chosen.map(entry=>entry.key),['beta','alpha']);
assert.equal(bibliographyText(chosen),second+'\n\n'+first+'\n');
assert.equal(bibliographyText(selectBibliography(entries,[])),'');
assert.throws(()=>selectBibliography(entries,['https://arxiv.org/abs/2610.12345v1']),/no matching citation/);
assert.throws(()=>selectBibliography(entries,[entries[1].url,entries[1].url]),/Duplicate/);
''')

    def test_ambiguous_and_incomplete_bibliographies_fail_closed(self):
        self.node(r'''
import assert from 'node:assert/strict';
import {parseBibliography} from './site/bibliography.mjs';
const valid='@misc{a,title={A},author={A},year={2026},url={https://example.org/a}}';
for(const bad of ['',valid.slice(0,-1),valid+'\n'+valid.replace('{a,','{A,'),
 valid+'\n'+valid.replace('{a,','{b,'),
 '@misc{a,title={A},url=unresolved_macro}',
 '@misc{a,title=unresolved_macro,url={https://example.org/a}}',
 '@misc{a,title={A},url={https://example.org/} # {a}}',
 '@misc{a,title={A},url="https://example.org/" # "a"}',
 valid+'\n@string{venue={Example}}',
 valid+'\n@preamble{"Example"}',
 '@misc{a,title={A},crossref={parent},url={https://example.org/a}}',
 '@misc{a,title={A},url={https://example.org/a},url={https://example.org/b}}',
 '@misc{a,title="unclosed,url={https://example.org/a}}']) assert.throws(()=>parseBibliography(bad));
''')

    def test_every_curated_paper_exports_its_original_source_entry(self):
        source=(ROOT/'references.bib').read_text()
        expected={}
        starts=list(re.finditer(r'^@\w+\{([^,\s]+),',source,re.M))
        for index,match in enumerate(starts):
            chunk=source[match.start():starts[index+1].start()if index+1<len(starts)else len(source)]
            end=chunk.rfind('}')
            entry=chunk[:end+1].strip()
            field_values={name:value.strip('{}" \t\n')for name,value in bib_fields(chunk[match.end()-match.start():end])or[]}
            if field_values.get('url'):expected[field_values['url']]={'key':match[1],'text':entry}
        result=json.loads(self.node('''
import {readFileSync} from 'node:fs';
import {resources} from './site/catalog.mjs';
import {parseBibliography,selectBibliography} from './site/bibliography.mjs';
console.log(JSON.stringify(selectBibliography(parseBibliography(readFileSync('references.bib','utf8')),resources.filter(r=>r.category==='Papers').map(r=>r.url))));
'''))
        papers=json.loads((ROOT/'site/papers.json').read_text())['papers']
        self.assertEqual([entry['url']for entry in result],[paper['url']for paper in papers])
        for entry in result:
            with self.subTest(url=entry['url']):
                self.assertEqual(entry['key'],expected[entry['url']]['key'])
                self.assertEqual(entry['text'],expected[entry['url']]['text'])

    def test_mobile_themes_match_desktop_choices_and_catalog_counts(self):
        data=json.loads((ROOT/'site/papers.json').read_text())
        for language,route in [('en','papers/index.html'),('zh','zh/papers/index.html')]:
            controls=ThemeControls((ROOT/'site'/route).read_text())
            self.assertEqual(set(controls.options),set(controls.buttons))
            expected={'':('All'if language=='en'else'全部')+f" ({len(data['papers'])})"}
            expected.update({theme['id']:theme['short'][language]+f" ({sum(paper['theme']==theme['id']for paper in data['papers'])})"for theme in data['themes']})
            self.assertEqual(controls.options,expected)

    def test_both_pages_use_a_hidden_progressive_export_and_current_bibtex_hash(self):
        digest=hashlib.sha256((ROOT/'references.bib').read_bytes()).hexdigest()[:12]
        for route in ['papers/index.html','zh/papers/index.html']:
            button=ExportButton((ROOT/'site'/route).read_text()).button
            self.assertIsNotNone(button)
            self.assertIn('hidden',button)
            url=urlsplit(button['data-bibliography'])
            self.assertEqual(url.path,'/references.bib')
            self.assertEqual(parse_qs(url.query),{'v':[digest]})
            self.assertEqual(url.fragment,'')
