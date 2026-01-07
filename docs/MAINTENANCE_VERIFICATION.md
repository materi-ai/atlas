# Atlas Docs Verification (TASKSET 7 & 8)

This document describes the verification gates that keep the Atlas docs permanently
"documentation-ready".

## What the gates check

### 1) Reference drift

Ensures generated reference artifacts (OpenAPI copy + protobuf summary snippet) are in sync with the
canonical sources.

From `platform/atlas`:

-   `python3 scripts/sync_reference.py --check`

### 2) Docs gate (no silent regression)

The docs repository still contains many stub pages while content is being expanded.
The docs gate is a **strict check on a protected set of pages** that must never regress back to
stub quality.

It fails if:

-   Any `docs.json` page is missing.
-   Any protected page is missing or flagged as stub.

Protected pages currently include:

-   Front door pages: `introduction`, `quickstart`, `architecture-overview`, `concepts`,
    `development`, `documentation-contract`
-   Developer contributing pages: `developer/contributing/*`
-   Developer recipes pages: `developer/recipes/*`

Run:

-   `python3 scripts/docs_audit.py --check`

### 3) Link check (broken internal links)

Validates that internal absolute links like `/customer/...` resolve to a docs page file.

Run:

-   `python3 scripts/check_links.py`

### 4) Ownership check (TASKSET 8)

Ensures every page in `docs.json` is covered by an ownership rule in `OWNERS.md`.

It fails if:

-   Any page lacks a matching ownership pattern.

Run:

-   `python3 scripts/check_ownership.py --check`

See `OWNERS.md` for the full ownership matrix and escalation paths.

## One-command local verification

From `platform/atlas`:

-   `npm run check:all`

## Deterministic local preview

Use the pinned Mintlify CLI:

-   `npm run dev`

This uses `npx -y mintlify@4.2.259 dev` so the preview behavior is consistent across machines.

## CI integration

A GitHub Actions workflow runs these checks on PRs that touch docs or schemas.
If any check fails, the PR should be treated as incomplete until fixed.
