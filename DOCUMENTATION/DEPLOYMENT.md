# Deployment and Docker Guide

This document captures the initial deployment and packaging steps for KAVACH.

## Docker

Build the backend container:

```bash
docker build -t kavach-backend .
```

Run the backend container:

```bash
docker run --rm -p 8000:8000 kavach-backend
```

The API will be available at `http://localhost:8000`.

## Docker Compose

Use Docker Compose to start both backend and frontend for local development:

```bash
docker compose up --build
```

This exposes:

- backend: `http://localhost:8000`
- frontend: `http://localhost:5173`

## CLI Startup

KAVACH now includes a CLI wrapper. From the repository root in a Python environment:

```bash
./kavach-env/bin/python -m backend.cli start
./kavach-env/bin/python -m backend.cli stop
./kavach-env/bin/python -m backend.cli status
```

The `start` command launches the backend with `uvicorn` in the background and records a PID file at `.kavach.pid`.

## Notes

- The Docker image installs runtime dependencies and enables the backend to run without requiring a local Python environment.
- The frontend is served via a Node.js service in compose mode; it is not currently bundled into the backend image.
