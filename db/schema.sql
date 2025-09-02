-- Cross-Coach Database Schema
-- Generated from SQLAlchemy models

-- Create enum for domain types
CREATE TYPE domainenum AS ENUM (
    'fitness',
    'climbing', 
    'learning',
    'reflection',
    'sleep',
    'other'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log entries table
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    domain domainenum NOT NULL,
    metric VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,
    notes TEXT
);

-- Correlation insights table
CREATE TABLE correlation_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    correlation_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Journal summaries table
CREATE TABLE journal_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    summary_text TEXT NOT NULL
);

-- Performance indexes
CREATE INDEX idx_log_entries_user_date ON log_entries(user_id, date);
CREATE INDEX idx_journal_summaries_user_date ON journal_summaries(user_id, date);

-- Additional useful indexes
CREATE INDEX idx_log_entries_domain ON log_entries(domain);
CREATE INDEX idx_log_entries_date ON log_entries(date);
CREATE INDEX idx_correlation_insights_user_id ON correlation_insights(user_id);
CREATE INDEX idx_correlation_insights_created_at ON correlation_insights(created_at); 