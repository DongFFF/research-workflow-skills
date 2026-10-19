---
name: publication-chart-skill
description: Create or revise publication figures, research frameworks, mechanism diagrams, technical routes and tables; export editable SVG with readable labels and verified layout.
---

# Publication Figures And Research Diagrams

First identify the scientific claim, input evidence, intended insertion width, and whether the request is a new figure, a revision, or an exact redraw. Preserve explicit style and geometry requirements.

## Select The Route

- For research frameworks, mechanism models, evidence chains and process diagrams, use editable native SVG. Read [layout rules](references/svg-layout.md).
- For quantitative plots, prefer the user's existing plotting code or `pubfig` when available. Read [plot and table routes](references/plots-and-tables.md).
- For exact values and comparisons that benefit from lookup, use a table. `pubtab` is useful for Excel/LaTeX conversions.
- For faithful redraw or translation, read [redraw rules](references/redraw.md) before changing geometry.

Probe only dependencies needed for the chosen route. Install into the selected project environment when needed and authorized. Report the actual package/API used and any failed route; follow the user's restrictions on substitutions.

## Diagram Production

1. Map entities, relations, arrow meanings and evidence status to the manuscript. Separate research steps from causal claims.
2. Establish a shared width, margins, grid, peer-box sizes, type hierarchy and arrow style across the set.
3. Fit text using measured glyph dimensions. Center the combined title/body block. Change line breaks or box height before shrinking below publication readability.
4. Preserve SVG text and shapes as editable elements. Use a genuine bitmap renderer for previews.
5. Check the preview at the intended insertion width. Inspect clipping, line crossings, arrow anchors, line weights, grayscale and label density.

For ordinary row-based diagrams, the bundled helper provides editable SVG and measured layout:

```sh
python scripts/make_framework.py framework.json --out-dir output --font /path/to/font.ttf --png
```

The helper is a starting point, not a universal layout engine. For complex feedback loops, swimlanes or exact redraws, create a tailored SVG while retaining the layout rules. Generated fit statistics do not replace visual QA.

## Delivery

Deliver the editable source, rendered preview, caption and insertion location when known. State the artifact's evidence status and any deliberate layout exception. Provide a companion exact-value table only when it serves a separate communication role. For multi-panel figures, align panel widths, axes and label styles before assembly.
