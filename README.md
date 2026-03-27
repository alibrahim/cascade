# Cascade

**AI-native coordination for multi-service development.**

Your AI coding agent works great inside one repo. But when a change needs to flow through multiple services, SDKs, and API contracts — it breaks down. Field names diverge. Contracts drift. Downstream services code against stale schemas. You end up manually coordinating what should be automatic.

Cascade fixes that. One orchestrator coordinates changes across all your services with dependency-aware propagation, automatic contract sync, and cross-service verification.

```
You: "Rename role to account_type across all services"

Cascade: plans the change → modifies auth-service first (upstream)
       → updates API contracts → propagates to catalog, order, notification
       → updates gateway + dashboard → verifies zero stale references
```

## The Problem

AI coding tools (Claude Code, Cursor, Copilot) work inside a single project. The moment you have interconnected services:

- **Session A** changes auth-service's API response shape
- **Session B** is still coding against the old shape in order-service
- **Session C** builds UI components against stale SDK types
- Nobody knows until something breaks in production

This is the coordination gap. Every team with microservices hits it.

## The Solution

Cascade is a Claude Code plugin that adds a multi-service orchestration layer. One session sees all your services and coordinates changes in the right order.

### 5 specialized agents

| Agent | Role |
|-------|------|
| **Planner** | Analyzes impact, maps every file that needs to change, writes a step-by-step plan |
| **Worker** | Implements code in one service at a time, follows TDD when tests exist |
| **Contracts** | Updates API contracts immediately after each service change — not at the end |
| **Verifier** | Checks for stale references, contract mismatches, uncommitted changes across all services |
| **Orchestrator** | Coordinates everything in dependency order: upstream first, then downstream |

### The workflow

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
        │          │  │            │  │            │
        └──────────┘  └────┬───────┘  └────────────┘
                           │
                    ┌──────▼──────┐
                    │ Contracts   │
                    └─────────────┘
```

1. **Plan** — Which services are affected? In what order?
2. **Implement** — One service at a time, upstream first
3. **Sync contracts** — After each service, not at the end
4. **Verify** — Grep for stale refs, check contract consistency, confirm commits
5. **Fix** — If verification fails, fix and re-verify

## Install

```
/plugin marketplace add alibrahim/cascade
/plugin install cascade@cascade
```

## Quick Start

```bash
# In your multi-service project root:
/cascade-init

# Then just describe what you want:
"Add a phone field to users and propagate to all services"
"Rename role to account_type everywhere"
"Add rate limiting headers to all services"
```

`/cascade-init` scans your project, detects services and their dependencies, and generates a `cascade.yaml` config. After that, any cross-service change request automatically activates the Cascade orchestrator.

## How We Got Here

Cascade emerged from a systematic comparison of three approaches to multi-service coordination:

**Approach A: Contract Guardian** — Each service gets its own Claude session with a sync-checker agent that reads shared contracts before/after work. Decentralized.

**Approach B: Meta-orchestrator** — One Claude session sits above all services with full visibility. Centralized.

**Approach C: Agent Teams** — Claude Code's experimental agent teams feature, where teammates work on different services and communicate via messaging.

We tested all three against a 12-change gauntlet that included breaking field renames, response restructuring, cross-cutting middleware, pagination, and new shared models:

| Approach | Score | Time | Key Issue |
|----------|-------|------|-----------|
| **B: Meta-orchestrator (Cascade)** | **24/24** | **24 min** | None |
| C: Agent Teams | ~17/24 | 35+ min | Coordination overhead burns turns |
| A: Per-service sessions | ~7/24 | 60+ min | Naming inconsistencies, 4x slower |

**Why the meta-orchestrator wins:** One session = consistent naming across all services. Dependency order enforced naturally. Contracts updated immediately. The verifier catches what self-evaluation misses.

Cascade is the productized version of Approach B, enhanced with planning (from [Superpowers](https://github.com/obra/superpowers)' methodology) and TDD.

## Configuration

After running `/cascade-init`, a `cascade.yaml` is created:

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

## Supported Stacks

Cascade is stack-agnostic. It works with any language that has HTTP APIs and text-based source files:

- **Python** — FastAPI, Flask, Django
- **JavaScript/TypeScript** — Express, Next.js, Nest.js
- **Go** — Standard library, Gin, Echo
- **Mixed stacks** — Python backend + TypeScript frontend? No problem.

## Works With Superpowers

Cascade is complementary to [Superpowers](https://github.com/obra/superpowers):

| Tool | Scope | Use for |
|------|-------|---------|
| **Superpowers** | Single service | TDD, planning, code review within one repo |
| **Cascade** | Multi-service | Cross-cutting changes, contract sync, dependency coordination |

Install both. Superpowers handles "how to write good code." Cascade handles "how to coordinate across services."

## Commands

| Command | Description |
|---------|-------------|
| `/cascade-init` | Scan services, detect dependencies, generate config |
| `/cascade-status` | Show service health, contract versions, uncommitted changes |

## Try It

The `examples/food-marketplace` directory contains a 6-service platform with 10 test changes (easy to hard) you can run to see Cascade in action.

## License

MIT
