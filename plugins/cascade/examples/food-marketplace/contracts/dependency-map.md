# Service Dependency Map

```
auth-service (9000)
    ↑
    ├── catalog-service (9001)
    │       ↑
    │       ├── order-service (9002)
    │       │       ↑
    │       │       └── notification-service (9003)
    │       │
    └───────┴─── gateway-api (9004)
                        ↑
                 dashboard-ui (9005)
```

## Change Order
auth → catalog → order → notification → gateway → dashboard

## Contract Versions
- auth-service: v1.0.0
- catalog-service: v1.0.0
- order-service: v1.0.0
- notification-service: v1.0.0
- gateway-api: v1.0.0
- dashboard-ui: v1.0.0
