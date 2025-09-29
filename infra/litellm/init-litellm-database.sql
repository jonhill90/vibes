-- Create separate LiteLLM database (SQL Server style approach)
-- This gives complete isolation from Supabase

-- Create the database
CREATE DATABASE litellm
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE litellm TO postgres;

-- Optional: Create comment for documentation
COMMENT ON DATABASE litellm IS 'LiteLLM proxy database for LLM API management';
