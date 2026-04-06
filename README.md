# GPAG

Workspace-level `uv` project with source organized under `src/modules`.

## Setup

```bash
uv sync
```

## Run alpha pipeline

```bash
uv run gpag --target 50 --generations 50 --population 200
```

## Lint

```bash
uv run ruff check .
```
