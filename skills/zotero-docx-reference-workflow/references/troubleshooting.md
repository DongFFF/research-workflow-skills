# Troubleshooting And Evidence

| Symptom | What to check | Evidence to retain |
| --- | --- | --- |
| Browser MCP times out | Tool transport, browser debugging connection, actual tab navigation | Tool name, timeout and visible-browser outcome |
| Scholar returns an empty page or challenge | Exact title match, challenge status, current proxy configuration | Query, page status, matching candidate or explicit no-match |
| DOI returns 403/429 | Publisher access controls versus DOI resolver outcome | Redirect/registry/publisher records and pending fields |
| Connector returns 201 | Zotero readback, library and actual collection membership | Returned/read-back identity and collection |
| Old metadata persists in Word | Whether the field still points to an older duplicate item | URI/key before and after repair |
| Deleted reference returns | Hidden items, other body fields, bibliography `uncited` settings | Parsed citation JSON and full-field deletion |
| Word opens only with repair | Namespace declarations and package relationships | Ordinary open outcome; treat repair as failure |
| Refresh macro returns immediately | Zotero operation may be asynchronous | Completed operation and saved result, not only macro return |

For refresh validation, activate the intended document before dispatching the installed Zotero Refresh command. Do not assume a macro name is universal. Observe completion, save, reopen and re-inspect. A controlled check on a disposable copy can replace one stale visible citation display and confirm Zotero regenerates it; preserve original citation identity and restore/check the final document. Do not edit live library metadata solely to test a refresh.

If the document was already correct and no visible change is expected, record what completion evidence is available and the resulting audit. Do not invent a successful mutation. A timeout, pending dialog or COM hang is a failed or unresolved attempt, even if fields remain in the saved package.

Record any remaining mismatch, unsupported Word field form or unavailable live environment. Local SQLite can be queried read-only when necessary; use a coherent read-only snapshot/backup and never modify the live database. Avoid treating a copied database without its current transaction state as definitive evidence of missing items.
