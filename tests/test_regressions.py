"""Regression checks for verified portfolio publication defects."""
from pathlib import Path
import re
import unittest
from test_site import ROOT


class PublicationRegressions(unittest.TestCase):
    def test_hidden_heading_breaks_preserve_word_boundaries(self):
        source = (ROOT / 'index.html').read_text()
        headings = re.findall(r'<h2\b[^>]*>(.*?)</h2>', source, re.S)
        for heading in headings:
            self.assertNotRegex(heading, r'\S<br\s*/?>\S', heading)
        for phrase in ('The systems around the science.', 'Methods meet production.',
                       'Making the work understandable.'):
            self.assertIn(phrase, re.sub(r'<[^>]+>', '', source))

    def test_timeline_assigns_achievements_to_grounded_roles(self):
        source = (ROOT / 'index.html').read_text()
        roles = re.findall(r'<li><p class="date">(.*?)</p><h3>(.*?)</h3><p>(.*?)</p></li>', source)
        self.assertIn(('Apr 2023–Oct 2025', 'Applied Scientist II',
                       'Built catalog enrichment, model monitoring, and segment-tailored recovery and checkout treatments.'), roles)
        self.assertIn(('Jun 2021–Mar 2023', 'Applied Scientist I',
                       'Built RTO risk models, real-time explanations, and customer segmentation foundations.'), roles)


    def test_link_audit_rejects_missing_social_and_canonical_targets(self):
        import shutil
        import tempfile
        from unittest.mock import patch
        import test_site
        for old, new in (
            ('https://jain-aayush.github.io/"', 'https://jain-aayush.github.io/missing.html"'),
            ('/static/images/social.png', '/static/images/missing.png'),
        ):
            with self.subTest(reference=new), tempfile.TemporaryDirectory() as directory:
                copy = Path(directory) / 'site'
                shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__'))
                page = copy / 'index.html'
                page.write_text(page.read_text().replace(old, new))
                with patch.object(test_site, 'ROOT', copy), self.assertRaises(AssertionError):
                    test_site.SiteTests().test_local_links_assets_and_heading_hierarchy()


    def test_readme_explains_automatic_master_publication_and_approval(self):
        readme = (ROOT / 'README.md').read_text()
        for phrase in ('Merging `master` automatically publishes',
                       'PR branch does not deploy', 'owner approval before merging',
                       'social.png', '1200×630', 'social.svg'):
            self.assertIn(phrase, readme)
        self.assertNotIn('deployment authorization are separate', readme)


    def test_print_toolkit_is_explicitly_kept_together_not_experience(self):
        from test_site import Document
        sections = Document(ROOT / 'resume.html').attrs('section')
        toolkit = next(a for a in sections if a.get('aria-labelledby') == 'resume-toolkit')
        experience = next(a for a in sections if a.get('aria-labelledby') == 'resume-experience')
        self.assertIn('print-keep-together', toolkit.get('class', '').split())
        self.assertNotIn('print-keep-together', experience.get('class', '').split())
        print_css = (ROOT / 'static/css/style.css').read_text().split('@media print {', 1)[1]
        self.assertIn('.resume .print-keep-together { break-inside: avoid; }', print_css)
        self.assertIn('font-size: 9pt', print_css)


if __name__ == '__main__':
    unittest.main()
