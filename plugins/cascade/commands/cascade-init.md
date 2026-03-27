---
name: cascade-init
description: Initialize Cascade in the current project. Scans for services, generates cascade.yaml config, creates contracts directory, and sets up the orchestration framework.
---

# Cascade Init

Set up Cascade orchestration for a multi-service project.

## Process

1. **Scan the project** for service directories:
   - Look for directories containing `app.py`, `main.py`, `index.ts`, `main.go`, `Cargo.toml`
   - Check for `package.json`, `requirements.txt`, `go.mod` to identify tech stacks
   - Check for existing `CLAUDE.md` files in service directories

2. **Detect dependencies** between services:
   - Search for HTTP client calls (httpx, fetch, http.Get) to other service URLs
   - Look for port references, service URL constants
   - Check for existing contract files or interface definitions

3. **Generate `cascade.yaml`** in the project root:
   ```yaml
   # Cascade Configuration
   version: "1.0"

   services:
     auth-service:
       path: services/auth-service
       port: 9000
       entry: app.py
       depends_on: []

     catalog-service:
       path: services/catalog-service
       port: 9001
       entry: app.py
       depends_on: [auth-service]

   contracts:
     path: contracts/api-contracts.yaml
     dependency_map: contracts/dependency-map.md

   progress: cascade-progress.txt
   plans: cascade-plans/
   ```

4. **Create contracts directory** if it doesn't exist

5. **Generate initial contracts** by scanning actual API endpoints:
   - Read each service's entry file
   - Extract route definitions, models, and response shapes
   - Write to `contracts/api-contracts.yaml`

6. **Generate dependency map** from the detected dependencies

7. **Commit** the configuration files

## Output

After initialization, the user can run any cross-service change with:
```
Implement [change description]
```

The cascade-orchestrator agent will automatically activate for multi-service changes.
