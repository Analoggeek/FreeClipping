"""OS-style desktop shell + day/night mode. Static checks — no server required."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class UiTheme(unittest.TestCase):
    def test_app_html_has_theme_bootstrap_and_controls(self):
        html = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('data-theme="night"', html.split('<body>')[0])
        self.assertIn("localStorage.getItem('freeclipping-theme')", html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn('id="clock"', html)
        self.assertIn('prefers-color-scheme', html)

    def test_app_html_has_os_shell(self):
        html = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('<header class="topbar">', html)
        self.assertIn('<nav class="dock"', html)
        self.assertIn('<main>', html)
        # the view buttons still exist (the e2e/static nav contract is data-view)
        self.assertEqual(html.count('data-view='), 2)
        self.assertIn('<span class="tb-clock" id="clock"', html)

    def test_app_html_keeps_the_library_badge_id(self):
        html = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('id="library-count"', html)

    def test_style_css_has_day_theme_and_shell_rules(self):
        css = (ROOT / 'style.css').read_text(encoding='utf-8')
        self.assertIn('html[data-theme="day"]', css)
        self.assertIn('.topbar', css)
        self.assertIn('.dock', css)
        self.assertIn('.tb-theme', css)
        self.assertIn('--scroll', css)
        # balanced braces
        self.assertEqual(css.count('{'), css.count('}'))

    def test_mobile_remote_has_theme_toggle(self):
        html = (ROOT / 'mobile.html').read_text(encoding='utf-8')
        self.assertIn('data-theme="night"', html)
        self.assertIn('id="theme-toggle"', html)
        self.assertIn("localStorage.getItem('freeclipping-theme')", html)

    def test_no_unclosed_script_tags(self):
        html = (ROOT / 'app' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('<script'), html.count('</script>'))


if __name__ == '__main__':
    unittest.main()
