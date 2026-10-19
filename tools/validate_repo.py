#!/usr/bin/env python3
"""Validate packaged skill names, linked resources and distributable file types."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path) -> list[str]:
    errors = []
    blocked = {".doc", ".docx", ".pdf", ".sqlite", ".db", ".ris", ".bib", ".pptx", ".vsdx", ".xlsx"}
    for path in root.rglob("*"):
        if any(part in {".git", ".venv", "build", "dist", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if path.suffix.lower() in blocked:
            errors.append(f"Unreviewed document/data file: {rel}")
        if path.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            text = path.read_text(encoding="utf-8")
            # Match real user-home paths, not generic path placeholders.
            if re.search(r"[A-Z]:[/\\]Users[/\\](?!<|USER|your)[A-Za-z0-9_.-]+[/\\]", text):
                errors.append(f"Machine-specific user path: {rel}")
            if re.search(r"gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}", text):
                errors.append(f"Possible credential: {rel}")
            if path.suffix == ".py":
                try:
                    ast.parse(text, filename=rel)
                except SyntaxError as exc:
                    errors.append(str(exc))
            if path.suffix == ".json":
                try:
                    json.loads(text)
                except ValueError as exc:
                    errors.append(f"{rel}: {exc}")
            if path.suffix == ".md":
                for link in re.findall(r"\]\(([^)]+)\)", text):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = link.split("#", 1)[0]
                    if target and not (path.parent / target).exists():
                        errors.append(f"Broken link in {rel}: {target}")
    for skill in (root / "skills").iterdir():
        if not skill.is_dir():
            continue
        entry = skill / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing SKILL.md: {skill.name}")
            continue
        text = entry.read_text(encoding="utf-8")
        match = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n", text)
        if not match or match.group(1) != skill.name:
            errors.append(f"Invalid skill frontmatter: {skill.name}")
    return errors


if __name__ == "__main__":
    errors = validate(ROOT)
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    raise SystemExit(bool(errors))
