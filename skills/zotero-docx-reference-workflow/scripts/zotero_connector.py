#!/usr/bin/env python3
"""Probe or save explicit items using the local Zotero Desktop Connector."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener


def validate_base(base: str) -> str:
    parsed = urlparse(base)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Connector base must be an HTTP loopback URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
        raise ValueError("Connector base must contain only scheme, loopback host and optional port")
    return base.rstrip("/")


def load_items(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    items = value.get("items") if isinstance(value, dict) else value
    if not isinstance(items, list) or not items:
        raise ValueError("Expected a non-empty item array or an object containing items")
    if any(not isinstance(item, dict) or not item.get("itemType") or not item.get("title") for item in items):
        raise ValueError("Each item requires Zotero itemType and title")
    return items


def request(base: str, command: str, items: list[dict] | None = None) -> dict:
    payload = None
    headers = {"Zotero-API-Version": "3"}
    endpoint = "/connector/ping"
    if command == "save":
        endpoint = "/connector/saveItems"
        payload = json.dumps({"sessionID": str(uuid.uuid4()), "items": items}).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(validate_base(base) + endpoint, data=payload, headers=headers)
    # Local library requests must not be sent through an ambient HTTP proxy.
    with build_opener(ProxyHandler({})).open(req, timeout=20) as response:
        result = {"status": response.status, "body": response.read().decode("utf-8", "replace")}
    if command == "save":
        result.update({"submitted_items": len(items or []), "readback_verified": False,
                       "collection_membership_verified": False,
                       "next_step": "Read actual item identities and collection membership through Zotero."})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:23119")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ping")
    save = sub.add_parser("save", help="Write supplied item metadata into the running Zotero library")
    save.add_argument("items", type=Path)
    args = parser.parse_args()
    items = load_items(args.items) if args.command == "save" else None
    print(json.dumps(request(args.base, args.command, items), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
