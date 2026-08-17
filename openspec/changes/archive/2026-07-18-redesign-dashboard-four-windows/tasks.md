## 1. Rewrite Dashboard Layout

- [x] 1.1 Refactor `DashboardScreen.compose()` to 2×2 grid using nested `Horizontal`/`Vertical` containers with four bordered `Static` panes
- [x] 1.2 Add CSS for four panes: equal `width: 1fr`, border styling, scrollable content, empty-state text alignment

## 2. Implement Data Loading & Four Panes

- [x] 2.1 Compute Top Tags (Counter, top 5) and render into pane with " Top Tags " border title
- [x] 2.2 Compute Top Titles (last 5 by date) and render into pane with " Top Titles " border title
- [x] 2.3 Compute Top Actresses (Counter, top 5) and render into pane with " Top Actresses " border title
- [x] 2.4 Compute Library Summary (total videos, tags, actresses, date range) and render into pane with " Library Summary " border title

## 3. Handle Edge Cases

- [x] 3.1 Show empty-state messages in all four panes when library is empty
- [x] 3.2 Handle missing fields (video with no date, no tags, no actresses) gracefully

## 4. Verify

- [x] 4.1 Run `ruff check jabletv/` — no new violations
- [x] 4.2 Run `mypy jabletv/` — no new type errors
- [x] 4.3 Run `python3 -m pytest tests/ -v` — all existing tests pass
