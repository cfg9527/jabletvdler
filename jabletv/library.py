from __future__ import annotations

import os
import platform
import subprocess
from typing import Any

from textual.app import ComposeResult, Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Static
from textual.widgets._data_table import DataTable

from .metadata_store import load_all_metadata, search_metadata


CSS = """
$border-muted: #5e5d5a;

#library-screen {
    align: center middle;
    width: 100%;
    height: 100%;
}

#library-search {
    width: 100%;
    margin-bottom: 1;
    background: $surface;
    border: solid $border-muted;
}

#library-search:focus {
    border: solid $accent;
}

#library-table {
    width: 100%;
    height: 14;
    border: solid $border-muted;
    margin-bottom: 1;
}

#library-table > .datatable--header {
    color: $accent;
    text-style: bold;
}

#library-table > .datatable--cursor {
    background: $accent 30%;
}

#library-detail {
    width: 100%;
    height: auto;
    min-height: 5;
    border: solid $border-muted;
    padding: 1;
    margin-bottom: 1;
    color: $text;
}

#library-empty {
    width: 100%;
    text-align: center;
    color: $text-muted;
    margin-top: 4;
}

#library-buttons {
    align: center middle;
    height: 3;
}

#btn-open-url {
    background: $primary;
    color: #fff;
    text-style: bold;
    margin-right: 1;
    min-width: 16;
}

#btn-open-url:hover {
    background: hotpink;
    color: #fff;
    text-style: bold;
}

#btn-back {
    background: $surface;
    color: $text;
    margin-left: 1;
    min-width: 16;
}

#btn-back:hover {
    background: hotpink;
    color: #fff;
    text-style: bold;
}
"""


class LibraryScreen(Screen[None]):
    CSS = CSS
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("o", "open_url", "Open URL"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.all_entries: list[dict[str, Any]] = []
        self._displayed: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        with Container(id="window-wrapper"):
            with Vertical(id="library-screen"):
                yield Input(
                    placeholder="Search by code, tag, actress, or category...",
                    id="library-search",
                )
                yield Static("No downloaded videos found.", id="library-empty")
                yield DataTable(id="library-table")
                yield Static("", id="library-detail")
                with Horizontal(id="library-buttons"):
                    yield Button("Open URL", id="btn-open-url", variant="primary")
                    yield Button("Back", id="btn-back")

    def on_mount(self) -> None:
        self.query_one("#window-wrapper").border_title = " Library "
        self._load_entries()

    def _load_entries(self) -> None:
        output_dir = os.environ.get("JABLETV_DOWNLOAD_DIR", "downloaded")
        self.all_entries = load_all_metadata(output_dir)

        empty_label = self.query_one("#library-empty", Static)
        table = self.query_one("#library-table", DataTable)
        detail = self.query_one("#library-detail", Static)

        if not self.all_entries:
            empty_label.display = True
            table.display = False
            detail.display = False
            return

        empty_label.display = False
        table.display = True
        detail.display = True
        self._refresh_table(self.all_entries)

    def _refresh_table(self, entries: list[dict[str, Any]]) -> None:
        table = self.query_one("#library-table", DataTable)
        table.clear()
        self._displayed = entries
        table.add_columns("Code", "Title", "Actresses", "Tags")

        for e in entries:
            table.add_row(
                e.get("code", ""),
                (e.get("title", "") or "")[:40],
                ", ".join(e.get("actresses", [])),
                ", ".join(e.get("tags", [])[:3]),
            )

    def _entry_at_cursor(self) -> dict[str, Any] | None:
        table = self.query_one("#library-table", DataTable)
        cursor_row = table.cursor_row
        if cursor_row is None:
            return None
        if cursor_row < 0 or cursor_row >= len(self._displayed):
            return None
        return self._displayed[cursor_row]

    def _show_detail(self, entry: dict[str, Any]) -> None:
        lines = [
            f"[bold]{entry.get('full_title', entry.get('title', ''))}[/bold]",
            f"Code: [bold cyan]{entry.get('code', '')}[/bold cyan]",
            f"Actresses: [bold yellow]{', '.join(entry.get('actresses', [])) or 'N/A'}[/bold yellow]",
            f"Views: {entry.get('views', 0):,}  |  Date: {entry.get('release_date', '') or 'N/A'}",
            f"Category: {entry.get('category', '') or 'N/A'}",
            f"Tags: [italic]{', '.join(entry.get('tags', []))}[/italic]",
        ]
        self.query_one("#library-detail", Static).update("\n".join(lines))

    def _open_url(self) -> None:
        entry = self._entry_at_cursor()
        if entry is None:
            return
        code = entry.get("code", "")
        if not code:
            return
        url = f"https://jable.tv/videos/{code.lower()}/"
        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.run(["open", url], check=False)
            elif system == "Linux":
                subprocess.run(["xdg-open", url], check=False)
            elif system == "Windows":
                os.startfile(url)  # type: ignore[attr-defined]
        except Exception as e:
            if hasattr(self.app, "_app_log"):
                self.app._app_log(f"[red]Failed to open URL: {e}[/red]")

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_open_url(self) -> None:
        self._open_url()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "library-search":
            filtered = search_metadata(self.all_entries, event.value)
            self._refresh_table(filtered)
            if filtered:
                self.query_one("#library-table", DataTable).display = True
                self.query_one("#library-empty", Static).display = False
            else:
                self.query_one("#library-table", DataTable).display = False
                self.query_one("#library-empty", Static).display = True

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.cursor_row is not None:
            entry = self._displayed[event.cursor_row] if 0 <= event.cursor_row < len(self._displayed) else None
            if entry:
                self._show_detail(entry)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.cursor_row is not None:
            entry = self._displayed[event.cursor_row] if 0 <= event.cursor_row < len(self._displayed) else None
            if entry:
                self._show_detail(entry)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-open-url":
            self._open_url()
        elif event.button.id == "btn-back":
            self.app.pop_screen()
