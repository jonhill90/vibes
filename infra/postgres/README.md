# PostgreSQL Configuration (VPS Production)

This is the **production configuration** from `remote.hill90.space` VPS.

## Database Details

- **Image**: postgres:16-alpine
- **LiteLLM Database**: `litellm`
- **LiteLLM User**: `litellm_user`

## Init Script

The `init-litellm-db.sh` script automatically:
1. Creates the `litellm` database
2. Creates the `litellm_user` 
3. Grants all necessary privileges

## Deployment

```bash
docker compose up -d
```

## Notes
- Last synced: 2025-10-12
- Used by: LiteLLM proxy
