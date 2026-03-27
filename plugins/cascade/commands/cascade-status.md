---
name: cascade-status
description: Show the current state of Cascade orchestration. Displays service health, contract versions, uncommitted changes, and progress.
---

# Cascade Status

Show a quick overview of the multi-service project state.

## Process

1. **Read `cascade.yaml`** (or detect services manually)

2. **For each service**, check:
   - Git status (uncommitted changes?)
   - Latest commit message
   - Contract version

3. **Check contracts**:
   - Current version in `api-contracts.yaml`
   - Any mismatches between contract and code (quick grep)

4. **Read progress file** for current state

5. **Output a status table**:

```
Cascade Status
══════════════

Services:
  ✓ auth-service      v2.0.0  [clean]   "auth: rename role to account_type"
  ✓ catalog-service   v2.0.0  [clean]   "catalog: update vendor validation"
  ⚠ order-service     v3.0.0  [dirty]   "order: restructure OrderItem"
  ✓ notification-svc  v1.0.0  [clean]   "Initial notification-service"
  ✓ gateway-api       v1.0.0  [clean]   "Initial gateway-api"
  ✓ dashboard-ui      v1.0.0  [clean]   "Initial dashboard-ui"

Contracts: v3.0.0 (api-contracts.yaml)
Progress: Change 6 complete, Change 7 next

⚠ order-service has uncommitted changes
```
