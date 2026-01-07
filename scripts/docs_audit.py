#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_JSON = REPO_ROOT / "docs.json"

MD_EXTS = [".mdx", ".md"]

STUB_MARKERS_RE = re.compile(
    r"\b(stub( file)?|todo|tbd|placeholder)\b",
    re.IGNORECASE,
)


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in MD_EXTS:
            continue

        parts = set(path.parts)
        if ".git" in parts or "node_modules" in parts or "__ignore__" in parts:
            continue
        yield path


def _page_to_file(page: str) -> Path | None:
    rel = Path(page)
    for ext in MD_EXTS:
        candidate = REPO_ROOT / f"{rel}{ext}"
        if candidate.exists():
            return candidate
    return None


@dataclass(frozen=True)
class PageAudit:
    page: str
    file: Path | None
    exists: bool
    is_stub: bool
    word_count: int
    nonempty_lines: int
    reason: str


def _audit_file(page: str, file_path: Path) -> PageAudit:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    first_chunk = "\n".join(lines[:40])

    stripped_lines = [ln.strip() for ln in lines]
    nonempty = [ln for ln in stripped_lines if ln]

    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text)

    is_stub = False
    reasons: list[str] = []

    if STUB_MARKERS_RE.search(first_chunk):
        is_stub = True
        reasons.append("stub-marker")

    if len(nonempty) < 18:
        is_stub = True
        reasons.append("too-short")

    if len(words) < 120:
        is_stub = True
        reasons.append("low-word-count")

    reason = ",".join(reasons) if reasons else "ok"

    return PageAudit(
        page=page,
        file=file_path,
        exists=True,
        is_stub=is_stub,
        word_count=len(words),
        nonempty_lines=len(nonempty),
        reason=reason,
    )


def _audit_page(page: str) -> PageAudit:
    file_path = _page_to_file(page)
    if file_path is None:
        return PageAudit(
            page=page,
            file=None,
            exists=False,
            is_stub=True,
            word_count=0,
            nonempty_lines=0,
            reason="missing",
        )
    return _audit_file(page, file_path)


def _load_docs_json_pages(docs_json_path: Path) -> list[str]:
    data = json.loads(docs_json_path.read_text(encoding="utf-8"))

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

    # De-duplicate but preserve order
    seen: set[str] = set()
    out: list[str] = []
    for p in pages:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def _load_docs_json_page_locations(docs_json_path: Path) -> dict[str, tuple[str, str]]:
    """Return page -> (tab, group) for pages present in docs.json navigation."""
    data = json.loads(docs_json_path.read_text(encoding="utf-8"))
    locations: dict[str, tuple[str, str]] = {}

    nav = data.get("navigation", {})
    tabs = nav.get("tabs", []) if isinstance(nav, dict) else []
    for tab in tabs:
        if not isinstance(tab, dict):
            continue
        tab_name = str(tab.get("tab", "(unknown tab)"))
        for group in tab.get("groups", []) or []:
            if not isinstance(group, dict):
                continue
            group_name = str(group.get("group", "(unknown group)"))
            for page in group.get("pages", []) or []:
                if isinstance(page, str) and page not in locations:
                    locations[page] = (tab_name, group_name)

    return locations


def _section_weight(page: str) -> int:
    if page in {"introduction", "quickstart", "architecture-overview", "concepts"}:
        return 100
    if page.startswith("customer/"):
        return 70
    if page.startswith("developer/"):
        return 80
    if page.startswith("enterprise/"):
        return 60
    if page.startswith("internal/"):
        return 40
    return 50


def _topic_boost(page: str) -> int:
    base = 0
    name = page.split("/")[-1]
    if name in {"overview", "getting-started", "architecture", "setup"}:
        base += 20
    if "authentication" in page or "auth" in page:
        base += 10
    if "deployment" in page:
        base += 10
    if "testing" in page:
        base += 8
    if "security" in page:
        base += 8
    return base


def _priority_score(a: PageAudit) -> int:
    # Missing and stub pages should bubble to the top
    score = _section_weight(a.page) + _topic_boost(a.page)
    if not a.exists:
        score += 100
    if a.is_stub:
        score += 60
    return score


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace(os.sep, "/")


def _strip_ext(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    return str(rel.with_suffix("")).replace(os.sep, "/")


def _coverage_by_service(audits: list[PageAudit]) -> dict[str, dict[str, PageAudit]]:
    # Service key is derived from common patterns in docs.json page paths.
    # Examples:
    # - developer/domain/<service>/<topic>
    # - developer/platform/<service>/<topic>
    # - developer/products/<product>/<topic>
    out: dict[str, dict[str, PageAudit]] = {}

    for a in audits:
        parts = a.page.split("/")
        if len(parts) < 4:
            continue
        if parts[0] != "developer":
            continue

        category = parts[1]
        service = parts[2]
        topic = parts[3]

        key = f"developer/{category}/{service}"
        out.setdefault(key, {})[topic] = a

    return out


def generate_report() -> str:
    referenced_pages = _load_docs_json_pages(DOCS_JSON)
    locations = _load_docs_json_page_locations(DOCS_JSON)
    audits = [_audit_page(p) for p in referenced_pages]

    missing = [a for a in audits if not a.exists]
    stubs = [a for a in audits if a.exists and a.is_stub]
    ok = [a for a in audits if a.exists and not a.is_stub]

    all_md = list(_iter_markdown_files(REPO_ROOT))
    referenced_set = set(referenced_pages)
    orphan_files = [p for p in all_md if _strip_ext(p) not in referenced_set]

    orphan_audits: list[PageAudit] = []
    for p in orphan_files:
        orphan_audits.append(_audit_file(_strip_ext(p), p))

    orphan_stub_count = sum(1 for a in orphan_audits if a.is_stub)

    prioritized = sorted(
        [a for a in audits if (not a.exists) or a.is_stub],
        key=_priority_score,
        reverse=True,
    )

    svc = _coverage_by_service(audits)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    lines: list[str] = []
    lines.append("# Atlas Documentation Gap Report (TASKSET 1)")
    lines.append("")
    lines.append(f"Generated: `{now}`")
    lines.append(f"Source: `{_rel(DOCS_JSON)}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Referenced pages (docs.json): **{len(referenced_pages)}**")
    lines.append(f"- ✅ Non-stub pages: **{len(ok)}**")
    lines.append(
        f"- 🟨 Stub pages (existing but placeholder-quality): **{len(stubs)}**"
    )
    lines.append(f"- ❌ Missing pages (referenced but no file): **{len(missing)}**")
    lines.append(f"- Orphan markdown files (not in docs.json): **{len(orphan_files)}**")
    lines.append(f"- Orphan stubs: **{orphan_stub_count}**")
    lines.append("")

    lines.append("## Navigation breakdown (tab / group)")
    lines.append("")
    lines.append("| Tab | Group | Pages | ✅ OK | 🟨 Stub | ❌ Missing |")
    lines.append("|---|---|---:|---:|---:|---:|")

    by_group: dict[tuple[str, str], list[PageAudit]] = {}
    for a in audits:
        tab, group = locations.get(a.page, ("(unassigned)", "(unassigned)"))
        by_group.setdefault((tab, group), []).append(a)

    def _counts(items: list[PageAudit]) -> tuple[int, int, int]:
        ok_n = sum(1 for x in items if x.exists and not x.is_stub)
        stub_n = sum(1 for x in items if x.exists and x.is_stub)
        missing_n = sum(1 for x in items if not x.exists)
        return ok_n, stub_n, missing_n

    for (tab, group), items in sorted(
        by_group.items(), key=lambda kv: (kv[0][0], kv[0][1])
    ):
        ok_n, stub_n, missing_n = _counts(items)
        lines.append(
            f"| {tab} | {group} | {len(items)} | {ok_n} | {stub_n} | {missing_n} |"
        )

    lines.append("")

    lines.append("## Front-door pages")
    lines.append("")
    front_door = [
        "introduction",
        "quickstart",
        "architecture-overview",
        "concepts",
        "development",
        "documentation-contract",
    ]
    for page in front_door:
        a = _audit_page(page)
        if not a.exists:
            lines.append(f"- `{page}`: **missing**")
        elif a.is_stub:
            lines.append(f"- `{page}`: **stub** (`{a.reason}`)")
        else:
            lines.append(f"- `{page}`: **ok**")
    lines.append("")

    lines.append("## Highest-priority gaps (top 30)")
    lines.append("")
    lines.append("| Priority | Page | Status | Reason |")
    lines.append("|---:|---|---|---|")
    for a in prioritized[:30]:
        status = "missing" if not a.exists else "stub"
        lines.append(
            f"| {_priority_score(a)} | `{a.page}` | **{status}** | `{a.reason}` |"
        )
    lines.append("")

    lines.append("## Missing pages (referenced in docs.json)")
    lines.append("")
    if missing:
        for a in sorted(missing, key=lambda x: x.page):
            lines.append(f"- `{a.page}`")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Stub pages (referenced in docs.json)")
    lines.append("")
    if stubs:
        for a in sorted(stubs, key=lambda x: (_section_weight(x.page) * -1, x.page)):
            file_str = _rel(a.file) if a.file else "(missing)"
            lines.append(
                f"- `{a.page}` → `{file_str}` ({a.word_count} words; {a.nonempty_lines} nonempty lines; `{a.reason}`)"
            )
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Orphan files (not in docs.json)")
    lines.append("")
    lines.append(
        "These files may be intentionally unlinked (e.g., internal notes), but are included here to make the baseline auditable."
    )
    lines.append("")
    lines.append("| Path | Stub? | Reason |")
    lines.append("|---|---:|---|")
    for a in sorted(orphan_audits, key=lambda x: (not x.is_stub, x.page))[:80]:
        stub = "yes" if a.is_stub else "no"
        lines.append(f"| `{_rel(a.file)}` | {stub} | `{a.reason}` |")
    if len(orphan_audits) > 80:
        lines.append("")
        lines.append(f"(Truncated; total orphan files: {len(orphan_audits)})")
    lines.append("")

    lines.append("## Coverage matrix (Developer services)")
    lines.append("")
    lines.append(
        "This matrix is derived from the pages referenced in `docs.json` under `developer/*`. It highlights the minimum baseline of docs per service."
    )
    lines.append("")
    lines.append(
        "| Service | Has overview | Has architecture | Has setup | Has testing | Has deployment | Missing/stub topics |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---|")

    required = ["overview", "architecture", "setup", "testing", "deployment"]

    for service_key in sorted(svc.keys()):
        topics = svc[service_key]

        flags = []
        for req in required:
            a = topics.get(req)
            ok_flag = bool(a and a.exists and (not a.is_stub))
            flags.append("✅" if ok_flag else "❌")

        missing_or_stub: list[str] = []
        for req in required:
            a = topics.get(req)
            if a is None:
                missing_or_stub.append(f"{req}:missing")
            elif (not a.exists) or a.is_stub:
                missing_or_stub.append(f"{req}:{'missing' if not a.exists else 'stub'}")

        # Also surface additional stubbed topics beyond the core set
        for topic, a in sorted(topics.items()):
            if topic in required:
                continue
            if (not a.exists) or a.is_stub:
                missing_or_stub.append(
                    f"{topic}:{'missing' if not a.exists else 'stub'}"
                )

        lines.append(
            f"| `{service_key}` | {flags[0]} | {flags[1]} | {flags[2]} | {flags[3]} | {flags[4]} | {', '.join(missing_or_stub) if missing_or_stub else ''} |"
        )

    lines.append("")
    lines.append("## Notes / next actions")
    lines.append("")
    lines.append(
        "- TASKSET 2 should not restructure navigation until the top-priority missing/stub pages are agreed (front door first)."
    )
    lines.append(
        "- TASKSET 3 should focus on automating references (OpenAPI/events/proto) to reduce drift before large-scale narrative writing."
    )

    return "\n".join(lines)


def _required_pages_for_gate(referenced_pages: list[str]) -> list[str]:
    """Pages that must never be stub/missing.

    This keeps the docs permanently "documentation-ready" even while the wider
    site still contains stubs.
    """

    required: set[str] = {
        # Front door (getting started)
        "introduction",
        "quickstart",
        "architecture-overview",
        "concepts",
        "development",
        "documentation-contract",
    }

    for page in referenced_pages:
        if page.startswith("developer/contributing/"):
            required.add(page)
        if page.startswith("developer/recipes/"):
            required.add(page)

    return sorted(required)


def _run_gate() -> int:
    referenced_pages = _load_docs_json_pages(DOCS_JSON)
    audits = [_audit_page(p) for p in referenced_pages]

    missing = [a for a in audits if not a.exists]
    required_pages = _required_pages_for_gate(referenced_pages)
    required_audits = {a.page: a for a in audits if a.page in set(required_pages)}

    required_missing = [p for p in required_pages if p not in required_audits]
    required_stub = [a for a in required_audits.values() if a.is_stub]

    if missing or required_missing or required_stub:
        print("Docs gate failed.")
        if missing:
            print(f"- Missing pages referenced by docs.json: {len(missing)}")
            for a in missing[:50]:
                print(f"  - {a.page}")
            if len(missing) > 50:
                print(f"  ... ({len(missing) - 50} more)")

        if required_missing:
            print(f"- Missing required pages: {len(required_missing)}")
            for p in required_missing:
                print(f"  - {p}")

        if required_stub:
            print(f"- Required pages flagged as stub: {len(required_stub)}")
            for a in required_stub:
                print(f"  - {a.page} ({a.reason})")

        return 1

    print("Docs gate passed.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit docs.json references for missing/stub pages"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail (exit 1) if docs gate conditions are not met (CI use).",
    )
    args = parser.parse_args()

    if args.check:
        raise SystemExit(_run_gate())

    report = generate_report()
    out_path = REPO_ROOT / "docs" / "TASKSET_1_GAP_MAP.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report + "\n", encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
