# Contributing

Describe the actual research workflow and provide a synthetic input that reproduces an issue. Avoid attaching unpublished manuscripts, personal library exports, account tokens, or identifiable interview material.

Keep skill instructions short and move conditional details into linked references. Use command-line arguments for paths, proxies, styles, and endpoints. Add tests for changes to field parsing, numbering logic, installation, or layout measurement.

Before submitting a change, run `python tools/validate_repo.py` and `python -m unittest discover -s tests -v`. For diagram changes, also generate a preview and inspect it at publication size. For Word/Zotero claims, describe the exact live verification performed; offline tests cannot stand in for a successful refresh.
