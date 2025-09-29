# Archon Path Configuration

## Overview
The `ARCHON_HOST_PATH` environment variable controls how Docker mounts volumes when running in Docker-in-Docker scenarios.

## Configuration

### Standard Docker Desktop Usage
If running `docker compose` directly from host:

```bash
# In docker-compose.yml volumes
volumes:
  - ./data:/app/data
```

### Docker-in-Docker Scenarios
If running Docker from inside the vibes container:

```bash
# In docker-compose.yml volumes
volumes:
  - ${ARCHON_HOST_PATH}/data:/app/data
```

Where `ARCHON_HOST_PATH=/Users/jon/source/vibes/infra/archon`

## Why This is Needed

When running Docker commands from inside a container, paths must be **host filesystem paths**:
- Container sees: `/workspace/vibes/infra/archon`
- Host actually has: `/Users/jon/source/vibes/infra/archon`
- Docker daemon needs: The host path

## Current Configuration

Set for Docker-in-Docker usage from vibes container:
- Host path: `/Users/jon/source/vibes/infra/archon`
- Container path: `/workspace/vibes/infra/archon`
