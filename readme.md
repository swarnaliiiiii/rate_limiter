# Devrate ⚡  
**Explainable, Distributed Rate Limiting & Decision Engine**

Devrate is a **production-grade rate limiting and abuse detection engine** designed for modern, multi-tenant systems.  
Unlike traditional rate limiters, Devrate focuses on **explainability**, **stateful decisions**, and **operator-first workflows** via a CLI.

---

## Why Devrate?

Most rate limiters answer only one question:

> ❌ *“Should this request be blocked?”*

Devrate answers three:

> ✅ *What decision was made?*  
> ✅ *Why was it made?*  
> ✅ *Which rule or signal triggered it?*

This makes Devrate ideal for:
- APIs with complex traffic patterns
- Fintech / auth / OTP flows
- Abuse-prone public endpoints
- Multi-tenant platforms

---

## Core Concepts

### 🔗 DAG-Based Decision Pipeline
Requests flow through a **Directed Acyclic Graph (DAG)** of decision nodes:
- Global limits
- Route-level limits
- User-level limits
- Abuse detection
- Penalty FSM

Each node can:
- Allow
- Throttle
- Block
- Escalate penalties

Execution short-circuits on terminal decisions.

---

### 🧠 Explainable Decisions
Every decision:
- Has a **Decision ID**
- Records **node-by-node execution**
- Can be replayed and inspected later

This is a first-class feature — not logs glued together.

---

### 🔐 Stateful Penalty FSM
Devrate supports **progressive penalties**:
- `ALLOW → WARN → THROTTLE → BLOCK`
- Automatic decay using TTL
- Escalation based on abuse signals

---

### ⚙️ Operator-First CLI
Devrate is **CLI-first**, not dashboard-first.

Operators can:
- Test decisions
- Inspect traces
- Debug production behavior
- Understand *why* traffic was blocked

---

## Architecture Overview

```

Request
│
▼
RequestContext
│
▼
Decision DAG
├─ Global Limit
├─ Route Limit
├─ User Limit
├─ Abuse Detection
└─ Penalty FSM
│
▼
Decision + Trace
│
├─ Redis (counters, penalties, traces)
└─ Async Logging

````

---

## API Endpoints

### Check a decision
```http
POST /v1/decision/check
````

**Request**

```json
{
  "tenant_id": "acme",
  "route": "/login",
  "method": "POST",
  "user_id": "u123"
}
```

**Response**

```json
{
  "decision_id": "d-9f2a3b1c",
  "action": "BLOCK",
  "reason": "burst_detected",
  "triggered_by": "abuse_check",
  "retry_after": 10
}
```

---

### Fetch decision trace

```http
GET /v1/decision/trace/{decision_id}
```

**Response**

```json
{
  "decision_id": "d-9f2a3b1c",
  "trace": [
    { "node": "global_limit", "result": "PASS", "latency_ms": 2 },
    { "node": "route_limit", "result": "PASS", "latency_ms": 1 },
    { "node": "abuse_check", "result": "FLAG" },
    { "node": "penalty_fsm", "result": "BLOCK" }
  ]
}
```

---

## CLI Usage

### Check a decision

```bash
devrate check \
  --tenant acme \
  --route /login \
  --method POST \
  --user u123
```

Output:

```
DECISION_ID : d-9f2a3b1c
ACTION      : BLOCK
REASON      : burst_detected
TRIGGERED   : abuse_check
```

---

### Inspect decision trace

```bash
devrate trace d-9f2a3b1c
```

Output:

```
✔ global_limit     PASS   (2ms)
✔ route_limit      PASS   (1ms)
⚠ abuse_check      FLAG
✖ penalty_fsm      BLOCK
```

---

## Tech Stack

* **Backend**: FastAPI
* **Rate Limiting**: Redis (sliding windows)
* **Config Storage**: PostgreSQL
* **CLI**: Typer + Rich
* **Tracing**: Redis (TTL-based)
* **Architecture**: DAG-based decision engine

---

## Design Principles

* Explainability over opacity
* Stateful decisions > static limits
* CLI-first observability
* Fail-safe defaults
* Multi-tenant by design

---

## Roadmap

* [ ] Inline trace output (`devrate check --trace`)
* [ ] Persistent trace storage (Postgres)
* [ ] Config management via CLI
* [ ] gRPC decision API
* [ ] Distributed executor support

---

## Status

🚧 **Active Development**
Core decision engine, DAG execution, CLI, and tracing are implemented.

