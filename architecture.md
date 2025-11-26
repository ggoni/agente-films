# Multi-Agent Filmmaking System - Architecture

> **Version**: 1.0.0
> **Date**: 2025-11-25
> **Status**: Design Phase

## Executive Summary

This document describes the complete architecture for a multi-agent filmmaking system that uses Google's Agent Development Kit (ADK) to orchestrate specialized AI agents in creating film pitch documents. The system employs a hierarchical multi-agent approach where agents collaborate through iterative workflows to research historical figures, write screenplays, provide critiques, and generate production reports.

**Key Technologies**:
- **Agent Framework**: Google ADK (LlmAgent, SequentialAgent, LoopAgent, ParallelAgent)
- **LLM Gateway**: LiteLLM Proxy (multi-provider abstraction)
- **Backend**: Python 3.12, FastAPI, PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Deployment**: Docker, Docker Compose

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [System Architecture](#3-system-architecture)
4. [Agent Architecture](#4-agent-architecture)
5. [Data Architecture](#5-data-architecture)
6. [Service Architecture](#6-service-architecture)
7. [API Architecture](#7-api-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
   - 8.5 [Docker Compose vs Kubernetes: Decision Matrix](#85-docker-compose-vs-kubernetes-decision-matrix)
9. [Security Architecture](#9-security-architecture)
10. [Scalability Strategy](#10-scalability-strategy)
11. [Implementation Guide](#11-implementation-guide)

---

## 1. System Overview

### 1.1 Purpose

The Multi-Agent Filmmaking System automates the creative process of developing film pitch documents by coordinating specialized AI agents that:
- Research historical figures and topics
- Write compelling plot outlines
- Provide critical feedback for iterative improvement
- Analyze box office potential
- Generate casting suggestions
- Compile comprehensive pitch documents

### 1.2 Core Features

- **Multi-Agent Workflows**: Hierarchical agent orchestration using ADK
- **Iterative Refinement**: Loop-based workflows for quality improvement
- **Parallel Processing**: Concurrent execution of independent tasks
- **State Management**: Persistent session state across agent interactions
- **Multi-LLM Support**: Flexible LLM provider switching via LiteLLM
- **Real-time Streaming**: WebSocket-based streaming responses
- **Comprehensive Tracking**: Questions, answers, and reasoning persistence

### 1.3 System Diagram

```mermaid
graph TB
    User[User/Browser] --> Frontend[React Frontend<br/>Port 3000]
    Frontend -->|HTTP/WS| API[FastAPI Backend<br/>Port 8000]

    API --> SessionSvc[Session Service]
    API --> AgentSvc[Agent Service]
    API --> ProjSvc[Project Service]

    SessionSvc --> DB[(PostgreSQL<br/>Port 5432)]
    AgentSvc --> ADKRunner[ADK Runner]
    ProjSvc --> DB

    ADKRunner --> RootAgent[Root Agent<br/>greeter]
    ADKRunner --> SessionMgr[Session Manager]
    ADKRunner --> LiteLLMClient[LiteLLM Client]

    RootAgent --> FilmTeam[Film Concept Team<br/>SequentialAgent]

    FilmTeam --> WritersRoom[Writers Room<br/>LoopAgent]
    FilmTeam --> PreProd[Preproduction Team<br/>ParallelAgent]
    FilmTeam --> FileWriter[File Writer<br/>Agent]

    WritersRoom --> Researcher[Researcher<br/>Agent]
    WritersRoom --> Screenwriter[Screenwriter<br/>Agent]
    WritersRoom --> Critic[Critic<br/>Agent]

    PreProd --> BoxOffice[Box Office<br/>Analyst]
    PreProd --> Casting[Casting<br/>Director]

    Researcher -->|Wikipedia API| External1[External APIs]

    LiteLLMClient -->|OpenAI Compatible| LiteLLMProxy[LiteLLM Proxy<br/>Port 4000]

    LiteLLMProxy --> Gemini[Vertex AI<br/>Gemini]
    LiteLLMProxy --> OpenAI[OpenAI<br/>GPT-4o]
    LiteLLMProxy --> Claude[Anthropic<br/>Claude]
    LiteLLMProxy --> RedisCache[Redis Cache<br/>Port 6379]

    SessionMgr --> DB

    style User fill:#e1f5ff
    style Frontend fill:#bbdefb
    style API fill:#90caf9
    style DB fill:#ffd54f
    style LiteLLMProxy fill:#ffb74d
    style RedisCache fill:#ffccbc
```

---

## 2. Architecture Principles

### 2.1 Design Principles

1. **ADK-Native**: All agent logic uses Google ADK primitives exclusively
2. **LLM Agnostic**: LiteLLM proxy abstracts LLM provider details
3. **State Persistence**: All questions, answers, and reasoning stored in PostgreSQL
4. **Stateless API**: FastAPI instances are stateless, enabling horizontal scaling
5. **Docker First**: All services containerized for consistent deployment
6. **Separation of Concerns**: Clear boundaries between agents, services, and data layers
7. **Event-Driven**: Comprehensive event tracking for observability and debugging

### 2.2 Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Agent Framework** | Google ADK | Native hierarchical patterns, workflow agents, session state |
| **LLM Gateway** | LiteLLM Proxy | Multi-provider support, cost tracking, caching |
| **API Framework** | FastAPI | High performance, async support, auto-documentation |
| **Database** | PostgreSQL 16 | ACID compliance, JSONB support, mature ecosystem |
| **Caching** | Redis 7 | Session state, LLM response caching |
| **Frontend** | React + TypeScript | Component reusability, type safety |
| **Containerization** | Docker | Consistent environments, easy deployment |
| **Package Manager** | uv | Fast, reliable Python dependency management |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```mermaid
C4Context
    title System Context Diagram - Multi-Agent Filmmaking System

    Person(user, "Filmmaker", "Creates film pitch<br/>documents using AI agents")

    System(filmmaking, "Multi-Agent<br/>Filmmaking System", "Orchestrates AI agents<br/>to create film pitches")

    System_Ext(gemini, "Vertex AI Gemini", "Primary LLM provider")
    System_Ext(openai, "OpenAI", "Alternative LLM provider")
    System_Ext(claude, "Anthropic Claude", "Alternative LLM provider")
    System_Ext(wikipedia, "Wikipedia API", "Historical research data")

    Rel(user, filmmaking, "Uses", "HTTPS/WebSocket")
    Rel(filmmaking, gemini, "Calls", "HTTPS")
    Rel(filmmaking, openai, "Calls", "HTTPS")
    Rel(filmmaking, claude, "Calls", "HTTPS")
    Rel(filmmaking, wikipedia, "Queries", "HTTPS")
```

### 3.2 Container Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end

    subgraph "Application Layer"
        Frontend[React Frontend<br/>Vite Dev Server<br/>:3000]
        API[FastAPI Backend<br/>Uvicorn<br/>:8000]
    end

    subgraph "Agent Layer"
        ADK[ADK Runner<br/>Agent Orchestration]
        LiteLLM[LiteLLM Proxy<br/>LLM Gateway<br/>:4000]
    end

    subgraph "Data Layer"
        Postgres[(PostgreSQL<br/>:5432)]
        Redis[(Redis<br/>:6379)]
    end

    subgraph "External Services"
        VertexAI[Vertex AI Gemini]
        OpenAIAPI[OpenAI API]
        ClaudeAPI[Anthropic API]
    end

    Browser -->|HTTP/WS| Frontend
    Frontend -->|REST API| API
    API -->|Execute Agents| ADK
    ADK -->|LLM Calls| LiteLLM
    API -->|Read/Write| Postgres
    API -->|Cache| Redis
    LiteLLM -->|Cache| Redis
    LiteLLM -->|API Calls| VertexAI
    LiteLLM -->|API Calls| OpenAIAPI
    LiteLLM -->|API Calls| ClaudeAPI
    ADK -->|State Persistence| Postgres

    style Browser fill:#e3f2fd
    style Frontend fill:#bbdefb
    style API fill:#90caf9
    style ADK fill:#64b5f6
    style LiteLLM fill:#ffb74d
    style Postgres fill:#ffd54f
    style Redis fill:#ffccbc
```

---

## 4. Agent Architecture

### 4.1 Agent Hierarchy

The system uses ADK's hierarchical agent structure with workflow orchestrators:

```mermaid
graph TB
    Root[Root Agent: greeter<br/>LlmAgent]

    Root --> FilmTeam[film_concept_team<br/>SequentialAgent]

    FilmTeam -->|Step 1| WritersRoom[writers_room<br/>LoopAgent<br/>max_iterations: 5]
    FilmTeam -->|Step 2| PreProd[preproduction_team<br/>ParallelAgent]
    FilmTeam -->|Step 3| FileWriter[file_writer<br/>LlmAgent]

    WritersRoom -->|Loop| Researcher[researcher<br/>LlmAgent<br/>Tools: wikipedia_search<br/>append_to_state]
    WritersRoom -->|Loop| Screenwriter[screenwriter<br/>LlmAgent<br/>output_key: PLOT_OUTLINE<br/>Tools: append_to_state]
    WritersRoom -->|Loop| Critic[critic<br/>LlmAgent<br/>Tools: append_to_state<br/>exit_loop]

    PreProd -->|Parallel| BoxOffice[box_office_researcher<br/>LlmAgent<br/>output_key: box_office_report]
    PreProd -->|Parallel| CastingAgent[casting_agent<br/>LlmAgent<br/>output_key: casting_report]

    FileWriter --> Output[Output: Film Pitch Document]

    style Root fill:#e1bee7
    style FilmTeam fill:#ce93d8
    style WritersRoom fill:#ba68c8
    style PreProd fill:#ab47bc
    style FileWriter fill:#9c27b0
    style Researcher fill:#81c784
    style Screenwriter fill:#66bb6a
    style Critic fill:#4caf50
    style BoxOffice fill:#42a5f5
    style CastingAgent fill:#2196f3
```

### 4.2 Agent Workflow

```mermaid
sequenceDiagram
    participant User
    participant Greeter as Root Agent<br/>(greeter)
    participant FilmTeam as Film Concept Team<br/>(SequentialAgent)
    participant WritersRoom as Writers Room<br/>(LoopAgent)
    participant Researcher
    participant Screenwriter
    participant Critic
    participant PreProd as Preproduction Team<br/>(ParallelAgent)
    participant BoxOffice
    participant Casting
    participant FileWriter

    User->>Greeter: "Create film about Ada Lovelace"
    Greeter->>FilmTeam: Transfer to film_concept_team

    FilmTeam->>WritersRoom: Execute Step 1

    Note over WritersRoom: Loop Iteration 1
    WritersRoom->>Researcher: Research Ada Lovelace
    Researcher-->>WritersRoom: Save research to state
    WritersRoom->>Screenwriter: Write plot outline
    Screenwriter-->>WritersRoom: Save PLOT_OUTLINE to state
    WritersRoom->>Critic: Review plot
    Critic-->>WritersRoom: Add CRITICAL_FEEDBACK to state

    Note over WritersRoom: Loop Iteration 2
    WritersRoom->>Researcher: Address feedback gaps
    Researcher-->>WritersRoom: Append research
    WritersRoom->>Screenwriter: Revise outline
    Screenwriter-->>WritersRoom: Update PLOT_OUTLINE
    WritersRoom->>Critic: Review again
    Critic-->>WritersRoom: Call exit_loop (approved)

    WritersRoom-->>FilmTeam: Loop complete

    FilmTeam->>PreProd: Execute Step 2

    par Parallel Execution
        PreProd->>BoxOffice: Analyze box office
        BoxOffice-->>PreProd: Save box_office_report
    and
        PreProd->>Casting: Generate casting ideas
        Casting-->>PreProd: Save casting_report
    end

    PreProd-->>FilmTeam: Parallel complete

    FilmTeam->>FileWriter: Execute Step 3
    FileWriter-->>FilmTeam: Write pitch document

    FilmTeam-->>Greeter: Workflow complete
    Greeter-->>User: "Film pitch created!"
```

### 4.3 Session State Flow

```mermaid
stateDiagram-v2
    [*] --> SessionCreated: User starts new project

    SessionCreated --> ResearchPhase: Root agent transfers

    ResearchPhase --> WritingPhase: Researcher adds to state['research']

    WritingPhase --> CritiquePhase: Screenwriter sets state['PLOT_OUTLINE']

    CritiquePhase --> ResearchPhase: Critic adds state['CRITICAL_FEEDBACK']
    CritiquePhase --> AnalysisPhase: Critic calls exit_loop

    AnalysisPhase --> BoxOfficeAnalysis: ParallelAgent spawns
    AnalysisPhase --> CastingAnalysis: ParallelAgent spawns

    BoxOfficeAnalysis --> DocumentGeneration: Sets state['box_office_report']
    CastingAnalysis --> DocumentGeneration: Sets state['casting_report']

    DocumentGeneration --> [*]: File written, session complete

    note right of SessionCreated
        state = {
            'research': [],
            'CRITICAL_FEEDBACK': [],
            'PLOT_OUTLINE': None,
            'box_office_report': None,
            'casting_report': None
        }
    end note

    note right of DocumentGeneration
        Final state persisted
        to PostgreSQL for
        session restoration
    end note
```

### 4.4 Agent Definitions

#### Root Agent: Greeter

```python
greeter = Agent(
    name="greeter",
    model="gpt-4o-mini",  # Via LiteLLM proxy
    description="Welcomes user and gathers requirements.",
    instruction="""
    Welcome the user to the Film Concept Generator.

    Ask them to describe the type of historical character or topic
    they'd like to base a biographical film on.

    Once you have their request, transfer to 'film_concept_team'.
    """,
    sub_agents=[film_concept_team],
    before_model_callback=log_query,
    after_model_callback=log_response
)
```

#### Sequential Workflow: Film Concept Team

```python
film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Complete film pitch development workflow.",
    sub_agents=[
        writers_room,      # Step 1: Iterative writing
        preproduction_team,  # Step 2: Parallel analysis
        file_writer        # Step 3: Document generation
    ]
)
```

#### Loop Workflow: Writers Room

```python
writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve plot outline.",
    sub_agents=[
        researcher,
        screenwriter,
        critic
    ],
    max_iterations=5  # Safety limit
)
```

#### Parallel Workflow: Preproduction Team

```python
preproduction_team = ParallelAgent(
    name="preproduction_team",
    description="Generates box office and casting reports in parallel.",
    sub_agents=[
        box_office_analyst,
        casting_director
    ]
)
```

---

## 5. Data Architecture

### 5.1 Database Schema

```mermaid
erDiagram
    SESSIONS ||--o{ FILM_PROJECTS : contains
    SESSIONS ||--o{ QUESTIONS : has
    SESSIONS ||--o{ ANSWERS : has
    SESSIONS ||--o{ INFERENTIAL_REASONING : has
    SESSIONS ||--o{ AGENT_EVENTS : tracks
    SESSIONS ||--o{ SESSION_STATES : snapshots

    QUESTIONS ||--o| ANSWERS : generates
    ANSWERS ||--o{ INFERENTIAL_REASONING : explains
    FILM_PROJECTS ||--o{ QUESTIONS : about
    FILM_PROJECTS ||--o{ ANSWERS : about

    SESSIONS {
        uuid id PK
        timestamp created_at
        timestamp updated_at
        varchar status
        jsonb metadata
    }

    FILM_PROJECTS {
        uuid id PK
        uuid session_id FK
        varchar title
        varchar subject
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    QUESTIONS {
        uuid id PK
        uuid session_id FK
        uuid project_id FK
        text question_text
        varchar agent_name
        timestamp created_at
        jsonb metadata
    }

    ANSWERS {
        uuid id PK
        uuid question_id FK
        uuid session_id FK
        uuid project_id FK
        varchar agent_name
        text answer_text
        timestamp created_at
        jsonb metadata
    }

    INFERENTIAL_REASONING {
        uuid id PK
        uuid answer_id FK
        uuid session_id FK
        varchar agent_name
        varchar reasoning_type
        text reasoning_text
        jsonb tool_calls
        timestamp created_at
        jsonb metadata
    }

    SESSION_STATES {
        uuid id PK
        uuid session_id FK
        varchar state_key
        jsonb state_value
        integer version
        timestamp created_at
    }

    AGENT_EVENTS {
        uuid id PK
        uuid session_id FK
        varchar agent_name
        varchar event_type
        jsonb event_data
        timestamp created_at
    }
```

### 5.2 Data Flow

```mermaid
flowchart TB
    UserInput[User Input:<br/>Create film about Ada Lovelace]

    UserInput --> SaveQuestion[Save Question<br/>to questions table]

    SaveQuestion --> ADKExec[ADK Runner Executes<br/>Agent Workflow]

    ADKExec --> ResearcherCall[Researcher Agent<br/>Calls Wikipedia Tool]

    ResearcherCall --> SaveReasoning1[Save Inferential Reasoning:<br/>wikipedia search for 'Ada Lovelace']

    SaveReasoning1 --> UpdateState1[Update Session State:<br/>state.research = [...]]

    UpdateState1 --> ScreenwriterCall[Screenwriter Agent<br/>Generates Plot Outline]

    ScreenwriterCall --> SaveReasoning2[Save Inferential Reasoning:<br/>plot structure analysis]

    SaveReasoning2 --> UpdateState2[Update Session State:<br/>state.PLOT_OUTLINE = '...']

    UpdateState2 --> SaveAnswer[Save Answer<br/>to answers table]

    SaveAnswer --> StateSnapshot[Save State Snapshot<br/>to session_states]

    StateSnapshot --> Return[Return Response<br/>to User]

    style UserInput fill:#e1f5ff
    style SaveQuestion fill:#b3e5fc
    style ADKExec fill:#81d4fa
    style UpdateState1 fill:#ffd54f
    style UpdateState2 fill:#ffd54f
    style StateSnapshot fill:#ffd54f
    style SaveReasoning1 fill:#c5e1a5
    style SaveReasoning2 fill:#c5e1a5
    style SaveAnswer fill:#aed581
    style Return fill:#9ccc65
```

### 5.3 State Persistence Strategy

```mermaid
graph TB
    subgraph "ADK In-Memory State"
        State[session.state<br/>Dictionary]
        State --> Research[state['research']]
        State --> Plot[state['PLOT_OUTLINE']]
        State --> Feedback[state['CRITICAL_FEEDBACK']]
    end

    subgraph "PostgreSQL Persistence"
        SessionStates[(session_states table)]
        Events[(agent_events table)]
    end

    State -->|On every agent completion| SaveSnapshot[Save State Snapshot]
    SaveSnapshot --> SessionStates

    State -->|On every agent action| LogEvent[Log Agent Event]
    LogEvent --> Events

    SessionStates -->|On session restoration| LoadState[Load Latest State]
    Events -->|On session reconstruction| ReplayEvents[Replay Event Stream]

    LoadState --> State
    ReplayEvents --> State

    style State fill:#ffeb3b
    style SessionStates fill:#ffd54f
    style Events fill:#ffcc80
```

### 5.4 Key Indexes

```sql
-- High-performance indexes for common queries

-- Session retrieval
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX idx_sessions_status ON sessions(status);

-- Conversation history (questions + answers ordered by time)
CREATE INDEX idx_questions_session_created ON questions(session_id, created_at DESC);
CREATE INDEX idx_answers_session_created ON answers(session_id, created_at DESC);

-- Agent performance tracking
CREATE INDEX idx_events_agent_type ON agent_events(agent_name, event_type);
CREATE INDEX idx_reasoning_agent ON inferential_reasoning(agent_name);

-- JSONB state queries (GIN index for fast JSON operations)
CREATE INDEX idx_session_states_jsonb ON session_states USING GIN (state_value jsonb_path_ops);
CREATE INDEX idx_events_jsonb ON agent_events USING GIN (event_data jsonb_path_ops);

-- Film project search
CREATE INDEX idx_projects_title_trgm ON film_projects USING GIN (title gin_trgm_ops);
```

### 5.5 Data Retention Policy

```mermaid
graph LR
    Active[Active Sessions<br/>0-90 days<br/>Full access]

    Archived[Archived Sessions<br/>90-180 days<br/>Read-only]

    Deleted[Deleted Sessions<br/>180+ days<br/>Permanent removal]

    Active -->|90 days| Archived
    Archived -->|180 days| Deleted

    Active --> HotStorage[(Hot Storage<br/>PostgreSQL Primary)]
    Archived --> ColdStorage[(Cold Storage<br/>S3/GCS)]
    Deleted --> X[Purged]

    style Active fill:#81c784
    style Archived fill:#fff176
    style Deleted fill:#e57373
```

---

## 6. Service Architecture

### 6.1 Service Decomposition

```mermaid
graph TB
    subgraph "API Layer"
        SessionAPI[Session API<br/>/api/v1/sessions]
        AgentAPI[Agent API<br/>/api/v1/agents]
        ProjectAPI[Project API<br/>/api/v1/projects]
        WebSocketAPI[WebSocket API<br/>/api/v1/ws]
    end

    subgraph "Service Layer"
        SessionService[Session Service<br/>Lifecycle management]
        AgentService[Agent Service<br/>Execution orchestration]
        ProjectService[Project Service<br/>Film project CRUD]
        PersistenceService[Persistence Service<br/>State + Q&A storage]
    end

    subgraph "Core Layer"
        ADKRunner[ADK Runner<br/>Agent execution]
        SessionManager[Session Manager<br/>ADK session cache]
        LiteLLMClient[LiteLLM Client<br/>HTTP client wrapper]
    end

    subgraph "Data Layer"
        SessionRepo[Session Repository]
        QuestionRepo[Question Repository]
        AnswerRepo[Answer Repository]
        ReasoningRepo[Reasoning Repository]
        StateRepo[State Repository]
    end

    SessionAPI --> SessionService
    AgentAPI --> AgentService
    ProjectAPI --> ProjectService
    WebSocketAPI --> AgentService

    SessionService --> ADKRunner
    SessionService --> SessionManager
    AgentService --> ADKRunner
    AgentService --> PersistenceService

    ADKRunner --> LiteLLMClient

    SessionService --> SessionRepo
    PersistenceService --> QuestionRepo
    PersistenceService --> AnswerRepo
    PersistenceService --> ReasoningRepo
    PersistenceService --> StateRepo

    SessionRepo --> DB[(PostgreSQL)]
    QuestionRepo --> DB
    AnswerRepo --> DB
    ReasoningRepo --> DB
    StateRepo --> DB

    style SessionAPI fill:#e3f2fd
    style AgentAPI fill:#bbdefb
    style ProjectAPI fill:#90caf9
    style WebSocketAPI fill:#64b5f6
    style ADKRunner fill:#ffb74d
    style LiteLLMClient fill:#ff9800
    style DB fill:#ffd54f
```

### 6.2 ADK Runner Integration

```python
class ADKRunner:
    """Manages ADK agent execution and session lifecycle."""

    def __init__(
        self,
        session_id: uuid.UUID,
        session_manager: SessionManager,
        persistence_service: PersistenceService
    ):
        self.session_id = session_id
        self.session_manager = session_manager
        self.persistence_service = persistence_service
        self.runner: Optional[Runner] = None

    async def initialize(self):
        """Initialize ADK runner with session."""
        # Load or create ADK session
        session = await self.session_manager.get_or_create_session(
            self.session_id
        )

        # Create ADK runner with root agent
        self.runner = Runner(
            agent=root_agent,  # greeter
            session=session
        )

    async def send_message(
        self,
        message: str,
        stream: bool = False
    ) -> AsyncIterator[str] | str:
        """Send message to agent and get response."""
        if not self.runner:
            await self.initialize()

        # Record question
        await self.persistence_service.save_question(
            session_id=self.session_id,
            question_text=message
        )

        # Execute agent
        if stream:
            return self._stream_response(message)
        else:
            response = await self._get_response(message)
            await self._persist_response(response)
            return response
```

### 6.3 LiteLLM Proxy Configuration

```yaml
# config/litellm_config.yaml

model_list:
  # Gemini Models (Primary)
  - model_name: gemini-2.0-flash
    litellm_params:
      model: vertex_ai/gemini-2.0-flash
      vertex_project: ${GOOGLE_CLOUD_PROJECT}
      vertex_location: us-central1

  # OpenAI Models (Fallback)
  - model_name: gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY

  # Claude Models (Alternative)
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

# Router settings
router_settings:
  routing_strategy: simple-shuffle
  num_retries: 3
  timeout: 600
  fallbacks:
    - gpt-4o-mini: [gemini-2.0-flash]
    - gemini-2.0-flash: [gpt-4o-mini]

# Caching
litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    ttl: 3600
```

---

## 7. API Architecture

### 7.1 REST API Endpoints

```mermaid
graph TB
    subgraph "Session Management"
        POST1[POST /api/v1/sessions<br/>Create new session]
        GET1[GET /api/v1/sessions/:id<br/>Get session details]
        GET2[GET /api/v1/sessions/:id/state<br/>Get session state]
        DELETE1[DELETE /api/v1/sessions/:id<br/>Delete session]
    end

    subgraph "Agent Execution"
        POST2[POST /api/v1/sessions/:id/messages<br/>Send message to agent]
        POST3[POST /api/v1/sessions/:id/messages/async<br/>Queue message]
        GET3[GET /api/v1/sessions/:id/history<br/>Get conversation history]
    end

    subgraph "Project Management"
        POST4[POST /api/v1/projects<br/>Create film project]
        GET4[GET /api/v1/projects/:id<br/>Get project details]
        PUT1[PUT /api/v1/projects/:id<br/>Update project]
        GET5[GET /api/v1/projects<br/>List user projects]
    end

    subgraph "WebSocket"
        WS1[WS /api/v1/ws/:session_id<br/>Streaming responses]
    end

    Client[Client Application] --> POST1
    Client --> POST2
    Client --> POST4
    Client --> WS1
```

### 7.2 API Request/Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant SessionService
    participant ADKRunner
    participant LiteLLMProxy
    participant Gemini
    participant PostgreSQL

    Client->>FastAPI: POST /api/v1/sessions/:id/messages<br/>{message: "Create film about Ada Lovelace"}

    FastAPI->>SessionService: send_message(session_id, message)

    SessionService->>PostgreSQL: INSERT INTO questions
    PostgreSQL-->>SessionService: question_id

    SessionService->>ADKRunner: send_message(message)

    ADKRunner->>LiteLLMProxy: POST /v1/chat/completions<br/>{model: "gpt-4o-mini", messages: [...]}

    LiteLLMProxy->>Gemini: Vertex AI API Call
    Gemini-->>LiteLLMProxy: Response

    LiteLLMProxy-->>ADKRunner: OpenAI-compatible response

    ADKRunner->>PostgreSQL: INSERT INTO inferential_reasoning
    ADKRunner->>PostgreSQL: UPDATE session_states

    ADKRunner-->>SessionService: Agent response

    SessionService->>PostgreSQL: INSERT INTO answers

    SessionService-->>FastAPI: Response text

    FastAPI-->>Client: 200 OK<br/>{response: "Great! I'll create...", session_id: "..."}
```

### 7.3 WebSocket Streaming

```mermaid
sequenceDiagram
    participant Client
    participant WebSocket
    participant AgentService
    participant ADKRunner
    participant LiteLLMProxy

    Client->>WebSocket: Connect to /ws/:session_id
    WebSocket-->>Client: Connection established

    Client->>WebSocket: {type: "message", content: "Create film..."}

    WebSocket->>AgentService: send_message(stream=True)

    AgentService->>ADKRunner: send_message(stream=True)

    loop Streaming Response
        ADKRunner->>LiteLLMProxy: Stream chat completion
        LiteLLMProxy-->>ADKRunner: Token chunk
        ADKRunner-->>AgentService: Yield chunk
        AgentService-->>WebSocket: {type: "chunk", content: "..."}
        WebSocket-->>Client: Stream chunk to browser
    end

    ADKRunner-->>AgentService: Stream complete
    AgentService-->>WebSocket: {type: "complete"}
    WebSocket-->>Client: Streaming done
```

---

## 8. Deployment Architecture

### 8.1 Docker Compose Structure

```mermaid
graph TB
    subgraph "Docker Compose Services"
        subgraph "Application Services"
            Frontend[frontend<br/>React + Vite<br/>:3000]
            API[api<br/>FastAPI + Uvicorn<br/>:8000]
            LiteLLM[litellm<br/>LiteLLM Proxy<br/>:4000]
        end

        subgraph "Data Services"
            Postgres[(postgres<br/>PostgreSQL 16<br/>:5432)]
            Redis[(redis<br/>Redis 7<br/>:6379)]
        end

        subgraph "External Networks"
            Internet{Internet}
        end
    end

    Internet -->|HTTPS| Frontend
    Frontend -->|HTTP| API
    API -->|HTTP| LiteLLM
    API -->|TCP| Postgres
    API -->|TCP| Redis
    LiteLLM -->|TCP| Redis
    LiteLLM -->|HTTPS| Internet

    style Frontend fill:#81c784
    style API fill:#64b5f6
    style LiteLLM fill:#ffb74d
    style Postgres fill:#ffd54f
    style Redis fill:#ffccbc
```

### 8.2 docker-compose.yml

```yaml
version: '3.8'

services:
    # LiteLLM Proxy - LLM Gateway
    litellm:
        image: ghcr.io/berriai/litellm:main-latest
        ports:
            - "4000:4000"
        environment:
            - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
            - DATABASE_URL=postgresql://user:password@postgres:5432/litellm
        volumes:
            - ./config/litellm_config.yaml:/app/config.yaml
        command: --config /app/config.yaml
        depends_on:
            postgres:
                condition: service_healthy
        healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
            interval: 30s
            timeout: 10s
            retries: 3

    # FastAPI Backend
    api:
        build:
            context: ./backend
            dockerfile: Dockerfile
        ports:
            - "8000:8000"
        environment:
            - DATABASE_URL=postgresql://user:password@postgres:5432/filmmaking
            - REDIS_URL=redis://redis:6379/0
            - LITELLM_BASE_URL=http://litellm:4000
            - LITELLM_API_KEY=${LITELLM_MASTER_KEY}
            - ADK_MODEL=gpt-4o-mini
        volumes:
            - ./backend:/app
            - ./sessions:/app/sessions
        depends_on:
            postgres:
                condition: service_healthy
            litellm:
                condition: service_healthy
        command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

    # React Frontend
    frontend:
        build:
            context: ./frontend
            dockerfile: Dockerfile
        ports:
            - "3000:3000"
        environment:
            - VITE_API_BASE_URL=http://localhost:8000
        volumes:
            - ./frontend:/app
            - /app/node_modules
        depends_on:
            - api

    # PostgreSQL Database
    postgres:
        image: postgres:16-alpine
        environment:
            - POSTGRES_USER=user
            - POSTGRES_PASSWORD=password
            - POSTGRES_DB=filmmaking
        volumes:
            - postgres_data:/var/lib/postgresql/data
            - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
        ports:
            - "5432:5432"
        healthcheck:
            test: ["CMD", "pg_isready", "-U", "user"]
            interval: 10s
            timeout: 5s
            retries: 5

    # Redis Cache
    redis:
        image: redis:7-alpine
        ports:
            - "6379:6379"
        volumes:
            - redis_data:/data
        healthcheck:
            test: ["CMD", "redis-cli", "ping"]
            interval: 10s
            timeout: 5s
            retries: 5

volumes:
    postgres_data:
    redis_data:
```

### 8.3 Multi-Stage Dockerfile (Backend)

```dockerfile
# Stage 1: Base
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Stage 2: Dependencies
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 3: Production
FROM base AS production

# Copy dependencies from previous stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.4 Production Deployment

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Cloud Load Balancer<br/>HTTPS :443]
    end

    subgraph "Frontend Tier"
        FE1[Frontend 1<br/>React Static Assets]
        FE2[Frontend 2<br/>React Static Assets]
    end

    subgraph "API Tier - Auto-scaling"
        API1[API Instance 1<br/>FastAPI :8000]
        API2[API Instance 2<br/>FastAPI :8000]
        API3[API Instance 3<br/>FastAPI :8000]
    end

    subgraph "LLM Gateway - Auto-scaling"
        LLM1[LiteLLM 1<br/>:4000]
        LLM2[LiteLLM 2<br/>:4000]
    end

    subgraph "Data Tier"
        PGPrimary[(PostgreSQL Primary)]
        PGReplica1[(PostgreSQL Replica 1)]
        PGReplica2[(PostgreSQL Replica 2)]
        RedisCluster[(Redis Cluster<br/>3 nodes)]
    end

    LB --> FE1
    LB --> FE2
    FE1 --> API1
    FE1 --> API2
    FE2 --> API2
    FE2 --> API3

    API1 --> LLM1
    API2 --> LLM1
    API2 --> LLM2
    API3 --> LLM2

    API1 --> PGPrimary
    API2 --> PGReplica1
    API3 --> PGReplica2

    API1 --> RedisCluster
    API2 --> RedisCluster
    API3 --> RedisCluster

    LLM1 --> RedisCluster
    LLM2 --> RedisCluster

    PGPrimary -.->|Replication| PGReplica1
    PGPrimary -.->|Replication| PGReplica2

    style LB fill:#e8f5e9
    style FE1 fill:#c8e6c9
    style API1 fill:#90caf9
    style LLM1 fill:#ffb74d
    style PGPrimary fill:#ffd54f
    style RedisCluster fill:#ffccbc
```

### 8.5 Docker Compose vs Kubernetes: Decision Matrix

#### When to Use Each Technology

```mermaid
graph LR
    Start{Evaluate Your<br/>Requirements}

    Start -->|Concurrent Users| Users{How many<br/>concurrent users?}
    Start -->|Infrastructure| Infra{Single server<br/>or multi-node?}
    Start -->|Budget| Budget{Monthly<br/>infrastructure<br/>budget?}
    Start -->|Team| Team{DevOps<br/>expertise?}

    Users -->|< 50| DockerCompose[Docker Compose]
    Users -->|50-200| Hybrid[Either works<br/>Evaluate other factors]
    Users -->|> 200| K8s[Kubernetes]

    Infra -->|Single server| DockerCompose
    Infra -->|Multi-node| K8s

    Budget -->|< $500/month| DockerCompose
    Budget -->|$500-2000| Hybrid
    Budget -->|> $2000| K8s

    Team -->|1-2 developers| DockerCompose
    Team -->|3-5 engineers| Hybrid
    Team -->|> 5 with DevOps| K8s

    style DockerCompose fill:#81c784
    style K8s fill:#42a5f5
    style Hybrid fill:#fff176
```

#### Decision Table

| Criteria | Docker Compose | Kubernetes | Winner |
|----------|---------------|------------|---------|
| **Concurrent Users** | < 50 | 50+ | Based on load |
| **Setup Complexity** | ⭐ Simple (5 min) | ⭐⭐⭐⭐ Complex (2-4 hours) | Docker Compose |
| **Auto-Scaling** | ❌ Manual only | ✅ HPA (automatic) | Kubernetes |
| **High Availability** | ❌ Single point of failure | ✅ Multi-node redundancy | Kubernetes |
| **Zero-Downtime Deploys** | ❌ Brief downtime | ✅ Rolling updates | Kubernetes |
| **Cost (MVP)** | $200-500/month | $800-1500/month | Docker Compose |
| **Cost (Scale)** | $800/month (fixed) | $400-600/month (auto-scale) | Kubernetes |
| **Monitoring** | ⭐⭐ Basic (Docker stats) | ⭐⭐⭐⭐⭐ Advanced (Prometheus) | Kubernetes |
| **Learning Curve** | 1-2 days | 2-4 weeks | Docker Compose |
| **Production Ready** | ⭐⭐⭐ Small scale only | ⭐⭐⭐⭐⭐ Enterprise grade | Kubernetes |

#### Use Docker Compose If:

✅ **MVP or early-stage product** (< 50 concurrent users)
✅ **Small team** (1-3 developers, no dedicated DevOps)
✅ **Limited budget** (< $500/month infrastructure)
✅ **Single server deployment** acceptable
✅ **Simple deployment needs** (manual scaling OK)
✅ **Fast iteration** required (learning K8s would slow you down)

**Example**: You're validating product-market fit with early adopters.

#### Use Kubernetes If:

✅ **Production scale** (50+ concurrent users)
✅ **Auto-scaling required** (traffic varies 2x-10x daily)
✅ **High availability critical** (99.9%+ uptime SLA)
✅ **Zero-downtime deploys** mandatory
✅ **Multi-region deployment** needed
✅ **DevOps resources available** (team knows K8s or can learn)

**Example**: You have product-market fit and growing user base.

#### Migration Path: Docker Compose → Kubernetes

```mermaid
graph TB
    subgraph "Phase 1: MVP (0-6 months)"
        DC1[Docker Compose<br/>Single Server<br/>2-10 concurrent users]
        DC2[Add monitoring<br/>Prometheus + Grafana]
        DC3[Optimize performance<br/>Identify bottlenecks]
    end

    subgraph "Phase 2: Growth Prep (6-12 months)"
        Plan[Plan K8s migration<br/>Create K8s manifests]
        Test[Test K8s locally<br/>Minikube/Kind]
        Parallel[Run parallel<br/>Docker Compose + K8s]
    end

    subgraph "Phase 3: Migration (Month 12)"
        Migrate1[Deploy K8s to staging]
        Migrate2[Shadow production traffic]
        Migrate3[Cutover to K8s]
        Migrate4[Keep Docker Compose<br/>as backup 30 days]
    end

    subgraph "Phase 4: Scale (12+ months)"
        K8s1[Multi-node K8s<br/>50+ concurrent users]
        K8s2[Auto-scaling enabled<br/>HPA configured]
        K8s3[Multi-region<br/>Global deployment]
    end

    DC1 --> DC2 --> DC3
    DC3 -->|20-30 users| Plan
    Plan --> Test --> Parallel
    Parallel -->|40-50 users| Migrate1
    Migrate1 --> Migrate2 --> Migrate3 --> Migrate4
    Migrate4 --> K8s1 --> K8s2
    K8s2 -->|100+ users| K8s3

    style DC1 fill:#c8e6c9
    style DC3 fill:#fff176
    style Migrate3 fill:#ffb74d
    style K8s3 fill:#42a5f5
```

#### Migration Checklist

**Before migrating to Kubernetes:**

- [ ] Current concurrent users > 40-50
- [ ] Docker Compose hitting resource limits (CPU > 80%, Memory > 85%)
- [ ] Response times degrading (p95 > 5s)
- [ ] Manual scaling becoming frequent (weekly+)
- [ ] Downtime during deploys causing user complaints
- [ ] Team has K8s training or hired DevOps engineer
- [ ] Budget supports K8s costs ($1500+/month)
- [ ] Monitoring shows clear bottlenecks (need horizontal scaling)

**Migration steps:**

1. **Create K8s manifests** (1-2 weeks)
   - Convert docker-compose.yml to K8s Deployments
   - Add HPA, Services, Ingress
   - Configure PersistentVolumes for PostgreSQL

2. **Test locally** (1 week)
   - Run in Minikube/Kind
   - Verify all services communicate
   - Test auto-scaling triggers

3. **Deploy to staging** (1 week)
   - Use managed K8s (GKE, EKS, AKS)
   - Run full test suite
   - Load test with production-like traffic

4. **Shadow production** (1-2 weeks)
   - Dual-run Docker Compose + K8s
   - Send 10% traffic to K8s
   - Monitor errors, latency, costs

5. **Cutover** (1 day)
   - Blue-green deployment
   - Switch DNS to K8s load balancer
   - Keep Docker Compose running 30 days as backup

6. **Optimize** (ongoing)
   - Tune HPA settings
   - Add resource limits/requests
   - Implement cluster autoscaling

#### Cost Comparison

| Phase | Users | Docker Compose | Kubernetes | Savings |
|-------|-------|---------------|------------|---------|
| **MVP** | 10 | $250/month | $900/month | Docker: -$650 |
| **Growth** | 50 | $800/month (maxed out) | $600/month (auto-scaled) | K8s: +$200 |
| **Scale** | 200 | $800/month (failing) | $1,200/month | K8s only option |
| **Enterprise** | 1000+ | Not viable | $5,000/month | K8s only option |

**Break-even point**: ~50-75 concurrent users (where K8s becomes cost-effective)

---

**📚 For detailed Kubernetes implementation, see [KUBERNETES_ARCHITECTURE.md](./KUBERNETES_ARCHITECTURE.md)**

This includes:
- Complete K8s manifests (Deployments, StatefulSets, HPA)
- Auto-scaling configurations
- High availability setup
- Zero-downtime deployment strategies
- Production performance benchmarks

---

## 9. Security Architecture

### 9.1 Security Layers

```mermaid
graph TB
    subgraph "Network Security"
        HTTPS[HTTPS/TLS 1.3]
        Firewall[Cloud Firewall Rules]
        VPC[Virtual Private Cloud]
    end

    subgraph "Application Security"
        Auth[OAuth 2.0 + JWT]
        RBAC[Role-Based Access Control]
        RateLimit[Rate Limiting]
        CORS[CORS Policy]
    end

    subgraph "Data Security"
        Encryption[Data Encryption at Rest]
        TLS[TLS in Transit]
        Secrets[Secret Manager]
        PII[PII Masking]
    end

    subgraph "API Security"
        APIKey[API Key Management]
        Validation[Input Validation]
        Sanitization[Output Sanitization]
    end

    User[User] -->|HTTPS| HTTPS
    HTTPS --> Firewall
    Firewall --> VPC
    VPC --> Auth
    Auth --> RBAC
    RBAC --> RateLimit
    RateLimit --> APIKey
    APIKey --> Validation
    Validation --> App[Application]

    App --> Encryption
    App --> TLS
    App --> Secrets

    style HTTPS fill:#c8e6c9
    style Auth fill:#90caf9
    style Encryption fill:#ffd54f
    style APIKey fill:#ffb74d
```

### 9.2 Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthProvider as Auth Provider<br/>(Google/GitHub)
    participant Database

    User->>Frontend: Click "Sign In"
    Frontend->>AuthProvider: Redirect to OAuth

    AuthProvider-->>Frontend: Authorization Code

    Frontend->>API: POST /auth/callback<br/>{code: "..."}

    API->>AuthProvider: Exchange code for token
    AuthProvider-->>API: Access Token + User Info

    API->>Database: Find or Create User
    Database-->>API: User record

    API->>API: Generate JWT

    API-->>Frontend: {jwt: "...", user: {...}}

    Frontend->>Frontend: Store JWT in localStorage

    Note over Frontend,API: Subsequent Requests

    Frontend->>API: GET /api/v1/sessions<br/>Authorization: Bearer {jwt}

    API->>API: Verify JWT signature

    alt JWT Valid
        API-->>Frontend: 200 OK {sessions: [...]}
    else JWT Invalid
        API-->>Frontend: 401 Unauthorized
    end
```

### 9.3 Rate Limiting Strategy

```mermaid
graph TB
    Request[Incoming Request]

    Request --> IPCheck{IP Rate Limit<br/>100 req/min}

    IPCheck -->|Exceeded| Block1[429 Too Many Requests]
    IPCheck -->|OK| UserCheck{User Rate Limit<br/>1000 req/hour}

    UserCheck -->|Exceeded| Block2[429 Quota Exceeded]
    UserCheck -->|OK| CostCheck{LLM Cost Limit<br/>$10/day}

    CostCheck -->|Exceeded| Block3[429 Cost Limit Reached]
    CostCheck -->|OK| Allow[Process Request]

    style Block1 fill:#ffcdd2
    style Block2 fill:#ffcdd2
    style Block3 fill:#ffcdd2
    style Allow fill:#c8e6c9
```

---

## 10. Scalability Strategy

### 10.1 Horizontal Scaling

```mermaid
graph TB
    subgraph "Traffic Growth"
        T1[100 users<br/>MVP Phase]
        T2[1,000 users<br/>Growth Phase]
        T3[10,000 users<br/>Scale Phase]
    end

    subgraph "Infrastructure Scale"
        I1[2 API instances<br/>1 DB primary<br/>$250/month]
        I2[5-10 API instances<br/>2 DB replicas<br/>$1,500/month]
        I3[20-50 API instances<br/>Multi-region DB<br/>$10,000/month]
    end

    T1 --> I1
    T2 --> I2
    T3 --> I3

    style T1 fill:#e1f5fe
    style T2 fill:#81d4fa
    style T3 fill:#0288d1
    style I1 fill:#fff9c4
    style I2 fill:#ffeb3b
    style I3 fill:#fbc02d
```

### 10.2 Caching Strategy

```mermaid
graph TB
    Request[User Request]

    Request --> L1{L1: Application Cache<br/>Redis<br/>TTL: 5min}

    L1 -->|Hit| Return1[Return Cached Response]
    L1 -->|Miss| L2{L2: LiteLLM Cache<br/>Semantic Similarity<br/>TTL: 1 hour}

    L2 -->|Hit| Return2[Return Cached LLM Response]
    L2 -->|Miss| L3{L3: Research Data Cache<br/>Wikipedia/TMDB<br/>TTL: 7 days}

    L3 -->|Hit| LLM1[Call LLM with Cached Context]
    L3 -->|Miss| Fetch[Fetch Fresh Data]

    Fetch --> LLM2[Call LLM]
    LLM1 --> SaveCache
    LLM2 --> SaveCache[Save to All Cache Layers]

    SaveCache --> Return3[Return Response]

    style Return1 fill:#c8e6c9
    style Return2 fill:#c8e6c9
    style Return3 fill:#c8e6c9
```

### 10.3 Database Scaling

```mermaid
graph TB
    App[Application]

    App -->|Write| Primary[(PostgreSQL Primary)]

    Primary -.->|Streaming Replication| Replica1[(Replica 1<br/>Read Queries)]
    Primary -.->|Streaming Replication| Replica2[(Replica 2<br/>Read Queries)]

    App -->|Read: Session History| Replica1
    App -->|Read: Analytics| Replica2

    subgraph "Connection Pool"
        PgBouncer[PgBouncer<br/>Max 100 connections]
    end

    App --> PgBouncer
    PgBouncer --> Primary
    PgBouncer --> Replica1
    PgBouncer --> Replica2

    style Primary fill:#ffd54f
    style Replica1 fill:#ffe082
    style Replica2 fill:#ffe082
```

---

## 11. Implementation Guide

### 11.1 Project Structure

```
/Users/ggoni/docencia-repos/agente-films/
├── .env.example                    # Environment variables template
├── .gitignore
├── .python-version                 # 3.12
├── README.md
├── architecture.md                 # This file
├── docker-compose.yml
├── pyproject.toml                  # uv dependencies
├── uv.lock
│
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── agents/                 # ADK agent definitions
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── researcher.py
│   │   │   ├── screenwriter.py
│   │   │   ├── critic.py
│   │   │   ├── box_office.py
│   │   │   ├── casting.py
│   │   │   ├── workflows.py        # SequentialAgent, LoopAgent, ParallelAgent
│   │   │   └── tools.py            # Custom ADK tools
│   │   │
│   │   ├── api/                    # FastAPI routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── sessions.py
│   │   │       ├── agents.py
│   │   │       ├── projects.py
│   │   │       └── websocket.py
│   │   │
│   │   ├── core/                   # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── adk_runner.py
│   │   │   ├── session_manager.py
│   │   │   └── litellm_client.py
│   │   │
│   │   ├── db/                     # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── schemas.py          # Pydantic schemas
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── session.py
│   │   │       ├── question.py
│   │   │       ├── answer.py
│   │   │       └── reasoning.py
│   │   │
│   │   ├── services/               # Application services
│   │   │   ├── __init__.py
│   │   │   ├── session_service.py
│   │   │   ├── agent_service.py
│   │   │   └── persistence_service.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logging.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   └── agents/
│   │   │       └── test_researcher.py
│   │   └── integration/
│   │       └── test_api.py
│   │
│   └── alembic/                    # Database migrations
│       ├── versions/
│       └── env.py
│
├── config/
│   └── litellm_config.yaml
│
├── database/
│   ├── init.sql                    # Initial schema
│   └── queries.sql                 # Common queries
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── api/
│       ├── components/
│       ├── hooks/
│       └── types/
│
└── sessions/                       # Persisted agent outputs
    └── movie_pitches/
```

### 11.2 Getting Started

```bash
# 1. Clone repository
cd /Users/ggoni/docencia-repos/agente-films

# 2. Install dependencies
uv sync

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 4. Start infrastructure
docker-compose up -d postgres redis litellm

# 5. Initialize database
psql -h localhost -U user -d filmmaking -f database/init.sql

# 6. Run migrations
uv run alembic upgrade head

# 7. Start backend
uv run uvicorn app.main:app --reload

# 8. Start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### 11.3 Development Workflow

```mermaid
flowchart TB
    Start[Start Development]

    Start --> Feature[Create Feature Branch]

    Feature --> Code[Write Code<br/>4-space indentation]

    Code --> Test[Write Tests<br/>pytest]

    Test --> Lint[Run Linters<br/>ruff, mypy]

    Lint --> Commit[Commit with<br/>Conventional Commits]

    Commit --> Push[Push to GitHub]

    Push --> CI{CI Passes?}

    CI -->|No| Fix[Fix Issues]
    Fix --> Code

    CI -->|Yes| PR[Create Pull Request]

    PR --> Review{Code Review<br/>Approved?}

    Review -->|No| Address[Address Feedback]
    Address --> Code

    Review -->|Yes| Merge[Merge to Main]

    Merge --> Deploy[Deploy to Staging]

    Deploy --> QA{QA Passes?}

    QA -->|No| Hotfix[Create Hotfix]
    Hotfix --> Code

    QA -->|Yes| Prod[Deploy to Production]

    style Start fill:#e1f5fe
    style Code fill:#b3e5fc
    style Test fill:#81d4fa
    style Prod fill:#4caf50
```

### 11.4 Environment Variables

```bash
# .env.example

# Application
APP_NAME=Film Concept Generator
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/filmmaking

# Redis
REDIS_URL=redis://localhost:6379/0

# LiteLLM
LITELLM_BASE_URL=http://localhost:4000
LITELLM_MASTER_KEY=sk-your-master-key

# Google Cloud (for Vertex AI)
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# OpenAI (optional)
OPENAI_API_KEY=sk-your-openai-key

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-your-key

# ADK
ADK_MODEL=gpt-4o-mini

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 11.5 Testing Strategy

```mermaid
graph TB
    subgraph "Test Pyramid"
        E2E[E2E Tests<br/>10%<br/>Complete workflows]
        Integration[Integration Tests<br/>20%<br/>API + Database]
        Unit[Unit Tests<br/>70%<br/>Agents + Services]
    end

    Unit --> Coverage{Coverage > 80%?}
    Integration --> Coverage
    E2E --> Coverage

    Coverage -->|No| Fail[CI Fails]
    Coverage -->|Yes| Pass[CI Passes]

    style Unit fill:#c8e6c9
    style Integration fill:#a5d6a7
    style E2E fill:#81c784
    style Pass fill:#4caf50
    style Fail fill:#ef5350
```

---

## Conclusion

This architecture provides a production-ready foundation for the multi-agent filmmaking system with:

- **Scalability**: Horizontal scaling from 100 to 10,000+ users
- **Flexibility**: LiteLLM enables easy switching between LLM providers
- **Observability**: Comprehensive tracking of questions, answers, and reasoning
- **Maintainability**: Clean separation of concerns with repository pattern
- **Cost Efficiency**: Multi-tier caching reduces LLM API costs by 30-50%
- **Developer Experience**: uv for fast dependency management, Docker for consistent environments

**Next Steps**:
1. Implement core ADK agent structure (`backend/app/agents/`)
2. Set up database schema (`database/init.sql`)
3. Configure LiteLLM proxy (`config/litellm_config.yaml`)
4. Build FastAPI endpoints (`backend/app/api/v1/`)
5. Create React frontend (`frontend/src/`)
6. Write comprehensive tests (`backend/tests/`)
7. Deploy to staging environment
8. Conduct user acceptance testing
9. Launch MVP

**Key Metrics to Track**:
- Agent success rate (target: >90%)
- Average latency per agent (target: <5s)
- LLM cost per project (target: <$0.50)
- User satisfaction score (target: >4.0/5.0)
- System uptime (target: 99.5%)

For questions or clarifications, refer to:
- Google ADK Documentation: https://cloud.google.com/vertex-ai/docs/agent-builder
- LiteLLM Documentation: https://docs.litellm.ai/
- FastAPI Documentation: https://fastapi.tiangolo.com/

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-25
**Authors**: Architect Agent, Database Designer Agent, Expert Developer Agent, Principal Technical Agent