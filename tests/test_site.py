"""Dependency-free publication checks. Run: python3 -m unittest discover -s tests -v."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.nodes = []
        self.text = []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))
    def handle_data(self, data):
        self.text.append(data)
    def attrs(self, tag):
        return [attrs for name, attrs in self.nodes if name == tag]

class SiteTests(unittest.TestCase):
    def test_home_presents_current_work_with_qualified_metrics(self):
        page = Document(ROOT / 'index.html')
        text = ' '.join(' '.join(page.text).split())
        for phrase in (
            'Machine learning for better commerce decisions.', 'Bengaluru',
            'Finding higher-value audiences', 'Turning customer value into targeting signals',
            'Making checkout risk actionable', '350M+', '13%', '2.5×', 'last-click',
            'not causal incrementality', '10M+', '₹500 crore+', 'GMV supported',
            '21%', '10% recall', '500K+', '20ms',
            'Senior Applied Scientist – Lead', 'Oct 2025', 'Applied Scientist II',
            'Apr 2023', 'Applied Scientist I', 'Jun 2021',
            'Qwen3', '3M+', '500M+', '100M+', '3 percentage points',
            '7 percentage points', 'hired and ramped three applied scientists',
            'Kaggle Notebooks Master', 'Techno Main Salt Lake', '8.99/10',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertEqual(len(page.attrs('h1')), 1)
        self.assertEqual(len(page.attrs('main')), 1)
        self.assertEqual(len(page.attrs('details')), 3)
        self.assertEqual(len([a for a in page.attrs('article') if a.get('class') == 'work-row']), 3)
        self.assertTrue(any(a.get('href') == '#main' for a in page.attrs('a')))
        self.assertFalse(page.attrs('img'), 'Work-led home must not use photographs')
        for stale in ('undergrad', 'open to work', 'HR@5', 'tel:', 'tracking', 'google-analytics'):
            self.assertNotIn(stale.lower(), (ROOT / 'index.html').read_text().lower())

    def test_home_has_social_metadata_and_accessible_local_theme(self):
        page = Document(ROOT / 'index.html')
        metadata = {a.get('name', a.get('property')): a.get('content') for a in page.attrs('meta')}
        self.assertIn('production', metadata.get('description', ''))
        for key in ('og:title', 'og:description', 'og:image', 'og:image:alt', 'og:url', 'twitter:card'):
            self.assertTrue(metadata.get(key), key)
        self.assertIn({'rel': 'canonical', 'href': 'https://jain-aayush.github.io/'}, page.attrs('link'))
        self.assertEqual(metadata['og:image'], 'https://jain-aayush.github.io/static/images/social.png')
        self.assertEqual(metadata['twitter:image'], metadata['og:image'])
        self.assertEqual(metadata['og:image:type'], 'image/png')
        self.assertEqual(metadata['og:image:width'], '1200')
        self.assertEqual(metadata['og:image:height'], '630')
        import struct
        raster = (ROOT / 'static/images/social.png').read_bytes()
        self.assertEqual(raster[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II', raster[16:24]), (1200, 630))
        self.assertTrue((ROOT / 'static/images/social.svg').exists())
        self.assertTrue((ROOT / 'static/images/favicon.svg').exists())
        css = (ROOT / 'static/css/style.css').read_text()
        for token in ('#2A78D6', '-apple-system', 'BlinkMacSystemFont', 'HKGrotesk-Regular.woff', ':focus-visible', 'prefers-reduced-motion', '@media', '@media print'):
            self.assertIn(token, css)
        self.assertNotIn('http', css)
        for attrs in page.attrs('script'):
            self.assertFalse(attrs.get('src', '').startswith('http'))

    def test_resume_is_printable_private_and_reachable(self):
        self.assertTrue((ROOT / 'resume.html').is_file(), 'Publish a clean HTML résumé')
        page = Document(ROOT / 'resume.html')
        text = ' '.join(' '.join(page.text).split())
        for phrase in ('Aayush Jain', 'Senior Applied Scientist – Lead', 'Oct 2025–Present', 'Apr 2023–Oct 2025', 'Jun 2021–Mar 2023', '350M+', 'last-click', 'not causal incrementality', 'GMV supported', '10% recall', '500K+', 'Qwen3', '8.99/10'):
            self.assertIn(phrase, text)
        self.assertEqual(len(page.attrs('h1')), 1)
        self.assertEqual(len(page.attrs('main')), 1)
        self.assertIn('Print', text)
        source = (ROOT / 'resume.html').read_text()
        self.assertNotIn('tel:', source)
        self.assertNotRegex(text, r'(?<!\d)\d{10}(?!\d)')
        self.assertFalse(list(ROOT.glob('*.pdf')))
        self.assertIn('window.print()', (ROOT / 'static/js/main.js').read_text())
        css = (ROOT / 'static/css/style.css').read_text()
        self.assertIn('.resume', css)
        readme = (ROOT / 'README.md').read_text()
        for phrase in ('python3 -m http.server', 'unittest discover', 'before merge', 'employer', '/alfred'):
            self.assertIn(phrase, readme)

    def test_local_links_assets_and_heading_hierarchy(self):
        from urllib.parse import urlsplit, unquote
        import re
        import xml.etree.ElementTree as ET
        for path in ROOT.rglob('*.html'):
            filename = str(path.relative_to(ROOT))
            page = Document(path)
            ids = [a['id'] for _, a in page.nodes if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)), filename)
            previous = 0
            for tag, attrs in page.nodes:
                if re.fullmatch(r'h[1-6]', tag):
                    level = int(tag[1])
                    self.assertLessEqual(level, previous + 1, f'{filename}: skipped heading level')
                    previous = level
                keys = ['href', 'src']
                if tag == 'meta' and attrs.get('property', attrs.get('name')) in ('og:url', 'og:image', 'twitter:image'):
                    keys.append('content')
                for key in keys:
                    value = attrs.get(key, '')
                    url = urlsplit(value)
                    if not value:
                        continue
                    if url.scheme or url.netloc:
                        if url.netloc != 'jain-aayush.github.io':
                            continue
                        destination = ROOT / unquote(url.path.lstrip('/'))
                    elif url.path.startswith('/'):
                        destination = ROOT / unquote(url.path.lstrip('/'))
                    else:
                        destination = path.parent / unquote(url.path) if url.path else path
                    if destination.is_dir():
                        destination /= 'index.html'
                    self.assertTrue(destination.is_file(), f'{filename}: missing {value}')
                    if url.fragment:
                        target_ids = [a['id'] for _, a in Document(destination).nodes if 'id' in a]
                        self.assertIn(unquote(url.fragment), target_ids, f'{filename}: missing anchor {value}')
            for tag in ('script', 'img'):
                for attrs in page.attrs(tag):
                    self.assertFalse(attrs.get('src', '').startswith(('http:', 'https:', '//')))
            self.assertNotRegex(path.read_text(), r'(?:tel:|\b\d{10}\b)')
        for csspath in ROOT.rglob('*.css'):
            for reference in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', csspath.read_text()):
                url = urlsplit(reference.strip())
                if url.scheme or url.netloc:
                    continue
                destination = ROOT / unquote(url.path.lstrip('/')) if url.path.startswith('/') else csspath.parent / unquote(url.path)
                self.assertTrue(destination.is_file(), reference)
        for filename in ('social.svg', 'favicon.svg'):
            ET.parse(ROOT / 'static/images' / filename)

    def test_skip_link_target_accepts_keyboard_focus(self):
        for filename in ('index.html', 'resume.html'):
            page = Document(ROOT / filename)
            target = next(a for tag, a in page.nodes if a.get('id') == 'main')
            self.assertEqual(target.get('tabindex'), '-1', filename)

    def test_main_has_visible_layout_neutral_keyboard_focus(self):
        css = (ROOT / 'static/css/style.css').read_text()
        self.assertIn('main:focus-visible', css)
        rule = css.split('main:focus-visible', 1)[1].split('}', 1)[0]
        self.assertIn('outline:', rule)
        self.assertNotIn('border:', rule)

    def test_print_keeps_short_resume_sections_together(self):
        css = (ROOT / 'static/css/style.css').read_text()
        self.assertIn('.resume section:not(:first-of-type) { break-inside: avoid; }', css)

    def test_alfred_is_byte_for_byte_preserved(self):
        expected = {
            'index.html': '58adf688268f9c4c7b5a24ebf3c37bacdcf0d3930b773b9ba92e5abc9f15427e',
            'privacy.html': 'f570e71bd55d1a4932be5d67aa2047b0b0a047d580edba39f019a2f7f62ee190',
        }
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / 'alfred' / name).read_bytes()).hexdigest(), digest)

if __name__ == '__main__':
    unittest.main()
