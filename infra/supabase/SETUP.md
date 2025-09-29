# Supabase Self-Hosting Setup

This directory contains the Docker configuration for self-hosting Supabase.

## Quick Start

1. **Pull latest images:**
   ```bash
   docker compose pull
   ```

2. **Start services:**
   ```bash
   docker compose up -d
   ```

3. **Access Supabase Studio:**
   - URL: http://localhost:8000
   - Username: supabase
   - Password: this_password_is_insecure_and_should_be_updated

## Important Security Steps

⚠️ **CHANGE DEFAULT CREDENTIALS IMMEDIATELY** ⚠️

1. **Update .env file** with secure values:
   - `POSTGRES_PASSWORD`
   - `JWT_SECRET` 
   - `DASHBOARD_USERNAME`
   - `DASHBOARD_PASSWORD`
   - Generate new `ANON_KEY` and `SERVICE_ROLE_KEY`

2. **Restart services** after updating .env:
   ```bash
   docker compose down
   docker compose up -d
   ```

## API Endpoints

- REST: http://localhost:8000/rest/v1/
- Auth: http://localhost:8000/auth/v1/
- Storage: http://localhost:8000/storage/v1/
- Realtime: http://localhost:8000/realtime/v1/

## Database Access

- Session-based: `postgres://postgres.your-tenant-id:your-super-secret-and-long-postgres-password@localhost:5432/postgres`
- Pooled: `postgres://postgres.your-tenant-id:your-super-secret-and-long-postgres-password@localhost:6543/postgres`

## Files

- `docker-compose.yml` - Main configuration
- `.env` - Environment variables (customize this!)
- `volumes/` - Persistent data storage
- `reset.sh` - Clean up script

## Documentation

Original source: https://github.com/supabase/supabase/tree/master/docker
Documentation: https://supabase.com/docs/guides/self-hosting/docker
