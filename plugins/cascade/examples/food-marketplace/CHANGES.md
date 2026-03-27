# Change List for Testing Cascade

Run these one at a time. Each one tests a different aspect of cross-service coordination.
Start a new Claude session for each change (or continue in the same one).

## How to Run

```bash
cd examples/food-marketplace
claude "Implement Change N from CHANGES.md"
```

---

## Change 1: Add `phone` field to users (easy, additive)
- Add `phone: str | None` to User model in auth-service
- Add phone to all seed users
- notification-service should use phone for SMS notifications
- dashboard-ui should show phone in customer profile
- **Tests:** Field propagation, downstream consumption

## Change 2: Add `rating` field to menu items (medium, cross-service)
- Add `rating: float` (1.0-5.0) to MenuItem in catalog-service
- Add ratings to all seed menu items
- order-service should include item ratings in order details
- gateway-api vendor summary should show average rating
- dashboard-ui should show ratings with star display
- **Tests:** Aggregation logic, UI rendering

## Change 3: Rename `role` → `account_type` across all services (hard, breaking rename)
- Rename in auth-service User model
- Update validate endpoint response
- ALL downstream services must update every reference to `role`
- Update contracts
- **Tests:** Breaking rename propagation, stale reference detection

## Change 4: Add order `delivery_address` and `estimated_delivery` (medium, multi-field)
- Add `delivery_address: str` and `estimated_delivery: str | None` to Order
- order-service calculates estimated_delivery (30 min from now) on creation
- notification-service includes delivery info in order_confirmed messages
- gateway-api passes through in customer profile
- dashboard-ui shows delivery info in orders table
- **Tests:** Multiple new fields, time calculation, message formatting

## Change 5: Add `allergens` to menu items (medium, array field)
- Add `allergens: list[str]` to MenuItem (e.g., ["gluten", "dairy", "nuts"])
- Add allergens to all seed items
- catalog-service: add `?allergen_free=gluten` filter (exclude items with that allergen)
- order-service: include allergens in order item details
- dashboard-ui: show allergen badges
- **Tests:** Array field propagation, filtering logic

## Change 6: Restructure order items (hard, breaking response shape change)
- Change OrderItem from flat to nested:
  ```
  Before: {menu_item_id, quantity, unit_price, subtotal}
  After:  {item: {id, name, price}, quantity, subtotal}
  ```
- notification-service must parse new structure for order messages
- gateway-api must handle new structure
- dashboard-ui must render new structure
- **Tests:** Response shape migration, downstream parsing

## Change 7: Add rate limiting headers to all services (hard, cross-cutting middleware)
- Every service adds middleware/decorator for response headers:
  - `X-RateLimit-Limit: 100`
  - `X-RateLimit-Remaining: 99`
  - `X-Request-Id: <uuid>`
- gateway-api passes through upstream X-Request-Id
- **Tests:** Middleware addition across 6 services

## Change 8: Add health check dependencies (medium, infrastructure)
- Each /health endpoint checks upstream services
- Returns `{"status": "healthy"|"degraded", "dependencies": {"auth": "up", "catalog": "down"}, "version": "1.x.0"}`
- Services with no dependencies just return healthy + version
- **Tests:** Dependency awareness, graceful degradation

## Change 9: Add pagination to all list endpoints (hard, systematic)
- Every GET endpoint that returns arrays supports `?page=1&per_page=20`
- Response includes `{items: [...], page, per_page, total, total_pages}`
- This affects: auth/users, catalog/menu, orders/list, notifications/list
- gateway-api passes through pagination params
- dashboard-ui shows page controls
- **Tests:** Systematic change across many endpoints

## Change 10: Add `currency` support (hard, requires new model)
- Add Currency model: {code: "USD"|"EUR"|"GBP", symbol: "$"|"€"|"£", rate: float}
- catalog-service: menu item prices include currency
- order-service: orders include currency, totals calculated with rate
- gateway-api: stats include currency
- dashboard-ui: amounts display with currency symbol
- **Tests:** New shared model, calculation logic, display formatting

---

## Scoring Guide

After each change, verify:
1. **All services start** without errors → `bash start-services.sh`
2. **Contracts updated** → check contracts/api-contracts.yaml matches reality
3. **No stale references** → `grep -r "old_field" services/ --include="*.py"`
4. **Downstream works** → curl each endpoint that should have the new data
5. **UI displays correctly** → open http://localhost:9005
