# Contributing to Cascade

Thanks for your interest in contributing to Cascade. Here's how to get involved.

## Quick Start

1. Fork the repo
2. Clone your fork
3. Install the plugin locally:
   ```
   /plugin marketplace add ./path/to/your/fork
   /plugin install cascade@cascade
   ```
4. Test against the food-marketplace example:
   ```bash
   cd plugins/cascade/examples/food-marketplace
   /cascade-init
   "Add a phone field to users and propagate to all services"
   ```

## What to Contribute

### High Impact
- **New example projects** — different stacks (Node/Express, Go, mixed), different domains
- **Bug reports with reproduction steps** — run a change, show what went wrong
- **Agent prompt improvements** — if an agent misses something, improve its instructions

### Medium Impact
- **New skills** — e.g., database migration coordination, API versioning strategies
- **Stack-specific worker variants** — workers optimized for Go, Rust, Java projects
- **Better verification checks** — more grep patterns, syntax validators per language

### Always Welcome
- Documentation improvements
- Typo fixes
- Test cases for edge cases the agents miss

## Project Structure

```
plugins/cascade/
├── agents/           # Agent definitions (the core logic)
│   ├── orchestrator.md
│   ├── cascade-planner.md
│   ├── cascade-worker.md
│   ├── cascade-contracts.md
│   └── cascade-verifier.md
├── skills/           # Reusable knowledge
├── commands/         # Slash commands (/cascade-init, /cascade-status)
├── hooks/            # Lifecycle hooks
└── examples/         # Demo projects
```

## How Agents Work

Each agent is a Markdown file with YAML frontmatter. The frontmatter defines the agent's name, description, tools, and model. The body is the system prompt.

When modifying an agent:
- Keep the description specific — Claude uses it to decide when to delegate
- Test your changes against the food-marketplace example
- Run at least one breaking rename (Change 3) and one parallel change (Change 7) to verify

## Pull Request Process

1. Create a branch from `main`
2. Make your changes
3. Test against the example project
4. Open a PR with:
   - What you changed
   - Why
   - How you tested it
5. Keep PRs focused — one change per PR

## Code of Conduct

Be kind. Be constructive. We're all here to build better tools.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
