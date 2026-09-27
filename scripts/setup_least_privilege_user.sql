-- ==============================================================================
-- Lumina Dental Studio - Neon PostgreSQL Least Privilege Role Setup
-- Fulfills OWASP / HIPAA Principle of Least Privilege (Test 9)
-- ==============================================================================

-- 1. Create dedicated application role if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lumina_app_user') THEN
        CREATE ROLE lumina_app_user WITH LOGIN PASSWORD 'CHANGE_IN_PRODUCTION_ENV_ONLY';
    END IF;
END
$$;

-- 2. Revoke administrative and database creation privileges
REVOKE ALL ON DATABASE neondb FROM lumina_app_user;
REVOKE CREATE ON SCHEMA public FROM lumina_app_user;

-- 3. Grant connection only to target database
GRANT CONNECT ON DATABASE neondb TO lumina_app_user;
GRANT USAGE ON SCHEMA public TO lumina_app_user;

-- 4. Grant strictly necessary DML privileges (SELECT, INSERT, UPDATE, DELETE)
-- Explicitly OMIT: DROP, ALTER, TRUNCATE, REFERENCES, TRIGGER
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lumina_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO lumina_app_user;

-- 5. Set default privileges for future tables created in schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO lumina_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO lumina_app_user;
