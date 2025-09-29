# Supabase Self-Hosting Setup

This directory contains the Docker configuration for self-hosting Supabase.

## Quick Start

1. **Configure path (if needed):**
   - See `PATH_CONFIG.md` for details
   - Default is set for vibes container usage
   - For standard usage, set `SUPABASE_HOST_PATH=.` in `.env`

2. **Pull latest images:**
   ```bash
   docker compose pull
   ```

3. **Start services:**
   ```bash
   docker compose up -d
   ```

4. **Access Supabase Studio:**
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
   - `SUPABASE_HOST_PATH` (see PATH_CONFIG.md)
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

- Session-based (port 5432): `postgres://postgres:your-super-secret-and-long-postgres-password@localhost:5432/postgres`
- Pooled (port 6543): `postgres://postgres:your-super-secret-and-long-postgres-password@localhost:6543/postgres`

## Services

All services run without "test" suffix:
- supabase-db (PostgreSQL)
- supabase-auth (GoTrue)
- supabase-rest (PostgREST)
- supabase-realtime
- supabase-storage
- supabase-studio
- supabase-kong (API Gateway)
- supabase-meta
- supabase-edge-functions
- supabase-analytics
- supabase-pooler
- supabase-vector (Logging)
- supabase-imgproxy

## Files

- `docker-compose.yml` - Main configuration
- `.env` - Environment variables (customize this!)
- `volumes/` - Persistent data storage
- `PATH_CONFIG.md` - Path configuration guide
- `DOCKER_SETUP.md` - Docker Desktop setup (legacy)

## Troubleshooting

### Path Issues
See `PATH_CONFIG.md` for configuring `SUPABASE_HOST_PATH`

### Service Not Starting
Check logs: `docker compose logs <service-name>`

### Port Conflicts
Edit `.env` to change ports if needed

## Documentation

- Original source: https://github.com/supabase/supabase/tree/master/docker
- Documentation: https://supabase.com/docs/guides/self-hosting/docker
