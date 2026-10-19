# Discovery And Ingestion

## Scholar First

1. Search using the available Scholar MCP/search tool. Log query and access time.
2. If the tool fails, navigate to Scholar in a visible supported browser. Check actual page content: a challenge page or HTTP 200 with no matching result is not successful candidate verification.
3. If challenged, ask the user to complete human verification. Report the specific failed tool/browser route. Do not bypass the challenge.
4. Capture title, authors/source line, landing/version URLs, snippet, and cited-by count when available. Record whether the target title actually matches. Prefer the result's Cite/export metadata when accessible.
5. Use DOI registries and publisher pages to complete and verify selected candidates. Use a different discovery source only when requested or allowed by the user's fallback preferences.

Do not relabel a Scholar snippet as the publisher's abstract. Avoid storing full copyrighted text in a public manifest. Distinguish a failed network request from a nonexistent paper.

## Metadata Record

Collect full structured creators, title, venue, year and date basis, volume/issue, pages or article number, DOI/ISBN/ISSN where applicable, landing URL, abstract/snippet provenance and keywords when available. Track missing fields as missing or not-applicable. Institutional authors use a single literal name; personal names retain supplied family/given boundaries and compound surnames.

For DOI second-pass verification, start with the DOI URL, record the redirect/landing outcome, and compare title, authors, publication, year and pagination. A redirect alone is insufficient. Distinguish online-first from issue year. Registration records can omit page ranges or misparse names; reconcile with publisher records and record conflicts.

If access restrictions prevent publisher confirmation, record the fallback source and verification level. An identifier with failed resolution remains pending under DOI-only verification requirements.

## Zotero Save And Readback

Search for an existing item by DOI/title before creating duplicates. Create/select a project collection through a supported tool, then verify its actual membership after saving. A tag is not a collection. The Connector save endpoint may use the current Desktop selection; do not assume it selects the requested project collection.

After saving, read metadata and actual URI/key from Zotero. Zotero Web API IDs, local itemIDs, user-library URIs and group-library URIs are different representations; use the identity returned for that library. Never synthesize an account ID or item key.

The bundled Connector client accepts a JSON array of Zotero translator-style items, or an object containing `items`. It has no built-in collection/readback operation. Use MCP/Desktop for those stages and report when they remain pending.

For a manifest template, see [the bundled example](../examples/reference-manifest.example.json). The example is intentionally incomplete and must never be cited as a verified paper.
