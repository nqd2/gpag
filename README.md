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

Default mode is real WQB flow (requires credentials).

Run mock flow:

```bash
uv run gpag --target 50 --generations 50 --population 200 --is-mock true
```

## Lint

```bash
uv run ruff check .
```
