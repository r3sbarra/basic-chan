# Contributing to Basic-chan

We welcome contributions to the `-chan` foundational ecosystem!

## Development Setup

1. Clone or navigate to the repository:
   ```bash
   cd basic-chan
   ```

2. Run the automated installer:
   ```bash
   ./install.sh
   ```

3. Run verification and self-tests:
   ```bash
   ./setup.sh
   ```

## Running Tests

```bash
.venv/bin/pytest tests/ -v
```

## Pull Request Guidelines

- Ensure all existing unit tests pass.
- Write tests for new functionality in `tests/`.
- Keep the core engine 100% daemonless (zero background server requirements).
- Preserve the clean `BaseChan` API and dynamic sister discovery protocols.
