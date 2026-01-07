#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parents[1]
DOCS_JSON = ATLAS_ROOT / "docs.json"

MD_EXTS = [".mdx", ".md"]

# Basic markdown link: [text](target)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _page_to_file(page: str) -> Path | None:
    rel = Path(page)
    for ext in MD_EXTS:
        candidate = ATLAS_ROOT / f"{rel}{ext}"
        if candidate.exists():
            return candidate
    return None


def _load_docs_json_pages() -> list[str]:
    import json

    data = json.loads(DOCS_JSON.read_text(encoding="utf-8"))

    pages: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "pages" and isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            pages.append(item)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data.get("navigation", {}))

    seen: set[str] = set()
    out: list[str] = []
    for p in pages:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def _normalize_internal_target(target: str) -> str | None:
    """Return a docs page path (no leading slash, no fragment) or None if ignored."""

    target = target.strip().strip('"').strip("'")

    if not target:
        return None

    # Ignore code fences / weird markdown.
    if target.startswith("<"):
        return None

    # Ignore external links and mail.
    if target.startswith("http://") or target.startswith("https://"):
        return None
    if target.startswith("mailto:"):
        return None

    # Ignore pure fragments.
    if target.startswith("#"):
        return None

    # Only enforce absolute-site links like /customer/... (stable under Mintlify)
    if not target.startswith("/"):
        return None

    # Drop query/fragment.
    target = target.split("#", 1)[0].split("?", 1)[0]

    # Allow links to static assets.
    if target in {"/openapi/openapi.json", "/favicon.svg"}:
        return None

    # Snippets are not pages.
    if target.startswith("/snippets/"):
        return None

    # Normalize /foo/ -> foo
    page = target.lstrip("/")
    if page.endswith("/"):
        page = page[:-1]

    return page or None


def _check_file_links(file_path: Path, page: str) -> list[str]:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []

    for raw_target in MD_LINK_RE.findall(text):
        normalized = _normalize_internal_target(raw_target)
        if not normalized:
            continue

        # Allow direct file references (rare but possible)
        if (
            normalized.endswith(".json")
            or normalized.endswith(".png")
            or normalized.endswith(".svg")
        ):
            # Map to atlas root.
            candidate = ATLAS_ROOT / normalized
            if not candidate.exists():
                errors.append(f"{page}: broken asset link {raw_target}")
            continue

        if _page_to_file(normalized) is None:
            errors.append(f"{page}: broken internal link {raw_target}")

    return errors


def main() -> None:
    pages = _load_docs_json_pages()

    all_errors: list[str] = []

    for page in pages:
        file_path = _page_to_file(page)
        if file_path is None:
            # Missing pages are handled by docs_audit gate.
            continue
        all_errors.extend(_check_file_links(file_path, page))

    if all_errors:
        print("Broken links detected:")
        for e in all_errors[:200]:
            print(f"- {e}")
        if len(all_errors) > 200:
            print(f"... ({len(all_errors) - 200} more)")
        raise SystemExit(1)

    print("Link check passed.")


if __name__ == "__main__":
    main()
