# Rate Limiter & Decision Engine

This project is a **real-time backend decision engine** that evaluates incoming API requests and decides whether they should be **allowed, throttled, or blocked** based on usage patterns and past behavior.

The focus is on **production-style backend logic**, not UI or CRUD APIs.

---

## What This System Does (Current)

At a high level, the system:

* Accepts API request metadata (tenant, route, method, etc.)
* Evaluates the request in real time
* Returns a clear decision:

  * `ALLOW`
  * `THROTTLE`
  * `BLOCK`
* Explains *why* the decision was made

All decisions are made in **milliseconds**, without hitting a database on the hot path.

---

## Core Flow

```
Request → Context → Decision Engine → Decision
```

1. A request hits the FastAPI endpoint
2. It is converted into an immutable `RequestContext`
3. The decision engine evaluates it
4. A decision is returned immediately

---

##  Implemented Features (So Far)

### 1. Real-Time Decision API

* `POST /v1/decision/check`
* Stateless FastAPI endpoint
* Clean and stable API contract

---

### 2. Sliding Window Rate Limiting

* True sliding window (not fixed window)
* Uses a ring buffer approach
* Fair across time boundaries
* Prevents burst abuse
* Redis-backed for shared state and horizontal scaling

---

### 3. Penalty Escalation (Finite State Machine)

Instead of blocking instantly, the system escalates penalties gradually:

```
NORMAL → WARN → THROTTLE → TEMP_BLOCK → BLOCK
```

* Penalties are applied only when rate limits are repeatedly exceeded
* Each penalty state has a TTL
* Clients are automatically forgiven after cooldowns
* Penalty state is stored in Redis

This mirrors how real systems like API gateways and WAFs handle abuse.

---

### 4. Explainable Decisions

Every response includes:

* The final action (`ALLOW`, `THROTTLE`, `BLOCK`)
* The reason for the decision
* The component that triggered it
* Optional retry timing

Example response:

```json
{
  "action": "BLOCK",
  "reason": "PENALTY_TEMP_BLOCK",
  "triggered_by": "PenaltyFSM",
  "retry_after": 60
}
```

---

### 5. No Database on the Hot Path

* No SQL
* No ORM
* No CRUD during request evaluation

All real-time logic uses in-memory processing + Redis for speed and safety.

---

## Tech Stack

* **Python**
* **FastAPI**
* **Redis**
* **Postman** (for testing)

---

## Upcoming Features

Planned next steps include:

* **Policy-driven rate limits**

  * Different limits per tenant
  * Different limits per route
  * Config-based behavior instead of hardcoded values

* **Decision logging**

  * Async logging to Postgres
  * Audit trail for decisions
  * Metrics and analytics support

* **Policy orchestration**

  * DAG-based execution of multiple rules
  * Early exits and explainable paths

* **Admin / Observability APIs**

  * Inspect current limits and penalties
  * View active penalty states

---

## Goal of This Project

The goal is to build a **production-style backend control plane** that demonstrates:

* Systems thinking
* State management
* Real-time decision making
* Abuse prevention patterns
* Clean architecture and extensibility


---

##  Running the Project

```bash
uvicorn app.main:app --reload
```

Test using Postman:

```
POST http://127.0.0.1:8000/v1/decision/check
```


