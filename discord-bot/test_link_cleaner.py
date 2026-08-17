import unittest
import urllib.parse

from link_cleaner import find_cleaned_links, is_tiktok_redirect_url
from rules import get_default_rules


class TestFindCleanedLinks(unittest.TestCase):
    def setUp(self):
        self.rules = get_default_rules({})

    def test_finds_dirty_url_in_message(self):
        links = find_cleaned_links("look at https://x.com/user/status/123?utm_source=discord", self.rules)
        self.assertEqual(
            links,
            [("https://x.com/user/status/123?utm_source=discord", "https://vxtwitter.com/user/status/123")],
        )

    def test_preserves_trailing_sentence_punctuation(self):
        links = find_cleaned_links("read http://example.com/path?utm_source=test.", self.rules)
        self.assertEqual(links, [("http://example.com/path?utm_source=test.", "https://example.com/path.")])

    def test_returns_multiple_cleaned_links(self):
        links = find_cleaned_links(
            "one https://www.tiktok.com/@user/video/123 and two http://example.com",
            self.rules,
        )
        self.assertEqual(
            links,
            [
                ("https://www.tiktok.com/@user/video/123", "https://tnktok.com/@user/video/123"),
                ("http://example.com", "https://example.com"),
            ],
        )

    def test_identifies_tiktok_redirect_urls(self):
        self.assertTrue(is_tiktok_redirect_url("https://vm.tiktok.com/ZM123abc/"))
        self.assertTrue(is_tiktok_redirect_url("https://www.tiktok.com/t/ZP8WSnC62/"))
        self.assertFalse(is_tiktok_redirect_url("https://www.tiktok.com/@user/video/123"))

    def test_ignores_clean_links(self):
        links = find_cleaned_links("already clean https://example.com/path", self.rules)
        self.assertEqual(links, [])

    def test_unwraps_facebook_redirect(self):
        inner = "https://example.com/page?foo=bar"
        url = f"https://l.facebook.com/l.php?u={urllib.parse.quote(inner)}&h=abc123"
        links = find_cleaned_links(url, self.rules)
        self.assertEqual(links, [(url, inner)])


if __name__ == "__main__":
    unittest.main()
