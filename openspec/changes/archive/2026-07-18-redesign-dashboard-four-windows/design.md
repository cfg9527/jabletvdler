## Context

The current `DashboardScreen` (`jabletv/dashboard.py:75`) displays a single `DataTable` of all tags with a small stats line showing total videos and the top actress. As the library grows, users need to see multiple dimensions at once without scrolling: which tags appear most, which titles are newest, which actresses are most common, and aggregate library stats. The four-window layout fulfills this while maintaining the app's established TUI aesthetic (border titles, `$surface`/`$accent` colors, hotpink hover).

Data source: `jabletv/metadata_store.py` — `load_all_metadata()` returns a list of VideoInfo dicts (keys: `title`, `code`, `actresses`, `tags`, `date`, `path`, etc.). No schema changes needed.

## Goals / Non-Goals

**Goals:**
- Four equally-sized panes arranged in a 2×2 grid inside the dashboard screen
- Each pane shows a border title and a vertically-scrollable top-5 or summary list
- Pane 1: **Top Tags** (top 5 tags by frequency)
- Pane 2: **Top Titles** (last 5 videos by date, with code + title)
- Pane 3: **Top Actresses** (top 5 actresses by video count)
- Pane 4: **Library Summary** (total videos, total tags, total actresses, date range)
- All panes use the same border-title and color conventions as the rest of the app

**Non-Goals:**
- No interactive sorting or filtering within panes (future enhancement)
- No pagination (top-5 is fixed)
- No chart/graph widgets — text-only lists
- No changes to `metadata_store.py`

## Decisions

1. **2×2 grid via nested Horizontal/Vertical containers** — Textual's `Horizontal` with two `Vertical` children, each containing two `Static` or `ScrollableContainer` panes. Avoids custom CSS grid which is not natively supported in Textual.
2. **Static widgets for each pane** — Each pane is a `Static` with `border: solid $border-muted` and `border_title` set. Content is a multi-line string. Simpler and more consistent than four `DataTable` widgets.
3. **Reuse `load_all_metadata`** — No new queries or indexes. Sorting and counting is done in-memory with Python's `Counter` and `sorted()`. The library is small (<1000 entries), so performance is not a concern.
4. **`ScrollableContainer` only if needed** — If content may exceed 5 lines, wrap pane in `ScrollableContainer`. For top-5 lists this is unlikely, but we add it for the Library Summary pane which may have longer date ranges.

## Risks / Trade-offs

- **Window width on narrow terminals** → The 2×2 grid expects at least 80 columns. Each pane gets `width: 1fr`. On very narrow terminals, text may wrap awkwardly. Mitigation: use `min-width` on panes and let Horizontal/Textual's layout engine shrink gracefully.
- **Empty library edge case** → If `load_all_metadata` returns `[]`, all four panes show "No data yet." The empty state is handled in `_load_report()`.
- **Long tag/actress names** → Names like "佐々波 綾" may be truncated if pane is too narrow. Mitigation: use `max-width` with `overflow: ellipsis` on pane content.
