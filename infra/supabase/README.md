# Supabase Self-Hosted Instance

Production-ready Supabase setup for Archon and other applications.

## Quick Access

**Studio Dashboard:** http://localhost:8000  
**API Gateway:** http://localhost:8000  
**Default Credentials:** `supabase` / `this_password_is_insecure_and_should_be_updated`

⚠️ **Change credentials in `.env` before production use!**

## Configuration

### Path Setup (Important!)
This setup uses `SUPABASE_HOST_PATH` in `.env` to handle Docker-in-Docker scenarios.

**Current setting:** `/Users/jon/source/vibes/infra/supabase`

For standard Docker usage, change to: `SUPABASE_HOST_PATH=.`

See `PATH_CONFIG.md` for details.

## Quick Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f [service-name]

# Check status
docker compose ps
```

## Services Running

All 13 Supabase services with clean names (no "test" suffix):
- ✅ PostgreSQL Database (supabase-db)
- ✅ Authentication (supabase-auth)
- ✅ REST API (supabase-rest)
- ✅ Realtime (realtime-dev.supabase-realtime)
- ✅ Storage (supabase-storage)
- ✅ Studio Dashboard (supabase-studio)
- ✅ API Gateway (supabase-kong)
- ✅ Metadata API (supabase-meta)
- ✅ Edge Functions (supabase-edge-functions)
- ✅ Analytics (supabase-analytics)
- ✅ Connection Pooler (supabase-pooler)
- ✅ Logging (supabase-vector)
- ✅ Image Proxy (supabase-imgproxy)

## Documentation

- `SETUP.md` - Full setup guide with security steps
- `PATH_CONFIG.md` - Path configuration for different environments
- `DOCKER_SETUP.md` - Docker Desktop configuration (legacy)

## API Endpoints

| Service | Endpoint |
|---------|----------|
| REST API | http://localhost:8000/rest/v1/ |
| Auth | http://localhost:8000/auth/v1/ |
| Storage | http://localhost:8000/storage/v1/ |
| Realtime | http://localhost:8000/realtime/v1/ |

## Database Connection

```bash
# Session-based (direct)
postgres://postgres:your-super-secret-and-long-postgres-password@localhost:5432/postgres

# Pooled (recommended)
postgres://postgres:your-super-secret-and-long-postgres-password@localhost:6543/postgres
```

## For Archon Integration

Use these environment variables in Archon:
```
SUPABASE_URL=http://localhost:8000
SUPABASE_ANON_KEY=[from .env file]
SUPABASE_SERVICE_ROLE_KEY=[from .env file]
DATABASE_URL=postgres://postgres:[password]@localhost:6543/postgres
```

## Source

Cloned from: https://github.com/supabase/supabase/tree/master/docker
