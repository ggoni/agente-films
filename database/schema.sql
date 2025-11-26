-- =============================================================================
-- PostgreSQL Database Schema for Multi-Agent Filmmaking System with ADK
-- =============================================================================
-- Version: 1.0
-- Description: Optimized schema for ADK session state, agent workflows,
--              and film project management with performance optimizations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- Core Tables
-- =============================================================================

-- Users table: Track system users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true
);

-- Sessions table: ADK conversation sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- ADK state dictionary for session reconstruction
    state JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Session metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Agent configuration snapshot
    root_agent_name VARCHAR(100),
    agent_config JSONB,

    -- Session status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'archived')),

    -- Performance tracking
    total_events INTEGER DEFAULT 0,
    total_tool_calls INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Film projects table: Film metadata
CREATE TABLE film_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Film details
    title VARCHAR(500),
    historical_subject VARCHAR(500),
    genre VARCHAR(100),

    -- Project status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'archived')),

    -- Film content (stored in state but denormalized for queries)
    plot_outline TEXT,
    research_summary TEXT,
    casting_report TEXT,
    box_office_report TEXT,

    -- File reference
    output_file_path TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- Agent Workflow Tables
-- =============================================================================

-- Questions table: User inputs in conversation
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Question content
    content TEXT NOT NULL,

    -- Context
    context JSONB DEFAULT '{}'::jsonb,

    -- Sequencing
    sequence_number INTEGER NOT NULL,

    -- Timing
    asked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Answers table: Agent outputs in conversation
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,

    -- Answer content
    content TEXT NOT NULL,

    -- Agent information
    agent_name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(100),

    -- Sequencing
    sequence_number INTEGER NOT NULL,

    -- Performance metrics
    tokens_used INTEGER,
    response_time_ms INTEGER,

    -- Timing
    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Inferential reasoning table: Agent thinking/reasoning
CREATE TABLE inferential_reasoning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    answer_id UUID REFERENCES answers(id) ON DELETE CASCADE,

    -- Agent information
    agent_name VARCHAR(100) NOT NULL,
    agent_role VARCHAR(200),

    -- Reasoning content
    reasoning_type VARCHAR(100) CHECK (reasoning_type IN (
        'research', 'planning', 'critique', 'analysis', 'decision', 'other'
    )),
    content TEXT NOT NULL,

    -- State changes made during reasoning
    state_delta JSONB,

    -- Sequencing
    sequence_number INTEGER NOT NULL,

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Events table: Agent execution events (partitioned by date)
CREATE TABLE events (
    id UUID DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Event type classification
    event_type VARCHAR(100) NOT NULL CHECK (event_type IN (
        'user_message', 'agent_response', 'tool_call', 'tool_response',
        'agent_transfer', 'state_update', 'loop_iteration', 'error', 'other'
    )),

    -- Agent context
    agent_name VARCHAR(100),
    parent_agent_name VARCHAR(100),

    -- Event details
    event_data JSONB NOT NULL,

    -- Tool information (if applicable)
    tool_name VARCHAR(100),
    tool_input JSONB,
    tool_output JSONB,

    -- State changes
    state_delta JSONB,

    -- Performance
    duration_ms INTEGER,
    tokens_used INTEGER,

    -- Error tracking
    error_message TEXT,

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create partitions for events table (monthly partitions)
CREATE TABLE events_2025_01 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02 PARTITION OF events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE events_2025_03 PARTITION OF events
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE events_2025_04 PARTITION OF events
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE events_2025_05 PARTITION OF events
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

CREATE TABLE events_2025_06 PARTITION OF events
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

CREATE TABLE events_2025_07 PARTITION OF events
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

CREATE TABLE events_2025_08 PARTITION OF events
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE events_2025_09 PARTITION OF events
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

CREATE TABLE events_2025_10 PARTITION OF events
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE events_2025_11 PARTITION OF events
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE events_2025_12 PARTITION OF events
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Agent transfers table: Track conversation flow between agents
CREATE TABLE agent_transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    event_id UUID,

    -- Transfer details
    from_agent VARCHAR(100) NOT NULL,
    to_agent VARCHAR(100) NOT NULL,
    transfer_reason TEXT,

    -- Timing
    transferred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- State snapshots table: Point-in-time state captures for recovery
CREATE TABLE state_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Snapshot details
    snapshot_type VARCHAR(50) CHECK (snapshot_type IN ('manual', 'automatic', 'checkpoint')),
    state JSONB NOT NULL,
    event_sequence_number INTEGER,

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- =============================================================================
-- Indexes for Performance Optimization
-- =============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Sessions indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);
CREATE INDEX idx_sessions_user_started ON sessions(user_id, started_at DESC);
CREATE INDEX idx_sessions_active ON sessions(status, started_at DESC) WHERE status = 'active';

-- JSONB GIN indexes for state queries
CREATE INDEX idx_sessions_state ON sessions USING GIN(state jsonb_path_ops);
CREATE INDEX idx_sessions_metadata ON sessions USING GIN(metadata jsonb_path_ops);

-- Film projects indexes
CREATE INDEX idx_film_projects_session_id ON film_projects(session_id);
CREATE INDEX idx_film_projects_user_id ON film_projects(user_id);
CREATE INDEX idx_film_projects_status ON film_projects(status);
CREATE INDEX idx_film_projects_created_at ON film_projects(created_at DESC);
CREATE INDEX idx_film_projects_title_trgm ON film_projects USING GIN(title gin_trgm_ops);
CREATE INDEX idx_film_projects_subject_trgm ON film_projects USING GIN(historical_subject gin_trgm_ops);

-- Questions indexes
CREATE INDEX idx_questions_session_id ON questions(session_id, sequence_number);
CREATE INDEX idx_questions_user_id ON questions(user_id);
CREATE INDEX idx_questions_asked_at ON questions(asked_at DESC);

-- Full-text search on questions
CREATE INDEX idx_questions_content_trgm ON questions USING GIN(content gin_trgm_ops);

-- Answers indexes
CREATE INDEX idx_answers_session_id ON answers(session_id, sequence_number);
CREATE INDEX idx_answers_question_id ON answers(question_id);
CREATE INDEX idx_answers_agent_name ON answers(agent_name);
CREATE INDEX idx_answers_answered_at ON answers(answered_at DESC);

-- Full-text search on answers
CREATE INDEX idx_answers_content_trgm ON answers USING GIN(content gin_trgm_ops);

-- Inferential reasoning indexes (partitioned approach)
CREATE INDEX idx_reasoning_session_id ON inferential_reasoning(session_id, sequence_number);
CREATE INDEX idx_reasoning_question_id ON inferential_reasoning(question_id);
CREATE INDEX idx_reasoning_answer_id ON inferential_reasoning(answer_id);
CREATE INDEX idx_reasoning_agent ON inferential_reasoning(agent_name);
CREATE INDEX idx_reasoning_type ON inferential_reasoning(reasoning_type);
CREATE INDEX idx_reasoning_created_at ON inferential_reasoning(created_at DESC);

-- JSONB indexes for reasoning
CREATE INDEX idx_reasoning_state_delta ON inferential_reasoning USING GIN(state_delta jsonb_path_ops);

-- Events indexes (applied to all partitions)
CREATE INDEX idx_events_session_id ON events(session_id, created_at DESC);
CREATE INDEX idx_events_type ON events(event_type, created_at DESC);
CREATE INDEX idx_events_agent ON events(agent_name, created_at DESC);
CREATE INDEX idx_events_tool ON events(tool_name) WHERE tool_name IS NOT NULL;

-- JSONB indexes for events
CREATE INDEX idx_events_data ON events USING GIN(event_data jsonb_path_ops);
CREATE INDEX idx_events_state_delta ON events USING GIN(state_delta jsonb_path_ops);

-- Agent transfers indexes
CREATE INDEX idx_transfers_session_id ON agent_transfers(session_id, transferred_at DESC);
CREATE INDEX idx_transfers_from_agent ON agent_transfers(from_agent);
CREATE INDEX idx_transfers_to_agent ON agent_transfers(to_agent);

-- State snapshots indexes
CREATE INDEX idx_snapshots_session_id ON state_snapshots(session_id, created_at DESC);
CREATE INDEX idx_snapshots_type ON state_snapshots(snapshot_type);
CREATE INDEX idx_snapshots_state ON state_snapshots USING GIN(state jsonb_path_ops);

-- =============================================================================
-- Materialized Views for Analytics
-- =============================================================================

-- Session summary view
CREATE MATERIALIZED VIEW session_summary AS
SELECT
    s.id AS session_id,
    s.user_id,
    s.session_name,
    s.status,
    s.started_at,
    s.ended_at,
    EXTRACT(EPOCH FROM (COALESCE(s.ended_at, NOW()) - s.started_at)) AS duration_seconds,
    s.total_events,
    s.total_tool_calls,
    s.total_tokens_used,
    COUNT(DISTINCT q.id) AS total_questions,
    COUNT(DISTINCT a.id) AS total_answers,
    COUNT(DISTINCT ir.id) AS total_reasoning_events,
    ARRAY_AGG(DISTINCT a.agent_name) FILTER (WHERE a.agent_name IS NOT NULL) AS agents_used,
    fp.id AS film_project_id,
    fp.title AS film_title,
    fp.status AS film_status
FROM sessions s
LEFT JOIN questions q ON s.id = q.session_id
LEFT JOIN answers a ON s.id = a.session_id
LEFT JOIN inferential_reasoning ir ON s.id = ir.session_id
LEFT JOIN film_projects fp ON s.id = fp.session_id
GROUP BY s.id, fp.id;

CREATE UNIQUE INDEX idx_session_summary_id ON session_summary(session_id);
CREATE INDEX idx_session_summary_user ON session_summary(user_id);
CREATE INDEX idx_session_summary_status ON session_summary(status);

-- Agent performance view
CREATE MATERIALIZED VIEW agent_performance AS
SELECT
    agent_name,
    COUNT(*) AS total_responses,
    AVG(tokens_used) AS avg_tokens,
    AVG(response_time_ms) AS avg_response_time_ms,
    MIN(answered_at) AS first_used,
    MAX(answered_at) AS last_used,
    COUNT(DISTINCT session_id) AS sessions_count
FROM answers
WHERE agent_name IS NOT NULL
GROUP BY agent_name;

CREATE UNIQUE INDEX idx_agent_perf_name ON agent_performance(agent_name);

-- Daily activity view
CREATE MATERIALIZED VIEW daily_activity AS
SELECT
    DATE(created_at) AS activity_date,
    COUNT(DISTINCT session_id) AS sessions_count,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE event_type = 'tool_call') AS tool_calls_count,
    SUM(tokens_used) AS total_tokens,
    AVG(duration_ms) AS avg_event_duration_ms
FROM events
GROUP BY DATE(created_at);

CREATE UNIQUE INDEX idx_daily_activity_date ON daily_activity(activity_date);

-- =============================================================================
-- Functions and Triggers
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_film_projects_updated_at BEFORE UPDATE ON film_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to increment session event counters
CREATE OR REPLACE FUNCTION increment_session_counters()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sessions
    SET
        total_events = total_events + 1,
        total_tool_calls = total_tool_calls + CASE WHEN NEW.event_type = 'tool_call' THEN 1 ELSE 0 END,
        total_tokens_used = total_tokens_used + COALESCE(NEW.tokens_used, 0)
    WHERE id = NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_event_counters AFTER INSERT ON events
    FOR EACH ROW EXECUTE FUNCTION increment_session_counters();

-- Function to create new monthly partition for events
CREATE OR REPLACE FUNCTION create_events_partition(partition_date DATE)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := 'events_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := DATE_TRUNC('month', partition_date);
    end_date := start_date + INTERVAL '1 month';

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF events FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY session_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY agent_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_activity;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Data Retention and Archival
-- =============================================================================

-- Archive old sessions function
CREATE OR REPLACE FUNCTION archive_old_sessions(days_threshold INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE sessions
    SET status = 'archived'
    WHERE status = 'completed'
        AND ended_at < NOW() - MAKE_INTERVAL(days => days_threshold)
        AND status != 'archived';

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Delete old archived data function
CREATE OR REPLACE FUNCTION delete_archived_data(days_threshold INTEGER DEFAULT 180)
RETURNS TABLE(
    sessions_deleted INTEGER,
    events_deleted INTEGER
) AS $$
DECLARE
    session_count INTEGER;
    event_count INTEGER;
BEGIN
    -- Delete sessions and cascade to related data
    WITH deleted_sessions AS (
        DELETE FROM sessions
        WHERE status = 'archived'
            AND ended_at < NOW() - MAKE_INTERVAL(days => days_threshold)
        RETURNING id
    )
    SELECT COUNT(*) INTO session_count FROM deleted_sessions;

    -- Delete old event partitions
    DELETE FROM events
    WHERE created_at < NOW() - MAKE_INTERVAL(days => days_threshold);

    GET DIAGNOSTICS event_count = ROW_COUNT;

    RETURN QUERY SELECT session_count, event_count;
END;
$$ LANGUAGE plpgsql;

-- Drop old event partitions
CREATE OR REPLACE FUNCTION drop_old_event_partitions(months_threshold INTEGER DEFAULT 12)
RETURNS void AS $$
DECLARE
    partition_record RECORD;
    cutoff_date DATE;
BEGIN
    cutoff_date := DATE_TRUNC('month', NOW() - MAKE_INTERVAL(months => months_threshold));

    FOR partition_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
            AND tablename LIKE 'events_%'
            AND tablename ~ 'events_\d{4}_\d{2}'
    LOOP
        -- Extract date from partition name and compare
        IF TO_DATE(SUBSTRING(partition_record.tablename FROM 'events_(\d{4}_\d{2})'), 'YYYY_MM') < cutoff_date THEN
            EXECUTE format('DROP TABLE IF EXISTS %I', partition_record.tablename);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Comments for Documentation
-- =============================================================================

COMMENT ON TABLE sessions IS 'ADK conversation sessions with state management';
COMMENT ON COLUMN sessions.state IS 'JSONB state dictionary for ADK session reconstruction';
COMMENT ON TABLE events IS 'Time-series agent execution events, partitioned by month';
COMMENT ON TABLE questions IS 'User inputs in conversation';
COMMENT ON TABLE answers IS 'Agent outputs in conversation';
COMMENT ON TABLE inferential_reasoning IS 'Agent thinking and reasoning processes';
COMMENT ON TABLE film_projects IS 'Film project metadata and outputs';
COMMENT ON TABLE state_snapshots IS 'Point-in-time state captures for recovery';

-- =============================================================================
-- Initial Data and Configuration
-- =============================================================================

-- Create default configuration table
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO system_config (key, value, description) VALUES
    ('retention_days', '90', 'Days before sessions are archived'),
    ('deletion_days', '180', 'Days before archived data is deleted'),
    ('partition_retention_months', '12', 'Months to retain event partitions'),
    ('max_state_size_kb', '1024', 'Maximum size of state JSONB in KB'),
    ('analytics_refresh_hours', '6', 'Hours between analytics view refreshes');
