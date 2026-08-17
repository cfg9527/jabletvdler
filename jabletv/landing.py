from __future__ import annotations

from textual.app import ComposeResult, Screen
from textual.containers import Center, Container, Horizontal, Middle
from textual.widgets import Button, Label, Static


import pyfiglet

JABLETV_DL_ART = pyfiglet.figlet_format("JABLETV_DL", font="slant")

WARNING_EN = (
    "WARNING: This site contains adult content. "
    "You must be at least 18 years old to enter. "
    "By entering, you confirm that you are of legal age."
)

WARNING_JP = (
    "警告：このサイトには成人向けコンテンツが含まれています。"
    "入場するには18歳以上である必要があります。"
    "入場することにより、あなたが法的な成人年齢（18歳以上）であることを確認したことになります。"
)


class LandingScreen(Screen[None]):
    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        with Container(id="window-wrapper"):
            with Center():
                with Middle():
                    yield Static(JABLETV_DL_ART, id="age-gate-art")
                    yield Label(WARNING_EN, id="warning-en")
                    yield Label(WARNING_JP, id="warning-jp")
                    with Horizontal(id="age-gate-buttons"):
                        yield Button("Yes, I am 18+", id="btn-yes", variant="primary")
                        yield Button("No", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#window-wrapper").border_title = " Age Gate "

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.app.pop_screen()
        elif event.button.id == "btn-no":
            self.app.exit()
