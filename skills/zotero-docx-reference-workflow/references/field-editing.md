# Word Field Editing

A complex Word field has a begin marker, instruction text, separator, display result and end marker. A bibliography often spans multiple paragraphs. Fields may also appear inside hyperlinks or content controls. Count actual fields, not paragraphs or raw marker substrings.

The instruction for a Zotero citation contains `ADDIN ZOTERO_ITEM CSL_CITATION` and citation JSON. Bibliography instructions contain `ADDIN ZOTERO_BIBL`. Parse JSON structurally and use `citationItems[].uris` as the preferred identity. Preserve local item IDs and URI identity; displayed citation numbers are formatting, not library IDs.

## Editing Rules

- Back up the source and work on a new output file.
- Delete or replace the complete field span. Editing only visible brackets leaves hidden citation items active.
- Preserve run formatting, hyperlinks, bookmarks, equations and drawings. Rebuilding a complete paragraph from plain text can destroy them.
- A multi-item citation is legitimate. Inspect its items and display before any repair. If splitting is required, create unique citation IDs, update each field's display metadata, and preserve item identities.
- For numbered styles, derive first-appearance order from body citations, then let Zotero format/rebuild references. Check display/result/formatting consistency. Do not rewrite `citationItems[].id` to the reference-list number.
- Keep citation placement tied to supported claims. Observe journal rules on abstract, figure notes, and discussion citations rather than imposing universal bans.
- Preserve document preferences and unrelated custom properties. Confirm package relationships/content types for `docProps/custom.xml`.
- When rewriting XML, retain namespace declarations referenced in `mc:Ignorable`; an ordinary Word open must succeed without repair.
- Use a known-good document/template structure when programmatic field insertion is necessary. Use compact CSL `itemData`, not a raw Zotero API item object.

The auditor reports numbered visible references only under a recognized References/Bibliography heading. Author-year references require style-aware/manual comparison. Missing numbered entries in an author-year manuscript are not evidence that its bibliography is broken.

Header/footer/footnote/endnote XML parts are scanned separately. Numbering checks are limited to the main document story; note-style manuscripts require Word/Zotero verification of ordering. Tracked deleted content is excluded from active counts, but unresolved revisions should be reviewed in Word before delivery.
