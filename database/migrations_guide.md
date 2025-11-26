# Database Migration Strategy

## Alembic Setup and Configuration

### Installation

```bash
uv add alembic psycopg2-binary
```

### Initialization

```bash
# Initialize Alembic in your project
alembic init alembic

# This creates:
# - alembic/
#   - versions/    # Migration files
#   - env.py       # Alembic environment config
#   - script.py.mako
# - alembic.ini    # Alembic configuration
```

### Configuration

**alembic.ini**
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/agente_films

# Partitioned tables support
version_locations = alembic/versions

# Timezone for migration timestamps
timezone = UTC
```

**alembic/env.py**
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os

# Import your models
from your_app.models import Base

config = context.config

# Override with environment variable if available
db_url = os.getenv('DATABASE_URL', config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Important for partitioned tables
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Support for partitioned tables
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Zero-Downtime Migration Strategy

### Principles

1. **Additive Changes First**: Add new columns/tables before removing old ones
2. **Backward Compatibility**: Ensure application works with both old and new schema
3. **Phased Rollout**: Deploy schema changes separately from application changes
4. **Validation**: Test migrations on staging with production-like data

### Migration Patterns

#### Pattern 1: Adding a Column

```python
# Migration 001: Add column with default
def upgrade():
    op.add_column('sessions',
        sa.Column('new_field', sa.String(100), nullable=True, server_default='default_value')
    )
    # Backfill data if needed
    op.execute("UPDATE sessions SET new_field = 'computed_value' WHERE new_field IS NULL")

def downgrade():
    op.drop_column('sessions', 'new_field')
```

**Deployment Steps**:
1. Deploy migration (column is nullable or has default)
2. Deploy application that can handle both NULL and populated values
3. Backfill data if needed
4. Make column NOT NULL if required (separate migration)

#### Pattern 2: Renaming a Column (Zero Downtime)

```python
# Migration 001: Add new column
def upgrade():
    op.add_column('sessions',
        sa.Column('new_name', sa.String(100), nullable=True)
    )
    # Copy data
    op.execute("UPDATE sessions SET new_name = old_name")

def downgrade():
    op.drop_column('sessions', 'new_name')

# After deployment, in Migration 002:
def upgrade():
    # Make new column NOT NULL
    op.alter_column('sessions', 'new_name', nullable=False)
    # Drop old column
    op.drop_column('sessions', 'old_name')

def downgrade():
    op.add_column('sessions',
        sa.Column('old_name', sa.String(100), nullable=True)
    )
    op.execute("UPDATE sessions SET old_name = new_name")
    op.alter_column('sessions', 'new_name', nullable=True)
```

**Deployment Steps**:
1. Deploy Migration 001 with dual-write in application
2. Verify data consistency
3. Deploy Migration 002 and remove dual-write

#### Pattern 3: Adding Indexes (Non-Blocking)

```python
# Use CONCURRENTLY to avoid locks
def upgrade():
    # Cannot use op.create_index with concurrent=True in transaction
    # Must use raw SQL
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_started
        ON sessions(user_id, started_at DESC)
    """)

def downgrade():
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_sessions_user_started")
```

**Important**: CONCURRENT index creation cannot run in a transaction. Configure Alembic:

```python
# In migration file
def upgrade():
    connection = op.get_bind()
    connection.execute("commit")  # Exit transaction
    connection.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON table(column)
    """)

# Or use transaction_per_migration in alembic/env.py
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    transaction_per_migration=False,  # For CONCURRENT operations
)
```

#### Pattern 4: Partitioned Table Migration

```python
# Migration to add monthly partition
def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS events_2026_01
        PARTITION OF events
        FOR VALUES FROM ('2026-01-01') TO ('2026-02-01')
    """)

    # Copy indexes from parent
    op.execute("""
        CREATE INDEX IF NOT EXISTS events_2026_01_session_id_idx
        ON events_2026_01(session_id, created_at DESC)
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS events_2026_01")
```

#### Pattern 5: Materialized View Updates

```python
def upgrade():
    # Create new version
    op.execute("""
        CREATE MATERIALIZED VIEW session_summary_v2 AS
        SELECT ... (new definition)
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_session_summary_v2_id
        ON session_summary_v2(session_id)
    """)

    # Swap views atomically
    op.execute("DROP MATERIALIZED VIEW IF EXISTS session_summary_old")
    op.execute("ALTER MATERIALIZED VIEW session_summary RENAME TO session_summary_old")
    op.execute("ALTER MATERIALIZED VIEW session_summary_v2 RENAME TO session_summary")

def downgrade():
    op.execute("ALTER MATERIALIZED VIEW session_summary RENAME TO session_summary_v2")
    op.execute("ALTER MATERIALIZED VIEW session_summary_old RENAME TO session_summary")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS session_summary_v2")
```

### Migration Checklist

Before deploying:
- [ ] Test on staging with production-like data volume
- [ ] Estimate migration time for large tables
- [ ] Check for blocking queries (pg_stat_activity)
- [ ] Backup database
- [ ] Plan rollback strategy
- [ ] Schedule during low-traffic period
- [ ] Monitor replication lag (if applicable)

During deployment:
- [ ] Run migration with verbose logging
- [ ] Monitor database performance metrics
- [ ] Check application error rates
- [ ] Verify data integrity

After deployment:
- [ ] Run ANALYZE on affected tables
- [ ] Check query plan changes
- [ ] Monitor slow query log
- [ ] Update documentation

## Initial Migration

### Creating Initial Schema

```bash
# Create initial migration from schema.sql
alembic revision -m "initial_schema"
```

**Initial migration file**:

```python
"""initial_schema

Revision ID: 001_initial
Create Date: 2025-01-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"btree_gin\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\"")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true')
    )

    # Continue with all tables from schema.sql...
    # (See schema.sql for complete table definitions)

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active'],
                    postgresql_where=sa.text('is_active = true'))

    # Create triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    op.drop_table('users')
    # Drop other tables in reverse order...
```

### Applying Initial Migration

```bash
# Check migration status
alembic current

# Show pending migrations
alembic show

# Apply migration
alembic upgrade head

# Or apply specific revision
alembic upgrade 001_initial

# Rollback
alembic downgrade -1  # Previous version
alembic downgrade base  # Complete rollback
```

## Automated Partition Creation

### Scheduled Job for New Partitions

```python
# create_monthly_partitions.py
from datetime import datetime, timedelta
import psycopg2
import os

def create_next_partition():
    """Create partition for next month if it doesn't exist"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    # Calculate next month
    next_month = (datetime.now() + timedelta(days=32)).replace(day=1)

    # Create partition
    cur.execute("SELECT create_events_partition(%s)", (next_month.date(),))
    conn.commit()

    print(f"Partition created for {next_month.strftime('%Y-%m')}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    create_next_partition()
```

**Cron job** (run monthly):
```bash
0 0 1 * * /path/to/venv/bin/python /path/to/create_monthly_partitions.py
```

## Testing Migrations

### Testing Framework

```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
import os

@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", os.getenv('TEST_DATABASE_URL'))
    return config

@pytest.fixture
def db_engine():
    engine = create_engine(os.getenv('TEST_DATABASE_URL'))
    yield engine
    engine.dispose()

def test_upgrade_downgrade(alembic_config, db_engine):
    """Test migration up and down"""
    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Verify tables exist
    inspector = sa.inspect(db_engine)
    tables = inspector.get_table_names()
    assert 'sessions' in tables
    assert 'events' in tables

    # Downgrade
    command.downgrade(alembic_config, "base")

    # Verify tables removed
    inspector = sa.inspect(db_engine)
    tables = inspector.get_table_names()
    assert 'sessions' not in tables

def test_data_integrity_after_migration(alembic_config, db_engine):
    """Test data survives migration"""
    # Setup initial schema
    command.upgrade(alembic_config, "001_initial")

    # Insert test data
    with db_engine.connect() as conn:
        conn.execute("""
            INSERT INTO users (email, username)
            VALUES ('test@example.com', 'testuser')
        """)
        conn.commit()

    # Apply next migration
    command.upgrade(alembic_config, "head")

    # Verify data still exists
    with db_engine.connect() as conn:
        result = conn.execute("""
            SELECT * FROM users WHERE email = 'test@example.com'
        """)
        assert result.rowcount == 1
```

### Running Tests

```bash
# Set test database
export TEST_DATABASE_URL="postgresql://user:pass@localhost/test_agente_films"

# Run migration tests
pytest tests/test_migrations.py -v
```

## Monitoring Migrations

### Migration Metrics

```python
# migration_monitor.py
import time
import psycopg2
import logging

class MigrationMonitor:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)
        self.logger = logging.getLogger(__name__)

    def monitor_table_locks(self):
        """Check for blocking locks during migration"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                blocked_locks.pid AS blocked_pid,
                blocked_activity.usename AS blocked_user,
                blocking_locks.pid AS blocking_pid,
                blocking_activity.usename AS blocking_user,
                blocked_activity.query AS blocked_statement,
                blocking_activity.query AS blocking_statement
            FROM pg_catalog.pg_locks blocked_locks
            JOIN pg_catalog.pg_stat_activity blocked_activity
                ON blocked_activity.pid = blocked_locks.pid
            JOIN pg_catalog.pg_locks blocking_locks
                ON blocking_locks.locktype = blocked_locks.locktype
                AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                AND blocking_locks.pid != blocked_locks.pid
            JOIN pg_catalog.pg_stat_activity blocking_activity
                ON blocking_activity.pid = blocking_locks.pid
            WHERE NOT blocked_locks.granted
        """)

        locks = cur.fetchall()
        if locks:
            self.logger.warning(f"Found {len(locks)} blocking locks")
            for lock in locks:
                self.logger.warning(f"Blocked PID: {lock[0]}, Blocking PID: {lock[2]}")

        cur.close()
        return locks

    def estimate_migration_time(self, table_name):
        """Estimate time for full table scan"""
        cur = self.conn.cursor()
        cur.execute(f"""
            SELECT
                pg_size_pretty(pg_total_relation_size('{table_name}')),
                pg_total_relation_size('{table_name}'),
                n_live_tup
            FROM pg_stat_user_tables
            WHERE relname = '{table_name}'
        """)

        size_pretty, size_bytes, row_count = cur.fetchone()

        # Rough estimate: 50MB/sec sequential scan
        estimated_seconds = size_bytes / (50 * 1024 * 1024)

        self.logger.info(f"Table {table_name}: {size_pretty}, {row_count:,} rows")
        self.logger.info(f"Estimated scan time: {estimated_seconds:.1f} seconds")

        cur.close()
        return estimated_seconds
```

## Best Practices

1. **Always Test First**
   - Test on staging with production data volume
   - Run migrations during maintenance windows for critical changes

2. **Use Transactions Wisely**
   - Most DDL in PostgreSQL is transactional
   - Exception: CREATE INDEX CONCURRENTLY requires no transaction

3. **Monitor Performance**
   - Watch for lock contention
   - Check query performance after schema changes
   - Run ANALYZE after large data changes

4. **Version Control**
   - Commit migration files to git
   - Include both upgrade and downgrade paths
   - Document breaking changes

5. **Partition Management**
   - Pre-create partitions before needed
   - Automate partition creation
   - Set retention policies

6. **Materialized Views**
   - Refresh during low-traffic periods
   - Use CONCURRENTLY when possible
   - Consider refresh frequency vs query performance
