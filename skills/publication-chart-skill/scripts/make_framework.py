#!/usr/bin/env python3
"""Generate an editable row-based SVG framework from a small JSON specification."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import ImageFont


SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def element(parent: ET.Element, name: str, **attrs) -> ET.Element:
    return ET.SubElement(parent, f"{{{SVG}}}{name}", {k.replace("_", "-"): str(v) for k, v in attrs.items()})


def find_font(explicit: str | None) -> str:
    choices = [explicit] if explicit else [
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf",
    ]
    for candidate in choices:
        try:
            ImageFont.truetype(candidate, 24)
            return candidate
        except OSError:
            continue
    raise ValueError("No measurable font found; supply --font /path/to/font.ttf")


def wrap(text: str, font, width: float) -> list[str]:
    result = []
    for raw in text.splitlines():
        if not raw:
            result.append("")
            continue
        # Preserve normal word boundaries; break long tokens and CJK at glyph boundaries.
        words = raw.split(" ")
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if font.getlength(candidate) <= width:
                line = candidate
                continue
            if line:
                result.append(line)
                line = ""
            for glyph in word:
                if line and font.getlength(line + glyph) > width:
                    result.append(line)
                    line = ""
                line += glyph
        if line:
            result.append(line)
    return result


def fit(title: str, body: str, width: float, height: float, font_path: str) -> dict:
    inner_w, inner_h = width - 32, height - 24
    for size in range(44, 19, -1):
        font = ImageFont.truetype(font_path, size)
        body_font = ImageFont.truetype(font_path, max(18, int(size * 0.80)))
        lines = [(t, font, True) for t in wrap(title, font, inner_w * 0.88)]
        lines += [(t, body_font, False) for t in wrap(body, body_font, inner_w * 0.88)]
        metrics = []
        for text, line_font, bold in lines:
            bbox = line_font.getbbox(text or "Ag", anchor="ls")
            metrics.append((text, line_font, bold, bbox))
        glyph_heights = [bbox[3] - bbox[1] for _, _, _, bbox in metrics]
        total_h = sum(glyph_heights) + max(0, len(lines) - 1) * size * 0.25
        widest = max((bbox[2] - bbox[0] for _, _, _, bbox in metrics), default=0)
        if total_h <= inner_h * 0.90 and widest <= inner_w * 0.90:
            return {"metrics": metrics, "height": total_h, "gap": size * 0.25,
                    "occupancy": max(widest / inner_w, total_h / inner_h)}
    raise ValueError(f"Text does not fit: {title!r}. Shorten labels or increase row_height.")


def render(spec: dict, font_path: str) -> tuple[bytes, dict]:
    width = float(spec.get("width", 1600))
    row_height = float(spec.get("row_height", 175))
    rows = spec.get("rows")
    if not isinstance(rows, list) or not rows or any(not isinstance(row, list) or not row for row in rows):
        raise ValueError("rows must be a non-empty list of non-empty node lists")
    if not math.isfinite(width) or not math.isfinite(row_height) or width < 600 or row_height < 100:
        raise ValueError("width must be >=600 and row_height >=100, both finite")
    if any(len(row) > 4 for row in rows):
        raise ValueError("Use at most four nodes per row; use a tailored SVG for denser structures")
    margin, gap, row_gap, top = 40.0, 40.0, 100.0, 100.0
    height = top + len(rows) * row_height + (len(rows) - 1) * row_gap + margin
    root = ET.Element(f"{{{SVG}}}svg", {"width": str(width), "height": str(height),
        "viewBox": f"0 0 {width:g} {height:g}", "role": "img"})
    element(root, "title").text = str(spec.get("title", "Research framework"))
    defs = element(root, "defs")
    marker = element(defs, "marker", id="arrow", markerWidth=10, markerHeight=10, refX=9, refY=5, orient="auto")
    element(marker, "path", d="M0,0 L9,5 L0,10 Z", fill="#222")
    element(root, "rect", width=width, height=height, fill="white")
    family = ImageFont.truetype(font_path, 24).getname()[0]
    title = element(root, "text", x=width / 2, y=48, text_anchor="middle", font_family=family, font_size=30, fill="#111")
    title.text = str(spec.get("title", "Research framework"))
    title_font = ImageFont.truetype(font_path, 30)
    if title_font.getlength(title.text) > width - 2 * margin:
        raise ValueError("Figure title exceeds canvas width; shorten it")
    boxes = {}
    fitted = {}
    for ri, row in enumerate(rows):
        box_width = (width - 2 * margin - (len(row) - 1) * gap) / len(row)
        for ci, node in enumerate(row):
            key = str(node["id"])
            if key in boxes:
                raise ValueError(f"Duplicate node id: {key}")
            x, y = margin + ci * (box_width + gap), top + ri * (row_height + row_gap)
            boxes[key] = {"x": x, "y": y, "width": box_width, "height": row_height, "row": ri}
            fitted[key] = fit(str(node["title"]), str(node.get("body", "")), box_width, row_height, font_path)

    # Mid-gap lanes keep adjacent-row connectors out of node interiors.
    edges = spec.get("edges", [])
    pairs = set()
    lane_counts = {}
    for source, target in edges:
        if source not in boxes or target not in boxes:
            raise ValueError(f"Unknown edge: {source} -> {target}")
        if boxes[target]["row"] != boxes[source]["row"] + 1:
            raise ValueError("Helper supports edges between adjacent rows only; use a tailored SVG for feedback")
        if (source, target) in pairs:
            raise ValueError(f"Duplicate edge: {source} -> {target}")
        pairs.add((source, target))
        ri = boxes[source]["row"]
        lane_counts[ri] = lane_counts.get(ri, 0) + 1
    used_lanes = {}
    for source, target in edges:
        a, b = boxes[source], boxes[target]
        ri = a["row"]
        used_lanes[ri] = used_lanes.get(ri, 0) + 1
        lane_y = a["y"] + row_height + row_gap * used_lanes[ri] / (lane_counts[ri] + 1)
        x1, y1, x2, y2 = a["x"] + a["width"] / 2, a["y"] + row_height, b["x"] + b["width"] / 2, b["y"]
        element(root, "path", d=f"M{x1:g},{y1:g} V{lane_y:g} H{x2:g} V{y2:g}", fill="none", stroke="#222",
                stroke_width=2.2, marker_end="url(#arrow)")
    for row in rows:
        for node in row:
            key = str(node["id"])
            box, layout = boxes[key], fitted[key]
            group = element(root, "g", id=key)
            element(group, "rect", x=box["x"], y=box["y"], width=box["width"], height=row_height,
                    rx=4, fill="#f7f7f7", stroke="#222", stroke_width=2)
            cursor = box["y"] + (row_height - layout["height"]) / 2
            for text, line_font, bold, bbox in layout["metrics"]:
                # Baseline compensates for the actual top glyph bearing.
                line = element(group, "text", x=box["x"] + box["width"] / 2,
                    y=round(cursor - bbox[1], 3), text_anchor="middle", font_family=family,
                    font_size=line_font.size, fill="#111")
                # Use the same measured face. Hierarchy comes from size, not unmeasured synthetic bold.
                line.text = text
                cursor += bbox[3] - bbox[1] + layout["gap"]
    report = {"width": width, "height": height, "font_family": family, "boxes": boxes,
        "node_count": len(boxes), "edge_count": len(edges),
        "text_occupancy": {key: round(value["occupancy"], 3) for key, value in fitted.items()},
        "fit_verified": True, "visual_review_required": True}
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--font")
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
    source, report = render(spec, find_font(args.font))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    svg = args.out_dir / "framework.svg"
    svg.write_bytes(source)
    if args.png:
        import cairosvg
        cairosvg.svg2png(bytestring=source, write_to=str(args.out_dir / "framework.png"))
    (args.out_dir / "layout-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"svg": str(svg), "node_count": report["node_count"], "fit_verified": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
