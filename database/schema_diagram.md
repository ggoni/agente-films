# Database Schema Visual Diagram

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-AGENT FILMMAKING SYSTEM                         │
│                          PostgreSQL Database Schema                          │
└─────────────────────────────────────────────────────────────────────────────┘


┌──────────────────┐
│     USERS        │
├──────────────────┤
│ id (PK)          │
│ email            │◄───────────────────────────────┐
│ username         │                                │
│ created_at       │                                │
│ metadata (JSONB) │                                │
│ is_active        │                                │
└──────────────────┘                                │
        │                                           │
        │ 1:N                                       │
        ▼                                           │
┌──────────────────────────────┐                   │
│        SESSIONS              │                   │
├──────────────────────────────┤                   │
│ id (PK)                      │                   │
│ user_id (FK) ────────────────┼───────────────────┘
│ session_name                 │
│                              │
│ ┌──────────────────────────┐ │
│ │ ADK STATE MANAGEMENT     │ │
│ ├──────────────────────────┤ │
│ │ state (JSONB) ★          │ │  ★ ADK session state dictionary
│ │ agent_config (JSONB)     │ │     for session reconstruction
│ │ root_agent_name          │ │
│ └──────────────────────────┘ │
│                              │
│ status (active/completed)    │
│ total_events                 │
│ total_tool_calls             │
│ total_tokens_used            │
│ started_at, ended_at         │
└──────────────────────────────┘
        │
        │ 1:N
        ├───────────────────────────────────────┐
        │                                       │
        │                                       │
┌───────▼──────────────┐               ┌────────▼───────────────┐
│     QUESTIONS        │               │    FILM PROJECTS       │
├──────────────────────┤               ├────────────────────────┤
│ id (PK)              │               │ id (PK)                │
│ session_id (FK)      │               │ session_id (FK)        │
│ user_id (FK)         │               │ user_id (FK)           │
│ content (TEXT)       │               │                        │
│ sequence_number      │               │ title                  │
│ asked_at             │               │ historical_subject     │
│ context (JSONB)      │               │ genre, status          │
└──────────────────────┘               │                        │
        │                              │ ┌────────────────────┐ │
        │ 1:N                          │ │ DENORMALIZED       │ │
        │                              │ │ FROM STATE         │ │
        ▼                              │ ├────────────────────┤ │
┌──────────────────────────────────┐  │ │ plot_outline (TEXT)│ │
│   INFERENTIAL REASONING          │  │ │ research_summary   │ │
├──────────────────────────────────┤  │ │ casting_report     │ │
│ id (PK)                          │  │ │ box_office_report  │ │
│ session_id (FK)                  │  │ └────────────────────┘ │
│ question_id (FK) ────────────────┤  │                        │
│ answer_id (FK)                   │  │ output_file_path       │
│                                  │  │ metadata (JSONB)       │
│ agent_name                       │  └────────────────────────┘
│ agent_role                       │
│ reasoning_type                   │
│   - research                     │
│   - planning                     │               │
│   - critique                     │               │ 1:N
│   - analysis                     │               │
│   - decision                     │               ▼
│                                  │  ┌──────────────────────────────────┐
│ content (TEXT)                   │  │  EVENTS (PARTITIONED BY MONTH)   │
│ state_delta (JSONB) ★            │  ├──────────────────────────────────┤
│ sequence_number                  │  │ id (PK), created_at (PK)         │
│ created_at                       │  │ session_id (FK)                  │
└──────────────────────────────────┘  │                                  │
        │                             │ event_type:                      │
        │ N:1                         │   - user_message                 │
        │                             │   - agent_response               │
        ▼                             │   - tool_call                    │
┌──────────────────────┐              │   - tool_response                │
│      ANSWERS         │              │   - agent_transfer               │
├──────────────────────┤              │   - state_update                 │
│ id (PK)              │              │   - loop_iteration               │
│ session_id (FK)      │              │   - error                        │
│ question_id (FK)     │              │                                  │
│                      │              │ agent_name                       │
│ content (TEXT)       │              │ parent_agent_name                │
│ agent_name           │              │                                  │
│ agent_type           │              │ event_data (JSONB)               │
│ sequence_number      │              │ state_delta (JSONB) ★            │
│                      │              │                                  │
│ tokens_used          │              │ tool_name                        │
│ response_time_ms     │              │ tool_input (JSONB)               │
│ answered_at          │              │ tool_output (JSONB)              │
└──────────────────────┘              │                                  │
                                      │ duration_ms                      │
┌──────────────────────┐              │ tokens_used                      │
│  AGENT TRANSFERS     │              │ error_message                    │
├──────────────────────┤              └──────────────────────────────────┘
│ id (PK)              │                     │
│ session_id (FK)      │                     │
│ event_id             │              ┌──────┴───────┬───────────┬────────┐
│                      │              │              │           │        │
│ from_agent           │        events_2025_01  events_2025_02  ...  events_2025_12
│ to_agent             │         (Partition)    (Partition)           (Partition)
│ transfer_reason      │
│ transferred_at       │
└──────────────────────┘

┌──────────────────────┐
│  STATE SNAPSHOTS     │
├──────────────────────┤
│ id (PK)              │
│ session_id (FK)      │
│                      │
│ snapshot_type        │
│   - manual           │
│   - automatic        │
│   - checkpoint       │
│                      │
│ state (JSONB) ★      │
│ event_sequence_num   │
│ description          │
│ created_at           │
└──────────────────────┘

┌──────────────────────┐
│   SYSTEM CONFIG      │
├──────────────────────┤
│ key (PK)             │
│ value (JSONB)        │
│ description          │
│ updated_at           │
└──────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                         MATERIALIZED VIEWS (Analytics)
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────┐
│      SESSION_SUMMARY            │
├─────────────────────────────────┤
│ session_id (UNIQUE)             │
│ user_id                         │
│ session_name                    │
│ status                          │
│ started_at, ended_at            │
│ duration_seconds                │
│                                 │
│ total_events                    │
│ total_questions                 │
│ total_answers                   │
│ total_reasoning_events          │
│                                 │
│ agents_used (ARRAY)             │
│ film_project_id                 │
│ film_title                      │
│ film_status                     │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     AGENT_PERFORMANCE           │
├─────────────────────────────────┤
│ agent_name (UNIQUE)             │
│ total_responses                 │
│ avg_tokens                      │
│ avg_response_time_ms            │
│ first_used                      │
│ last_used                       │
│ sessions_count                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      DAILY_ACTIVITY             │
├─────────────────────────────────┤
│ activity_date (UNIQUE)          │
│ sessions_count                  │
│ total_events                    │
│ tool_calls_count                │
│ total_tokens                    │
│ avg_event_duration_ms           │
└─────────────────────────────────┘
```

## Data Flow: Question → Reasoning → Answer

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CONVERSATION WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

    USER INPUT
        │
        ▼
    ┌───────────────────────────────┐
    │      QUESTION                 │
    ├───────────────────────────────┤
    │ Sequence: 1                   │
    │ Content: "Film about ancient  │
    │          doctor"              │
    └───────────────────────────────┘
                │
                ▼
    ┌───────────────────────────────────────────────────────────┐
    │               INFERENTIAL REASONING                       │
    └───────────────────────────────────────────────────────────┘
                │
                ├──► ┌──────────────────────────────────┐
                │    │ Agent: researcher                │
                │    │ Type: research                   │
                │    │ Content: "Found Zhang Zhongjing │
                │    │          (150-219 CE)..."        │
                │    │ State Delta:                     │
                │    │   {"research": [...]}            │
                │    └──────────────────────────────────┘
                │
                ├──► ┌──────────────────────────────────┐
                │    │ Agent: screenwriter              │
                │    │ Type: planning                   │
                │    │ Content: "Creating three-act     │
                │    │          structure..."           │
                │    │ State Delta:                     │
                │    │   {"PLOT_OUTLINE": "..."}        │
                │    └──────────────────────────────────┘
                │
                └──► ┌──────────────────────────────────┐
                     │ Agent: critic                    │
                     │ Type: critique                   │
                     │ Content: "Needs more depth       │
                     │          in Act II"              │
                     │ State Delta:                     │
                     │   {"CRITICAL_FEEDBACK": "..."}   │
                     └──────────────────────────────────┘
                │
                ▼
    ┌───────────────────────────────┐
    │         ANSWER                │
    ├───────────────────────────────┤
    │ Agent: file_writer            │
    │ Content: "Plot saved to       │
    │          file..."             │
    │ Tokens: 2500                  │
    │ Response Time: 3200ms         │
    └───────────────────────────────┘
                │
                ▼
           USER SEES RESULT


    ═══════════════════════════════════════════════════════════════
                     SESSION STATE EVOLUTION
    ═══════════════════════════════════════════════════════════════

    Initial State:  {}

    After Research: {
                      "research": ["Zhang Zhongjing was..."]
                    }

    After Writing:  {
                      "research": ["Zhang Zhongjing was..."],
                      "PLOT_OUTLINE": "Act I: Young Zhang..."
                    }

    After Critique: {
                      "research": ["Zhang Zhongjing was..."],
                      "PLOT_OUTLINE": "Act I: Young Zhang...",
                      "CRITICAL_FEEDBACK": "Add more depth..."
                    }
```

## Index Strategy Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          INDEX TYPES                                     │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────┐
│   B-TREE INDEXES      │  Default for most columns
├───────────────────────┤
│ - Primary Keys        │  Fast equality, range queries
│ - Foreign Keys        │  Sorted data
│ - Timestamps          │
│ - Sequence Numbers    │
└───────────────────────┘

┌───────────────────────────────────┐
│   GIN INDEXES (JSONB)             │
├───────────────────────────────────┤
│ jsonb_path_ops (PREFERRED)        │  30% smaller, faster
│   - state @> '{"key": "value"}'   │  Containment only
│                                   │
│ jsonb_ops (FULL SUPPORT)          │  All JSONB operators
│   - state ? 'key'                 │  Key existence
│   - state ?& array['k1','k2']     │  Multiple keys
└───────────────────────────────────┘

┌───────────────────────────────────┐
│   GIN INDEXES (TRIGRAM)           │
├───────────────────────────────────┤
│ gin_trgm_ops                      │  Fuzzy text search
│   - title % 'search'              │  Similarity matching
│   - SIMILARITY(title, 'search')   │  Ranking
└───────────────────────────────────┘

┌───────────────────────────────────┐
│   PARTIAL INDEXES                 │
├───────────────────────────────────┤
│ WHERE status = 'active'           │  Index subset only
│ WHERE tool_name IS NOT NULL       │  50% smaller
│                                   │  Faster updates
└───────────────────────────────────┘

┌───────────────────────────────────┐
│   COVERING INDEXES                │
├───────────────────────────────────┤
│ (user_id, started_at DESC)        │  Index-only scans
│ INCLUDE (session_name, status)    │  No table lookup
└───────────────────────────────────┘
```

## Partition Strategy Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVENTS TABLE PARTITIONING                             │
└─────────────────────────────────────────────────────────────────────────┘

                         EVENTS (Parent Table)
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
  ┌───────────┐          ┌───────────┐           ┌───────────┐
  │ 2025-01   │          │ 2025-02   │           │ 2025-03   │
  ├───────────┤          ├───────────┤           ├───────────┤
  │ 500K rows │          │ 480K rows │           │ 510K rows │
  │ 2.1 GB    │          │ 2.0 GB    │           │ 2.2 GB    │
  └───────────┘          └───────────┘           └───────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                    QUERY WITH TIME FILTER
                                │
                    WHERE created_at >= '2025-01-01'
                      AND created_at < '2025-02-01'
                                │
                    ┌───────────┴───────────┐
                    │   PARTITION PRUNING   │
                    │   Only scans 2025-01  │
                    │   90%+ reduction      │
                    └───────────────────────┘


    LIFECYCLE:

    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
    │ Created  │────►│  Active  │────►│ Archived │────►│ Dropped  │
    │ Month -1 │     │ 0-90 days│     │90-180 day│     │  180+ d  │
    └──────────┘     └──────────┘     └──────────┘     └──────────┘
```

## Performance Optimization Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    QUERY OPTIMIZATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

    Query Arrives
        │
        ▼
    ┌─────────────────────┐
    │ Connection Pool     │  PgBouncer: Reuse connections
    │ (PgBouncer)         │  Avoid connection overhead
    └─────────────────────┘
        │
        ▼
    ┌─────────────────────┐
    │ Query Planner       │  Choose optimal execution plan
    └─────────────────────┘  Consider indexes, statistics
        │
        ├──► Partition Pruning (if partitioned table)
        │    └──► Scan only relevant partitions
        │
        ├──► Index Selection
        │    ├──► B-tree for equality/range
        │    ├──► GIN for JSONB/full-text
        │    └──► Partial for filtered queries
        │
        ▼
    ┌─────────────────────┐
    │ Shared Buffers      │  In-memory cache
    │ (PostgreSQL Cache)  │  99%+ hit ratio
    └─────────────────────┘
        │
        │ Cache Miss?
        ▼
    ┌─────────────────────┐
    │ Disk I/O (SSD)      │  Fast sequential reads
    └─────────────────────┘
        │
        ▼
    ┌─────────────────────┐
    │ Materialized View?  │  Pre-aggregated results
    └─────────────────────┘  Refresh every 6 hours
        │
        ▼
    Results Returned


    OPTIMIZATION LAYERS:

    Application Layer
    ├─ Connection Pooling (PgBouncer)
    ├─ Query Caching (Redis)
    └─ Batch Operations

    Database Layer
    ├─ Indexes (B-tree, GIN, Partial, Covering)
    ├─ Partitioning (Partition Pruning)
    ├─ Materialized Views (Pre-aggregation)
    └─ Shared Buffers (Cache)

    Storage Layer
    ├─ SSD for fast I/O
    └─ Tablespace optimization
```

## State Management Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ADK STATE DICTIONARY                                │
└─────────────────────────────────────────────────────────────────────────┘

    sessions.state (JSONB)
    {
        "PLOT_OUTLINE": "Act I: Young Zhang witnesses...",

        "research": [
            "Zhang Zhongjing (150-219 CE)",
            "Chinese physician during Han Dynasty",
            "Wrote Treatise on Cold Damage Disorders"
        ],

        "CRITICAL_FEEDBACK": "Add more emotional depth...",

        "attractions": ["Sphinx", "Pyramids"],

        "iteration_count": 3,

        "agent_states": {
            "researcher": {"last_query": "Zhang Zhongjing"},
            "screenwriter": {"draft_version": 2}
        }
    }


    QUERY PATTERNS:

    ┌────────────────────────────────────────────┐
    │ Containment (@>)                           │
    ├────────────────────────────────────────────┤
    │ WHERE state @> '{"PLOT_OUTLINE": "..."}'  │
    │ Index: GIN jsonb_path_ops                  │
    └────────────────────────────────────────────┘

    ┌────────────────────────────────────────────┐
    │ Key Existence (?)                          │
    ├────────────────────────────────────────────┤
    │ WHERE state ? 'PLOT_OUTLINE'              │
    │ Index: GIN jsonb_ops                       │
    └────────────────────────────────────────────┘

    ┌────────────────────────────────────────────┐
    │ Value Extraction (->)                      │
    ├────────────────────────────────────────────┤
    │ SELECT state->'research' AS research       │
    │ SELECT state->>'PLOT_OUTLINE' AS plot     │
    └────────────────────────────────────────────┘

    ┌────────────────────────────────────────────┐
    │ Array Operations                           │
    ├────────────────────────────────────────────┤
    │ WHERE jsonb_array_length(                  │
    │         state->'research') > 0             │
    └────────────────────────────────────────────┘
```

## Legend

```
┌─────────────────────────────────────────────────────────────────┐
│ SYMBOLS                                                          │
├─────────────────────────────────────────────────────────────────┤
│ (PK)  = Primary Key                                             │
│ (FK)  = Foreign Key                                             │
│ ★     = Critical for ADK state management                       │
│ ◄──   = Foreign key relationship                                │
│ 1:N   = One-to-many relationship                                │
│ N:1   = Many-to-one relationship                                │
│ ▼     = Data flow direction                                     │
└─────────────────────────────────────────────────────────────────┘
```
