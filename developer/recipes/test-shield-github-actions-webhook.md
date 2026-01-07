---
title: 'Test the Shield GitHub Actions webhook locally'
description: 'Send a signed workflow_run payload to Shield and confirm it queues processing'
---

This recipe helps you validate the Shield CI/CD webhook receiver end-to-end.
It is based on the implementation in `domain/shield/apps/cicd/webhooks.py`.

## Prerequisites

-   Shield running locally.
-   `GITHUB_WEBHOOK_SECRET` configured for the Shield service (this is what the code reads).

## 1) Confirm the health endpoint

By default, the GitHub Actions webhook routes are mounted under:

-   `GET /api/v1/webhooks/github-actions/health`

```bash
export SHIELD_BASE_URL="http://localhost:8000"
curl -sS "$SHIELD_BASE_URL/api/v1/webhooks/github-actions/health" | cat
```

If this does not return 200/healthy, check Shield routing and logs.

## 2) Send a signed workflow_run payload

Create a minimal payload (this is a small subset of what GitHub sends):

```bash
payload='{
  "action": "completed",
  "workflow_run": {
    "id": 123456,
    "run_number": 1,
    "status": "completed",
    "conclusion": "success",
    "head_branch": "main",
    "head_sha": "abc123",
    "html_url": "https://github.com/acme/app/actions/runs/123",
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T11:00:00Z",
    "actor": { "login": "developer1" },
    "name": "CI Pipeline",
    "workflow_id": 789,
    "run_attempt": 1,
    "event": "push"
  },
  "repository": {
    "full_name": "acme/app",
    "html_url": "https://github.com/acme/app"
  }
}'
```

Now sign and send it. This reuses the standard GitHub-style signature header.

import SendSigned from '/snippets/examples/webhooks/send-signed-webhook-bash.mdx'

<SendSigned />

Important: for GitHub Actions payloads, set these headers:

-   `X-GitHub-Event: workflow_run`
-   `X-GitHub-Delivery: <unique id>`

Update the snippet’s endpoint to:

-   `POST /api/v1/webhooks/github-actions/`

## Expected results

-   HTTP `202` with a JSON body indicating the event was queued.
-   Shield logs should show receipt of the delivery id and event type.

## Troubleshooting

-   `401 Invalid signature`: verify `GITHUB_WEBHOOK_SECRET` matches what you used to sign.
-   `400 Invalid JSON payload`: ensure the request body is valid JSON and sent with
    `Content-Type: application/json`.
