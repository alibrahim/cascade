# Changelog

## [1.0.0] - 2026-03-28

### Added
- Cascade orchestrator agent with dependency-aware coordination
- Cascade planner agent for impact analysis and step-by-step planning
- Cascade worker agent with TDD support and mandatory commits
- Cascade contracts agent for API contract sync and versioning
- Cascade verifier agent for cross-service consistency checks
- Parallel execution by dependency tiers
- `/cascade-init` command for project setup
- `/cascade-status` command for service health overview
- Skills: multi-service-orchestration, contract-management, cross-service-verification
- Food marketplace example with 6 services and 10 test changes
- Demo GIFs: parallel execution + dependency propagation

### Tested
- 24/24 on 12-change gauntlet (breaking renames, response restructuring, cross-cutting middleware)
- Outperformed Agent Teams (17/24) and per-service sessions (7/24)
- Verified on 3-service and 6-service projects
