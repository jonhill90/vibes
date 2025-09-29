-- Initialize LiteLLM schema in Supabase PostgreSQL
-- This keeps LiteLLM tables isolated from Supabase tables

-- Create dedicated schema for LiteLLM
CREATE SCHEMA IF NOT EXISTS litellm;

-- Grant usage to postgres user (default Supabase user)
GRANT USAGE ON SCHEMA litellm TO postgres;
GRANT CREATE ON SCHEMA litellm TO postgres;

-- Grant all privileges on future tables in the schema
ALTER DEFAULT PRIVILEGES IN SCHEMA litellm GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA litellm GRANT ALL ON SEQUENCES TO postgres;

-- Optional: Create a dedicated user for LiteLLM (more secure)
-- Uncomment if you want separate user management
-- CREATE USER litellm_user WITH PASSWORD 'your-secure-litellm-password';
-- GRANT USAGE ON SCHEMA litellm TO litellm_user;
-- GRANT CREATE ON SCHEMA litellm TO litellm_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA litellm GRANT ALL ON TABLES TO litellm_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA litellm GRANT ALL ON SEQUENCES TO litellm_user;
