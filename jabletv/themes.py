from __future__ import annotations


class PinkyTheme:
    ACCENT = "#fe628e"
    SECONDARY_PINK = "#ff6a88"
    CORAL = "#ff8382"
    DEEPPINK = "#ff1493"
    PRIMARY_GRADIENT_START = "#91a5f4"
    PRIMARY_GRADIENT_END = "#b08cf9"
    SURFACE_DARK = "#161a26"
    SURFACE_LIGHT = "#191d28"
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_MUTED = "#8e9194"
    TEXT_SECONDARY = "#b8babc"
    SUCCESS_GREEN = "#1db954"
    BORDER_MUTED = "#5e5d5a"
    WARNING_YELLOW = "#ffd700"
    WARNING_AMBER = "#ff8c00"
    BUTTON_NO_BG = "#3a3a3a"
    BUTTON_NO_TEXT = "#888888"
    VARIANT_CORAL = "#ff6b6b"
    VARIANT_SAGE = "#4a5d4e"
    VARIANT_EMERALD = "#10b981"
    VARIANT_AMBER = "#f59e0b"

    CSS = f"""
    Screen {{
        background: {SURFACE_DARK};
    }}

    $primary: {PRIMARY_GRADIENT_START};
    $accent: {ACCENT};
    $surface: {SURFACE_DARK};
    $text: {TEXT_PRIMARY};
    $text-muted: {TEXT_MUTED};
    $error: {CORAL};
    $success: {SUCCESS_GREEN};

    #window-wrapper {{
        width: 100%;
        height: 100%;
        border: heavy $accent;
        background: {SURFACE_DARK};
    }}

    #main-container {{
        width: 80%;
        max-width: 80;
        height: auto;
        border: solid {BORDER_MUTED};
        padding: 1 2;
    }}

    #main-container:focus-within {{
        border: solid $accent;
    }}

    #url-input {{
        width: 100%;
        margin-bottom: 1;
        background: {SURFACE_LIGHT};
        border: solid {BORDER_MUTED};
    }}

    #url-input:focus {{
        border: solid $accent;
    }}

    #action-buttons {{
        width: 100%;
        height: 3;
        margin-bottom: 1;
    }}

    #download-btn {{
        width: 1fr;
        background: {PRIMARY_GRADIENT_START};
        color: #fff;
        margin-right: 1;
    }}

    #download-btn:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
    }}

    #library-btn {{
        width: 1fr;
        background: {SURFACE_LIGHT};
        color: $text;
        margin-right: 1;
    }}

    #library-btn:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
        border: solid hotpink;
    }}

    #dashboard-btn {{
        width: 1fr;
        background: {SURFACE_LIGHT};
        color: $text;
    }}

    #dashboard-btn:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
        border: solid hotpink;
    }}

    #progress {{
        width: 100%;
        margin-bottom: 1;
    }}

    ProgressBar > .bar {{
        background: {SURFACE_LIGHT};
    }}

    ProgressBar > .bar > .bar-fill {{
        background: $accent;
    }}

    #speed-sparkline {{
        height: 3;
        width: 100%;
        margin-bottom: 1;
        color: $accent;
    }}

    #status-label {{
        width: 100%;
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }}

    #metadata {{
        width: 100%;
        height: auto;
        min-height: 5;
        border: solid {SURFACE_LIGHT};
        padding: 1;
        margin-bottom: 1;
        color: $text;
    }}

    #log {{
        width: 100%;
        height: 10;
        border: solid {SURFACE_LIGHT};
        margin-bottom: 1;
    }}

    .hidden {{
        display: none;
    }}

    Header {{
        background: {SURFACE_DARK};
        color: $accent;
    }}

    Header > HeaderTitle {{
        color: $accent;
    }}

    Header > HeaderClock {{
        color: $text-muted;
    }}

    Footer {{
        background: {SURFACE_DARK};
    }}

    Footer > FooterKey > .key {{
        color: {SECONDARY_PINK};
    }}

    Footer > FooterKey > .text {{
        color: $text-muted;
    }}

    #age-gate-art {{
        color: {DEEPPINK};
        text-style: bold;
        width: 100%;
        text-align: center;
    }}

    #warning-en {{
        color: {WARNING_YELLOW};
        text-style: bold;
        width: 100%;
        text-align: center;
        margin-top: 1;
        padding: 0 2;
    }}

    #warning-jp {{
        color: {WARNING_AMBER};
        width: 100%;
        text-align: center;
        margin-top: 1;
        padding: 0 2;
    }}

    #age-gate-buttons {{
        align: center middle;
        margin-top: 2;
        height: 3;
    }}

    #btn-yes {{
        background: {ACCENT};
        color: #fff;
        text-style: bold;
        margin-right: 1;
        min-width: 20;
    }}

    #btn-yes:hover {{
        background: {SECONDARY_PINK};
    }}

    #btn-no {{
        background: {BUTTON_NO_BG};
        color: {BUTTON_NO_TEXT};
        margin-left: 1;
        min-width: 10;
    }}

    #btn-no:hover {{
        background: #555;
        color: #ccc;
    }}

    #complete-screen {{
        align: center middle;
        width: 100%;
        height: 100%;
    }}

    #variant-banner {{
        color: $accent;
        text-style: bold;
        width: 100%;
        text-align: center;
    }}

    #variant-art, #variant-confetti, #variant-checkmark {{
        color: {TEXT_SECONDARY};
        width: 100%;
        text-align: center;
    }}

    #variant-headline {{
        color: $text;
        text-style: bold;
        width: 100%;
        text-align: center;
        margin-top: 1;
    }}

    #variant-body {{
        color: $text-muted;
        width: 100%;
        text-align: center;
        margin-top: 1;
    }}

    #metrics-spacer {{
        height: 1;
    }}

    #metrics-display {{
        color: {TEXT_MUTED};
        width: auto;
        text-align: left;
        border: solid {BORDER_MUTED};
        padding: 1 2;
        margin-top: 1;
    }}

    #complete-buttons {{
        align: center middle;
        margin-top: 2;
        height: 3;
    }}

    #btn-another {{
        background: {PRIMARY_GRADIENT_START};
        color: #fff;
        text-style: bold;
        margin-right: 1;
        min-width: 20;
    }}

    #btn-another:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
    }}

    #btn-open {{
        background: {SURFACE_LIGHT};
        color: $text;
        margin-left: 1;
        margin-right: 1;
        min-width: 16;
    }}

    #btn-open:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
        border: solid hotpink;
    }}

    #btn-quit {{
        background: {BUTTON_NO_BG};
        color: {BUTTON_NO_TEXT};
        margin-left: 1;
        min-width: 10;
    }}

    #btn-quit:hover {{
        background: hotpink;
        color: #fff;
        text-style: bold;
    }}

    #farewell-art {{
        color: {DEEPPINK};
        text-style: bold;
        width: 100%;
        text-align: center;
    }}

    #farewell-msg {{
        color: $text-muted;
        width: 100%;
        text-align: center;
        margin-top: 2;
    }}
    """
