# Food Marketplace Example

A 6-service food marketplace platform for trying Cascade hands-on.

## Services

| Service | Port | Role | Depends On |
|---------|------|------|------------|
| auth-service | 9000 | User management, validation | — |
| catalog-service | 9001 | Menu items, categories, search | auth |
| order-service | 9002 | Orders, lifecycle, stats | auth, catalog |
| notification-service | 9003 | User notifications | auth, order |
| gateway-api | 9004 | Aggregation gateway | all backends |
| dashboard-ui | 9005 | Web dashboard | gateway, auth, catalog |

## Try it

```bash
# 1. Clone and navigate
git clone https://github.com/alibrahim/cascade.git
cd cascade/plugins/cascade/examples/food-marketplace

# 2. Start all services
pip install fastapi uvicorn httpx flask
bash start-services.sh

# 3. Open Claude Code and initialize Cascade
claude
/cascade-init

# 4. Run a cross-service change
"Add a phone field to users and propagate to all services"
```

## 10 Test Changes (easy to hard)

See `CHANGES.md` for the full list. Recommended order:

| # | Change | Difficulty | What it tests |
|---|--------|-----------|---------------|
| 1 | Add `phone` to users | Easy | Field propagation |
| 2 | Add `rating` to menu items | Medium | Aggregation logic |
| 3 | Rename `role` to `account_type` | **Hard** | Breaking rename |
| 4 | Add delivery address + ETA | Medium | Multi-field addition |
| 5 | Add `allergens` array | Medium | Array field + filtering |
| 6 | Restructure order items | **Hard** | Breaking shape change |
| 7 | Rate limit headers everywhere | **Hard** | Cross-cutting middleware |
| 8 | Health check dependencies | Medium | Infrastructure |
| 9 | Pagination on all lists | **Hard** | Systematic change |
| 10 | Currency support | **Hard** | New shared model |

## Verified Results

Changes 1, 3, 6, and 7 have been tested with Cascade and passed with zero stale references, correct contract updates, and all services starting cleanly.
