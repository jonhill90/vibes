-- Create basic roles for Supabase
-- This runs during database initialization

-- Create auth schema and roles
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION supabase_admin;
CREATE SCHEMA IF NOT EXISTS storage AUTHORIZATION supabase_admin;
CREATE SCHEMA IF NOT EXISTS realtime AUTHORIZATION supabase_admin;

-- Grant usage on auth schema to service_role and authenticated roles
GRANT USAGE ON SCHEMA auth TO postgres, anon, authenticated, service_role;
GRANT USAGE ON SCHEMA storage TO postgres, anon, authenticated, service_role;

-- Enable Row Level Security
ALTER SCHEMA auth ENABLE ROW LEVEL SECURITY;
ALTER SCHEMA storage ENABLE ROW LEVEL SECURITY;
