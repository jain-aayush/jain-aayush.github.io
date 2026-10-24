"""Structural guardrails for the original, fact-grounded visual field guide.
Actual viewport composition and print pagination still require browser review.
"""
import re
import unittest
import xml.etree.ElementTree as ET
from test_site import ROOT


class VisualFieldGuideTests(unittest.TestCase):
    def test_hero_contains_original_accessible_commerce_diagram(self):
        source = (ROOT / 'index.html').read_text()
        hero = source.split('<section class="hero"', 1)[1].split('</section>', 1)[0]
        self.assertIn('hero-visual', hero)
        self.assertIn('<svg', hero)
        self.assertIn('Illustrative', hero)
        for phrase in ('Audience', 'Customer value', 'Checkout risk'):
            self.assertIn(phrase, hero)

    def test_each_case_has_a_distinct_explanatory_visual(self):
        source = (ROOT / 'index.html').read_text()
        for case in ('audience', 'value', 'risk'):
            with self.subTest(case=case):
                self.assertIn(f'data-case="{case}"', source, 'Each case needs its own visual identity')
                article = source.split(f'data-case="{case}"', 1)[1].split('</article>', 1)[0]
                self.assertIn('<svg', article)
                self.assertIn('Illustrative', article)
        for phrase in ('User tower', 'Brand tower', 'Match', 'SHAP', 'Real-time', 'Batch'):
            self.assertIn(phrase, source)

    def test_all_inline_diagrams_have_unique_accessible_names_and_descriptions(self):
        source = (ROOT / 'index.html').read_text()
        diagrams = re.findall(r'<svg\b.*?</svg>', source, re.S)
        self.assertGreaterEqual(len(diagrams), 5)
        ids = set()
        for svg in diagrams:
            node = ET.fromstring(svg)
            self.assertEqual(node.get('role'), 'img')
            self.assertIsNotNone(node.get('viewBox'))
            titles = {el.get('id'): el for el in node if el.tag in ('title', 'desc')}
            labelled = node.get('aria-labelledby', '').split()
            self.assertEqual(len(labelled), 2)
            for label in labelled:
                self.assertIn(label, titles)
                self.assertNotIn(label, ids)
                self.assertTrue(''.join(titles[label].itertext()).strip())
                ids.add(label)

    def test_enrichment_comparison_uses_only_verified_endpoints(self):
        source = (ROOT / 'index.html').read_text()
        self.assertIn('class="enrichment-visual"', source, 'Show the verified before/after comparison')
        graphic = source.split('class="enrichment-visual"', 1)[1].split('</figure>', 1)[0]
        for phrase in ('2 min', '0.3 sec', 'per item', 'Before', 'After'):
            self.assertIn(phrase, graphic)
        self.assertNotIn('<polyline', graphic)
        self.assertIn('not a distribution', graphic)

    def test_larger_readable_type_and_compact_composition_are_explicit(self):
        css = (ROOT / 'static/css/style.css').read_text()
        for token in ('--body-size: 1.0625rem', '--label-size: .875rem',
                      '.hero-layout', '.hero-visual', '[data-case="audience"]',
                      '[data-case="risk"]', '.case-visual', '.enrichment-visual'):
            self.assertIn(token, css)
        self.assertIn('font-size: 1rem', css.split('nav a {', 1)[1].split('}', 1)[0])
        self.assertIn('font-size: 1rem', css.split('details {', 1)[1].split('}', 1)[0])


if __name__ == '__main__':
    unittest.main()
