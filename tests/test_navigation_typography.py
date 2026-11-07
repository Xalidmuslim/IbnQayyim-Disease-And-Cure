"""Regression contracts for Android Back gesture and compact chapter headings."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACT = ROOT / 'app/src/main/java/com/xalidmuslim/diseaseandcure/MainActivity.kt'
MAN = ROOT / 'app/src/main/AndroidManifest.xml'
HTML = ROOT / 'app/src/main/assets/index.html'
CSS = ROOT / 'app/src/main/assets/compact_sections.css'

class NavigationTypographyRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.android = ACT.read_text(encoding='utf-8')
        cls.manifest = MAN.read_text(encoding='utf-8')
        cls.html = HTML.read_text(encoding='utf-8')

    def test_android_13_plus_gesture_is_registered_and_unregistered(self):
        self.assertIn('OnBackInvokedCallback', self.android)
        self.assertIn('registerOnBackInvokedCallback', self.android)
        self.assertIn('unregisterOnBackInvokedCallback', self.android)
        self.assertIn('VERSION_CODES.TIRAMISU', self.android)
        self.assertIn('android:enableOnBackInvokedCallback="true"', self.manifest)

    def test_both_system_back_paths_call_the_same_reader_navigation(self):
        self.assertIn('override fun onBackPressed()', self.android)
        self.assertIn('private fun navigateBackInReader()', self.android)
        self.assertIn('window.__androidBack', self.android)
        self.assertGreaterEqual(self.android.count('navigateBackInReader()'), 3)
        self.assertIn('window.__androidBack=back', self.html)

    def test_reading_defaults_are_17_px_and_140_percent(self):
        self.assertIn("size:get('size',17),space:get('space',1.40)", self.html)
        self.assertIn("document.documentElement.style.setProperty('--lh',settings.space)", self.html)

    def test_compact_font_is_scoped_to_chapter_card_titles(self):
        css = CSS.read_text(encoding='utf-8')
        self.assertIn('font-family: Roboto, "Arial", sans-serif', css)
        self.assertNotIn('font-family: "Reader Navigation"',css)
        self.assertIn('font-weight: 500',css)
        self.assertNotIn('font-weight: 600',css)
        self.assertIn('#root .item .itemtitle', css)
        self.assertIn('font-size: 13.5px', css)
        self.assertIn('line-height: 1.22', css)
        self.assertNotIn('.reader h2', css)
        self.assertNotIn('.booktext', css)
        self.assertIn('onPageFinished', self.android)
        self.assertIn('compact_sections.css', self.android)

    def test_v48_install_cannot_overwrite_previous_install(self):
        gradle = (ROOT/'app/build.gradle.kts').read_text(encoding='utf-8')
        self.assertIn('versionCode = 48', gradle)
        self.assertIn('applicationIdSuffix = ".preview48"', gradle)

if __name__ == '__main__': unittest.main()
