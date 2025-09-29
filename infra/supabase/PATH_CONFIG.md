# Supabase Path Configuration

## Overview
The `SUPABASE_HOST_PATH` environment variable controls how Docker mounts the volumes directory.

## Configuration

### Standard Docker Desktop Usage
If you're running `docker compose` directly from your host machine:

```bash
# In .env file
SUPABASE_HOST_PATH=.
```

This uses relative paths (current directory).

### Docker-in-Docker Scenarios
If you're running Docker from inside another container (like the vibes container):

```bash
# In .env file
SUPABASE_HOST_PATH=/Users/username/actual/path/to/vibes/infra/supabase
```

This uses absolute host paths that the Docker daemon can access.

## Why This is Needed

When running Docker commands from inside a container (Docker-in-Docker), the paths you reference must be **host filesystem paths**, not container paths. 

For example:
- Container sees: `/workspace/vibes/infra/supabase`
- Host actually has: `/Users/jon/source/vibes/infra/supabase`
- Docker daemon needs: The host path

## Current Configuration

The current `.env` file is set for Docker-in-Docker usage from the vibes container:

```bash
SUPABASE_HOST_PATH=/Users/jon/source/vibes/infra/supabase
```

## Changing Systems

If you move this setup to a different system or want to run it differently:

1. Edit `.env`
2. Update `SUPABASE_HOST_PATH` to match your situation
3. Restart services: `docker compose down && docker compose up -d`

## Verification

To check if paths are configured correctly:

```bash
docker compose config | grep volumes
```

You should see the correct paths being used.
