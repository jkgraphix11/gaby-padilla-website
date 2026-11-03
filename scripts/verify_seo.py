#!/usr/bin/env python3
"""Check the prepared package or live production crawl/indexing configuration.

This verifies technical eligibility, not inclusion in a search engine's index.
Run before upload: python3 scripts/verify_seo.py --directory _publish
Run after upload:  python3 scripts/verify_seo.py
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

BASE = 'https://gabypadillamakeup.com'
PAIRS = [('/', '/en/'), ('/novias/', '/en/bridal/'),
         ('/xv-anos/', '/en/quinceanera/')]
PATHS = [path for pair in PAIRS for path in pair] + ['/tienda/']
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9',
      'x': 'http://www.w3.org/1999/xhtml'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta, self.links, self.schemas, self.titles, self.h1s = [], [], [], [], []
        self.current, self.buffer = None, ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta.append(attrs)
        elif tag == 'link':
            self.links.append(attrs)
        if tag in ('title', 'h1') or (tag == 'script' and attrs.get('type') == 'application/ld+json'):
            self.current, self.buffer = tag, ''

    def handle_data(self, data):
        if self.current:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag != self.current:
            return
        if tag == 'title':
            self.titles.append(self.buffer.strip())
        elif tag == 'h1':
            self.h1s.append(self.buffer.strip())
        else:
            self.schemas.append(json.loads(self.buffer))
        self.current, self.buffer = None, ''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()

    def fetch(path):
        if args.directory:
            filename = path.lstrip('/') + ('index.html' if path.endswith('/') else '')
            return (args.directory / filename).read_text(encoding='utf-8'), ''
        request = urllib.request.Request(BASE + path, headers={'User-Agent': 'GabyPadilla-SEO-Verification/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            assert response.status == 200, (path, response.status)
            assert response.url == BASE + path, (path, 'unexpected redirect', response.url)
            expected_type = 'text/html' if path.endswith('/') else ('xml' if path.endswith('.xml') else 'text/plain')
            assert expected_type in response.headers.get('Content-Type', ''), (path, 'wrong content type')
            return response.read().decode('utf-8'), ','.join(response.headers.get_all('X-Robots-Tag', []))

    paths = PATHS + ['/robots.txt', '/sitemap.xml']
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = dict(zip(paths, pool.map(fetch, paths)))
    robots = RobotFileParser()
    robots.parse(responses['/robots.txt'][0].splitlines())
    assert BASE + '/sitemap.xml' in (robots.site_maps() or []), 'Sitemap missing from robots.txt'
    sitemap = ET.fromstring(responses['/sitemap.xml'][0])
    nodes = sitemap.findall('s:url', NS)
    locations = [node.findtext('s:loc', namespaces=NS) for node in nodes]
    assert len(locations) == len(set(locations)), 'Duplicate sitemap URLs'
    assert set(locations) == {BASE + path for path in PATHS}, 'Sitemap URL set differs from public pages'
    sitemap_nodes = dict(zip(locations, nodes))
    titles, descriptions = set(), set()
    for path in PATHS:
        html, headers = responses[path]
        page = Page(html)
        rules = [item.get('content', '').lower() for item in page.meta
                 if item.get('name', '').lower() in ('robots', 'googlebot', 'bingbot', 'oai-searchbot')]
        rules.append(headers.lower())
        assert not any(re.search(r'\b(noindex|nofollow|none|nosnippet)\b', rule) for rule in rules), (path, 'restrictive robots rule')
        assert any('index' in rule and 'follow' in rule for rule in rules), (path, 'index/follow missing')
        assert any('max-image-preview:large' in rule.replace(' ', '') for rule in rules), (path, 'large image preview missing')
        for bot in ('Googlebot', 'Googlebot-Image', 'Bingbot', 'OAI-SearchBot'):
            assert robots.can_fetch(bot, BASE + path), (path, bot, 'blocked by robots.txt')
        canonical = [link.get('href') for link in page.links if link.get('rel') == 'canonical']
        assert canonical == [BASE + path], (path, 'canonical mismatch', canonical)
        assert len(page.titles) == 1 and page.titles[0], (path, 'missing or duplicate title')
        assert page.titles[0] not in titles, (path, 'duplicate title across pages')
        titles.add(page.titles[0])
        description = [item.get('content') for item in page.meta if item.get('name') == 'description']
        assert len(description) == 1 and description[0], (path, 'description missing or duplicated')
        assert description[0] not in descriptions, (path, 'duplicate description across pages')
        descriptions.add(description[0])
        assert len(page.h1s) == 1 and page.h1s[0], (path, 'expected one H1')
        if path != '/tienda/':
            assert page.schemas, (path, 'structured data missing')
            es, en = next(pair for pair in PAIRS if path in pair)
            expected = {'es-MX': BASE + es, 'en': BASE + en, 'x-default': BASE + es}
            for links in (page.links, [node.attrib for node in sitemap_nodes[BASE + path].findall('x:link', NS)]):
                alternates = [link for link in links if link.get('hreflang')]
                assert len(alternates) == 3, (path, 'missing or duplicate hreflang')
                assert {link['hreflang']: link.get('href') for link in alternates} == expected, (path, 'hreflang mismatch')
        print(f'PASS {path}: crawl access, robots, canonical, metadata, sitemap' + (', hreflang, JSON-LD' if path != '/tienda/' else ''))
    print('PASS all seven public pages. Search Console is required to confirm actual indexing.')


if __name__ == '__main__':
    main()
