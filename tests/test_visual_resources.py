"""Regression checks for original design resources and Android WebView scaling."""
from pathlib import Path
import hashlib
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'
MAIN = ROOT / 'app/src/main/java/com/xalidmuslim/diseaseandcure/MainActivity.kt'

# Git blob SHA-1 of each asset from the original v1.19 APK. Do not replace by similarly-named assets.
ORIGINAL_BLOBS = {
    'app_icon.png':'c069c8b8745d95fc015271fb2484df054336c1f2',
    'app_icon.webp':'2c91f1d616a74a9dca61cf0d0c3d969515c02a1e',
    'app_paper_tile.webp':'5d84820198414b0ef8b30e0e0ed076f826f2aebf',
    'bg_antique.png':'23a456977c0d70a50d453e363118edf84fce9407',
    'bg_antique_edge_v11.webp':'bb7ac432033671288f600cb116b22eda516a0ce6',
    'bg_paper.png':'83fedf807f754746c4a2f5b3af576ece94632860',
    'bg_soft_antique.webp':'d64b7acb6b87eda4b859d84f170e289f2b5c2f14',
    'bg_soft_antique_v119.webp':'0675ac04f7a074b454a92612f70b1806c2f70f77',
    'bg_soft_edge_v10.webp':'d9ea28222c3aa0cd26457f2046751d46efb28f74',
    'bg_soft_edge_v7.webp':'fc2208d278b051b7b3225342445e7b7912212928',
    'bg_soft_edge_v8.webp':'8f2fde713ced932d18df8421c88fcd99981005e8',
    'font-andika-script-v15.ttf':'2908870924ab456b7e54d27c89465ed4d14826b5',
    'font-citation-license-v15.txt':'c8193bd5d82107a1adebe52176b4ef26e9e6e7f2',
    'font-heritage-cyrillic-v13.woff2':'ef2ae371c331aae9eece0d31b9728206a250288c',
    'font-license.txt':'5303054dc8fe29cde1b9b39d23b8a76b48807faf',
    'font-navigation-license.txt':'bafe4a2cfc075f9b2b178eea4a78ff32a7ed66f1',
    'font-navigation.woff2':'fe83210f26e9f13e9f8467346c795695a66bca24',
    'font-noto-serif-v15.ttf':'6bcc4335531ff08e4f979ac63bb783180d5ade15',
    'font-writing.woff2':'786a1f6a2a097e1d11d2e515d19548aec4536dc1',
    'home_books_premium.webp':'dcf4dbba4fecbfc08298aa98aa60696085790a5b',
    'paper_frame_reference.webp':'0a1f242360d722fd3008eb085619e76ce4ecaf2b',
    'quote_green_books.webp':'2714bf88e07a55c5d5bb4fbbf7b08cf3cae316f1',
    'user_parchment.webp':'9cee3010163b3ae099558655f1873efb118d7600',
}

class VisualResourceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ASSETS / 'index.html').read_text(encoding='utf-8')

    def test_original_resources_sha(self):
        for name, expected in ORIGINAL_BLOBS.items():
            with self.subTest(resource=name):
                data=(ASSETS / name).read_bytes()
                git_sha=hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
                self.assertEqual(expected, git_sha, name)

    def test_every_css_local_resource_is_bundled(self):
        urls=re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',self.html)
        missing=sorted({u for u in urls if not (u.startswith(('data:','http:','https:','#')) or (ASSETS / u).is_file())})
        self.assertEqual([],missing)

    def test_system_font_scale_does_not_change_css_px(self):
        source=MAIN.read_text(encoding='utf-8')
        self.assertIn('settings.textZoom = 100',source)
        self.assertIn('settings.useWideViewPort = true',source)
        self.assertIn('settings.loadWithOverviewMode = false',source)

    def test_debug_install_is_side_by_side(self):
        gradle=(ROOT / "app/build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn('applicationIdSuffix = ".preview47"', gradle)
        label=(ROOT / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
        self.assertIn('android:label="Болезнь и исцеление v47"', label)

    def test_launcher_icon_is_original(self):
        manifest=(ROOT / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")
        self.assertIn('android:icon="@mipmap/ic_launcher"', manifest)
        self.assertEqual((ASSETS / "app_icon.png").read_bytes(),(ROOT / "app/src/main/res/mipmap-xxxhdpi/ic_launcher.png").read_bytes())

    def test_all_book_content_unchanged(self):
        html=(ASSETS / 'index.html').read_bytes()
        self.assertEqual('4ed99bfcbd061b8f9490e485af23560e17ceba20494eac2055bc13bf364b2ded',hashlib.sha256(html).hexdigest())

if __name__ == '__main__':unittest.main()