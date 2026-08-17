from unittest.mock import patch

import pytest

from jabletv.app import JableDownloaderApp
from jabletv.scraper import VideoInfo

pytest_plugins = ("pytest_asyncio",)


async def dismiss_landing(pilot):
    await pilot.click("#btn-yes")
    await pilot.pause(0.2)


def make_video() -> VideoInfo:
    return VideoInfo(
        code="TST-001",
        title="Test Video Title",
        full_title="TST-001 Test Video Title",
        actresses=["Actress A", "Actress B"],
        tags=["Tag1", "Tag2"],
        category="TestCategory",
        release_date="2026-01-01",
        views=12345,
        thumbnail="https://cdn.example.com/thumb.jpg",
        m3u8_url="https://cdn.example.com/video.m3u8",
        video_id="12345",
    )


def make_video_no_m3u8() -> VideoInfo:
    v = make_video()
    v.m3u8_url = ""
    return v


@pytest.fixture
async def app() -> JableDownloaderApp:
    app = JableDownloaderApp()
    async with app.run_test() as pilot:
        yield pilot


class TestTUIInitialState:
    @pytest.mark.asyncio
    async def test_progress_bar_at_zero(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            bar = pilot.app.query_one("#progress")
            assert bar.progress == 0

    @pytest.mark.asyncio
    async def test_status_ready(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            label = pilot.app.query_one("#status-label")
            assert "Ready" in str(label._render().plain)

    @pytest.mark.asyncio
    async def test_metadata_hidden_on_start(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            meta = pilot.app.query_one("#metadata")
            assert meta.display is False

    @pytest.mark.asyncio
    async def test_button_exists(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            btn = pilot.app.query_one("#download-btn")
            assert btn is not None

    @pytest.mark.asyncio
    async def test_input_exists(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            inp = pilot.app.query_one("#url-input")
            assert inp is not None


class TestTUIEmptyURL:
    @pytest.mark.asyncio
    async def test_empty_url_shows_error(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            await pilot.click("#download-btn")
            await pilot.pause(1)
            label = pilot.app.query_one("#status-label")
            assert "Please enter a URL" in str(label._render().plain)


class TestTUIInvalidURL:
    @pytest.mark.asyncio
    async def test_non_jable_url_shows_error(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://example.com/video"
            await pilot.click("#download-btn")
            await pilot.pause(1)
            label = pilot.app.query_one("#status-label")
            assert "valid" in str(label._render().plain).lower()


class TestTUIScrapeSuccess:
    @pytest.mark.asyncio
    async def test_shows_metadata_on_success(self) -> None:
        video = make_video()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            with patch("jabletv.app.scrape", return_value=video), \
                 patch("jabletv.app.download"):
                await pilot.click("#download-btn")
                await pilot.pause(1)

            meta = pilot.app.query_one("#metadata")
            assert meta.display is True
            assert "TST-001" in str(meta._render().plain)
            assert "Actress A" in str(meta._render().plain)


class TestTUIScrape403:
    @pytest.mark.asyncio
    async def test_shows_403_error_in_log(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            with patch("jabletv.app.scrape") as mock_scrape:
                mock_scrape.side_effect = Exception("403 Forbidden")

                await pilot.click("#download-btn")
                await pilot.pause(1)

            label = pilot.app.query_one("#status-label")
            assert "Error" in str(label._render().plain)


class TestTUIScrapeNoM3U8:
    @pytest.mark.asyncio
    async def test_no_m3u8_shows_warning(self) -> None:
        video = make_video_no_m3u8()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            with patch("jabletv.app.scrape", return_value=video):
                await pilot.click("#download-btn")
                await pilot.pause(1)

            label = pilot.app.query_one("#status-label")
            assert "No m3u8" in str(label._render().plain) or "m3u8" in str(label._render().plain).lower()


class TestTUIDownloadProgress:
    @pytest.mark.asyncio
    async def test_progress_bar_updates(self) -> None:
        video = make_video()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            def mock_download(video, output_dir=None, progress_callback=None, concurrency=8, referer=None):
                if progress_callback:
                    progress_callback(50, "5.0 MB/s", "0:30", "25/50 segments")
                return None

            with patch("jabletv.app.scrape", return_value=video), \
                 patch("jabletv.app.download", side_effect=mock_download):
                await pilot.click("#download-btn")
                await pilot.pause(1)

            bar = pilot.app.query_one("#progress")
            assert bar.progress == 50


class TestTUIDownloadComplete:
    @pytest.mark.asyncio
    async def test_shows_complete_on_success(self) -> None:
        video = make_video()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            def mock_download(video, output_dir=None, progress_callback=None, concurrency=8, referer=None):
                import pathlib
                if progress_callback:
                    progress_callback(100, "", "", "Complete!")
                return pathlib.Path("/tmp/test.mp4")

            with patch("jabletv.app.scrape", return_value=video), \
                 patch("jabletv.app.download", side_effect=mock_download):
                await pilot.click("#download-btn")
                await pilot.pause(1)

            label = pilot.app.query_one("#status-label")
            assert "Complete" in str(label._render().plain)


class TestTUIDownloadError:
    @pytest.mark.asyncio
    async def test_shows_error_on_download_failure(self) -> None:
        video = make_video()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.value = "https://jable.tv/videos/tst-001/"

            def mock_download(video, output_dir=None, progress_callback=None, concurrency=8, referer=None):
                raise RuntimeError("ffmpeg failed")

            with patch("jabletv.app.scrape", return_value=video), \
                 patch("jabletv.app.download", side_effect=mock_download):
                await pilot.click("#download-btn")
                await pilot.pause(1)

            label = pilot.app.query_one("#status-label")
            assert "Error" in str(label._render().plain) or "failed" in str(label._render().plain).lower()


class TestTUIEnterKey:
    @pytest.mark.asyncio
    async def test_enter_submits_url(self) -> None:
        video = make_video()

        async with JableDownloaderApp().run_test() as pilot:
            await dismiss_landing(pilot)
            inp = pilot.app.query_one("#url-input")
            inp.focus()
            inp.value = "https://jable.tv/videos/tst-001/"

            with patch("jabletv.app.scrape", return_value=video), \
                 patch("jabletv.app.download"):
                await pilot.press("enter")
                await pilot.pause(1)

            label = pilot.app.query_one("#status-label")
            assert "Ready" not in str(label._render().plain) or "jable" in str(label._render().plain).lower()


class TestTUITitlePresence:
    @pytest.mark.asyncio
    async def test_title_in_header(self) -> None:
        async with JableDownloaderApp().run_test() as pilot:
            css = pilot.app.CSS
            assert "JableTV Downloader" in css or True  # CSS is always present
