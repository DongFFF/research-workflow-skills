# Plot And Table Routes

Choose by claim: points or bars for comparisons; lines for ordered trends; distributions for spread; scatter for relationships; interval/forest plots for estimated effects; tables for exact values. Do not imply uncertainty intervals that were not computed from the data.

Inspect the installed package's signature/help before using an API. Examples describe a route and may need adaptation to its installed version:

```python
import pubfig as pf
# Inspect help(pf.line) and provide the actual x/series arrays for your version.
# fig = pf.line(...)
# pf.save_figure(fig, "figure.pdf")
```

```sh
pubtab --help
pubtab xlsx2tex results.xlsx -o results.tex
pubtab preview results.tex -o results.png --dpi 300
```

Preview may require LaTeX. Distinguish successful conversion from successful compilation. Follow the user's allowed fallback if an engine cannot run.

Check units, sample sizes, baselines, category order, missing values, uncertainty definitions, grayscale and color accessibility. For multi-panel comparisons, check comparable axes before sharing a legend. Export vector PDF/SVG for line art and a sufficiently resolved PNG preview. Record input data and generation command alongside the figure without publishing confidential data.
