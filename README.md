# Cascade

**AI-native coordination for multi-service development.**

Your AI coding agent works great inside one repo. But when a field rename needs to flow through 8 services, 3 SDKs, and an API contract — it falls apart. Cascade fixes that.

## What it does

One orchestrator session coordinates changes across all your services:

```
You: "Rename role to account_type across all services"
Cascade: plans → implements upstream first → syncs contracts → propagates downstream → verifies zero stale refs
```

## Install

```
/plugin install cascade
```

## Quick start

```bash
# In your multi-service project root:
/cascade-init

# Then just describe what you want:
"Add a phone field to users and propagate to all services"
"Rename role to account_type everywhere"
"Add rate limiting headers to all 6 services"
```

## How it works

Cascade uses 5 specialized agents coordinated by an orchestrator:

```
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │ (dependency-aware │
                    │   coordination)  │
                    └───┬───┬───┬───┬──┘
                        │   │   │   │
              ┌─────────┘   │   │   └─────────┐
              │             │   │             │
        ┌─────▼────┐  ┌────▼───▼───┐  ┌──────▼─────┐
        │ Planner  │  │  Worker    │  │  Verifier  │
        │(analyze, │  │(implement, │  │(check stale│
        │ plan)    │  │ TDD, commit│  │ refs, sync)│
        └──────────┘  └────┬───────┘  └────────────┘
                           │
                    ┌──────▼──────┐
                    │ Contracts   │
                    │(sync APIs   │
                    │ after each) │
                    └─────────────┘
```

### The workflow

1. **Plan** — Analyzes which services are affected and in what order
2. **Implement** — Modifies one service at a time, following dependency order
3. **Sync contracts** — Updates API contracts after each service (not at the end)
4. **Verify** — Checks for stale references, contract mismatches, uncommitted changes
5. **Fix** — Addresses any verification failures and re-verifies

### Why dependency order matters

```
auth-service → catalog-service → order-service → notification-service
     ↑                                                      │
     └──────────────── gateway-api ◄────────────────────────┘
```

If you rename `role` to `account_type` in auth-service but update catalog-service first, catalog's code will reference a field that doesn't exist yet. Cascade enforces upstream-first ordering automatically.

## Test results

Tested against a 12-change gauntlet (including breaking renames, response restructuring, and cross-cutting middleware):

| Approach | Score | Time |
|----------|-------|------|
| **Cascade (meta-orchestrator)** | **24/24** | **24 min** |
| Agent Teams | ~17/24 | 35+ min |
| Per-service sessions | ~7/24 | 60+ min |

## Configuration

After running `/cascade-init`, a `cascade.yaml` file is created:

```yaml
version: "1.0"

services:
  auth-service:
    path: services/auth-service
    port: 9000
    entry: app.py
    depends_on: []

  order-service:
    path: services/order-service
    port: 9002
    entry: app.py
    depends_on: [auth-service, catalog-service]

contracts:
  path: contracts/api-contracts.yaml
  dependency_map: contracts/dependency-map.md
```

## Supported stacks

Cascade is stack-agnostic. It works with:
- **Python**: FastAPI, Flask, Django
- **JavaScript/TypeScript**: Express, Next.js, Nest.js
- **Go**: Standard library, Gin, Echo
- **Any language** with HTTP APIs and text-based source files

## Works with Superpowers

Cascade is complementary to [Superpowers](https://github.com/obra/superpowers):

| Tool | Scope | Use for |
|------|-------|---------|
| **Superpowers** | Single service | TDD, planning, code review within one repo |
| **Cascade** | Multi-service | Cross-cutting changes, contract sync, dependency coordination |

Install both — Superpowers handles the "how to write code" part, Cascade handles the "how to coordinate across services" part.

## Commands

| Command | Description |
|---------|-------------|
| `/cascade-init` | Initialize Cascade in your project |
| `/cascade-status` | Show service health, contract versions, uncommitted changes |

## License

MIT
