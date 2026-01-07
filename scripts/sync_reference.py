#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

ATLAS_ROOT = Path(__file__).resolve().parents[1]
# Monorepo root is the parent of `platform/`.
REPO_ROOT = ATLAS_ROOT.parents[1]

DEFAULT_OPENAPI_SOURCE = ATLAS_ROOT / "__ignore__" / "api-reference" / "openapi.json"
OPENAPI_DEST = ATLAS_ROOT / "openapi" / "openapi.json"

PROTO_ROOT = REPO_ROOT / "shared" / "proto"
SNIPPETS_DIR = ATLAS_ROOT / "snippets" / "generated"
PROTO_SNIPPET = SNIPPETS_DIR / "events-proto-summary.mdx"
SOURCES_MANIFEST = ATLAS_ROOT / "openapi" / "SOURCES.json"


@dataclass(frozen=True)
class SourceItem:
    kind: str
    source_path: Path
    dest_path: Path | None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    """Hash a file or directory deterministically.

    For directories, hashes the relative path + sha256 of each contained file.
    """
    if path.is_file():
        return sha256_file(path)

    if path.is_dir():
        h = hashlib.sha256()
        for p in sorted([p for p in path.rglob("*") if p.is_file()]):
            rel = p.relative_to(path).as_posix().encode("utf-8")
            h.update(rel)
            h.update(b"\0")
            h.update(sha256_file(p).encode("utf-8"))
            h.update(b"\n")
        return h.hexdigest()

    raise FileNotFoundError(str(path))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_if_changed(src: Path, dst: Path) -> bool:
    """Copy src -> dst if content differs. Returns True if dst changed."""
    if not src.exists():
        raise FileNotFoundError(str(src))

    ensure_dir(dst.parent)

    if dst.exists() and sha256_file(src) == sha256_file(dst):
        return False

    shutil.copyfile(src, dst)
    return True


MESSAGE_RE = re.compile(r"^\s*message\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{\s*$")


def extract_proto_messages(proto_text: str) -> list[str]:
    names: list[str] = []
    for line in proto_text.splitlines():
        m = MESSAGE_RE.match(line)
        if m:
            names.append(m.group("name"))
    return names


def generate_proto_snippet(proto_dir: Path) -> str:
    if not proto_dir.exists():
        return "## Event schemas (protobuf)\n\n" "Proto directory not found.\n"

    proto_files = sorted(p for p in proto_dir.glob("*.proto") if p.is_file())
    lines: list[str] = []

    lines.append("## Event schemas (protobuf)")
    lines.append("")
    lines.append(
        "This snippet is generated from the canonical protobuf files in `shared/proto`. "
        "It is intended to be embedded into event reference pages to prevent drift."
    )
    lines.append("")
    lines.append("### Sources")
    lines.append("")

    for p in proto_files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        lines.append(f"- `{rel}` (`sha256:{sha256_file(p)[:12]}`)")

    lines.append("")
    lines.append("### Message index")
    lines.append("")
    lines.append("| File | Messages |")
    lines.append("|---|---|")

    for p in proto_files:
        messages = extract_proto_messages(
            p.read_text(encoding="utf-8", errors="replace")
        )
        rel = p.relative_to(REPO_ROOT).as_posix()
        msg_str = ", ".join(f"`{m}`" for m in messages) if messages else "(none)"
        lines.append(f"| `{rel}` | {msg_str} |")

    lines.append("")
    return "\n".join(lines)


def build_sources_manifest(items: list[SourceItem]) -> dict:
    sources: list[dict] = []
    for it in items:
        sources.append(
            {
                "kind": it.kind,
                "source": (
                    it.source_path.relative_to(REPO_ROOT).as_posix()
                    if it.source_path.is_absolute()
                    and REPO_ROOT in it.source_path.parents
                    else str(it.source_path)
                ),
                "dest": (
                    it.dest_path.relative_to(ATLAS_ROOT).as_posix()
                    if it.dest_path
                    else None
                ),
                "sha256": (
                    sha256_path(it.source_path) if it.source_path.exists() else None
                ),
            }
        )
    return {
        "generated_by": "platform/atlas/scripts/sync_reference.py",
        "atlas_root": ATLAS_ROOT.as_posix(),
        "repo_root": REPO_ROOT.as_posix(),
        "sources": sources,
    }


def check_manifest_matches_expected(expected: dict) -> bool:
    if not SOURCES_MANIFEST.exists():
        return False
    try:
        current = json.loads(SOURCES_MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        return False

    # Ignore path fields that can vary across machines.
    for key in ["atlas_root", "repo_root"]:
        current.pop(key, None)
        expected.pop(key, None)

    return current == expected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync and verify reference sources (OpenAPI + protobuf event schemas) for Atlas docs."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not modify files; exit non-zero if output is out of sync.",
    )
    args = parser.parse_args()

    ensure_dir(SNIPPETS_DIR)
    ensure_dir(OPENAPI_DEST.parent)

    sources: list[SourceItem] = []

    # OpenAPI
    openapi_src = DEFAULT_OPENAPI_SOURCE
    sources.append(
        SourceItem(kind="openapi", source_path=openapi_src, dest_path=OPENAPI_DEST)
    )

    # Proto events
    sources.append(SourceItem(kind="proto", source_path=PROTO_ROOT, dest_path=None))

    if args.check:
        ok = True

        if not openapi_src.exists() or not OPENAPI_DEST.exists():
            ok = False
        elif sha256_file(openapi_src) != sha256_file(OPENAPI_DEST):
            ok = False

        expected_snippet = generate_proto_snippet(PROTO_ROOT)
        current_snippet = (
            PROTO_SNIPPET.read_text(encoding="utf-8") if PROTO_SNIPPET.exists() else ""
        )

        def _norm(s: str) -> str:
            return s.replace("\r\n", "\n").rstrip()

        if _norm(current_snippet) != _norm(expected_snippet):
            ok = False

        expected_manifest = build_sources_manifest(
            [
                SourceItem(
                    kind="openapi", source_path=openapi_src, dest_path=OPENAPI_DEST
                ),
                SourceItem(kind="proto", source_path=PROTO_ROOT, dest_path=None),
            ]
        )
        if not check_manifest_matches_expected(expected_manifest):
            ok = False

        if not ok:
            print(
                "Reference outputs are out of sync. Run: python3 scripts/sync_reference.py"
            )
            return 1

        print("Reference outputs are in sync.")
        return 0

    # Sync mode
    changed = False

    if copy_if_changed(openapi_src, OPENAPI_DEST):
        changed = True

    snippet = generate_proto_snippet(PROTO_ROOT)
    if (not PROTO_SNIPPET.exists()) or PROTO_SNIPPET.read_text(
        encoding="utf-8"
    ) != snippet:
        PROTO_SNIPPET.write_text(snippet + "\n", encoding="utf-8")
        changed = True

    manifest = build_sources_manifest(
        [
            SourceItem(kind="openapi", source_path=openapi_src, dest_path=OPENAPI_DEST),
            SourceItem(kind="proto", source_path=PROTO_ROOT, dest_path=None),
        ]
    )
    SOURCES_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Synced. Changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
