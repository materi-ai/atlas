---
title: 'Verify webhook signatures (HMAC-SHA256)'
description: 'How to validate X-Hub-Signature-256 in webhook receivers (matches Shield)'
---

Materi uses GitHub-style webhook signatures in several places: a request body is signed with
HMAC-SHA256, and the signature is carried in the `X-Hub-Signature-256` header as:

-   `sha256=<hex>`

This recipe is aligned with the Shield implementation in `domain/shield/apps/cicd/webhooks.py`.

## Inputs

You need three pieces of data:

-   `payload_bytes`: the raw HTTP request body bytes (before JSON parsing)
-   `signature_header`: the header value from `X-Hub-Signature-256`
-   `secret`: the shared secret configured on both sides

## Python

import VerifyPython from '/snippets/examples/webhooks/verify-signature-python.mdx'

<VerifyPython />

## Node.js

import VerifyNode from '/snippets/examples/webhooks/verify-signature-node.mdx'

<VerifyNode />

## Receiver checklist

-   Reject missing/invalid signatures with `401`.
-   Verify against raw bytes.
-   Use constant-time comparison.
-   Log only high-level info (avoid logging secrets or full payloads in production).
