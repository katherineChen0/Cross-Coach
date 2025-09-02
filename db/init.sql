CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	email TEXT UNIQUE NOT NULL,
	name TEXT,
	password_hash TEXT,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Generic logs table covering various domains via type and metrics JSONB
CREATE TABLE IF NOT EXISTS logs (
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	log_date DATE NOT NULL,
	domain TEXT NOT NULL CHECK (domain IN ('fitness','climbing','coding','mood','sleep','journaling')),
	value NUMERIC NULL,
	metrics JSONB NULL,
	note TEXT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Weekly insights table
CREATE TABLE IF NOT EXISTS insights (
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	week_start DATE NOT NULL,
	summary TEXT,
	correlations JSONB,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	UNIQUE(user_id, week_start)
);

-- Helpful index for analytics queries
CREATE INDEX IF NOT EXISTS idx_logs_user_date ON logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_logs_domain ON logs(domain); 