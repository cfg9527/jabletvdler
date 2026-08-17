## Why

The current dashboard shows a single flat table of tags with only a text stat showing the top actress. As the library grows, users need at-a-glance visibility into multiple dimensions of their collection — top tags, top titles, top actresses, and video count trends — without scrolling or navigating. A four-window layout provides instant peripheral awareness of the library's composition.

## What Changes

- Replace the single DataTable dashboard with a **four-quadrant layout** using Textual's `Vertical`/`Horizontal` containers
- Each quadrant displays a **top-5 ranked list** for a specific dimension
- Retain the existing border-title TUI style matching the rest of the app
- Remove the old `#dashboard-table` and `#dashboard-stats` widgets

## Capabilities

### New Capabilities
- `dashboard-four-windows`: A four-pane dashboard screen showing Top Tags, Top Titles, Top Actresses, and Library Summary (total count, date range) — each window scrollable, sorted, and styled consistently

### Modified Capabilities
- *(none — first dashboard spec)*

## Impact

- **jabletv/dashboard.py**: Full rewrite of `DashboardScreen.compose()` and `_load_report()`
- **jabletv/metadata_store.py**: No changes expected (reuses existing `load_all_metadata`)
- No new dependencies, no API changes
