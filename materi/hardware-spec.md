---
id: materi-infrastructure-spec
slug: /infrastructure/cto-spec
sidebar_label: CTO Infrastructure Specification
sidebar_position: 1
title: 'Materi – CTO-Level Hardware, Infrastructure & Systems Specification'
description: "A production-grade, AI-first infrastructure specification for Materi's real-time collaboration platform. Covers compute, networking, GPU strategy, MLOps, observability, and ADHD-optimized developer experience."
keywords:
    - infrastructure specification
    - AI company hardware
    - real-time collaboration infrastructure
    - GPU strategy
    - MLOps
    - distributed systems
    - CTO playbook
    - developer experience
authors:
    - name: Office of the CTO
tags:
    - infrastructure
    - hardware
    - mlops
    - platform
last_update:
    date: 2025-01-15
---

import TabItem from "@theme/TabItem";
import Tabs from "@theme/Tabs";

# Executive Summary

This document defines the **complete infrastructure specification** for Materi — a real-time collaboration platform built on event-driven microservices (Go, Rust, Python), operational transformation, and AI-augmented features.

This is not a wishlist. It's an **operational playbook** covering:

-   **Compute tiers** (developer workstations → GPU nodes → cloud elastic)
-   **Network architecture** (spine-leaf, RDMA, WebSocket routing)
-   **Data infrastructure** (PostgreSQL, Redis, object storage, feature stores)
-   **AI/ML operations** (training, inference, experiment tracking, eval gates)
-   **Observability** (metrics, traces, logs, cost attribution)
-   **Security posture** (zero-trust, secrets management, audit)
-   **Developer experience** (ADHD-optimized, friction-free onboarding)

The guiding principle: **If a developer has to think about the tool, the tool has failed.**

---

# 1. Compute Architecture

## 1.1 Compute Tiers Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Materi Compute Architecture                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Tier 0        │   │   Tier 1        │   │   Tier 2        │
│   Developer     │   │   Shared GPU    │   │   Production    │
│   Workstations  │   │   Cluster       │   │   Fleet         │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│ • Local dev     │   │ • Training jobs │   │ • API servers   │
│ • Unit tests    │   │ • Fine-tuning   │   │ • Collab nodes  │
│ • Small models  │   │ • Eval runs     │   │ • Inference     │
│ • IDE + tools   │   │ • Experiments   │   │ • Event buses   │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Tier 3            │
                    │   Cloud Elastic     │
                    ├─────────────────────┤
                    │ • Burst training    │
                    │ • Spot instances    │
                    │ • DR / failover     │
                    │ • Global edge       │
                    └─────────────────────┘
```

## 1.2 Developer Workstations (Tier 0)

### All Engineers

| Component    | Specification                             | Rationale                                               | URL                                                                                                                                                                                                                                                           |
| ------------ | ----------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Laptop**   | MacBook Pro 14" M3 Pro / ThinkPad P16s    | Unified memory for local inference, Linux kernel access | [Apple](https://www.apple.com/macbook-pro/) / [Lenovo](https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpadp/thinkpad-p16s-gen-2-(16-inch-amd)-mobile-workstation/len101t0075)                                                                            |
| **RAM**      | 32 GB minimum, 64 GB preferred            | Local model loading, container density                  | [Crucial](https://www.crucial.com/memory/ddr5/ct2k32g56c46s5)                                                                                                                                                                                                 |
| **Storage**  | 1 TB NVMe minimum                         | Monorepo + container images + model checkpoints         | [Samsung 990 Pro](https://semiconductor.samsung.com/consumer-storage/internal-ssd/990-pro/)                                                                                                                                                                   |
| **Display**  | 1× ultrawide 3440×1440 + 1× vertical 4K   | Context without fragmentation                           | [Dell U3425WE](https://www.dell.com/en-us/shop/dell-ultrasharp-34-curved-thunderbolt-hub-monitor-u3425we/apd/210-bmds/monitors-monitor-accessories)                                                                                                           |
| **Keyboard** | Mechanical, hot-swap preferred            | Ergonomics, personal preference                         | [Keychron Q1 Pro](https://www.keychron.com/products/keychron-q1-pro-qmk-via-wireless-custom-mechanical-keyboard)                                                                                                                                              |
| **Audio**    | ANC headphones (Sony WH-1000XM5 or equiv) | Deep work protection                                    | [Sony](https://electronics.sony.com/audio/headphones/headband/p/wh1000xm5-b)                                                                                                                                                                                  |

### Founding Engineer

| Component      | Specification                                 | Rationale                                         | URL                                                                                                                                                                                                                                                           |
| -------------- | --------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Laptop**     | MacBook Pro 16" M3 Max, 128 GB unified        | Local LLM inference (70B quantized), long battery | [Apple](https://www.apple.com/shop/buy-mac/macbook-pro/16-inch-m3-max)                                                                                                                                                                                        |
| **Secondary**  | Framework Laptop 16 (AMD)                     | Driver hacking, Linux kernel experiments          | [Framework](https://frame.work/products/laptop16-diy-amd-7040)                                                                                                                                                                                                |
| **Display**    | 49" ultrawide 5K2K + 27" vertical 4K          | Command center without cognitive overload         | [Samsung Odyssey G9](https://www.samsung.com/us/computing/monitors/gaming/49-odyssey-g9-gaming-monitor-lc49g95tssnxza/)                                                                                                                                       |
| **Portable**   | 16" OLED USB-C monitor                        | Travel-capable deep work                          | [ASUS ZenScreen](https://www.asus.com/us/displays-desktops/monitors/zenscreen/zenscreen-oled-mq16ah/)                                                                                                                                                         |
| **Input**      | Split ergo (ZSA Moonlander), trackball, Wacom | RSI prevention, diagramming                       | [ZSA](https://www.zsa.io/moonlander) / [Logitech MX Ergo](https://www.logitech.com/en-us/products/mice/mx-ergo-wireless-trackball-mouse.910-005178.html)                                                                                                      |
| **Automation** | Stream Deck XL                                | One-press context switches, env bootstraps        | [Elgato](https://www.elgato.com/us/en/p/stream-deck-xl)                                                                                                                                                                                                       |

### ML / Research Lead Augmentation

| Component     | Specification                             | Rationale                         | URL                                                                                                                                                                                                                                                           |
| ------------- | ----------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local GPU** | NVIDIA RTX 4090 or RTX 6000 Ada (desktop) | Iteration without cluster latency | [NVIDIA](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/)                                                                                                                                                                             |
| **RAM**       | 128 GB+ system memory                     | Large dataset preprocessing       | [G.SKILL](https://www.gskill.com/products/1/165/374/Trident-Z5-RGB-DDR5-Intel-XMP)                                                                                                                                                                            |
| **Storage**   | 4 TB NVMe + 8 TB SATA SSD                 | Model checkpoints, datasets       | [Samsung 990 Pro](https://semiconductor.samsung.com/consumer-storage/internal-ssd/990-pro/) / [Samsung 870 QVO](https://semiconductor.samsung.com/consumer-storage/internal-ssd/870qvo/)                                                                      |

---

# 2. GPU Infrastructure

## 2.1 Philosophy

**Local iteration, cluster training, cloud burst.**

-   Developers iterate locally on small models / subsets
-   Shared cluster handles real training jobs with proper tracking
-   Cloud provides elastic burst for large runs and spot arbitrage

## 2.2 On-Prem GPU Cluster

### Hardware Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                    GPU Cluster Topology                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Spine Switch (400G)                         │
│                    Mellanox SN4700                              │
└───────────┬─────────────────┬─────────────────┬─────────────────┘
            │                 │                 │
    ┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │  Leaf Switch  │ │  Leaf Switch  │ │  Leaf Switch  │
    │   (100G)      │ │   (100G)      │ │   (100G)      │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
    ┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
    │  GPU Node 1   │ │  GPU Node 2   │ │  GPU Node 3   │
    │  8× H100 SXM  │ │  8× H100 SXM  │ │  8× H100 SXM  │
    │  NVLink 4.0   │ │  NVLink 4.0   │ │  NVLink 4.0   │
    │  2 TB RAM     │ │  2 TB RAM     │ │  2 TB RAM     │
    │  30 TB NVMe   │ │  30 TB NVMe   │ │  30 TB NVMe   │
    └───────────────┘ └───────────────┘ └───────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  InfiniBand       │
                    │  400 Gbps NDR     │
                    │  (GPU-to-GPU)     │
                    └───────────────────┘
```

### Node Specifications

| Component        | Specification              | Quantity    |
| ---------------- | -------------------------- | ----------- |
| **GPU**          | NVIDIA H100 SXM 80GB       | 8 per node  |
| **Interconnect** | NVLink 4.0 (900 GB/s)      | Full mesh   |
| **Network**      | 400 Gbps InfiniBand NDR    | 2× per node |
| **CPU**          | AMD EPYC 9654 (96 cores)   | 2 per node  |
| **RAM**          | 2 TB DDR5-4800 ECC         | Per node    |
| **Storage**      | 30 TB NVMe (local scratch) | Per node    |
| **Nodes**        | 3 minimum (expandable)     |             |

### Job Orchestration

| Layer          | Tool                               | Purpose                          |
| -------------- | ---------------------------------- | -------------------------------- |
| **Scheduler**  | SLURM or Kubernetes + GPU Operator | Job queuing, resource allocation |
| **Multi-node** | PyTorch FSDP / DeepSpeed           | Distributed training             |
| **Experiment** | Weights & Biases                   | Tracking, hyperparameter sweeps  |
| **Artifacts**  | MLflow Model Registry              | Model versioning, staging        |

## 2.3 Cloud GPU Strategy

### Provider Matrix

| Provider        | Use Case                   | Instance Type      | Cost Strategy        |
| --------------- | -------------------------- | ------------------ | -------------------- |
| **AWS**         | Burst training             | p5.48xlarge (H100) | Spot + Savings Plans |
| **GCP**         | Inference, TPU experiments | a3-highgpu-8g      | Committed use        |
| **Lambda Labs** | Cost-sensitive training    | 8×H100             | On-demand            |
| **CoreWeave**   | Large-scale training       | HGX H100           | Reserved             |

### Cost Controls

-   **Per-experiment cost tagging** — every job tagged with experiment ID
-   **Idle GPU reaper** — terminate instances with &lt;10% utilization for 30 min
-   **Spot interruption handling** — checkpointing every 15 min
-   **Weekly cost review** — automated report to engineering leads

---

# 3. Data Infrastructure

## 3.1 Data Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Materi Data Architecture                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Operational   │   │   Analytical    │   │   ML-Specific   │
│   Data          │   │   Data          │   │   Data          │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│ PostgreSQL      │   │ ClickHouse      │   │ Feature Store   │
│ • Documents     │   │ • Events        │   │ • Feast         │
│ • Users         │   │ • Metrics       │   │ • Online/Offline│
│ • Permissions   │   │ • Audit logs    │   │                 │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│ Redis           │   │ Object Storage  │   │ Vector Store    │
│ • Sessions      │   │ • S3/MinIO      │   │ • pgvector      │
│ • Cache         │   │ • Checkpoints   │   │ • Embeddings    │
│ • Streams       │   │ • Datasets      │   │ • RAG index     │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Data Catalog      │
                    │   (DataHub/Amundsen)│
                    │   • Lineage         │
                    │   • Discovery       │
                    │   • Quality scores  │
                    └─────────────────────┘
```

## 3.2 Operational Databases

### PostgreSQL Configuration

| Parameter              | Value                                 | Rationale                               |
| ---------------------- | ------------------------------------- | --------------------------------------- |
| **Version**            | 16+                                   | JSONB improvements, logical replication |
| **Primary**            | 64 vCPU, 256 GB RAM, NVMe             | Headroom for OLTP spikes                |
| **Replicas**           | 2× read replicas                      | Shield service queries, analytics       |
| **Connection pooling** | PgBouncer (transaction mode)          | Connection efficiency                   |
| **Extensions**         | pgvector, pg_stat_statements, pg_cron | Embeddings, observability, scheduling   |

### Redis Configuration

| Cluster      | Purpose                    | Configuration                                |
| ------------ | -------------------------- | -------------------------------------------- |
| **Sessions** | Auth tokens, user sessions | 3-node cluster, persistence                  |
| **Cache**    | Permission cache, hot data | 3-node cluster, no persistence               |
| **Streams**  | Event bus (Redis Streams)  | 3-node cluster, persistence, consumer groups |

## 3.3 ML Data Infrastructure

### Dataset Versioning

| Tool           | Purpose                                      |
| -------------- | -------------------------------------------- |
| **DVC**        | Dataset versioning, pipeline reproducibility |
| **LakeFS**     | Git-like branching for data lakes            |
| **Delta Lake** | ACID transactions on object storage          |

### Feature Store

| Layer        | Tool            | Purpose                        |
| ------------ | --------------- | ------------------------------ |
| **Offline**  | Feast + Parquet | Training feature retrieval     |
| **Online**   | Feast + Redis   | Low-latency inference features |
| **Registry** | Feast registry  | Feature definitions, lineage   |

### Annotation Pipeline

| Stage         | Tool                         | Purpose                   |
| ------------- | ---------------------------- | ------------------------- |
| **Labeling**  | Label Studio (self-hosted)   | Human annotation          |
| **QA**        | Custom review UI             | Inter-annotator agreement |
| **Synthetic** | LLM-generated + human review | Data augmentation         |

---

# 4. Network Architecture

## 4.1 Core Network Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                    Network Architecture                         │
└─────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │   Internet      │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │   Edge / CDN    │
                         │   (Cloudflare)  │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │   Load Balancer │
                         │   (HAProxy)     │
                         │   • L7 routing  │
                         │   • WebSocket   │
                         │   • TLS term    │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
     │  API Service    │ │  Collab Service │ │  Shield Service │
     │  (Go/Fiber)     │ │  (Rust/Axum)    │ │  (Django)       │
     └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  Service Mesh   │
                         │  (Linkerd)      │
                         │  • mTLS         │
                         │  • Retries      │
                         │  • Observability│
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
     │  PostgreSQL     │ │  Redis Cluster  │ │  Object Storage │
     └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 4.2 Network Specifications

| Layer          | Technology          | Bandwidth | Purpose             |
| -------------- | ------------------- | --------- | ------------------- |
| **Spine**      | Mellanox SN4700     | 400 Gbps  | Core switching      |
| **Leaf**       | Mellanox SN3700     | 100 Gbps  | Rack switching      |
| **Server NIC** | Mellanox ConnectX-7 | 100 Gbps  | Server connectivity |
| **GPU Fabric** | InfiniBand NDR      | 400 Gbps  | GPU-to-GPU (RDMA)   |
| **Storage**    | NVMe-oF             | 100 Gbps  | Storage access      |

## 4.3 Protocol Stack

| Layer                  | Protocol           | Use Case               |
| ---------------------- | ------------------ | ---------------------- |
| **External API**       | HTTPS/2            | Client → Load balancer |
| **Real-time**          | WebSocket over TLS | Collaboration sessions |
| **Service-to-service** | gRPC + mTLS        | Internal APIs          |
| **Event streaming**    | Redis Streams      | Cross-service events   |
| **Data serialization** | Protocol Buffers   | Event schemas          |
| **Batch data**         | Apache Arrow       | In-memory analytics    |
| **Storage format**     | Parquet + ZSTD     | Columnar, compressed   |

## 4.4 WebSocket Routing

The Collaboration Service requires sticky sessions for OT consistency:

```
┌─────────────────────────────────────────────────────────────────┐
│                 WebSocket Routing Strategy                      │
└─────────────────────────────────────────────────────────────────┘

  Client                  HAProxy                 Collab Nodes
    │                        │                         │
    │── WS Upgrade ─────────▶│                         │
    │                        │── Hash(doc_id) ────────▶│
    │                        │                    Node selected
    │◀──────────────── WS Established ────────────────│
    │                        │                         │
    │── Operations ─────────▶│── Sticky (cookie) ─────▶│
    │                        │                         │
```

-   **Routing key**: Document ID hash
-   **Failover**: Session migration via Redis-backed state
-   **Health check**: `/health` endpoint, 5s interval

---

# 5. AI/ML Operations

## 5.1 Model Development Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    ML Development Lifecycle                     │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  Data   │───▶│ Train   │───▶│  Eval   │───▶│ Deploy  │
  │         │    │         │    │         │    │         │
  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ DVC     │    │ W&B     │    │ Eval    │    │ Model   │
  │ LakeFS  │    │ MLflow  │    │ Harness │    │ Registry│
  │         │    │         │    │         │    │         │
  └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

## 5.2 Experiment Tracking

| Aspect              | Tool             | Configuration                    |
| ------------------- | ---------------- | -------------------------------- |
| **Metrics**         | Weights & Biases | All training runs logged         |
| **Artifacts**       | MLflow           | Model checkpoints, datasets      |
| **Hyperparameters** | W&B Sweeps       | Bayesian optimization            |
| **Comparison**      | W&B Reports      | Experiment comparison dashboards |

### Mandatory Logging

Every training run **must** log:

-   Git commit SHA
-   Dataset version (DVC hash)
-   Full hyperparameter config
-   Hardware configuration
-   Training curves (loss, metrics)
-   Evaluation results
-   Model checkpoints (best + final)

## 5.3 Evaluation Infrastructure

### Offline Evaluation

| Eval Type      | Tool            | Gate Criteria              |
| -------------- | --------------- | -------------------------- |
| **Accuracy**   | Custom harness  | >baseline on held-out set  |
| **Latency**    | Benchmark suite | p99 < threshold            |
| **Regression** | A/B comparison  | No metric regression >1%   |
| **Safety**     | Red-team suite  | Pass all adversarial tests |

### Online Evaluation

| Strategy          | Implementation                     | Rollback Trigger            |
| ----------------- | ---------------------------------- | --------------------------- |
| **Shadow deploy** | Duplicate traffic, compare outputs | Manual review               |
| **Canary**        | 5% traffic, monitor metrics        | Auto-rollback on regression |
| **A/B test**      | Feature flag controlled            | Statistical significance    |

## 5.4 Model Serving

### Inference Stack

| Component         | Technology              | Purpose                       |
| ----------------- | ----------------------- | ----------------------------- |
| **Serving**       | vLLM / TensorRT-LLM     | High-throughput LLM inference |
| **Orchestration** | Triton Inference Server | Multi-model, batching         |
| **Gateway**       | Custom (Go)             | Auth, rate limiting, routing  |
| **Scaling**       | Kubernetes HPA          | GPU utilization based         |

### Latency SLOs

| Endpoint                    | p50        | p99        | Max     |
| --------------------------- | ---------- | ---------- | ------- |
| **Embeddings**              | 10ms       | 50ms       | 100ms   |
| **Completions (streaming)** | 100ms TTFT | 500ms TTFT | 1s TTFT |
| **Document analysis**       | 500ms      | 2s         | 5s      |

---

# 6. Observability

## 6.1 Observability Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observability Architecture                   │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │   Metrics   │  │   Traces    │  │    Logs     │
  │ Prometheus  │  │   Jaeger    │  │    Loki     │
  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                 ┌────────▼────────┐
                 │    Grafana      │
                 │  • Dashboards   │
                 │  • Alerting     │
                 │  • Correlation  │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │  AlertManager   │
                 │  → PagerDuty    │
                 │  → Slack        │
                 └─────────────────┘
```

## 6.2 Metrics

### Application Metrics

| Service             | Key Metrics                                          |
| ------------------- | ---------------------------------------------------- |
| **API (Go)**        | Request rate, latency histogram, error rate, DB pool |
| **Collab (Rust)**   | Active connections, ops/sec, OT latency, memory      |
| **Shield (Django)** | Auth rate, permission cache hit rate, audit volume   |
| **Inference**       | Tokens/sec, batch size, queue depth, GPU utilization |

### Infrastructure Metrics

| Component      | Key Metrics                                           |
| -------------- | ----------------------------------------------------- |
| **PostgreSQL** | Connections, query latency, replication lag, disk I/O |
| **Redis**      | Memory, hit rate, stream lag, connected clients       |
| **GPU nodes**  | GPU utilization, memory, temperature, power           |
| **Network**    | Bandwidth, packet loss, latency                       |

## 6.3 Distributed Tracing

| Aspect          | Implementation                      |
| --------------- | ----------------------------------- |
| **Protocol**    | OpenTelemetry (OTLP)                |
| **Backend**     | Jaeger                              |
| **Sampling**    | 100% errors, 10% success (adaptive) |
| **Propagation** | W3C Trace Context                   |

### Trace Requirements

Every service **must**:

-   Propagate trace context on all outbound calls
-   Create spans for DB queries, Redis ops, external calls
-   Add relevant attributes (user_id, doc_id, operation type)
-   Record errors with stack traces

## 6.4 Alerting

### Alert Tiers

| Tier            | Response Time     | Channel           | Example                               |
| --------------- | ----------------- | ----------------- | ------------------------------------- |
| **P1 Critical** | 5 min             | PagerDuty (phone) | Service down, data loss risk          |
| **P2 High**     | 30 min            | PagerDuty (push)  | Degraded performance, high error rate |
| **P3 Medium**   | 4 hours           | Slack             | Elevated latency, capacity warning    |
| **P4 Low**      | Next business day | Email             | Non-critical warnings                 |

---

# 7. Security

## 7.1 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Architecture                        │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   WAF / DDoS    │
                    │   (Cloudflare)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Zero Trust    │
                    │   Gateway       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
  ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐
  │   mTLS      │    │   RBAC        │   │   Secrets   │
  │   (Linkerd) │    │   (Shield)    │   │   (Vault)   │
  └─────────────┘    └───────────────┘   └─────────────┘
```

## 7.2 Authentication & Authorization

| Layer            | Mechanism               | Implementation        |
| ---------------- | ----------------------- | --------------------- |
| **User auth**    | JWT + refresh tokens    | Shield service        |
| **API auth**     | API keys (hashed)       | Shield service        |
| **Service auth** | mTLS                    | Linkerd               |
| **Database**     | Per-service credentials | Vault dynamic secrets |

## 7.3 Secrets Management

| Aspect              | Tool                  | Configuration           |
| ------------------- | --------------------- | ----------------------- |
| **Secrets store**   | HashiCorp Vault       | HA cluster, auto-unseal |
| **Dynamic secrets** | Vault database engine | PostgreSQL, Redis       |
| **Rotation**        | Vault lease renewal   | 24h TTL, auto-rotate    |
| **Injection**       | Vault Agent Sidecar   | Kubernetes integration  |

## 7.4 Compliance

| Requirement         | Implementation                                    |
| ------------------- | ------------------------------------------------- |
| **Audit logging**   | All auth events, data access, admin actions       |
| **Data encryption** | AES-256 at rest, TLS 1.3 in transit               |
| **PII handling**    | Tokenization, access controls, retention policies |
| **GDPR**            | Data export, deletion workflows, consent tracking |

---

# 8. Developer Experience

## 8.1 ADHD-Optimized Environment Design

### Principle: Reduce Context Switching at Every Layer

| Layer             | Implementation                           | Impact                           |
| ----------------- | ---------------------------------------- | -------------------------------- |
| **Onboarding**    | One-command dev setup (`make dev`)       | Zero-to-productive in &lt;1 hour |
| **Environment**   | Nix flakes for reproducibility           | "Works on my machine" eliminated |
| **Notifications** | Zero by default, opt-in channels         | Deep work protected              |
| **Dashboards**    | Now / Next / Later structure             | Priority always visible          |
| **Documentation** | Self-documenting systems, inline context | Answers before questions         |

### Development Workflow

```bash
# Clone and setup (one command)
git clone <repo> && cd materi && make dev

# What `make dev` does:
# 1. Checks Nix installation (installs if needed)
# 2. Enters Nix devshell (all tools available)
# 3. Pulls/builds containers
# 4. Starts local stack (Postgres, Redis, services)
# 5. Runs DB migrations
# 6. Opens browser to local dashboard
# 7. Tails logs in terminal

# Total time: <5 minutes on good connection
```

## 8.2 Local Development Stack

| Component           | Local Implementation               |
| ------------------- | ---------------------------------- |
| **Services**        | Docker Compose (all services)      |
| **Databases**       | PostgreSQL + Redis (containerized) |
| **Object storage**  | MinIO (S3-compatible)              |
| **Model inference** | Ollama (local LLMs)                |
| **Observability**   | Grafana + Prometheus (local)       |

## 8.3 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                               │
└─────────────────────────────────────────────────────────────────┘

  Push    ──▶  Lint/Format  ──▶  Unit Tests  ──▶  Integration
    │              │                 │                │
    │              │                 │                │
    ▼              ▼                 ▼                ▼
  ┌────┐      ┌────────┐       ┌─────────┐     ┌───────────┐
  │ PR │      │ < 30s  │       │ < 2 min │     │ < 10 min  │
  └────┘      └────────┘       └─────────┘     └─────────────┘
                                                      │
                                                      ▼
                              Build  ──▶  Deploy Staging  ──▶  Deploy Prod
                                │              │                   │
                                ▼              ▼                   ▼
                          ┌─────────┐   ┌───────────┐      ┌─────────────┐
                          │ < 5 min │   │ Auto      │      │ Manual gate │
                          └─────────┘   └───────────┘      └─────────────┘
```

### Pipeline Requirements

| Stage           | Tool                                | SLO                |
| --------------- | ----------------------------------- | ------------------ |
| **Lint**        | golangci-lint, clippy, ruff, eslint | &lt;30s            |
| **Unit tests**  | go test, cargo test, pytest         | &lt;2 min          |
| **Integration** | docker-compose + test harness       | &lt;10 min         |
| **Build**       | Nix (hermetic)                      | &lt;5 min (cached) |
| **Deploy**      | ArgoCD (GitOps)                     | &lt;5 min          |

## 8.4 Tooling Standards

| Category      | Tool                    | Rationale                         |
| ------------- | ----------------------- | --------------------------------- |
| **IDE**       | VS Code / Cursor / Zed  | Team choice, shared configs       |
| **Terminal**  | Warp / Alacritty + tmux | GPU-accelerated, scriptable       |
| **Knowledge** | Obsidian (local-first)  | Personal knowledge graphs         |
| **Tasks**     | Linear                  | Strict WIP limits, keyboard-first |
| **Docs**      | Docusaurus              | Versioned, searchable             |
| **Diagrams**  | Mermaid + Excalidraw    | Code-based + freeform             |

---

# 9. Capacity Planning

## 9.1 Growth Projections

| Metric                  | Current | 6 Month | 12 Month |
| ----------------------- | ------- | ------- | -------- |
| **DAU**                 | 10K     | 50K     | 200K     |
| **Concurrent sessions** | 1K      | 5K      | 20K      |
| **Documents**           | 100K    | 500K    | 2M       |
| **Events/day**          | 10M     | 50M     | 200M     |
| **Storage**             | 1 TB    | 5 TB    | 20 TB    |

## 9.2 Scaling Strategy

| Bottleneck                | Scaling Approach                         |
| ------------------------- | ---------------------------------------- |
| **API throughput**        | Horizontal pod scaling                   |
| **WebSocket connections** | Add Collab nodes, consistent hashing     |
| **Database reads**        | Read replicas, caching                   |
| **Database writes**       | Connection pooling, write batching       |
| **Event processing**      | Consumer group scaling                   |
| **Inference**             | GPU node addition, batching optimization |

---

# 10. Budget Framework

## 10.1 Investment Priorities

**Spend aggressively on:**

-   Developer productivity (time is the scarcest resource)
-   Compute locality (latency kills iteration speed)
-   Observability (you can't fix what you can't see)
-   Ergonomics (prevent burnout, RSI)
-   Security (breach cost >> prevention cost)

**Save aggressively on:**

-   Always-on cloud compute (use spot, right-size)
-   Over-centralized data lakes (start small, grow as needed)
-   Premature multi-region (solve it when you need it)
-   Enterprise software licenses (prefer open source)

## 10.2 Cost Attribution

Every resource **must** have:

-   **Team owner** — who's responsible
-   **Project tag** — what it's for
-   **Environment tag** — dev/staging/prod
-   **Experiment ID** — for ML workloads

Weekly automated reports to engineering leads. Monthly review with finance.

---

# 11. Disaster Recovery

## 11.1 Backup Strategy

| Data                   | RPO       | RTO     | Method                          |
| ---------------------- | --------- | ------- | ------------------------------- |
| **PostgreSQL**         | 1 hour    | 4 hours | WAL archiving + daily snapshots |
| **Redis (persistent)** | 1 hour    | 1 hour  | RDB snapshots to S3             |
| **Object storage**     | Real-time | 1 hour  | Cross-region replication        |
| **Model checkpoints**  | Real-time | 1 hour  | S3 versioning                   |

## 11.2 Failure Scenarios

| Scenario                | Detection             | Response                      |
| ----------------------- | --------------------- | ----------------------------- |
| **Single node failure** | Health checks         | Auto-restart, traffic reroute |
| **Database failure**    | Replication lag alert | Promote replica               |
| **Region failure**      | External monitoring   | Failover to DR region         |
| **Data corruption**     | Integrity checks      | Point-in-time recovery        |

---

# 12. Governance

## 12.1 Change Management

| Change Type         | Approval                 | Review             |
| ------------------- | ------------------------ | ------------------ |
| **Code**            | 1 peer review            | PR merge           |
| **Infrastructure**  | Terraform PR + 1 review  | GitOps apply       |
| **Database schema** | 2 reviews + DBA          | Migration pipeline |
| **Security config** | Security team + 1 review | Audited apply      |

## 12.2 Documentation Requirements

| Artifact                          | Owner             | Review Cadence |
| --------------------------------- | ----------------- | -------------- |
| **Architecture Decision Records** | Tech leads        | Per decision   |
| **Runbooks**                      | On-call engineers | Quarterly      |
| **API documentation**             | Service owners    | Per release    |
| **This spec**                     | CTO               | Quarterly      |

---

# Appendix A: Quick Reference

## Service Ports

| Service         | Port | Protocol  |
| --------------- | ---- | --------- |
| API (Go)        | 8080 | HTTP      |
| Collab (Rust)   | 8081 | HTTP + WS |
| Shield (Django) | 8082 | HTTP      |
| PostgreSQL      | 5432 | TCP       |
| Redis           | 6379 | TCP       |
| Prometheus      | 9090 | HTTP      |
| Grafana         | 3000 | HTTP      |

## Key Contacts

| Role               | Escalation Path    |
| ------------------ | ------------------ |
| **On-call**        | PagerDuty rotation |
| **Security**       | security@materi.io |
| **Infrastructure** | infra@materi.io    |
| **Data**           | data@materi.io     |

---

_This document is maintained by the Office of the CTO and reviewed quarterly._

_Last updated: 2025-01-15_
