# Food Marketplace Example

A 6-service food marketplace platform for testing Cascade.

## Services
- auth-service (9000) — user management
- catalog-service (9001) — menu items
- order-service (9002) — orders
- notification-service (9003) — notifications
- gateway-api (9004) — aggregation gateway
- dashboard-ui (9005) — web dashboard

## Quick start

```bash
cd examples/food-marketplace
/cascade-init
# Then run any of the 10 changes in CHANGES.md
```

## 10 Test Changes (easy → hard)

See CHANGES.md for the full list. Highlights:
- Change 1: Add phone field (easy, field propagation)
- Change 3: Rename role → account_type (hard, breaking rename)
- Change 7: Rate limit headers on all services (hard, cross-cutting)
- Change 9: Pagination on all list endpoints (hard, systematic)
