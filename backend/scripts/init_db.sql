-- Initialize database with PostGIS and TimescaleDB extensions

-- Create PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create indexes for common queries
-- These will be created by SQLAlchemy models, but we can add additional ones here

-- Create GIN index for JSONB columns if needed
-- CREATE INDEX IF NOT EXISTS idx_profiles_metadata ON profiles USING GIN (metadata);
-- CREATE INDEX IF NOT EXISTS idx_floats_metadata ON argo_floats USING GIN (metadata);

