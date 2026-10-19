#!/usr/bin/env python3
"""Read-only audit of Zotero fields in DOCX; no Word or Zotero needed."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def identity(item: dict) -> str:
    uris = item.get("uris") or []
    if uris:
        return str(uris[0])
    data = item.get("itemData") or {}
    for value in (item.get("uri"), data.get("DOI"), item.get("id"), data.get("id")):
        if value is not None:
            return str(value)
    return json.dumps(item, sort_keys=True, ensure_ascii=False)


def citation_data(instruction: str) -> dict | None:
    marker = instruction.find("CSL_CITATION")
    brace = instruction.find("{", marker) if marker >= 0 else -1
    if brace < 0:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(instruction[brace:])
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def parse_fields(root: ET.Element, part: str) -> tuple[list[dict], list[str]]:
    """Track field stacks over the whole story, including cross-paragraph fields."""
    stack: list[dict] = []
    fields: list[dict] = []
    warnings: list[str] = []
    paragraph = 0
    position = 0

    def visit(node: ET.Element) -> None:
        nonlocal paragraph, position
        if node.tag in {W + "del", W + "moveFrom"}:
            return
        if node.tag == W + "p":
            paragraph += 1
            for field in stack:
                if field["in_result"] and field["display_parts"]:
                    field["display_parts"].append("\n")
        if node.tag == W + "fldSimple":
            position += 1
            fields.append({
                "part": part, "paragraph": paragraph, "position": position,
                "instruction": node.get(W + "instr", ""),
                "display": "".join(n.text or "" for n in node.iter(W + "t")),
                "complete": True,
            })
            return
        if node.tag == W + "fldChar":
            kind = node.get(W + "fldCharType")
            if kind == "begin":
                position += 1
                stack.append({
                    "part": part, "paragraph": paragraph, "position": position,
                    "instruction_parts": [], "display_parts": [], "in_result": False,
                })
            elif kind == "separate" and stack:
                stack[-1]["in_result"] = True
            elif kind == "end":
                if stack:
                    finish(stack.pop(), True)
                else:
                    warnings.append(f"{part}: unmatched field end near paragraph {paragraph}")
        elif node.tag == W + "instrText" and stack:
            stack[-1]["instruction_parts"].append(node.text or "")
        elif node.tag in {W + "t", W + "tab", W + "br"}:
            value = node.text or "" if node.tag == W + "t" else ("\t" if node.tag == W + "tab" else "\n")
            for field in stack:
                if field["in_result"]:
                    field["display_parts"].append(value)
        for child in node:
            visit(child)

    def finish(field: dict, complete: bool) -> None:
        fields.append({
            "part": field["part"], "paragraph": field["paragraph"], "position": field["position"],
            "instruction": "".join(field["instruction_parts"]),
            "display": "".join(field["display_parts"]).strip(), "complete": complete,
        })

    visit(root)
    for field in stack:
        finish(field, False)
        warnings.append(f"{part}: unclosed field near paragraph {field['paragraph']}")
    return sorted(fields, key=lambda f: f["position"]), warnings


def visible_references(root: ET.Element) -> list[str]:
    entries = []
    active = False
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if re.fullmatch(r"references?|bibliography|参考文献", text, re.I):
            active = True
            continue
        # Stop at a subsequent heading, while allowing bibliography-styled paragraphs.
        style = p.find(f"{W}pPr/{W}pStyle")
        if active and style is not None and re.match(r"Heading[1-9]$", style.get(W + "val", ""), re.I):
            break
        if active and re.match(r"^\[\d+\]\s*", text):
            entries.append(text)
    return entries


def inspect_docx(path: Path) -> dict:
    fields = []
    warnings = []
    with ZipFile(path) as package:
        parts = [n for n in package.namelist() if re.fullmatch(
            r"word/(document|footnotes|endnotes|header\d+|footer\d+)\.xml", n
        )]
        parts.sort(key=lambda n: (n != "word/document.xml", n))
        roots = {}
        for part in parts:
            roots[part] = ET.fromstring(package.read(part))
            found, messages = parse_fields(roots[part], part)
            fields.extend(found)
            warnings.extend(messages)
        preferences = False
        if "docProps/custom.xml" in package.namelist():
            custom = ET.fromstring(package.read("docProps/custom.xml"))
            preferences = any(p.get("name", "").startswith("ZOTERO_PREF") for p in custom)

    citations = []
    bibliographies = []
    first_seen = {}
    sequence_mismatches = []
    citation_ids = []
    for field in fields:
        instr = field.pop("instruction")
        if "ZOTERO_ITEM" in instr:
            data = citation_data(instr)
            raw_items = data.get("citationItems", []) if data else []
            valid_items = isinstance(raw_items, list) and all(isinstance(x, dict) for x in raw_items)
            items = raw_items if valid_items else []
            props = data.get("properties") or {} if data else {}
            if not isinstance(props, dict):
                props = {}
            citation_id = data.get("citationID") if data else None
            if citation_id:
                citation_ids.append(str(citation_id))
            keys = [identity(item) for item in items]
            field.update({
                "json_parse_ok": data is not None,
                "citation_items_valid": valid_items,
                "citation_id": citation_id, "item_count": len(items), "identities": keys,
            })
            citations.append(field)
            if field["part"] == "word/document.xml":
                for key in keys:
                    first_seen.setdefault(key, len(first_seen) + 1)
                shown = re.fullmatch(r"\[(\d+)\]", field["display"])
                if len(keys) == 1 and shown:
                    expected = f"[{first_seen[keys[0]]}]"
                    displays = [field["display"], props.get("plainCitation"), props.get("formattedCitation")]
                    if any(value is not None and value != expected for value in displays):
                        sequence_mismatches.append({"paragraph": field["paragraph"], "expected": expected, "displays": displays})
        elif "ZOTERO_BIBL" in instr:
            bibliographies.append(field)

    unique = {key for field in citations for key in field["identities"]}
    refs = visible_references(roots["word/document.xml"])
    id_counts = Counter(citation_ids)
    return {
        "docx": str(path), "checked_at": datetime.now(timezone.utc).isoformat(),
        "zotero_item_fields": len(citations), "zotero_bibl_fields": len(bibliographies),
        "multi_item_fields": sum(f["item_count"] > 1 for f in citations),
        "empty_display_fields": sum(not f["display"] for f in citations),
        "json_parse_failures": sum(not f["json_parse_ok"] for f in citations),
        "invalid_citation_item_payloads": sum(not f["citation_items_valid"] for f in citations),
        "unclosed_zotero_fields": sum(not f["complete"] for f in citations + bibliographies),
        "unique_cited_items": len(unique), "visible_numbered_references": len(refs),
        "document_preferences_present": preferences,
        "duplicate_citation_ids": sorted(key for key, count in id_counts.items() if count > 1),
        "numbered_sequence_mismatches": sequence_mismatches,
        "visible_references": refs, "citation_fields": citations, "bibliography_fields": bibliographies,
        "warnings": warnings, "live_refresh_verified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    report = inspect_docx(args.docx)
    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "zotero-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {k: v for k, v in report.items() if k not in {
        "citation_fields", "bibliography_fields", "visible_references", "docx", "checked_at"
    }}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
