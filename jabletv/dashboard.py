from __future__ import annotations

import os
from collections import Counter

from textual.app import ComposeResult, Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static

from .metadata_store import load_all_metadata


CSS = """
$border-muted: #5e5d5a;

#window-wrapper {
    width: 100%;
    height: 100%;
}

#dashboard-screen {
    width: 100%;
    height: 100%;
}

.dashboard-pane {
    width: 1fr;
    height: 1fr;
    border: solid $border-muted;
    padding: 0 1;
    overflow-y: auto;
}

.dashboard-pane > .pane-title {
    text-style: bold;
    color: $accent;
    padding-bottom: 1;
}

.dashboard-pane > .pane-row {
    padding: 0 0 0 1;
}

.dashboard-pane > .pane-empty {
    color: $text-muted;
    text-align: center;
    margin-top: 1;
}

#dashboard-buttons {
    align: center middle;
    height: 3;
    dock: bottom;
}

#btn-back {
    background: $surface;
    color: $text;
    min-width: 16;
}

#btn-back:hover {
    background: hotpink;
    color: #fff;
    text-style: bold;
}
"""


class DashboardScreen(Screen[None]):
    CSS = CSS
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="window-wrapper"):
            with Vertical(id="dashboard-screen"):
                with Horizontal():
                    with Vertical(classes="dashboard-pane", id="pane-tags"):
                        yield Static("Top Tags", classes="pane-title")
                    with Vertical(classes="dashboard-pane", id="pane-titles"):
                        yield Static("Top Titles", classes="pane-title")
                with Horizontal():
                    with Vertical(classes="dashboard-pane", id="pane-actresses"):
                        yield Static("Top Actresses", classes="pane-title")
                    with Vertical(classes="dashboard-pane", id="pane-summary"):
                        yield Static("Library Summary", classes="pane-title")
                with Horizontal(id="dashboard-buttons"):
                    yield Button("Back", id="btn-back")

    def on_mount(self) -> None:
        self.query_one("#window-wrapper").border_title = " Dashboard "
        self._load_report()

    def _load_report(self) -> None:
        output_dir = os.environ.get("JABLETV_DOWNLOAD_DIR", "downloaded")
        entries = load_all_metadata(output_dir)

        tag_counter: Counter[str] = Counter()
        actress_counter: Counter[str] = Counter()
        total_videos = len(entries)
        dates: list[str] = []

        for e in entries:
            for tag in e.get("tags", []):
                tag_counter[tag] += 1
            for actress in e.get("actresses", []):
                actress_counter[actress] += 1
            date = e.get("date")
            if date:
                dates.append(date)

        self._render_tags(tag_counter, total_videos)
        self._render_titles(entries, total_videos)
        self._render_actresses(actress_counter, total_videos)
        self._render_summary(total_videos, tag_counter, actress_counter, dates)

    def _render_tags(self, tag_counter: Counter[str], total: int) -> None:
        pane = self.query_one("#pane-tags", Vertical)
        if total == 0 or not tag_counter:
            pane.mount(Static("No tags yet", classes="pane-empty"))
            return
        sorted_items = sorted(tag_counter.items(), key=lambda x: -x[1])[:5]
        for tag, count in sorted_items:
            pane.mount(Static(f"{tag} [dim]{count}[/dim]", classes="pane-row"))

    def _render_titles(self, entries: list[dict], total: int) -> None:
        pane = self.query_one("#pane-titles", Vertical)
        if total == 0:
            pane.mount(Static("No titles yet", classes="pane-empty"))
            return
        sorted_entries = sorted(
            [e for e in entries if e.get("date")],
            key=lambda x: x["date"],
            reverse=True,
        )[:5]
        if not sorted_entries:
            pane.mount(Static("No titles yet", classes="pane-empty"))
            return
        for e in sorted_entries:
            code = e.get("code", "")
            title = e.get("title", "")
            label = f"{code} - {title}" if code and title else (code or title)
            pane.mount(Static(label, classes="pane-row"))

    def _render_actresses(self, actress_counter: Counter[str], total: int) -> None:
        pane = self.query_one("#pane-actresses", Vertical)
        if total == 0 or not actress_counter:
            pane.mount(Static("No actresses yet", classes="pane-empty"))
            return
        sorted_items = sorted(actress_counter.items(), key=lambda x: -x[1])[:5]
        for actress, count in sorted_items:
            pane.mount(Static(f"{actress} [dim]{count}[/dim]", classes="pane-row"))

    def _render_summary(
        self,
        total: int,
        tag_counter: Counter[str],
        actress_counter: Counter[str],
        dates: list[str],
    ) -> None:
        pane = self.query_one("#pane-summary", Vertical)
        if total == 0:
            pane.mount(Static("No data yet", classes="pane-empty"))
            return
        lines = [
            f"Total videos: [bold]{total}[/bold]",
            f"Unique tags: [bold]{len(tag_counter)}[/bold]",
            f"Unique actresses: [bold]{len(actress_counter)}[/bold]",
        ]
        if dates:
            sorted_dates = sorted(dates)
            lines.append(f"Earliest: {sorted_dates[0]}")
            lines.append(f"Latest: {sorted_dates[-1]}")
        for line in lines:
            pane.mount(Static(line, classes="pane-row"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
