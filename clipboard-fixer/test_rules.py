import unittest
import urllib.parse

from rules import (
    Rule,
    clean_url,
    get_default_rules,
    _strip_utm,
    _remove_amp,
    _x_to_vxtwitter,
    _tiktok_to_tnktok,
    _facebook_to_fixacebook,
    _unwrap_facebook,
    _unwrap_google,
    _force_https,
)
from main import is_tiktok_redirect_url


class TestStripUtm(unittest.TestCase):
    def test_removes_all_utm_params(self):
        url = "https://example.com?utm_source=twitter&utm_medium=social&utm_campaign=test"
        self.assertEqual(_strip_utm(url), "https://example.com")

    def test_preserves_non_utm_params(self):
        url = "https://example.com?foo=bar&utm_source=twitter"
        self.assertEqual(_strip_utm(url), "https://example.com?foo=bar")

    def test_no_utm_unchanged(self):
        url = "https://example.com?foo=bar"
        self.assertEqual(_strip_utm(url), url)


class TestRemoveAmp(unittest.TestCase):
    def test_removes_amp_path_suffix(self):
        self.assertEqual(_remove_amp("https://example.com/article/amp"), "https://example.com/article")

    def test_removes_amp_path_suffix_with_trailing_slash(self):
        self.assertEqual(_remove_amp("https://example.com/article/amp/"), "https://example.com/article")

    def test_removes_amp_query_param(self):
        self.assertEqual(_remove_amp("https://example.com/article?amp=1"), "https://example.com/article")

    def test_no_amp_unchanged(self):
        url = "https://example.com/article"
        self.assertEqual(_remove_amp(url), url)


class TestXToVxtwitter(unittest.TestCase):
    def test_replaces_x_com(self):
        self.assertEqual(
            _x_to_vxtwitter("https://x.com/user/status/123"),
            "https://vxtwitter.com/user/status/123",
        )

    def test_replaces_www_x_com(self):
        self.assertEqual(
            _x_to_vxtwitter("https://www.x.com/user/status/123"),
            "https://vxtwitter.com/user/status/123",
        )

    def test_preserves_query_string(self):
        self.assertEqual(
            _x_to_vxtwitter("https://x.com/user/status/123?s=20"),
            "https://vxtwitter.com/user/status/123?s=20",
        )

    def test_does_not_affect_box_com(self):
        url = "https://box.com/something"
        self.assertEqual(_x_to_vxtwitter(url), url)

    def test_does_not_affect_other_domains(self):
        url = "https://example.com/path"
        self.assertEqual(_x_to_vxtwitter(url), url)


class TestTiktokToTnktok(unittest.TestCase):
    def test_replaces_tiktok_com(self):
        self.assertEqual(
            _tiktok_to_tnktok("https://www.tiktok.com/@user/video/123"),
            "https://tnktok.com/@user/video/123",
        )

    def test_replaces_bare_tiktok_com(self):
        self.assertEqual(
            _tiktok_to_tnktok("https://tiktok.com/@user/video/123"),
            "https://tnktok.com/@user/video/123",
        )

    def test_preserves_query_string(self):
        self.assertEqual(
            _tiktok_to_tnktok("https://www.tiktok.com/@user/video/123?is_from_webapp=1"),
            "https://tnktok.com/@user/video/123?is_from_webapp=1",
        )

    def test_does_not_affect_other_domains(self):
        url = "https://example.com/path"
        self.assertEqual(_tiktok_to_tnktok(url), url)


class TestTikTokRedirectDetection(unittest.TestCase):
    def test_identifies_short_tiktok_hosts_and_paths(self):
        self.assertTrue(is_tiktok_redirect_url("https://vm.tiktok.com/ZM123abc/"))
        self.assertTrue(is_tiktok_redirect_url("https://www.tiktok.com/t/ZP8WSnC62/"))
        self.assertFalse(is_tiktok_redirect_url("https://www.tiktok.com/@user/video/123"))


class TestFacebookToFixacebook(unittest.TestCase):
    def test_replaces_facebook_com(self):
        self.assertEqual(
            _facebook_to_fixacebook("https://www.facebook.com/user/videos/123"),
            "https://fixacebook.com/user/videos/123",
        )

    def test_replaces_bare_facebook_com(self):
        self.assertEqual(
            _facebook_to_fixacebook("https://facebook.com/reel/123"),
            "https://fixacebook.com/reel/123",
        )

    def test_preserves_path_and_query(self):
        self.assertEqual(
            _facebook_to_fixacebook("https://www.facebook.com/watch?v=123456"),
            "https://fixacebook.com/watch?v=123456",
        )

    def test_does_not_affect_l_facebook_com(self):
        url = "https://l.facebook.com/l.php?u=https%3A%2F%2Fexample.com"
        self.assertEqual(_facebook_to_fixacebook(url), url)

    def test_does_not_affect_other_domains(self):
        url = "https://example.com/page"
        self.assertEqual(_facebook_to_fixacebook(url), url)


class TestUnwrapFacebook(unittest.TestCase):
    def test_unwraps_redirect(self):
        inner = "https://example.com/page?foo=bar"
        url = f"https://l.facebook.com/l.php?u={urllib.parse.quote(inner)}&h=abc123"
        self.assertEqual(_unwrap_facebook(url), inner)

    def test_non_facebook_unchanged(self):
        url = "https://example.com/page"
        self.assertEqual(_unwrap_facebook(url), url)

    def test_wrong_path_unchanged(self):
        url = "https://l.facebook.com/other?u=https%3A%2F%2Fexample.com"
        self.assertEqual(_unwrap_facebook(url), url)


class TestUnwrapGoogle(unittest.TestCase):
    def test_unwraps_redirect(self):
        inner = "https://example.com/page"
        url = f"https://www.google.com/url?q={urllib.parse.quote(inner)}&sa=D"
        self.assertEqual(_unwrap_google(url), inner)

    def test_non_google_unchanged(self):
        url = "https://example.com/page"
        self.assertEqual(_unwrap_google(url), url)

    def test_wrong_path_unchanged(self):
        url = "https://www.google.com/search?q=hello"
        self.assertEqual(_unwrap_google(url), url)


class TestForceHttps(unittest.TestCase):
    def test_upgrades_http(self):
        self.assertEqual(_force_https("http://example.com/path"), "https://example.com/path")

    def test_leaves_https_unchanged(self):
        url = "https://example.com/path"
        self.assertEqual(_force_https(url), url)


class TestCleanUrl(unittest.TestCase):
    def test_all_rules_applied_in_sequence(self):
        rules = get_default_rules({})
        url = "http://x.com/user/status/123?utm_source=twitter"
        self.assertEqual(clean_url(url, rules), "https://vxtwitter.com/user/status/123")

    def test_disabled_rule_is_skipped(self):
        rules = [Rule("force_https", False, _force_https)]
        url = "http://example.com"
        self.assertEqual(clean_url(url, rules), url)

    def test_empty_rules_list_unchanged(self):
        url = "https://example.com?utm_source=foo"
        self.assertEqual(clean_url(url, []), url)


if __name__ == "__main__":
    unittest.main()
