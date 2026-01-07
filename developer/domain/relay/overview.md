---
title: 'Relay service'
description: 'WebSocket collaboration engine (operations + presence)'
---

Relay provides real-time collaboration over WebSockets.

Treat Relay as the low-latency interaction surface: clients connect, establish session context, and
exchange collaboration operations and presence updates.

## Responsibilities

-   WebSocket session management
-   Concurrent editing coordination (operational transform)
-   Presence (cursor/selection) streaming
-   Event-driven synchronization with the rest of the system

## Interfaces

-   WebSocket protocol: message shapes, handshake, and lifecycle
-   Event consumption/production: integration with the broader event-driven system

## Related docs

-   [/concepts](/concepts) for collaboration primitives
-   [/developer/domain/relay/websocket-protocol](/developer/domain/relay/websocket-protocol) for protocol details

## Integration notes (baseline)

-   Design clients to reconnect and resubscribe safely.
-   Assume ordering guarantees are limited unless documented otherwise.
