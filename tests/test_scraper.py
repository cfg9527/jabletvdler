from unittest.mock import patch

import pytest

from jabletv.scraper import (
    VideoInfo,
    _extract_m3u8,
    _extract_video_id,
    _extract_thumbnail,
    _extract_actresses,
    _extract_tags,
    _extract_category,
    _extract_release_date,
    _extract_views,
    scrape,
)


class TestExtractM3U8:
    def test_extracts_from_hlsurl_var_single_quotes(self) -> None:
        html = "var hlsUrl = 'https://cdn.example.com/60476.m3u8';"
        assert _extract_m3u8(html) == "https://cdn.example.com/60476.m3u8"

    def test_extracts_from_hlsurl_var_double_quotes(self) -> None:
        html = 'var hlsUrl = "https://cdn.example.com/60476.m3u8";'
        assert _extract_m3u8(html) == "https://cdn.example.com/60476.m3u8"

    def test_extracts_bare_m3u8_url(self) -> None:
        html = '<script>src="something" https://cdn.example.com/video.m3u8?token=abc other</script>'
        assert "https://cdn.example.com/video.m3u8?token=abc" in _extract_m3u8(html)

    def test_returns_empty_for_no_match(self) -> None:
        assert _extract_m3u8("<html><body>no video</body></html>") == ""

    def test_handles_escaped_url(self) -> None:
        html = r"var hlsUrl = 'https:\/\/cdn.example.com\/video.m3u8';"
        result = _extract_m3u8(html)
        assert "https://cdn.example.com/video.m3u8" in result

    def test_extracts_from_real_page(self, roe505_html: str) -> None:
        result = _extract_m3u8(roe505_html)
        assert "m3u8" in result
        assert result.startswith("https://")


class TestExtractVideoId:
    def test_extracts_video_id(self) -> None:
        html = "videoId: '60476',"
        assert _extract_video_id(html) == "60476"

    def test_returns_empty(self) -> None:
        assert _extract_video_id("") == ""

    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_video_id(roe505_html)
        assert result.isdigit()
        assert len(result) >= 4


class TestExtractThumbnail:
    def test_extracts_poster(self) -> None:
        html = '<video poster="https://cdn.example.com/preview.jpg" id="player">'
        assert _extract_thumbnail(html) == "https://cdn.example.com/preview.jpg"

    def test_returns_empty(self) -> None:
        assert _extract_thumbnail("") == ""

    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_thumbnail(roe505_html)
        assert result.startswith("https://")
        assert ".jpg" in result or ".png" in result


class TestExtractActresses:
    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_actresses(roe505_html)
        assert isinstance(result, list)
        assert len(result) >= 1
        assert "吉永塔子" in result

    def test_empty_html(self) -> None:
        assert _extract_actresses("") == []


class TestExtractTags:
    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_tags(roe505_html)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_empty_html(self) -> None:
        assert _extract_tags("") == []


class TestExtractCategory:
    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_category(roe505_html)
        assert isinstance(result, str)

    def test_empty_html(self) -> None:
        assert _extract_category("") == ""


class TestExtractReleaseDate:
    def test_extracts_date(self) -> None:
        html = "上市於 2026-07-06"
        assert _extract_release_date(html) == "2026-07-06"

    def test_returns_empty(self) -> None:
        assert _extract_release_date("") == ""

    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_release_date(roe505_html)
        assert isinstance(result, str)


class TestExtractViews:
    def test_extracts_with_space(self) -> None:
        html = '<span class="mr-3"> 42 554 </span>'
        assert _extract_views(html) == 42554

    def test_extracts_with_comma(self) -> None:
        html = '<span class="mr-3"> 1,234,567 </span>'
        assert _extract_views(html) == 1234567

    def test_returns_zero(self) -> None:
        assert _extract_views("") == 0

    def test_from_real_page(self, roe505_html: str) -> None:
        result = _extract_views(roe505_html)
        assert result > 0


class TestFetchPage:
    def test_curl_cffi_preferred(self) -> None:
        from jabletv import scraper as scraper_mod

        mock_html = "<html>mocked</html>"

        with patch.object(scraper_mod, "_fetch_page", return_value=mock_html):
            result = scraper_mod._fetch_page("https://jable.tv/videos/test/")
            assert result == mock_html

    def test_rotates_profiles_when_one_403s(self) -> None:
        """If a curl_cffi profile is flagged, later profiles must still
        get a chance before the httpx fallback."""
        from jabletv import scraper as scraper_mod

        calls: list[str] = []

        def cffi_get(url, headers=None, impersonate=None, **kwargs):
            calls.append(impersonate)
            if impersonate == "chrome120":
                raise Exception("HTTP Error 403: ")

            class FakeResp:
                text = "<html>rotated</html>"

                def raise_for_status(self):
                    pass

            return FakeResp()

        with patch("curl_cffi.requests.get", side_effect=cffi_get):
            result = scraper_mod._fetch_page("https://jable.tv/videos/test/")

        assert result == "<html>rotated</html>"
        assert calls[0] == "chrome120"
        assert len(calls) > 1

    def test_falls_back_to_httpx_when_curl_cffi_403(self) -> None:
        """jable.tv intermittently 403s curl_cffi's TLS fingerprint while
        serving the same URL to plain httpx; the fallback must kick in."""
        from jabletv import scraper as scraper_mod

        def cffi_403(url: str, headers=None, **kwargs):
            raise Exception("HTTP Error 403: ")

        class FakeResp:
            def __init__(self, text: str):
                self.text = text

            def raise_for_status(self) -> None:
                pass

        with patch("curl_cffi.requests.get", side_effect=cffi_403):
            with patch.object(
                scraper_mod.httpx, "get", return_value=FakeResp("<html>fallback</html>")
            ) as mock_get:
                result = scraper_mod._fetch_page("https://jable.tv/videos/test/")

        assert result == "<html>fallback</html>"
        mock_get.assert_called_once()

    def test_propagates_when_httpx_also_403(self) -> None:
        import httpx as httpx_mod

        from jabletv import scraper as scraper_mod

        def cffi_403(url: str, headers=None, **kwargs):
            raise Exception("HTTP Error 403: ")

        def httpx_403(url, headers=None, **kwargs):
            resp = httpx_mod.Response(
                403, request=httpx_mod.Request("GET", url)
            )
            resp.raise_for_status()
            return resp

        with patch("curl_cffi.requests.get", side_effect=cffi_403):
            with patch.object(scraper_mod.httpx, "get", side_effect=httpx_403):
                with pytest.raises(httpx_mod.HTTPStatusError):
                    scraper_mod._fetch_page("https://jable.tv/videos/test/")



class TestScrapeRealPage:
    def test_scrape_with_mocked_fetch(self, roe505_html: str) -> None:
        with patch("jabletv.scraper._fetch_page", return_value=roe505_html):
            video = scrape("https://jable.tv/videos/roe-505/")

        assert video.code == "ROE-505"
        assert len(video.title) > 5
        assert len(video.full_title) > 10
        assert video.m3u8_url.startswith("https://")
        assert ".m3u8" in video.m3u8_url
        assert video.video_id.isdigit()
        assert video.views > 0
        assert len(video.tags) > 0
        assert len(video.thumbnail) > 0

    def test_scrape_missing_m3u8(self) -> None:
        html = "<html><head></head><body><h4>ABC-123 No Video</h4></body></html>"
        with patch("jabletv.scraper._fetch_page", return_value=html):
            video = scrape("https://jable.tv/videos/abc-123/")

        assert video.code == "ABC-123"
        assert video.m3u8_url == ""

    def test_scrape_httpx_fallback_on_import_error(self) -> None:
        html = """<html><head></head><body><h4>TEST-001 Test Video</h4>
        <script>var hlsUrl = 'https://cdn.example.com/video.m3u8';</script>
        <span class="mr-3"> 1 234 </span></body></html>"""

        with patch("jabletv.scraper._fetch_page", return_value=html):
            video = scrape("https://jable.tv/videos/test-001/")

        assert video.code == "TEST-001"
        assert video.m3u8_url == "https://cdn.example.com/video.m3u8"
        assert video.views == 1234


class TestScrape403Handling:
    def test_403_raises_in_scrape(self) -> None:
        import httpx

        def mock_403(url: str) -> str:
            raise httpx.HTTPStatusError(
                "403 Forbidden",
                request=httpx.Request("GET", url),
                response=httpx.Response(403),
            )

        with patch("jabletv.scraper._fetch_page", side_effect=mock_403):
            with pytest.raises(httpx.HTTPStatusError):
                scrape("https://jable.tv/videos/blocked/")

    def test_403_then_curl_cffi_succeeds(self) -> None:
        """Verify _fetch_page uses curl_cffi (tested by mock)."""
        html = "<html><body><h4>OK Video</h4></body></html>"
        with patch("jabletv.scraper._fetch_page", return_value=html):
            video = scrape("https://jable.tv/videos/test/")
        assert video.code == "OK"


class TestVideoInfo:
    def test_output_filename_with_code_only(self) -> None:
        v = VideoInfo(code="ROE-505", title="Test")
        assert ".mp4" in v.output_filename
        assert "ROE-505" in v.output_filename

    def test_output_filename_with_actresses(self) -> None:
        v = VideoInfo(code="ROE-505", actresses=["吉永塔子"])
        assert "吉永塔子" in v.output_filename

    def test_output_filename_with_multiple_actresses(self) -> None:
        v = VideoInfo(code="ABC-123", actresses=["A", "B"])
        assert "ABC-123" in v.output_filename

    def test_default_values(self) -> None:
        v = VideoInfo()
        assert v.code == ""
        assert v.actresses == []
        assert v.tags == []
        assert v.m3u8_url == ""
        assert v.views == 0

    def test_full_title_parsing_from_real_page(self, roe505_html: str) -> None:
        with patch("jabletv.scraper._fetch_page", return_value=roe505_html):
            video = scrape("https://jable.tv/videos/roe-505/")
        assert video.full_title.startswith("ROE-505")
        assert len(video.full_title) > 20
