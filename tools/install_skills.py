#!/usr/bin/env python3
"""Install skill folders without overwriting existing skills by default."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def install(source: Path, dest: Path, replace: bool = False, dry_run: bool = False) -> dict:
    source = source.resolve()
    target = dest.expanduser().resolve() / source.name
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Installation source and target must not overlap")
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"Not a skill folder: {source.name}")
    if target.is_symlink():
        raise ValueError(f"Refusing to replace a symlink: {target}")
    record = {"skill": source.name, "target": str(target), "dry_run": dry_run}
    if target.exists() and not replace:
        return {**record, "action": "skipped-existing"}
    if dry_run:
        return {**record, "action": "would-replace-with-backup" if target.exists() else "would-install"}
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f".{target.name}.install-{uuid.uuid4().hex}")
    shutil.copytree(source, staging, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    backup = None
    try:
        if target.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = target.with_name(f"{target.name}.backup-{stamp}")
            target.rename(backup)
        staging.rename(target)
    except Exception:
        if backup and not target.exists():
            backup.rename(target)
        raise
    return {**record, "action": "installed", "backup": str(backup) if backup else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills")
    choices = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    parser.add_argument("--skill", action="append", choices=choices)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    results = [install(ROOT / "skills" / name, args.dest, args.replace, args.dry_run) for name in args.skill or choices]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
