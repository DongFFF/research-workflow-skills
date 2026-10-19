---
name: zotero-docx-reference-workflow
description: Search and verify literature, organize Zotero items, and inspect or maintain Zotero-linked Word citations and bibliographies through manuscript revisions.
---

# Zotero And Word Reference Workflow

Treat discovery, metadata verification, Zotero ingestion, citation insertion and refresh validation as separate stages with separate evidence. Use the user's specified tools and fallback restrictions. Discover available MCP tools before claiming a server is unavailable.

## Discovery And Verification

Read [discovery and ingestion](references/discovery-and-ingestion.md) when adding references. Prefer Google Scholar for discovery. Try the available search tool and a visible browser route if needed; use the user's configured proxy only after checking it. No proxy product or port is assumed.

Select candidates by relevance and claim support, using citation trails as context. Citation counts alone do not make a source mandatory. Official laws and policy documents may be verified at the issuing body's site. Resolve DOI-bearing works and compare metadata in a second pass. Mark missing information and access failures accurately.

## Zotero

Prefer Zotero MCP for search, collection management and readback. If unavailable, use the local Desktop/Connector route when allowed. The bundled client can probe or save explicit item metadata:

```sh
python scripts/zotero_connector.py ping
python scripts/zotero_connector.py save verified-items.json
```

HTTP success is not evidence of item keys or collection membership. Read back real item identities and metadata before citing. Preserve existing item keys during metadata repairs. Never write to Zotero's SQLite database. Library candidates and manuscript citations are distinct sets.

## Inspect And Edit

Make a timestamped backup before editing a manuscript. Run:

```sh
python scripts/inspect_zotero_docx.py manuscript.docx --out-dir audit
```

Review actual field counts, hidden items, JSON failures, empty displays, bibliography fields, document preferences, duplicate citation IDs and numbered-display mismatches. Multi-item fields are valid Zotero structures; inspect them for unintended hidden items. A one-item-per-field editing convention may be used when explicitly useful. Do not split author-year clusters mechanically.

Read [field editing rules](references/field-editing.md) before inserting, deleting or restructuring fields. Edit whole fields, retain formatting and namespaces, and preserve real item identity. Prefer Word/Zotero integration for insertion. First insertion may use IEEE when no journal/user style is specified; preserve an established style unless a change is requested. Obtain CSL from the user's chosen file or installed Zotero styles.

## Refresh And Delivery

Read [troubleshooting](references/troubleshooting.md) for browser, Connector and refresh failures. Field presence and successful macro dispatch do not prove completed refresh. Verify the completed Zotero operation, re-inspect the saved file and open it normally in Word. If live validation is unavailable, describe it as refresh-unverified.

Report search route and matched candidates, DOI status, ingestion/readback route, collection status, style, backup/output/audit paths, field counts, unique items, visible reference count and actual refresh evidence. Follow user restrictions if a required stage is blocked; do not deliver a silent static substitute.
