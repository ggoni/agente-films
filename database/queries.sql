-- =============================================================================
-- Common Query Patterns for Multi-Agent Filmmaking System
-- =============================================================================
-- Description: Optimized queries for common operations with performance notes

-- =============================================================================
-- Session Retrieval and Reconstruction
-- =============================================================================

-- Query 1: Get complete session context for ADK state reconstruction
-- Performance: Uses indexes on session_id, efficient JSONB aggregation
-- Use case: Restore ADK session state
SELECT
    s.id,
    s.state AS current_state,
    s.root_agent_name,
    s.agent_config,
    COALESCE(
        JSON_AGG(
            JSON_BUILD_OBJECT(
                'id', e.id,
                'type', e.event_type,
                'agent', e.agent_name,
                'data', e.event_data,
                'state_delta', e.state_delta,
                'created_at', e.created_at
            ) ORDER BY e.created_at
        ) FILTER (WHERE e.id IS NOT NULL),
        '[]'::json
    ) AS events
FROM sessions s
LEFT JOIN events e ON s.id = e.session_id
WHERE s.id = $1
GROUP BY s.id;

-- Query 2: Get conversation history with questions and answers
-- Performance: Indexed joins, sequential ordering
-- Use case: Display conversation thread
WITH conversation AS (
    SELECT
        q.sequence_number,
        'question' AS type,
        q.content,
        NULL AS agent_name,
        q.asked_at AS timestamp
    FROM questions q
    WHERE q.session_id = $1

    UNION ALL

    SELECT
        a.sequence_number,
        'answer' AS type,
        a.content,
        a.agent_name,
        a.answered_at AS timestamp
    FROM answers a
    WHERE a.session_id = $1
)
SELECT * FROM conversation
ORDER BY sequence_number, timestamp;

-- Query 3: Get session with full context (questions, answers, reasoning)
-- Performance: Multiple indexed lookups, JSONB aggregation
-- Use case: Complete session analysis
SELECT
    s.id AS session_id,
    s.session_name,
    s.status,
    s.state,
    JSON_BUILD_OBJECT(
        'questions', (
            SELECT JSON_AGG(
                JSON_BUILD_OBJECT(
                    'id', q.id,
                    'sequence', q.sequence_number,
                    'content', q.content,
                    'asked_at', q.asked_at,
                    'reasoning', (
                        SELECT JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'type', ir.reasoning_type,
                                'content', ir.content,
                                'agent', ir.agent_name
                            ) ORDER BY ir.sequence_number
                        )
                        FROM inferential_reasoning ir
                        WHERE ir.question_id = q.id
                    ),
                    'answers', (
                        SELECT JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'id', a.id,
                                'content', a.content,
                                'agent', a.agent_name,
                                'tokens', a.tokens_used,
                                'answered_at', a.answered_at
                            ) ORDER BY a.sequence_number
                        )
                        FROM answers a
                        WHERE a.question_id = q.id
                    )
                ) ORDER BY q.sequence_number
            )
            FROM questions q
            WHERE q.session_id = s.id
        )
    ) AS conversation_context
FROM sessions s
WHERE s.id = $1;

-- =============================================================================
-- Agent Workflow Analysis
-- =============================================================================

-- Query 4: Get agent transfer flow for session
-- Performance: Indexed on session_id and transferred_at
-- Use case: Visualize agent workflow
SELECT
    at.from_agent,
    at.to_agent,
    at.transfer_reason,
    at.transferred_at,
    LAG(at.to_agent) OVER (ORDER BY at.transferred_at) AS previous_agent
FROM agent_transfers at
WHERE at.session_id = $1
ORDER BY at.transferred_at;

-- Query 5: Agent activity timeline
-- Performance: Partition-aware, indexed on agent_name
-- Use case: Track which agents were active when
SELECT
    e.agent_name,
    MIN(e.created_at) AS first_active,
    MAX(e.created_at) AS last_active,
    COUNT(*) AS event_count,
    COUNT(*) FILTER (WHERE e.event_type = 'tool_call') AS tool_calls,
    SUM(e.tokens_used) AS total_tokens
FROM events e
WHERE e.session_id = $1
    AND e.agent_name IS NOT NULL
GROUP BY e.agent_name
ORDER BY first_active;

-- Query 6: Tool usage by agent
-- Performance: Indexed on tool_name, filtered WHERE clause
-- Use case: Understand tool usage patterns
SELECT
    e.agent_name,
    e.tool_name,
    COUNT(*) AS usage_count,
    AVG(e.duration_ms) AS avg_duration_ms,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'input', e.tool_input,
            'output', e.tool_output,
            'timestamp', e.created_at
        ) ORDER BY e.created_at
    ) AS tool_calls
FROM events e
WHERE e.session_id = $1
    AND e.event_type = 'tool_call'
    AND e.tool_name IS NOT NULL
GROUP BY e.agent_name, e.tool_name
ORDER BY e.agent_name, usage_count DESC;

-- =============================================================================
-- State Management Queries
-- =============================================================================

-- Query 7: Get state evolution over time
-- Performance: JSONB aggregation with ORDER BY
-- Use case: Track state changes through session
SELECT
    e.created_at,
    e.agent_name,
    e.event_type,
    e.state_delta
FROM events e
WHERE e.session_id = $1
    AND e.state_delta IS NOT NULL
ORDER BY e.created_at;

-- Query 8: Query specific state key across sessions
-- Performance: GIN index on JSONB, jsonb_path_ops
-- Use case: Find sessions with specific state values
SELECT
    s.id,
    s.session_name,
    s.state->>'PLOT_OUTLINE' AS plot_outline,
    s.state->>'research' AS research,
    s.started_at
FROM sessions s
WHERE s.state ? 'PLOT_OUTLINE'  -- Check if key exists
    AND s.status = 'completed'
ORDER BY s.started_at DESC;

-- Query 9: Find sessions by state content (full-text search in JSONB)
-- Performance: GIN index for JSONB search
-- Use case: Search for content within state
SELECT
    s.id,
    s.session_name,
    s.state,
    s.started_at
FROM sessions s
WHERE s.state::text ILIKE '%' || $1 || '%'
ORDER BY s.started_at DESC
LIMIT 20;

-- Query 10: Get latest state snapshot
-- Performance: Indexed on session_id and created_at DESC
-- Use case: Restore from last checkpoint
SELECT
    ss.id,
    ss.state,
    ss.snapshot_type,
    ss.created_at,
    ss.description
FROM state_snapshots ss
WHERE ss.session_id = $1
ORDER BY ss.created_at DESC
LIMIT 1;

-- =============================================================================
-- Film Project Queries
-- =============================================================================

-- Query 11: Get film projects with session details
-- Performance: Indexed joins
-- Use case: List user's film projects
SELECT
    fp.id,
    fp.title,
    fp.historical_subject,
    fp.status AS film_status,
    fp.created_at,
    s.session_name,
    s.status AS session_status,
    s.total_events,
    u.username
FROM film_projects fp
JOIN sessions s ON fp.session_id = s.id
JOIN users u ON fp.user_id = u.id
WHERE u.id = $1
ORDER BY fp.created_at DESC;

-- Query 12: Search films by subject or title (fuzzy matching)
-- Performance: GIN trigram indexes for similarity search
-- Use case: Flexible film search
SELECT
    fp.id,
    fp.title,
    fp.historical_subject,
    fp.genre,
    fp.status,
    SIMILARITY(fp.title, $1) AS title_similarity,
    SIMILARITY(fp.historical_subject, $1) AS subject_similarity
FROM film_projects fp
WHERE
    fp.title % $1  -- Trigram similarity operator
    OR fp.historical_subject % $1
ORDER BY GREATEST(title_similarity, subject_similarity) DESC
LIMIT 20;

-- Query 13: Get complete film project with all content
-- Performance: Single join, JSONB extraction
-- Use case: Export complete film project
SELECT
    fp.id,
    fp.title,
    fp.historical_subject,
    fp.genre,
    fp.plot_outline,
    fp.research_summary,
    fp.casting_report,
    fp.box_office_report,
    fp.output_file_path,
    fp.metadata,
    s.state AS session_state,
    JSON_BUILD_OBJECT(
        'session_name', s.session_name,
        'total_events', s.total_events,
        'started_at', s.started_at,
        'ended_at', s.ended_at
    ) AS session_info
FROM film_projects fp
JOIN sessions s ON fp.session_id = s.id
WHERE fp.id = $1;

-- =============================================================================
-- Analytics and Reporting Queries
-- =============================================================================

-- Query 14: User activity summary
-- Performance: Materialized view, pre-aggregated
-- Use case: User dashboard
SELECT
    u.id,
    u.username,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(DISTINCT fp.id) AS total_films,
    SUM(s.total_events) AS total_events,
    SUM(s.total_tokens_used) AS total_tokens,
    MAX(s.started_at) AS last_active
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN film_projects fp ON u.id = fp.user_id
WHERE u.id = $1
GROUP BY u.id;

-- Query 15: Agent performance metrics
-- Performance: Materialized view agent_performance
-- Use case: System analytics
SELECT
    ap.agent_name,
    ap.total_responses,
    ROUND(ap.avg_tokens::numeric, 2) AS avg_tokens,
    ROUND(ap.avg_response_time_ms::numeric, 2) AS avg_response_time_ms,
    ap.sessions_count,
    ap.first_used,
    ap.last_used
FROM agent_performance ap
ORDER BY ap.total_responses DESC;

-- Query 16: System activity over time
-- Performance: Materialized view daily_activity
-- Use case: Usage trends
SELECT
    da.activity_date,
    da.sessions_count,
    da.total_events,
    da.tool_calls_count,
    da.total_tokens,
    ROUND(da.avg_event_duration_ms::numeric, 2) AS avg_event_duration_ms
FROM daily_activity da
WHERE da.activity_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY da.activity_date DESC;

-- Query 17: Top active sessions
-- Performance: Pre-aggregated in materialized view
-- Use case: Identify complex sessions
SELECT
    ss.session_id,
    ss.session_name,
    ss.status,
    ss.total_events,
    ss.total_answers,
    ss.total_reasoning_events,
    ss.total_tokens_used,
    ss.duration_seconds,
    ss.agents_used,
    ss.film_title
FROM session_summary ss
ORDER BY ss.total_events DESC
LIMIT 20;

-- =============================================================================
-- Reasoning and Debugging Queries
-- =============================================================================

-- Query 18: Get reasoning chain for question
-- Performance: Indexed on question_id
-- Use case: Debug agent decision making
SELECT
    ir.agent_name,
    ir.reasoning_type,
    ir.content,
    ir.state_delta,
    ir.sequence_number,
    ir.created_at
FROM inferential_reasoning ir
WHERE ir.question_id = $1
ORDER BY ir.sequence_number;

-- Query 19: Error analysis
-- Performance: Partition-aware, filtered on event_type
-- Use case: Debug failures
SELECT
    e.created_at,
    e.session_id,
    e.agent_name,
    e.error_message,
    e.event_data
FROM events e
WHERE e.event_type = 'error'
    AND e.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY e.created_at DESC;

-- Query 20: Session performance breakdown
-- Performance: Multiple aggregations with window functions
-- Use case: Identify performance bottlenecks
SELECT
    e.agent_name,
    COUNT(*) AS events,
    AVG(e.duration_ms) AS avg_duration,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.duration_ms) AS median_duration,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY e.duration_ms) AS p95_duration,
    MAX(e.duration_ms) AS max_duration
FROM events e
WHERE e.session_id = $1
    AND e.duration_ms IS NOT NULL
GROUP BY e.agent_name
ORDER BY avg_duration DESC;

-- =============================================================================
-- Data Management Queries
-- =============================================================================

-- Query 21: Archive old completed sessions
-- Use case: Automated cleanup job
SELECT archive_old_sessions(90);

-- Query 22: Delete archived data older than threshold
-- Use case: Permanent cleanup
SELECT * FROM delete_archived_data(180);

-- Query 23: Create partition for upcoming month
-- Use case: Proactive partition management
SELECT create_events_partition(DATE_TRUNC('month', NOW() + INTERVAL '1 month'));

-- Query 24: Refresh analytics views
-- Use case: Scheduled refresh job
SELECT refresh_analytics_views();

-- Query 25: Get partition sizes
-- Performance: System catalog query
-- Use case: Monitor partition growth
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS bytes
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename LIKE 'events_%'
ORDER BY bytes DESC;

-- =============================================================================
-- Advanced JSONB Queries
-- =============================================================================

-- Query 26: Extract specific paths from state
-- Performance: GIN index on jsonb_path_ops
-- Use case: Analyze state structure
SELECT
    s.id,
    s.session_name,
    s.state->'PLOT_OUTLINE' AS plot_outline,
    s.state->'research' AS research,
    s.state->'attractions' AS attractions,
    s.state->'CRITICAL_FEEDBACK' AS feedback
FROM sessions s
WHERE s.state IS NOT NULL
    AND s.state != '{}'::jsonb
ORDER BY s.started_at DESC;

-- Query 27: Find sessions with nested JSONB conditions
-- Performance: jsonb_path_query for complex paths
-- Use case: Advanced state filtering
SELECT
    s.id,
    s.session_name,
    jsonb_pretty(s.state) AS state_formatted
FROM sessions s
WHERE
    jsonb_typeof(s.state->'research') = 'array'
    AND jsonb_array_length(s.state->'research') > 0
ORDER BY s.started_at DESC;

-- Query 28: Aggregate state values across sessions
-- Performance: JSONB unnesting and aggregation
-- Use case: Content analysis
SELECT
    jsonb_object_keys(s.state) AS state_key,
    COUNT(*) AS sessions_with_key,
    COUNT(*) FILTER (WHERE jsonb_typeof(s.state->jsonb_object_keys(s.state)) = 'array') AS array_values,
    COUNT(*) FILTER (WHERE jsonb_typeof(s.state->jsonb_object_keys(s.state)) = 'object') AS object_values,
    COUNT(*) FILTER (WHERE jsonb_typeof(s.state->jsonb_object_keys(s.state)) = 'string') AS string_values
FROM sessions s
WHERE s.state IS NOT NULL
GROUP BY state_key
ORDER BY sessions_with_key DESC;

-- =============================================================================
-- Performance Monitoring Queries
-- =============================================================================

-- Query 29: Index usage statistics
-- Use case: Identify unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

-- Query 30: Table statistics and bloat
-- Use case: Monitor table health
SELECT
    schemaname,
    tablename,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
