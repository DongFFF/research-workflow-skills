# SVG Layout Rules

## Geometry

Use one `viewBox` width and shared side margins for a figure set. Prefer changing height as complexity varies. Boxes with the same role share width and, where practical, height. Route connectors along the grid and terminate at box edges; use separate lanes for feedback.

Default to black, white and restrained gray for grant diagrams. Keep stroke weights, arrowheads and corner radii consistent. Color should encode meaning, not decorate the diagram.

## Typography

Measure with the font that will render the figure. Center the combined title/body group horizontally and vertically, accounting for glyph bearings and line height. Use start alignment only for genuine lists or tables, with the complete group vertically centered.

Aim for roughly 80%–88% occupation on the limiting inner dimension when practical. This is a compactness preference, not a mandate to overfill every box. Never use `textLength`, glyph stretching or nonuniform transforms to hit the target. Empty space can be meaningful when visual hierarchy requires it.

At the final insertion width, labels should normally remain at least 7–8 pt, subject to journal requirements. A large source-canvas font is not proof of readability after scaling. Increase height, split a figure or edit labels when needed.

## Checks

- Confirm equal set widths and peer-box dimensions numerically.
- Check all text against its box interior using actual glyph metrics.
- Confirm no connector crosses labels or enters unrelated boxes.
- Render every SVG and inspect at publication width and 100% zoom.
- Inspect Chinese and English glyph fallback separately when both appear.
- Confirm embedded document images use sufficient resolution; keep the SVG source.

The generator's JSON accepts a `width`, `title`, `rows` of nodes, and explicit `edges` between node IDs in adjacent rows. Nodes have `id`, `title`, and optional `body`. Edges represent the relationship declared by the author; the tool does not infer causality. See [the bundled example](../examples/framework.json).
