from pathlib import Path
from unittest.mock import patch

import pytest

from jabletv.missav_scraper import (
    MissavVideoInfo,
    _unpack_js_packed,
    _extract_m3u8_from_eval,
    _extract_full_title,
    _extract_code,
    _extract_actresses,
    _extract_thumbnail,
    _extract_video_id,
    is_missav_url,
    scrape_missav,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def missav_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "missav-abp-664.html").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# JS Packer decoder
# ---------------------------------------------------------------------------


class TestUnpackJsPacked:
    def test_decodes_simple_url(self) -> None:
        """The typical missav packed encoding of m3u8 URLs."""
        packed = (
            "f='8://7.6/5-4-3-2-1/e.0';"
            "d='8://7.6/5-4-3-2-1/c/9.0';"
            "b='8://7.6/5-4-3-2-1/a/9.0';"
        )
        words = [
            "m3u8", "9a0799511b2f", "b371", "4e35", "702b",
            "487fe7bf", "com", "surrit", "https", "video",
            "1280x720", "source1280", "842x480", "source842",
            "playlist", "source",
        ]
        decoded = _unpack_js_packed(packed, words)
        assert "source='https://surrit.com/487fe7bf-702b-4e35-b371-9a0799511b2f/playlist.m3u8'" in decoded
        assert "source842='https://surrit.com/487fe7bf-702b-4e35-b371-9a0799511b2f/842x480/video.m3u8'" in decoded
        assert "source1280='https://surrit.com/487fe7bf-702b-4e35-b371-9a0799511b2f/1280x720/video.m3u8'" in decoded

    def test_preserves_non_word_chars(self) -> None:
        packed = "0://1.2"
        words = ["m3u8", "site", "com"]
        decoded = _unpack_js_packed(packed, words)
        assert decoded == "m3u8://site.com"

    def test_returns_unknown_tokens_as_is(self) -> None:
        packed = "x://y.z"
        words = ["https"]
        decoded = _unpack_js_packed(packed, words)
        # 'x', 'y', 'z' are not in words (only index 0 'https' is)
        # 'x' has no base36 mapping, so stays as-is
        assert "://" in decoded


# ---------------------------------------------------------------------------
# m3u8 extraction from HTML
# ---------------------------------------------------------------------------


class TestExtractM3U8FromEval:
    def test_extracts_from_real_page(self, missav_html: str) -> None:
        result = _extract_m3u8_from_eval(missav_html)
        assert result.startswith("https://")
        assert ".m3u8" in result
        assert "playlist.m3u8" in result or "surrit.com" in result

    def test_returns_empty_for_no_eval(self) -> None:
        assert _extract_m3u8_from_eval("<html></html>") == ""

    def test_returns_empty_for_unbalanced_braces(self) -> None:
        html = "<script>eval(function(p,a,c,k,e,d){</script>"
        assert _extract_m3u8_from_eval(html) == ""


# ---------------------------------------------------------------------------
# Metadata extraction helpers
# ---------------------------------------------------------------------------


class TestExtractFullTitle:
    def test_from_h1(self, missav_html: str) -> None:
        title = _extract_full_title(missav_html)
        assert "ABP-664" in title
        assert len(title) > 10

    def test_fallback_to_og_title(self) -> None:
        html = '<meta property="og:title" content="TEST-001 A Title" />'
        assert _extract_full_title(html) == "TEST-001 A Title"

    def test_returns_empty(self) -> None:
        assert _extract_full_title("<html></html>") == ""


class TestExtractCode:
    def test_from_full_title(self) -> None:
        assert _extract_code("ABP-664 超高級巨乳風俗女") == "ABP-664"

    def test_returns_empty(self) -> None:
        assert _extract_code("No Code Here") == ""


class TestExtractActresses:
    def test_from_real_page(self, missav_html: str) -> None:
        result = _extract_actresses(missav_html)
        assert isinstance(result, list)
        assert len(result) >= 1
        assert "彩美旬果" in result

    def test_empty_html(self) -> None:
        assert _extract_actresses("<html></html>") == []


class TestExtractThumbnail:
    def test_from_real_page(self, missav_html: str) -> None:
        result = _extract_thumbnail(missav_html)
        assert result.startswith("https://")
        assert "cover" in result or ".jpg" in result

    def test_returns_empty(self) -> None:
        assert _extract_thumbnail("") == ""


class TestExtractVideoId:
    def test_from_dvd_id(self) -> None:
        html = 'dvd_id: "abp-664-uncensored-leak"'
        assert _extract_video_id(html) == "abp-664-uncensored-leak"

    def test_from_api_path(self) -> None:
        html = '/api/items/kruzfekb/save'
        assert _extract_video_id(html) == "kruzfekb"

    def test_returns_empty(self) -> None:
        assert _extract_video_id("") == ""


# ---------------------------------------------------------------------------
# URL detection
# ---------------------------------------------------------------------------


class TestIsMissavUrl:
    def test_missav_ws(self) -> None:
        assert is_missav_url("https://missav.ws/dm26/abp-664-uncensored-leak") is True

    def test_missav_com(self) -> None:
        assert is_missav_url("https://missav.com/dm26/test-video") is True

    def test_msav_ws(self) -> None:
        assert is_missav_url("https://msav.ws/something") is True

    def test_jable_tv(self) -> None:
        assert is_missav_url("https://jable.tv/videos/test/") is False

    def test_other_domain(self) -> None:
        assert is_missav_url("https://example.com/video") is False

    def test_empty(self) -> None:
        assert is_missav_url("") is False


# ---------------------------------------------------------------------------
# Full scrape (mocked)
# ---------------------------------------------------------------------------


class TestScrapeMissav:
    def test_scrape_with_mocked_fetch(self, missav_html: str) -> None:
        with patch("jabletv.missav_scraper._fetch_page", return_value=missav_html):
            info = scrape_missav("https://missav.ws/dm26/abp-664-uncensored-leak")

        assert info.code == "ABP-664"
        assert len(info.title) > 5
        assert len(info.full_title) > 10
        assert info.m3u8_url.startswith("https://")
        assert ".m3u8" in info.m3u8_url
        assert info.thumbnail.startswith("https://")
        assert len(info.actresses) >= 1

    def test_scrape_returns_filename(self, missav_html: str) -> None:
        with patch("jabletv.missav_scraper._fetch_page", return_value=missav_html):
            info = scrape_missav("https://missav.ws/dm26/abp-664-uncensored-leak")

        assert info.output_filename.endswith(".mp4")
        assert info.code in info.output_filename
        assert "彩美旬果" in info.output_filename

    def test_scrape_missing_m3u8(self) -> None:
        html = """<html><head><meta property="og:title" content="ABC-123 Test"/></head>
        <body><h1>ABC-123 Test</h1></body></html>"""
        with patch("jabletv.missav_scraper._fetch_page", return_value=html):
            info = scrape_missav("https://missav.ws/dm26/abc-123-test")

        assert info.code == "ABC-123"
        assert info.m3u8_url == ""

    def test_scrape_httpx_fallback(self) -> None:
        """Simulates a simple page that would work after fetch."""
        html_with_eval = """<html><head><meta property="og:title" content="TEST-001 Eval"/></head>
        <body><h1>TEST-001 Title</h1>
        <script>eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\\\b'+e(c)+'\\\\b','g'),k[c])}}return p}('f=\\'0://1.2/3-4-5-6-7/e.8\\'',16,16,'m3u8|https|com|cdn|example|path|to|video|playlist'.split('|'),0,{}))</script>
        </body></html>"""
        with patch("jabletv.missav_scraper._fetch_page", return_value=html_with_eval):
            info = scrape_missav("https://missav.ws/dm26/test-001-eval")

        assert info.code == "TEST-001"
        # The mock eval should produce a URL (the words are different so it won't be valid)

    def test_scrape_raises_on_fetch_error(self) -> None:
        def mock_error(url: str) -> str:
            raise RuntimeError("Network error")

        with patch("jabletv.missav_scraper._fetch_page", side_effect=mock_error):
            with pytest.raises(RuntimeError, match="Network error"):
                scrape_missav("https://missav.ws/dm26/error-test")


class TestMissavVideoInfo:
    def test_output_filename_with_code_only(self) -> None:
        v = MissavVideoInfo(code="ABC-123", title="Test")
        assert ".mp4" in v.output_filename
        assert "ABC-123" in v.output_filename

    def test_output_filename_with_actresses(self) -> None:
        v = MissavVideoInfo(code="ABC-123", actresses=["女優名"])
        assert "女優名" in v.output_filename

    def test_default_values(self) -> None:
        v = MissavVideoInfo()
        assert v.code == ""
        assert v.actresses == []
        assert v.m3u8_url == ""
