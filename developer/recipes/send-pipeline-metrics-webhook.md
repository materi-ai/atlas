---
title: 'Send pipeline metrics to Shield'
description: 'Post a signed pipeline metrics payload to the Shield webhook endpoint'
---

Shield includes a pipeline metrics webhook endpoint designed for services to report CI/CD outcomes.
This recipe is aligned with `domain/shield/apps/cicd/webhooks.py`.

## Endpoint

-   `POST /api/v1/webhooks/pipeline-metrics/`
-   `GET /api/v1/webhooks/pipeline-metrics/` (health)

## Required fields (minimum)

The implementation requires:

-   `service`
-   `run_id`
-   `status`

Other fields (pipeline name, branch, stages, etc.) are supported and recommended.

## Example payload

```json
{
    "service": "manuscript",
    "pipeline": "msx-ci",
    "run_id": "123",
    "run_number": "42",
    "status": "success",
    "branch": "main",
    "commit_sha": "abc123def456",
    "triggered_by": "developer1",
    "event": "push",
    "repository": "acme/app",
    "workflow_url": "https://github.com/acme/app/actions/runs/123",
    "stages": {
        "build": "success",
        "test": "success"
    },
    "timestamp": "2026-01-07T00:00:00Z"
}
```

## Send it (signed)

Use the same signature header format as GitHub webhooks:

-   `X-Hub-Signature-256: sha256=<hex>`

import SendSigned from '/snippets/examples/webhooks/send-signed-webhook-bash.mdx'

<SendSigned />

Update the snippet as follows:

-   Set the endpoint to `POST /api/v1/webhooks/pipeline-metrics/`
-   Set `X-GitHub-Event: pipeline_metrics`
-   Set `X-GitHub-Delivery: <run_id>`

## Expected results

-   `202` or `200` JSON response indicating acceptance.
-   Metrics stored/forwarded according to Shield’s configuration.

## Common failures

-   `401 Invalid signature`: the secret doesn’t match `GITHUB_WEBHOOK_SECRET` in Shield.
-   `400 Missing required fields`: ensure `service`, `run_id`, and `status` are present.
