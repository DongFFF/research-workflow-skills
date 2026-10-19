# Faithful Redraw And Translation

Inventory the source: canvas ratio, text boxes, coordinates, strokes, anchor points, arrows, grouping, and reading order. Trace geometry before translating text.

For an explicit 1:1 request, preserve all lines and relationships. Fit translated text within existing boxes using wrapping and modest font adjustment. If faithful geometry makes text unreadable, explain the conflict and provide a clearly labeled alternative rather than silently moving lines.

Compare a rendered SVG with the source using an overlay or side-by-side view. Check each box and connector against the inventory, not only the overall silhouette. Report illegible source text as uncertain instead of guessing it.

SVG remains editable as vector elements. Inserting SVG into PowerPoint does not guarantee each object is editable. When separate PowerPoint objects are requested, generate native shapes/text/connectors and inspect the resulting deck separately.
