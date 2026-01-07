#!/usr/bin/env python3
"""
Check that all pages in docs.json are covered by an ownership rule in OWNERS.md.

Usage:
    python3 scripts/check_ownership.py         # Report mode
    python3 scripts/check_ownership.py --check # CI gate mode (exit non-zero if gaps)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parent.parent
DOCS_JSON = ATLAS_ROOT / "docs.json"
OWNERS_MD = ATLAS_ROOT / "OWNERS.md"


def extract_pages_from_docs_json() -> set[str]:
    """Extract all page paths from docs.json navigation."""
    data = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    pages: set[str] = set()

    def walk(obj):
        if isinstance(obj, dict):
            if "pages" in obj and isinstance(obj["pages"], list):
                for p in obj["pages"]:
                    if isinstance(p, str):
                        pages.add(p)
                    elif isinstance(p, dict):
                        walk(p)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data.get("navigation", {}))
    return pages


def extract_ownership_patterns() -> list[str]:
    """
    Extract ownership patterns from OWNERS.md.

    Patterns are extracted from table cells that look like paths with wildcards.
    e.g., `customer/overview/*` or `developer/domain/api/*`
    """
    content = OWNERS_MD.read_text(encoding="utf-8")
    patterns: list[str] = []

    # Parse markdown tables line by line
    for line in content.split("\n"):
        # Skip non-table lines and header separators
        if not line.startswith("|") or line.startswith("| ---") or "---" in line:
            continue

        # Split by | and get the first cell (after the leading |)
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 2:
            continue

        # First meaningful cell (index 1 because split creates empty string at start)
        candidate = cells[1].strip().strip("`")

        # Check if it looks like a path (contains / or is a known top-level page)
        if "/" in candidate or candidate in [
            "introduction",
            "quickstart",
            "development",
            "documentation-contract",
            "architecture-overview",
            "concepts",
        ]:
            # Skip header row labels
            if candidate.lower() in ["page", "section", "primary", "secondary", "team"]:
                continue
            patterns.append(candidate)

    return patterns


def page_matches_pattern(page: str, pattern: str) -> bool:
    """Check if a page matches an ownership pattern."""
    # Normalize escaped asterisks (from markdown formatting)
    pattern = pattern.replace("\\*", "*")

    if pattern.endswith("/*"):
        prefix = pattern[:-1]  # Remove the *
        return page.startswith(prefix)
    else:
        return page == pattern


def check_ownership_coverage(
    pages: set[str], patterns: list[str]
) -> tuple[set[str], set[str]]:
    """
    Check which pages are covered by ownership patterns.

    Returns (covered, uncovered) sets.
    """
    covered: set[str] = set()
    uncovered: set[str] = set()

    for page in pages:
        is_covered = False
        for pattern in patterns:
            if page_matches_pattern(page, pattern):
                is_covered = True
                break
        if is_covered:
            covered.add(page)
        else:
            uncovered.add(page)

    return covered, uncovered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that all docs pages have ownership defined."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any pages lack ownership coverage.",
    )
    args = parser.parse_args()

    if not OWNERS_MD.exists():
        print(f"OWNERS.md not found at {OWNERS_MD}")
        return 1

    pages = extract_pages_from_docs_json()
    patterns = extract_ownership_patterns()

    covered, uncovered = check_ownership_coverage(pages, patterns)

    print(f"Total pages in docs.json: {len(pages)}")
    print(f"Ownership patterns found: {len(patterns)}")
    print(f"Pages with ownership: {len(covered)}")
    print(f"Pages without ownership: {len(uncovered)}")

    if uncovered:
        print("\nPages missing ownership:")
        for page in sorted(uncovered):
            print(f"  - {page}")

    if args.check and uncovered:
        print("\nOwnership check failed. Add patterns to OWNERS.md.")
        return 1

    if not uncovered:
        print("\nAll pages have ownership defined.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
