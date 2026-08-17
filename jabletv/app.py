from __future__ import annotations

import os
import time

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    RichLog,
    Sparkline,
    Static,
)

from .downloader import download
from .landing import LandingScreen
from .dashboard import DashboardScreen
from .library import LibraryScreen
from .logger import get_logger, setup_logging
from .metadata_store import save_metadata
from .scraper import scrape, VideoInfo
from .missav_scraper import scrape_missav, is_missav_url, MissavVideoInfo
from .themes import PinkyTheme

logger = get_logger(__name__)


class MetadataDisplay(Static):
    def show_info(self, video: VideoInfo) -> None:
        lines = [
            f"[bold]{video.full_title}[/bold]",
            f"Code: [bold cyan]{video.code}[/bold cyan]",
            f"Actresses: [bold yellow]{', '.join(video.actresses) or 'N/A'}[/bold yellow]",
            f"Views: {video.views:,}  |  Date: {video.release_date or 'N/A'}",
            f"Category: {video.category or 'N/A'}",
            f"Tags: [italic]{', '.join(video.tags[:10])}[/italic]" + ("..." if len(video.tags) > 10 else ""),
        ]
        self.update("\n".join(lines))


class JableDownloaderApp(App):
    CSS = PinkyTheme.CSS
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("l", "open_library", "Library"),
        ("d", "open_dashboard", "Dashboard"),
    ]

    def __init__(self):
        super().__init__()
        self._download_start: float | None = None
        self._output_dir: str = ""
        self._breathing_pink = False
        self._speed_history: list[float] = []
        self._last_url: str = ""

    def compose(self) -> ComposeResult:
        with Container(id="window-wrapper"):
            yield Header(show_clock=True)
            with Center():
                with Container(id="main-container"):
                    yield Input(
                        placeholder="Paste video URL (jable.tv or missav.ws)",
                        id="url-input",
                    )
                    with Horizontal(id="action-buttons"):
                        yield Button("Download", id="download-btn", variant="primary")
                        yield Button("Library", id="library-btn")
                        yield Button("Dashboard", id="dashboard-btn")
                    yield ProgressBar(id="progress", total=100, show_eta=False)
                    yield Sparkline([], id="speed-sparkline", classes="hidden")
                    yield Label("Status: Ready", id="status-label")
                    yield MetadataDisplay("", id="metadata")
                    yield RichLog(id="log", highlight=True, markup=True)
            yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress", ProgressBar).update(progress=0)
        self.query_one("#metadata").display = False
        self.query_one("#main-container").border_title = " JableTV Downloader "
        self._breathe_border()
        self.push_screen(LandingScreen())

    @work(thread=True)
    def run_scrape(self, url: str) -> None:
        self._last_url = url
        self.call_from_thread(self._update_status, "Fetching metadata...")
        self._app_log("Fetching page...")
        try:
            if is_missav_url(url):
                raw = scrape_missav(url)
                video = _missav_to_videoinfo(raw)
            else:
                video = scrape(url)
            if not video.m3u8_url:
                self.call_from_thread(self._update_status, "Error: No m3u8 URL found")
                self._app_log("[red]Error: Could not find video source URL[/red]")
                return
            self.call_from_thread(self._on_metadata_loaded, video)
        except Exception as e:
            self.call_from_thread(self._update_status, f"Error: {e}")
            self._app_log(f"[red]Error: {e}[/red]")

    @work(thread=True)
    def run_download(self, video: VideoInfo, source_url: str = "") -> None:
        self._download_start = time.time()
        self._output_dir = os.environ.get("JABLETV_DOWNLOAD_DIR", "downloaded")
        output_dir = self._output_dir
        self.call_from_thread(self._update_status, "Starting download...")

        # Determine correct referer based on the source URL
        referer = None
        if is_missav_url(source_url):
            referer = "https://missav.ws/"

        def progress_cb(pct: int, speed: str, eta: str, status: str) -> None:
            self.call_from_thread(self._on_progress, pct, speed, eta, status)

        try:
            output_path = download(
                video,
                output_dir=output_dir,
                progress_callback=progress_cb,
                referer=referer,
            )
            self.call_from_thread(self._on_complete, str(output_path), video)
        except Exception as e:
            self.call_from_thread(self._on_error, str(e))

    def _app_log(self, message: str) -> None:
        log = self.query_one("#log", RichLog)
        log.write(message)

    def _update_status(self, message: str) -> None:
        self.query_one("#status-label", Label).update(f"Status: {message}")

    def _on_metadata_loaded(self, video: VideoInfo) -> None:
        metadata = self.query_one("#metadata", MetadataDisplay)
        metadata.show_info(video)
        metadata.display = True

        self._app_log(f"[green]Found: {video.code} - {video.title[:60]}[/green]")
        self._app_log("[green]Segments: resolving from m3u8...[/green]")

        self._update_status("Starting download...")
        self.run_download(video, source_url=self._last_url)

    def _on_progress(self, pct: int, speed: str, eta: str, status: str) -> None:
        self.query_one("#progress", ProgressBar).update(progress=pct)
        msg = f"{pct}%"
        if speed:
            msg += f" | {speed}"
            try:
                sp = float(speed.split()[0])
                self._speed_history.append(sp)
                if len(self._speed_history) > 50:
                    self._speed_history.pop(0)
                sl = self.query_one("#speed-sparkline", Sparkline)
                sl.remove_class("hidden")
                sl.data = self._speed_history
            except (ValueError, IndexError, Exception):
                pass
        if eta:
            msg += f" | ETA: {eta}"
        if status:
            msg += f" | {status}"
        self._update_status(msg)

    def _on_complete(self, path: str, video: VideoInfo) -> None:
        self._app_log(f"[bold green]Download complete: {path}[/bold green]")
        self._update_status("Complete!")

        try:
            save_metadata(video, self._output_dir)
            self._app_log(f"[dim]Metadata saved to jable_db/{video.code}.json[/dim]")
        except Exception as e:
            logger.warning("Failed to save metadata: %s", e)

        elapsed = time.time() - (self._download_start or time.time())
        file_size_mb = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0

        self._app_log(
            f"[dim]Size: {file_size_mb:.1f} MB, "
            f"Duration: {int(elapsed // 60)}:{int(elapsed % 60):02d}, "
            f"Speed: {file_size_mb / max(elapsed, 0.1):.1f} MB/s[/dim]"
        )

        self.action_open_dashboard()

    def _on_error(self, error: str) -> None:
        logger.error("Download failed: %s", error)
        self._app_log(f"[bold red]Download failed: {error}[/bold red]")
        self._update_status(f"Error: {error}")

    def _breathe_border(self) -> None:
        try:
            wrapper = self.query_one("#window-wrapper")
            self._breathing_pink = not self._breathing_pink
            target = "#ff69b4" if self._breathing_pink else "#fe628e"
            duration = 3.0
            wrapper.styles.animate("border_top_color", target, duration=duration)
            wrapper.styles.animate("border_right_color", target, duration=duration)
            wrapper.styles.animate("border_bottom_color", target, duration=duration)
            wrapper.styles.animate("border_left_color", target, duration=duration)
            self.set_timer(duration, self._breathe_border)
        except Exception:
            pass

    def action_open_library(self) -> None:
        self.push_screen(LibraryScreen())

    def action_open_dashboard(self) -> None:
        self.push_screen(DashboardScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dashboard-btn":
            self.action_open_dashboard()
        elif event.button.id == "library-btn":
            self.action_open_library()
        elif event.button.id == "download-btn":
            url = self.query_one("#url-input", Input).value.strip()
            if not url:
                self._update_status("Please enter a URL")
                return
            if not _is_supported_url(url):
                self._update_status("Please enter a valid jable.tv or missav.ws URL")
                return
            self.query_one("#progress", ProgressBar).update(progress=0)
            self._update_status("Fetching metadata...")
            self._app_log(f"Starting: {url}")
            self._speed_history.clear()
            sl = self.query_one("#speed-sparkline", Sparkline)
            sl.data = []
            sl.add_class("hidden")
            self.run_scrape(url)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input":
            url = event.value.strip()
            if url and _is_supported_url(url):
                self.query_one("#progress", ProgressBar).update(progress=0)
                self._update_status("Fetching metadata...")
                self._app_log(f"Starting: {url}")
                self._speed_history.clear()
                sl = self.query_one("#speed-sparkline", Sparkline)
                sl.data = []
                sl.add_class("hidden")
                self.run_scrape(url)


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------


def _is_supported_url(url: str) -> bool:
    """Check if the URL is from a supported site."""
    url_lower = url.lower()
    return "jable.tv" in url_lower or is_missav_url(url)


def _missav_to_videoinfo(m: MissavVideoInfo) -> VideoInfo:
    """Convert MissavVideoInfo to the common VideoInfo dataclass."""
    return VideoInfo(
        code=m.code,
        title=m.title,
        full_title=m.full_title,
        actresses=m.actresses,
        tags=[],
        category="",
        release_date="",
        views=0,
        thumbnail=m.thumbnail,
        m3u8_url=m.m3u8_url,
        video_id=m.video_id,
    )


def main() -> None:
    setup_logging()
    logger.info("JableTV Downloader starting")
    app = JableDownloaderApp()
    try:
        app.run()
    except Exception:
        logger.exception("Unhandled exception in app")
        raise
    finally:
        logger.info("JableTV Downloader shutting down")


if __name__ == "__main__":
    main()
