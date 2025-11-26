# Performance Optimization Guide

## Index Strategy

### GIN Indexes for JSONB

JSONB columns use GIN (Generalized Inverted Index) for efficient queries.

**Two operators available:**

1. **jsonb_ops** (default): Supports all JSONB operators
```sql
CREATE INDEX idx_sessions_state ON sessions USING GIN(state);

-- Supports queries like:
SELECT * FROM sessions WHERE state @> '{"status": "active"}';  -- Contains
SELECT * FROM sessions WHERE state ? 'PLOT_OUTLINE';  -- Key exists
```

2. **jsonb_path_ops**: Smaller, faster, but only supports @> operator
```sql
CREATE INDEX idx_sessions_state ON sessions USING GIN(state jsonb_path_ops);

-- Only supports containment:
SELECT * FROM sessions WHERE state @> '{"status": "active"}';
```

**Recommendation**: Use `jsonb_path_ops` for most cases (30% smaller, faster)

### Partial Indexes

Index only relevant subset of data for better performance:

```sql
-- Only index active sessions
CREATE INDEX idx_sessions_active
ON sessions(status, started_at DESC)
WHERE status = 'active';

-- Only index non-null tool calls
CREATE INDEX idx_events_tool
ON events(tool_name)
WHERE tool_name IS NOT NULL;
```

**Benefits:**
- Smaller index size
- Faster updates (fewer index entries)
- Better cache hit ratio

### Covering Indexes

Include additional columns to avoid table lookups:

```sql
-- Include session_name in index to avoid table lookup
CREATE INDEX idx_sessions_user_covering
ON sessions(user_id, started_at DESC)
INCLUDE (session_name, status);

-- Query can be satisfied from index alone:
SELECT session_name, status
FROM sessions
WHERE user_id = 'xxx'
ORDER BY started_at DESC;
```

### Index Maintenance

```sql
-- Find unused indexes (candidates for removal)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan < 10  -- Adjust threshold
    AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_sessions_state;

-- Or rebuild all indexes on table
REINDEX TABLE CONCURRENTLY sessions;
```

## Partition Strategy

### Time-Based Partitioning

Events table is partitioned by month for optimal performance:

**Benefits:**
- Faster queries with time-range filters
- Easy archival (drop old partitions)
- Parallel query execution across partitions
- Smaller indexes per partition

**Partition Pruning Example:**

```sql
-- Query only touches relevant partition
SELECT * FROM events
WHERE created_at >= '2025-01-01'
    AND created_at < '2025-02-01'
    AND session_id = 'xxx';

-- EXPLAIN shows partition pruning:
-- -> Seq Scan on events_2025_01
-- (only one partition scanned)
```

### Partition Management

```sql
-- Pre-create partitions for next 3 months
DO $$
DECLARE
    month_date DATE;
BEGIN
    FOR i IN 1..3 LOOP
        month_date := DATE_TRUNC('month', NOW() + (i || ' months')::INTERVAL);
        PERFORM create_events_partition(month_date);
    END LOOP;
END $$;

-- List existing partitions
SELECT
    inhrelid::regclass AS partition_name,
    pg_get_expr(relpartbound, inhrelid) AS partition_bounds
FROM pg_inherits
WHERE inhparent = 'events'::regclass;

-- Detach old partition (for archival)
ALTER TABLE events DETACH PARTITION events_2024_01;

-- Later: Attach archived partition if needed
ALTER TABLE events ATTACH PARTITION events_2024_01
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Reasoning Table Partitioning (Optional)

For high-volume systems, partition inferential_reasoning:

```sql
-- Convert to partitioned table
ALTER TABLE inferential_reasoning
RENAME TO inferential_reasoning_old;

CREATE TABLE inferential_reasoning (
    -- Same columns as before
    ...
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Migrate data
INSERT INTO inferential_reasoning
SELECT * FROM inferential_reasoning_old;

DROP TABLE inferential_reasoning_old;
```

## Query Optimization

### Query Plan Analysis

```sql
-- Use EXPLAIN ANALYZE for actual execution stats
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT
    s.id,
    s.state,
    COUNT(e.id) AS event_count
FROM sessions s
LEFT JOIN events e ON s.id = e.session_id
WHERE s.user_id = 'xxx'
GROUP BY s.id;

-- Key metrics to watch:
-- - Planning Time: Time to create query plan
-- - Execution Time: Actual query runtime
-- - Shared Buffers Hit: Cache hits (want high ratio)
-- - Rows: Estimated vs actual (large difference = bad stats)
```

### Index Usage Verification

```sql
-- Check if query uses index
EXPLAIN SELECT * FROM sessions
WHERE state @> '{"PLOT_OUTLINE": "..."}';

-- Should see:
-- -> Bitmap Index Scan on idx_sessions_state
-- NOT:
-- -> Seq Scan on sessions
```

### Statistics and ANALYZE

```sql
-- Update table statistics after bulk changes
ANALYZE sessions;

-- Check statistics freshness
SELECT
    schemaname,
    tablename,
    last_analyze,
    last_autoanalyze,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY last_analyze NULLS FIRST;

-- Increase statistics target for frequently queried columns
ALTER TABLE sessions ALTER COLUMN state SET STATISTICS 1000;
ANALYZE sessions;
```

### Join Optimization

```sql
-- Bad: N+1 query pattern
SELECT s.*,
    (SELECT COUNT(*) FROM events WHERE session_id = s.id) AS event_count,
    (SELECT COUNT(*) FROM questions WHERE session_id = s.id) AS question_count
FROM sessions s;

-- Good: Single query with joins
SELECT
    s.*,
    COUNT(DISTINCT e.id) AS event_count,
    COUNT(DISTINCT q.id) AS question_count
FROM sessions s
LEFT JOIN events e ON s.id = e.session_id
LEFT JOIN questions q ON s.id = q.session_id
GROUP BY s.id;

-- Even better: Use materialized view
SELECT * FROM session_summary WHERE session_id = 'xxx';
```

### Pagination Optimization

```sql
-- Bad: OFFSET gets slower with higher values
SELECT * FROM events
ORDER BY created_at DESC
OFFSET 10000 LIMIT 100;  -- Scans and discards 10000 rows

-- Good: Keyset pagination
SELECT * FROM events
WHERE created_at < '2025-01-15 10:30:00'  -- Last seen timestamp
ORDER BY created_at DESC
LIMIT 100;

-- Best: Use cursor with index
SELECT * FROM events
WHERE (created_at, id) < ('2025-01-15 10:30:00', 'last-uuid')
ORDER BY created_at DESC, id DESC
LIMIT 100;
```

## Materialized View Strategy

### Refresh Strategy

**Incremental Refresh (Manual)**:
```sql
-- Delete changed rows
DELETE FROM session_summary
WHERE session_id IN (
    SELECT id FROM sessions
    WHERE updated_at > (
        SELECT MAX(updated_at) FROM session_summary_metadata
    )
);

-- Insert new/updated rows
INSERT INTO session_summary
SELECT ... FROM sessions WHERE ...;
```

**Full Refresh (Scheduled)**:
```sql
-- Non-blocking refresh (requires UNIQUE index)
REFRESH MATERIALIZED VIEW CONCURRENTLY session_summary;

-- Fast but blocking
REFRESH MATERIALIZED VIEW session_summary;
```

**Scheduling**:
```sql
-- Create PostgreSQL scheduled job (pg_cron extension)
CREATE EXTENSION pg_cron;

-- Refresh every 6 hours
SELECT cron.schedule(
    'refresh-analytics',
    '0 */6 * * *',
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY session_summary$$
);

-- Or use external scheduler (cron, systemd timer)
```

### View Dependency Management

```sql
-- Check view dependencies
SELECT
    dependent_view.relname AS view_name,
    source_table.relname AS depends_on
FROM pg_depend
JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
JOIN pg_class AS dependent_view ON pg_rewrite.ev_class = dependent_view.oid
JOIN pg_class AS source_table ON pg_depend.refobjid = source_table.oid
WHERE dependent_view.relname = 'session_summary'
    AND source_table.relkind = 'r';
```

## Connection Pooling

### PgBouncer Configuration

**Installation**:
```bash
# Ubuntu/Debian
apt install pgbouncer

# macOS
brew install pgbouncer
```

**Configuration** (`/etc/pgbouncer/pgbouncer.ini`):
```ini
[databases]
agente_films = host=localhost port=5432 dbname=agente_films

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool mode
pool_mode = transaction  # Best for most use cases

# Connection limits
max_client_conn = 1000   # Max client connections
default_pool_size = 25   # Connections per database

# Server connection limits
max_db_connections = 50  # Total DB connections
max_user_connections = 50

# Timeouts
server_idle_timeout = 600
server_lifetime = 3600

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

**Pool Modes**:
- `session`: Client connection = server connection (safest)
- `transaction`: Connection released after transaction (recommended)
- `statement`: Connection released after statement (aggressive)

**Application Connection String**:
```python
# Direct PostgreSQL connection
DATABASE_URL = "postgresql://user:pass@localhost:5432/agente_films"

# PgBouncer connection
DATABASE_URL = "postgresql://user:pass@localhost:6432/agente_films"
```

### SQLAlchemy Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, QueuePool

# With PgBouncer (use NullPool)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Let PgBouncer handle pooling
)

# Without PgBouncer (use QueuePool)
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Base connections
    max_overflow=10,        # Additional connections under load
    pool_timeout=30,        # Wait time for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Verify connection before use
)
```

### Connection Monitoring

```sql
-- Current connections
SELECT
    datname,
    COUNT(*) AS connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle
FROM pg_stat_activity
GROUP BY datname;

-- Connection pool stats (PgBouncer)
SHOW POOLS;
SHOW STATS;

-- Long-running queries
SELECT
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
    AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY duration DESC;
```

## VACUUM and Bloat Management

### Auto-vacuum Tuning

```sql
-- Check auto-vacuum settings
SHOW autovacuum;
SHOW autovacuum_naptime;
SHOW autovacuum_vacuum_threshold;
SHOW autovacuum_vacuum_scale_factor;

-- Tune for high-write tables
ALTER TABLE events SET (
    autovacuum_vacuum_scale_factor = 0.02,  -- Default: 0.2
    autovacuum_vacuum_threshold = 1000,     -- Default: 50
    autovacuum_analyze_scale_factor = 0.01,
    autovacuum_analyze_threshold = 1000
);

-- Monitor auto-vacuum activity
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Manual VACUUM

```sql
-- Regular vacuum (non-blocking)
VACUUM sessions;

-- Verbose output
VACUUM VERBOSE sessions;

-- Full vacuum (locks table, reclaims space)
VACUUM FULL sessions;  -- Use with caution!

-- Analyze only (update statistics)
ANALYZE sessions;

-- Both vacuum and analyze
VACUUM ANALYZE sessions;
```

### Bloat Detection

```sql
-- Table bloat estimate
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Index bloat (requires pgstattuple extension)
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    100 - pgstatindex(indexname).avg_leaf_density AS bloat_pct
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Cache Optimization

### Shared Buffers

```sql
-- Check current setting
SHOW shared_buffers;

-- Recommended: 25% of system RAM
-- Set in postgresql.conf:
shared_buffers = 8GB
```

### Cache Hit Ratio

```sql
-- Overall cache hit ratio (want > 99%)
SELECT
    SUM(heap_blks_hit) / (SUM(heap_blks_hit) + SUM(heap_blks_read)) AS cache_hit_ratio
FROM pg_stattuple_approx('sessions');

-- Per-table cache hit ratio
SELECT
    schemaname,
    tablename,
    heap_blks_hit,
    heap_blks_read,
    ROUND(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_pct
FROM pg_stattuple
WHERE schemaname = 'public'
ORDER BY heap_blks_read DESC;

-- Index cache hit ratio
SELECT
    schemaname,
    tablename,
    indexname,
    idx_blks_hit,
    idx_blks_read,
    ROUND(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) AS hit_pct
FROM pg_stattuple
WHERE schemaname = 'public'
ORDER BY idx_blks_read DESC;
```

### Query Result Caching (Application Layer)

```python
from functools import lru_cache
import redis
import json

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_session_summary(session_id: str):
    cache_key = f"session_summary:{session_id}"

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database
    result = db.execute(
        "SELECT * FROM session_summary WHERE session_id = %s",
        (session_id,)
    ).fetchone()

    # Cache result (expire after 1 hour)
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result

# Invalidate cache on updates
def update_session(session_id: str, data: dict):
    db.execute("UPDATE sessions SET ... WHERE id = %s", ...)
    redis_client.delete(f"session_summary:{session_id}")
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Query Performance**
```sql
-- Slow queries (pg_stat_statements extension)
CREATE EXTENSION pg_stat_statements;

SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

2. **Lock Contention**
```sql
-- Current locks
SELECT
    locktype,
    relation::regclass,
    mode,
    transactionid,
    pid,
    granted
FROM pg_locks
WHERE NOT granted;
```

3. **Replication Lag** (if applicable)
```sql
SELECT
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag
FROM pg_stat_replication;
```

4. **Disk Usage**
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('agente_films'));

-- Table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                   pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Prometheus Metrics (postgres_exporter)

```yaml
# docker-compose.yml
version: '3'
services:
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://exporter:password@postgres:5432/agente_films?sslmode=disable"
    ports:
      - "9187:9187"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

**Key Alerts**:
- Cache hit ratio < 95%
- Connection pool > 80% utilization
- Query duration > 5 seconds
- Dead tuple ratio > 20%
- Replication lag > 10MB

## Performance Checklist

Daily:
- [ ] Monitor slow query log
- [ ] Check cache hit ratios
- [ ] Review connection pool stats
- [ ] Check for blocking queries

Weekly:
- [ ] Review index usage statistics
- [ ] Check table/index bloat
- [ ] Analyze partition sizes
- [ ] Review auto-vacuum activity

Monthly:
- [ ] Create new partitions (automated)
- [ ] Drop old partitions (if applicable)
- [ ] Review and optimize slow queries
- [ ] Update table statistics (ANALYZE)
- [ ] Review materialized view refresh frequency

Quarterly:
- [ ] Review index strategy
- [ ] Optimize connection pool settings
- [ ] Review partition retention policy
- [ ] Capacity planning based on growth
