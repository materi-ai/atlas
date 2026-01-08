---
title: "Slack Integration"
description: "Get real-time notifications, collaborate on content, and manage approvals directly in Slack"
icon: "slack"
---

# Slack Integration

The Slack integration brings Materi notifications and collaboration directly into your team's communication hub. Receive alerts for document changes, manage approval workflows, and interact with your content without leaving Slack.

## Integration Flow

```mermaid
flowchart LR
    subgraph Materi
        Events[Event Bus]
        Formatter[Message Formatter]
    end

    subgraph Slack["Slack Workspace"]
        Bot[Materi Bot]
        Channel[Channels]
        DM[Direct Messages]
        Thread[Threads]
    end

    subgraph Actions["User Actions"]
        Approve[Approve]
        Reject[Reject]
        Comment[Comment]
        View[View in Materi]
    end

    Events --> Formatter
    Formatter --> Bot
    Bot --> Channel
    Bot --> DM
    Channel --> Thread

    Approve --> Bot
    Reject --> Bot
    Comment --> Bot
    View --> Bot
    Bot --> Events
```

## Features

<CardGroup cols={2}>
  <Card title="Real-time Notifications" icon="bell">
    Instant alerts for document updates, comments, mentions, and review requests.
  </Card>
  <Card title="Approval Workflows" icon="check-double">
    Review and approve content changes directly from Slack with interactive buttons.
  </Card>
  <Card title="Threaded Discussions" icon="comments">
    Keep conversations organized with automatic threading for document discussions.
  </Card>
  <Card title="Slash Commands" icon="terminal">
    Quick access to Materi features with `/materi` slash commands.
  </Card>
</CardGroup>

## Prerequisites

Before setting up the Slack integration, ensure you have:

- A Slack workspace with admin permissions (for app installation)
- Materi workspace with Admin role
- Appropriate channels created for notifications

## Setup Instructions

<Steps>
  <Step title="Navigate to Integrations">
    Go to **Settings > Integrations** in your Materi workspace and locate the Slack integration card.
  </Step>
  <Step title="Add to Slack">
    Click **Add to Slack** to begin the OAuth flow. You'll be redirected to Slack to authorize the Materi app.

    <Note>
    The Materi Slack app requests the following permissions:
    - Post messages to channels
    - Send direct messages
    - Use slash commands
    - Add shortcuts to messages
    </Note>
  </Step>
  <Step title="Select Default Channel">
    Choose a default channel for notifications. You can configure additional channel routing later.
  </Step>
  <Step title="Configure Notification Preferences">
    Set up which events trigger notifications and how they're routed to channels or users.
  </Step>
  <Step title="Test the Integration">
    Click **Send Test Message** to verify the integration is working. You should see a test message in your selected channel.
  </Step>
</Steps>

## Notification Configuration

<Tabs>
  <Tab title="Event Types">
    ### Available Notification Events

    | Event | Description | Default |
    |-------|-------------|---------|
    | `document.created` | New document created | On |
    | `document.updated` | Document content changed | Off |
    | `document.published` | Document published to production | On |
    | `document.deleted` | Document deleted | On |
    | `comment.created` | New comment added | On |
    | `comment.mentioned` | User mentioned in comment | On |
    | `review.requested` | Review requested for document | On |
    | `review.approved` | Document review approved | On |
    | `review.rejected` | Document review rejected | On |
    | `workspace.member_added` | New member joined workspace | Off |

    Configure in **Settings > Integrations > Slack > Notifications**.
  </Tab>

  <Tab title="Channel Routing">
    ### Route Events to Specific Channels

    Configure different channels for different event types or document categories:

    ```json
    {
      "channel_routing": {
        "default": "#documentation",
        "rules": [
          {
            "event": "review.requested",
            "channel": "#doc-reviews"
          },
          {
            "event": "document.published",
            "channel": "#releases"
          },
          {
            "document_path": "/API/*",
            "channel": "#api-docs"
          },
          {
            "document_label": "urgent",
            "channel": "#urgent-updates"
          }
        ]
      }
    }
    ```

    Rules are evaluated in order; the first matching rule determines the channel.
  </Tab>

  <Tab title="User Notifications">
    ### Direct Message Preferences

    Users can configure their personal notification preferences:

    | Preference | Options | Description |
    |------------|---------|-------------|
    | Mentions | DM, Channel, Both, None | When mentioned in comments |
    | Assignments | DM, Channel, Both, None | When assigned as reviewer |
    | Approvals | DM, Channel, Both, None | When review is approved/rejected |
    | Digest | Daily, Weekly, None | Summary of workspace activity |

    Users configure their preferences via `/materi preferences` or in Materi settings.
  </Tab>
</Tabs>

## Message Formats

### Document Update Notification

```
-----------------------------------------
📄 Document Updated

*Getting Started Guide* was updated by Jane Doe

Changes: Updated installation instructions, added troubleshooting section

[View Document] [View Diff] [Comment]
-----------------------------------------
```

### Review Request

```
-----------------------------------------
📋 Review Requested

Jane Doe requested your review on *API Authentication Guide*

Document: /API/Authentication
Priority: High
Due: Jan 20, 2024

[Approve] [Request Changes] [View Document]
-----------------------------------------
```

### Comment Notification

```
-----------------------------------------
💬 New Comment

John Smith commented on *Getting Started Guide*:

> "Should we add a section about environment variables?"

[Reply] [View Thread] [Resolve]
-----------------------------------------
```

## Slash Commands

The Materi Slack app provides several slash commands for quick access:

| Command | Description | Example |
|---------|-------------|---------|
| `/materi search <query>` | Search documents | `/materi search authentication` |
| `/materi recent` | Show recently updated docs | `/materi recent` |
| `/materi status` | Check integration status | `/materi status` |
| `/materi link <url>` | Link Slack channel to document | `/materi link https://app.materi.io/doc/123` |
| `/materi preferences` | Open notification preferences | `/materi preferences` |
| `/materi help` | Show available commands | `/materi help` |

### Search Results

```
-----------------------------------------
🔍 Search Results for "authentication"

1. *API Authentication Guide* - /API/Authentication
   Last updated: 2 days ago by Jane Doe

2. *OAuth Setup* - /Guides/OAuth-Setup
   Last updated: 1 week ago by John Smith

3. *SSO Configuration* - /Admin/SSO
   Last updated: 3 days ago by Admin

[Show More Results]
-----------------------------------------
```

## Interactive Features

<AccordionGroup>
  <Accordion title="Approval Workflows">
    When a review is requested, team members can approve or reject directly from Slack:

    1. Click **Approve** to approve the document
    2. Click **Request Changes** to open a dialog for feedback
    3. Approval status updates in real-time across Slack and Materi

    **Approval Dialog:**
    - Add optional comments with your approval
    - Request specific changes before approval
    - Delegate to another reviewer
  </Accordion>

  <Accordion title="Threaded Discussions">
    Comments on documents automatically create threaded conversations:

    - Each document discussion maintains its own thread
    - Replies in Slack threads sync to Materi comments
    - Use @mentions to notify specific team members
    - Mark threads as resolved when discussions conclude
  </Accordion>

  <Accordion title="Quick Actions">
    Message shortcuts provide quick access to common actions:

    - **Create Task** - Create a follow-up task from any message
    - **Link to Document** - Associate a message with a Materi document
    - **Share to Materi** - Add message content as a document comment

    Access via the message menu (three dots) > More actions > Materi.
  </Accordion>

  <Accordion title="Document Previews">
    When Materi links are shared in Slack, rich previews appear automatically:

    - Document title and description
    - Last updated timestamp and author
    - Quick action buttons (View, Edit, Share)
    - Preview of document content (first 200 characters)
  </Accordion>
</AccordionGroup>

## Enterprise Features

<Tabs>
  <Tab title="Slack Connect">
    ### Cross-Organization Collaboration

    Share Materi notifications with external partners via Slack Connect:

    1. Create a Slack Connect channel with your partner
    2. Configure Materi to post to the Connect channel
    3. External partners see notifications but cannot perform actions
    4. Optional: Grant external users limited Materi access for full interaction

    <Warning>
    Ensure your security policies allow sharing document information with external parties before enabling Slack Connect notifications.
    </Warning>
  </Tab>

  <Tab title="Enterprise Grid">
    ### Multi-Workspace Support

    For Slack Enterprise Grid organizations:

    - Install Materi app across all workspaces or selected workspaces
    - Configure workspace-specific notification routing
    - Unified administration through Materi admin console
    - Cross-workspace search and linking

    Contact enterprise@materi.io for Enterprise Grid setup assistance.
  </Tab>

  <Tab title="Compliance">
    ### Data Retention and Compliance

    | Feature | Description |
    |---------|-------------|
    | Message Retention | Follows your Slack retention policies |
    | Audit Logging | All interactions logged in Materi audit log |
    | DLP Integration | Compatible with Slack Enterprise DLP |
    | eDiscovery | Messages included in Slack eDiscovery exports |

    Materi does not store copies of Slack messages. All message content remains in Slack.
  </Tab>
</Tabs>

## Configuration Reference

### Environment Variables

```bash
# Slack App Configuration
SLACK_CLIENT_ID=your_client_id
SLACK_CLIENT_SECRET=your_client_secret
SLACK_SIGNING_SECRET=your_signing_secret
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Optional: Custom App Settings
SLACK_NOTIFICATION_RATE_LIMIT=100  # messages per minute
SLACK_UNFURL_ENABLED=true
SLACK_THREADING_ENABLED=true
```

### Webhook Payload (Internal)

Materi sends events to Slack using this internal format:

```json
{
  "channel": "C0123456789",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "📄 Document Updated"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Getting Started Guide* was updated by Jane Doe"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "View Document"},
          "url": "https://app.materi.io/doc/123"
        }
      ]
    }
  ],
  "metadata": {
    "event_type": "document.updated",
    "document_id": "doc_123",
    "workspace_id": "ws_456"
  }
}
```

## Troubleshooting

<AccordionGroup>
  <Accordion title="Messages Not Appearing">
    **Symptoms:** Notifications configured but not appearing in Slack.

    **Solutions:**
    1. Verify the Materi bot is invited to the target channel (`/invite @Materi`)
    2. Check channel permissions allow bot posting
    3. Review notification filters in Materi settings
    4. Verify the integration is still connected (re-authorize if needed)
  </Accordion>

  <Accordion title="Buttons Not Working">
    **Symptoms:** Clicking action buttons shows an error or does nothing.

    **Solutions:**
    1. Ensure you're logged into Materi in your browser
    2. Check if your Materi session has expired
    3. Verify you have permission for the action (e.g., reviewer role for approvals)
    4. Clear Slack cache and restart the app
  </Accordion>

  <Accordion title="Missing Slash Commands">
    **Symptoms:** `/materi` commands not recognized.

    **Solutions:**
    1. Verify the Materi app is installed in your workspace
    2. Check if slash commands are enabled for the channel
    3. Try in a direct message with Materi bot first
    4. Contact workspace admin to verify app permissions
  </Accordion>

  <Accordion title="Duplicate Notifications">
    **Symptoms:** Receiving the same notification multiple times.

    **Solutions:**
    1. Check for multiple channel routing rules matching the same event
    2. Verify you're not subscribed to both DM and channel for the same event
    3. Review if multiple team members have forwarding rules
    4. Check for webhook retry attempts in the delivery log
  </Accordion>
</AccordionGroup>

## Rate Limits

Slack imposes rate limits on incoming messages:

| Tier | Messages/Minute | Burst Limit |
|------|-----------------|-------------|
| Standard | 1 per second | 100 |
| Plus | 1 per second | 100 |
| Enterprise | Higher limits | Contact Slack |

<Note>
Materi automatically queues and batches notifications to stay within Slack rate limits. During high-activity periods, some notifications may be delayed or consolidated.
</Note>

## Best Practices

<Tip>
**Use Dedicated Channels:** Create separate channels for different notification types (e.g., #doc-reviews, #doc-updates) to keep discussions organized.
</Tip>

<Tip>
**Enable Threading:** Keep related discussions in threads to maintain channel readability and make conversations easier to follow.
</Tip>

<Tip>
**Configure Digest Mode:** For less urgent notifications, consider daily or weekly digests instead of real-time alerts to reduce notification fatigue.
</Tip>

<Warning>
**Avoid Sensitive Data:** Be mindful that document titles and preview content appear in Slack messages. Use appropriate channel permissions for sensitive documentation.
</Warning>

## Related Resources

- [Notifications Guide](/guides/notifications) - Managing all notification types
- [Approval Workflows](/guides/approvals) - Setting up content approval processes
- [Slack API Documentation](https://api.slack.com) - Official Slack documentation
