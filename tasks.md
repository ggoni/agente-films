# Multi-Agent Filmmaking System - MVP Task List

> **Generated**: 2025-11-25
> **Based on**: architecture.md
> **Approach**: Test-Driven Development (TDD) with granular, single-responsibility tasks

---

## Task Execution Rules

**For the Engineering LLM:**
1. Complete ONE task at a time
2. Write tests BEFORE implementation (TDD)
3. Run tests after implementation
4. Commit after each task passes
5. Wait for human verification before proceeding to next task

**Success Criteria per Task:**
- ✅ Unit tests written and passing
- ✅ Code follows SOLID principles
- ✅ 4-space indentation (Python standard)
- ✅ Type hints on all functions
- ✅ Conventional commit message

---

## Phase 0: Project Setup (Foundation)

### Task 0.1: Initialize Python Project Structure
**Objective**: Create basic project structure with uv

**Steps**:
1. Ensure `.python-version` file exists with `3.12`
2. Verify `pyproject.toml` exists with correct metadata
3. Run `uv sync` to create virtual environment

**Tests**: None (infrastructure task)

**Success Criteria**:
- [ ] `.venv/` directory created
- [ ] `uv.lock` file generated
- [ ] `uv run python --version` returns 3.12.x

**Files Created**: None (uses existing files)

---

### Task 0.2: Install Core Dependencies
**Objective**: Add essential packages via uv

**Steps**:
```bash
uv add fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings
uv add --dev pytest pytest-asyncio pytest-cov httpx ruff mypy
```

**Tests**: None (infrastructure task)

**Success Criteria**:
- [ ] All packages in `pyproject.toml` [project.dependencies]
- [ ] Dev packages in [tool.uv.dev-dependencies]
- [ ] `uv.lock` updated

**Files Modified**: `pyproject.toml`, `uv.lock`

---

### Task 0.3: Create Backend Directory Structure
**Objective**: Establish folder hierarchy following architecture

**Steps**:
1. Create directory structure:
```
backend/
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   └── __init__.py
│   ├── api/
│   │   └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── repositories/
│   │       └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   └── __init__.py
    └── integration/
        └── __init__.py
```

**Tests**:
```python
# tests/test_structure.py
def test_backend_directory_exists():
    assert Path("backend/app").exists()

def test_all_init_files_exist():
    expected = [
        "backend/app/__init__.py",
        "backend/app/agents/__init__.py",
        # ... etc
    ]
    for path in expected:
        assert Path(path).exists()
```

**Success Criteria**:
- [ ] All directories created
- [ ] All `__init__.py` files present
- [ ] Tests pass

**Files Created**: Directory structure + `tests/test_structure.py`

---

## Phase 1: Database Layer (Data Persistence)

### Task 1.1: Create Database Configuration Module
**Objective**: Implement Pydantic settings for database connection

**Steps**:
1. Create `backend/app/config.py`
2. Implement `Settings` class extending `BaseSettings`
3. Add fields: `DATABASE_URL`, `DEBUG`, `APP_NAME`

**Tests**:
```python
# tests/unit/test_config.py
def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://test"

def test_settings_has_defaults():
    settings = Settings()
    assert settings.DEBUG is False
    assert settings.APP_NAME == "Film Concept Generator"
```

**Success Criteria**:
- [ ] Settings class implemented
- [ ] All tests pass
- [ ] Type hints on all attributes

**Files Created**: `backend/app/config.py`, `tests/unit/test_config.py`

**Implementation Hints**:
- Use `pydantic_settings.BaseSettings`
- Add `model_config = SettingsConfigDict(env_file=".env")`

---

### Task 1.2: Create SQLAlchemy Base and Engine
**Objective**: Set up database connection factory

**Steps**:
1. Create `backend/app/db/base.py`
2. Implement `get_engine()` function
3. Implement `get_session()` dependency
4. Create `Base = declarative_base()`

**Tests**:
```python
# tests/unit/db/test_base.py
def test_get_engine_returns_engine():
    engine = get_engine()
    assert isinstance(engine, Engine)

def test_get_session_yields_session():
    gen = get_session()
    session = next(gen)
    assert isinstance(session, Session)
```

**Success Criteria**:
- [ ] Engine creation works
- [ ] Session factory works
- [ ] Tests pass

**Files Created**: `backend/app/db/base.py`, `tests/unit/db/test_base.py`

**Implementation Hints**:
- Use connection pooling: `pool_size=20, max_overflow=40`
- Add `pool_pre_ping=True` for connection health checks

---

### Task 1.3: Create Session Model
**Objective**: Implement SQLAlchemy model for sessions table

**Steps**:
1. Create `backend/app/db/models.py`
2. Implement `Session` model with fields:
   - `id: UUID` (primary key)
   - `created_at: DateTime`
   - `updated_at: DateTime`
   - `status: String`
   - `metadata: JSON`

**Tests**:
```python
# tests/unit/db/test_models.py
def test_session_model_has_required_fields():
    session = Session(id=uuid4(), status="active")
    assert session.id is not None
    assert session.status == "active"

def test_session_defaults():
    session = Session(id=uuid4())
    assert session.status == "active"
    assert session.created_at is not None
```

**Success Criteria**:
- [ ] Model defined with all fields
- [ ] Default values work
- [ ] Tests pass

**Files Created**: `backend/app/db/models.py`, `tests/unit/db/test_models.py`

**Implementation Hints**:
- Use `Column(UUID(as_uuid=True), primary_key=True)`
- Use `server_default=text("gen_random_uuid()")` for id
- Use `JSONB` for metadata column

---

### Task 1.4: Create Pydantic Schema for Session
**Objective**: Create data validation schemas

**Steps**:
1. Create `backend/app/db/schemas.py`
2. Implement `SessionBase`, `SessionCreate`, `SessionResponse`

**Tests**:
```python
# tests/unit/db/test_schemas.py
def test_session_create_validation():
    data = SessionCreate(status="active")
    assert data.status == "active"

def test_session_response_from_orm():
    orm_session = Session(id=uuid4(), status="active")
    schema = SessionResponse.model_validate(orm_session)
    assert schema.id == orm_session.id
```

**Success Criteria**:
- [ ] Schemas defined
- [ ] Validation works
- [ ] ORM mode works
- [ ] Tests pass

**Files Created**: `backend/app/db/schemas.py`, `tests/unit/db/test_schemas.py`

**Implementation Hints**:
- Use `model_config = ConfigDict(from_attributes=True)`
- Inherit: `SessionCreate(SessionBase)`, `SessionResponse(SessionBase)`

---

### Task 1.5: Create Session Repository
**Objective**: Implement data access layer with repository pattern

**Steps**:
1. Create `backend/app/db/repositories/session.py`
2. Implement `SessionRepository` class with methods:
   - `create(session_data: SessionCreate) -> Session`
   - `get_by_id(session_id: UUID) -> Session | None`
   - `delete(session_id: UUID) -> bool`

**Tests**:
```python
# tests/unit/repositories/test_session.py
def test_create_session(db_session):
    repo = SessionRepository(db_session)
    data = SessionCreate(status="active")
    session = repo.create(data)
    assert session.id is not None
    assert session.status == "active"

def test_get_by_id_returns_session(db_session):
    repo = SessionRepository(db_session)
    created = repo.create(SessionCreate(status="active"))
    found = repo.get_by_id(created.id)
    assert found.id == created.id
```

**Success Criteria**:
- [ ] Repository class implemented
- [ ] All methods work
- [ ] Tests pass with fixtures

**Files Created**:
- `backend/app/db/repositories/session.py`
- `tests/unit/repositories/test_session.py`
- Update `tests/conftest.py` with `db_session` fixture

**Implementation Hints**:
- Repository takes `Session` in `__init__`
- Use dependency injection pattern
- Raise exceptions for not found cases

---

## Phase 2: Core Domain Logic (ADK Integration)

### Task 2.1: Install Google ADK
**Objective**: Add ADK to project dependencies

**Steps**:
```bash
uv add google-adk
```

**Tests**:
```python
# tests/unit/test_adk_import.py
def test_adk_imports():
    from google.adk import Agent, Runner
    from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
    assert Agent is not None
```

**Success Criteria**:
- [ ] google-adk in dependencies
- [ ] Import test passes

**Files Modified**: `pyproject.toml`, `uv.lock`

---

### Task 2.2: Create Base Agent Configuration
**Objective**: Setup shared agent utilities

**Steps**:
1. Create `backend/app/agents/base.py`
2. Implement helper functions:
   - `get_model_name() -> str`
   - `log_query(query: str) -> None`
   - `log_response(response: str) -> None`

**Tests**:
```python
# tests/unit/agents/test_base.py
def test_get_model_name_returns_string():
    model = get_model_name()
    assert isinstance(model, str)
    assert len(model) > 0

def test_log_query_accepts_string(caplog):
    log_query("test query")
    assert "test query" in caplog.text
```

**Success Criteria**:
- [ ] Functions implemented
- [ ] Logging works
- [ ] Tests pass

**Files Created**: `backend/app/agents/base.py`, `tests/unit/agents/test_base.py`

---

### Task 2.3: Create Researcher Agent
**Objective**: Implement first ADK LlmAgent

**Steps**:
1. Create `backend/app/agents/researcher.py`
2. Define `researcher` agent with:
   - `name="researcher"`
   - `model=get_model_name()`
   - `description="Researches historical figures"`
   - `instruction="..."`

**Tests**:
```python
# tests/unit/agents/test_researcher.py
def test_researcher_agent_created():
    from app.agents.researcher import researcher
    assert researcher.name == "researcher"

def test_researcher_has_tools():
    from app.agents.researcher import researcher
    assert len(researcher.tools) > 0
```

**Success Criteria**:
- [ ] Agent defined
- [ ] Has name, description, instruction
- [ ] Tests pass

**Files Created**: `backend/app/agents/researcher.py`, `tests/unit/agents/test_researcher.py`

**Implementation Hints**:
- Use template from architecture.md section 4.4
- Tools will be added in later tasks

---

### Task 2.4: Create Wikipedia Tool
**Objective**: Implement Wikipedia search tool for researcher

**Steps**:
1. Install wikipedia package: `uv add wikipedia`
2. Create `backend/app/agents/tools.py`
3. Implement `wikipedia_search(tool_context: ToolContext, query: str) -> dict`

**Tests**:
```python
# tests/unit/agents/test_tools.py
def test_wikipedia_search_returns_dict(mocker):
    mocker.patch("wikipedia.summary", return_value="Test content")
    result = wikipedia_search(Mock(), "Ada Lovelace")
    assert result["status"] == "success"
    assert "results" in result

def test_wikipedia_search_handles_errors(mocker):
    mocker.patch("wikipedia.summary", side_effect=Exception("Not found"))
    result = wikipedia_search(Mock(), "Invalid")
    assert result["status"] == "error"
```

**Success Criteria**:
- [ ] Tool function implemented
- [ ] Error handling works
- [ ] Tests pass with mocks

**Files Created**: `backend/app/agents/tools.py`, `tests/unit/agents/test_tools.py`

---

### Task 2.5: Create append_to_state Tool
**Objective**: Implement state management tool

**Steps**:
1. In `backend/app/agents/tools.py`, add:
2. Implement `append_to_state(tool_context: ToolContext, key: str, content: str) -> dict`

**Tests**:
```python
# tests/unit/agents/test_tools.py
def test_append_to_state_adds_content():
    mock_context = Mock()
    mock_context.state = {}
    result = append_to_state(mock_context, "research", "test data")
    assert mock_context.state["research"] == ["test data"]
    assert result["status"] == "success"

def test_append_to_state_appends_to_existing():
    mock_context = Mock()
    mock_context.state = {"research": ["existing"]}
    append_to_state(mock_context, "research", "new")
    assert mock_context.state["research"] == ["existing", "new"]
```

**Success Criteria**:
- [ ] Tool implemented
- [ ] Handles empty and existing state
- [ ] Tests pass

**Files Modified**: `backend/app/agents/tools.py`, `tests/unit/agents/test_tools.py`

---

### Task 2.6: Connect Tools to Researcher Agent
**Objective**: Add tools to researcher agent definition

**Steps**:
1. Modify `backend/app/agents/researcher.py`
2. Import tools: `from .tools import wikipedia_search, append_to_state`
3. Add `tools=[wikipedia_search, append_to_state]` to agent

**Tests**:
```python
# tests/unit/agents/test_researcher.py
def test_researcher_has_wikipedia_tool():
    from app.agents.researcher import researcher
    tool_names = [t.__name__ for t in researcher.tools]
    assert "wikipedia_search" in tool_names

def test_researcher_has_append_to_state_tool():
    from app.agents.researcher import researcher
    tool_names = [t.__name__ for t in researcher.tools]
    assert "append_to_state" in tool_names
```

**Success Criteria**:
- [ ] Tools imported
- [ ] Tools attached to agent
- [ ] Tests pass

**Files Modified**: `backend/app/agents/researcher.py`

---

### Task 2.7: Create Screenwriter Agent
**Objective**: Implement screenwriter LlmAgent with output_key

**Steps**:
1. Create `backend/app/agents/screenwriter.py`
2. Define agent with `output_key="PLOT_OUTLINE"`

**Tests**:
```python
# tests/unit/agents/test_screenwriter.py
def test_screenwriter_agent_created():
    from app.agents.screenwriter import screenwriter
    assert screenwriter.name == "screenwriter"

def test_screenwriter_has_output_key():
    from app.agents.screenwriter import screenwriter
    assert screenwriter.output_key == "PLOT_OUTLINE"
```

**Success Criteria**:
- [ ] Agent defined
- [ ] output_key set
- [ ] Tests pass

**Files Created**: `backend/app/agents/screenwriter.py`, `tests/unit/agents/test_screenwriter.py`

---

### Task 2.8: Create Critic Agent
**Objective**: Implement critic with exit_loop tool

**Steps**:
1. Create `backend/app/agents/critic.py`
2. Import `from google.adk.tools import exit_loop`
3. Add `tools=[append_to_state, exit_loop]`

**Tests**:
```python
# tests/unit/agents/test_critic.py
def test_critic_agent_created():
    from app.agents.critic import critic
    assert critic.name == "critic"

def test_critic_has_exit_loop_tool():
    from app.agents.critic import critic
    tool_names = [t.__name__ for t in critic.tools]
    assert "exit_loop" in tool_names
```

**Success Criteria**:
- [ ] Agent defined
- [ ] exit_loop tool attached
- [ ] Tests pass

**Files Created**: `backend/app/agents/critic.py`, `tests/unit/agents/test_critic.py`

---

### Task 2.9: Create Writers Room LoopAgent
**Objective**: Implement LoopAgent workflow orchestrator

**Steps**:
1. Create `backend/app/agents/workflows.py`
2. Import all sub-agents: `researcher`, `screenwriter`, `critic`
3. Define `writers_room = LoopAgent(...)`

**Tests**:
```python
# tests/unit/agents/test_workflows.py
def test_writers_room_is_loop_agent():
    from app.agents.workflows import writers_room
    from google.adk.agents import LoopAgent
    assert isinstance(writers_room, LoopAgent)

def test_writers_room_has_sub_agents():
    from app.agents.workflows import writers_room
    assert len(writers_room.sub_agents) == 3

def test_writers_room_max_iterations():
    from app.agents.workflows import writers_room
    assert writers_room.max_iterations == 5
```

**Success Criteria**:
- [ ] LoopAgent created
- [ ] Sub-agents correct
- [ ] max_iterations set
- [ ] Tests pass

**Files Created**: `backend/app/agents/workflows.py`, `tests/unit/agents/test_workflows.py`

---

### Task 2.10: Create Box Office Analyst Agent
**Objective**: Implement box office analysis agent

**Steps**:
1. Create `backend/app/agents/box_office.py`
2. Define agent with `output_key="box_office_report"`

**Tests**:
```python
# tests/unit/agents/test_box_office.py
def test_box_office_agent_created():
    from app.agents.box_office import box_office_analyst
    assert box_office_analyst.name == "box_office_researcher"

def test_box_office_has_output_key():
    from app.agents.box_office import box_office_analyst
    assert box_office_analyst.output_key == "box_office_report"
```

**Success Criteria**:
- [ ] Agent defined
- [ ] output_key set
- [ ] Tests pass

**Files Created**: `backend/app/agents/box_office.py`, `tests/unit/agents/test_box_office.py`

---

### Task 2.11: Create Casting Director Agent
**Objective**: Implement casting suggestions agent

**Steps**:
1. Create `backend/app/agents/casting.py`
2. Define agent with `output_key="casting_report"`

**Tests**:
```python
# tests/unit/agents/test_casting.py
def test_casting_agent_created():
    from app.agents.casting import casting_director
    assert casting_director.name == "casting_agent"

def test_casting_has_output_key():
    from app.agents.casting import casting_director
    assert casting_director.output_key == "casting_report"
```

**Success Criteria**:
- [ ] Agent defined
- [ ] output_key set
- [ ] Tests pass

**Files Created**: `backend/app/agents/casting.py`, `tests/unit/agents/test_casting.py`

---

### Task 2.12: Create Preproduction Team ParallelAgent
**Objective**: Implement parallel workflow for reports

**Steps**:
1. In `backend/app/agents/workflows.py`, add:
2. Define `preproduction_team = ParallelAgent(...)`

**Tests**:
```python
# tests/unit/agents/test_workflows.py
def test_preproduction_team_is_parallel():
    from app.agents.workflows import preproduction_team
    from google.adk.agents import ParallelAgent
    assert isinstance(preproduction_team, ParallelAgent)

def test_preproduction_team_has_two_agents():
    from app.agents.workflows import preproduction_team
    assert len(preproduction_team.sub_agents) == 2
```

**Success Criteria**:
- [ ] ParallelAgent created
- [ ] Sub-agents correct (box_office, casting)
- [ ] Tests pass

**Files Modified**: `backend/app/agents/workflows.py`

---

### Task 2.13: Create File Writer Agent
**Objective**: Implement document generation agent

**Steps**:
1. Create `backend/app/agents/file_writer.py`
2. Create `write_file` tool in `tools.py`
3. Attach tool to agent

**Tests**:
```python
# tests/unit/agents/test_file_writer.py
def test_file_writer_agent_created():
    from app.agents.file_writer import file_writer
    assert file_writer.name == "file_writer"

def test_write_file_tool_creates_file(tmp_path):
    mock_context = Mock()
    result = write_file(mock_context, "test", str(tmp_path), "content")
    assert result["status"] == "success"
    assert (tmp_path / "test.txt").exists()
```

**Success Criteria**:
- [ ] Agent defined
- [ ] write_file tool works
- [ ] Tests pass

**Files Created**: `backend/app/agents/file_writer.py`, `tests/unit/agents/test_file_writer.py`

---

### Task 2.14: Create Film Concept Team SequentialAgent
**Objective**: Implement main workflow orchestrator

**Steps**:
1. In `backend/app/agents/workflows.py`, add:
2. Define `film_concept_team = SequentialAgent(...)`
3. Sub-agents: `[writers_room, preproduction_team, file_writer]`

**Tests**:
```python
# tests/unit/agents/test_workflows.py
def test_film_concept_team_is_sequential():
    from app.agents.workflows import film_concept_team
    from google.adk.agents import SequentialAgent
    assert isinstance(film_concept_team, SequentialAgent)

def test_film_concept_team_order():
    from app.agents.workflows import film_concept_team
    agent_names = [a.name for a in film_concept_team.sub_agents]
    assert agent_names == ["writers_room", "preproduction_team", "file_writer"]
```

**Success Criteria**:
- [ ] SequentialAgent created
- [ ] Sub-agents in correct order
- [ ] Tests pass

**Files Modified**: `backend/app/agents/workflows.py`

---

### Task 2.15: Create Root Greeter Agent
**Objective**: Implement entry point agent

**Steps**:
1. Create `backend/app/agents/greeter.py`
2. Define agent with `sub_agents=[film_concept_team]`

**Tests**:
```python
# tests/unit/agents/test_greeter.py
def test_greeter_agent_created():
    from app.agents.greeter import greeter
    assert greeter.name == "greeter"

def test_greeter_has_film_concept_team():
    from app.agents.greeter import greeter
    assert len(greeter.sub_agents) == 1
    assert greeter.sub_agents[0].name == "film_concept_team"
```

**Success Criteria**:
- [ ] Agent defined
- [ ] Sub-agent attached
- [ ] Tests pass

**Files Created**: `backend/app/agents/greeter.py`, `tests/unit/agents/test_greeter.py`

---

## Phase 3: Service Layer (Business Logic)

### Task 3.1: Create Session Manager
**Objective**: Implement ADK session lifecycle management

**Steps**:
1. Create `backend/app/core/session_manager.py`
2. Implement `SessionManager` class with:
   - `get_or_create_session(session_id: UUID) -> ADKSession`
   - In-memory cache for active sessions

**Tests**:
```python
# tests/unit/core/test_session_manager.py
def test_session_manager_creates_new_session():
    manager = SessionManager()
    session_id = uuid4()
    session = manager.get_or_create_session(session_id)
    assert session is not None

def test_session_manager_returns_cached_session():
    manager = SessionManager()
    session_id = uuid4()
    session1 = manager.get_or_create_session(session_id)
    session2 = manager.get_or_create_session(session_id)
    assert session1 is session2  # Same object
```

**Success Criteria**:
- [ ] SessionManager class implemented
- [ ] Caching works
- [ ] Tests pass

**Files Created**: `backend/app/core/session_manager.py`, `tests/unit/core/test_session_manager.py`

---

### Task 3.2: Create Persistence Service
**Objective**: Implement Q&A and reasoning persistence

**Steps**:
1. Create `backend/app/services/persistence_service.py`
2. Implement methods:
   - `save_question(session_id, question_text) -> UUID`
   - `save_answer(session_id, agent_name, answer_text) -> UUID`
   - `save_state_snapshot(session_id, state: dict) -> None`

**Tests**:
```python
# tests/unit/services/test_persistence_service.py
def test_save_question(db_session):
    service = PersistenceService(db_session)
    question_id = service.save_question(uuid4(), "Test question")
    assert question_id is not None

def test_save_answer(db_session):
    service = PersistenceService(db_session)
    answer_id = service.save_answer(uuid4(), "researcher", "Test answer")
    assert answer_id is not None
```

**Success Criteria**:
- [ ] Service class implemented
- [ ] All methods work
- [ ] Tests pass

**Files Created**: `backend/app/services/persistence_service.py`, `tests/unit/services/test_persistence_service.py`

**Note**: Requires Question, Answer, SessionState models (create in separate tasks if needed)

---

### Task 3.3: Create ADK Runner
**Objective**: Implement ADK agent execution wrapper

**Steps**:
1. Create `backend/app/core/adk_runner.py`
2. Implement `ADKRunner` class with:
   - `__init__(session_id, session_manager, persistence_service)`
   - `initialize() -> None`
   - `send_message(message: str) -> str`

**Tests**:
```python
# tests/unit/core/test_adk_runner.py
@pytest.mark.asyncio
async def test_adk_runner_initializes():
    runner = ADKRunner(uuid4(), Mock(), Mock())
    await runner.initialize()
    assert runner.runner is not None

@pytest.mark.asyncio
async def test_adk_runner_sends_message(mocker):
    mocker.patch("google.adk.Runner.run", return_value="Test response")
    runner = ADKRunner(uuid4(), Mock(), Mock())
    await runner.initialize()
    response = await runner.send_message("Test")
    assert response == "Test response"
```

**Success Criteria**:
- [ ] ADKRunner class implemented
- [ ] Async methods work
- [ ] Tests pass with mocks

**Files Created**: `backend/app/core/adk_runner.py`, `tests/unit/core/test_adk_runner.py`

---

### Task 3.4: Create Session Service
**Objective**: Implement high-level session business logic

**Steps**:
1. Create `backend/app/services/session_service.py`
2. Implement `SessionService` class with:
   - `create_session() -> UUID`
   - `get_runner(session_id: UUID) -> ADKRunner`
   - `send_message(session_id, message) -> str`

**Tests**:
```python
# tests/unit/services/test_session_service.py
@pytest.mark.asyncio
async def test_session_service_creates_session(db_session):
    service = SessionService(db_session)
    session_id = await service.create_session()
    assert session_id is not None

@pytest.mark.asyncio
async def test_session_service_sends_message(db_session, mocker):
    mocker.patch.object(ADKRunner, "send_message", return_value="Response")
    service = SessionService(db_session)
    session_id = await service.create_session()
    response = await service.send_message(session_id, "Test")
    assert response == "Response"
```

**Success Criteria**:
- [ ] SessionService implemented
- [ ] Dependencies injected correctly
- [ ] Tests pass

**Files Created**: `backend/app/services/session_service.py`, `tests/unit/services/test_session_service.py`

---

## Phase 4: API Layer (HTTP Interface)

### Task 4.1: Create FastAPI Application
**Objective**: Initialize FastAPI app with basic config

**Steps**:
1. Create `backend/app/main.py`
2. Initialize `app = FastAPI(title="Film Concept Generator")`
3. Add health check endpoint

**Tests**:
```python
# tests/integration/test_main.py
def test_app_creation():
    from app.main import app
    assert app.title == "Film Concept Generator"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

**Success Criteria**:
- [ ] App initialized
- [ ] Health endpoint works
- [ ] Tests pass with test client

**Files Created**: `backend/app/main.py`, `tests/integration/test_main.py`

**Implementation Hints**:
- Add `client` fixture in `conftest.py` using `TestClient`

---

### Task 4.2: Create Session API Endpoints
**Objective**: Implement REST endpoints for sessions

**Steps**:
1. Create `backend/app/api/v1/sessions.py`
2. Implement routes:
   - `POST /api/v1/sessions` (create)
   - `POST /api/v1/sessions/{session_id}/messages` (send message)
   - `GET /api/v1/sessions/{session_id}/state` (get state)

**Tests**:
```python
# tests/integration/test_sessions_api.py
def test_create_session(client):
    response = client.post("/api/v1/sessions")
    assert response.status_code == 200
    assert "id" in response.json()

def test_send_message(client, mocker):
    mocker.patch.object(SessionService, "send_message", return_value="Response")
    session_response = client.post("/api/v1/sessions")
    session_id = session_response.json()["id"]

    response = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"message": "Test"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

**Success Criteria**:
- [ ] All endpoints implemented
- [ ] Dependency injection works
- [ ] Tests pass

**Files Created**: `backend/app/api/v1/sessions.py`, `tests/integration/test_sessions_api.py`

---

### Task 4.3: Add CORS Middleware
**Objective**: Enable frontend to call API

**Steps**:
1. In `backend/app/main.py`, add CORS middleware
2. Configure allowed origins from settings

**Tests**:
```python
# tests/integration/test_cors.py
def test_cors_headers_present(client):
    response = client.options("/api/v1/sessions", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert "access-control-allow-origin" in response.headers
```

**Success Criteria**:
- [ ] CORS middleware added
- [ ] Preflight requests work
- [ ] Tests pass

**Files Modified**: `backend/app/main.py`

---

### Task 4.4: Create Database Dependency
**Objective**: Implement database session injection

**Steps**:
1. Create `backend/app/api/dependencies.py`
2. Implement `get_db()` generator function

**Tests**:
```python
# tests/unit/api/test_dependencies.py
def test_get_db_yields_session():
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)

    # Cleanup
    try:
        next(gen)
    except StopIteration:
        pass  # Expected
```

**Success Criteria**:
- [ ] Dependency function implemented
- [ ] Session cleanup works
- [ ] Tests pass

**Files Created**: `backend/app/api/dependencies.py`, `tests/unit/api/test_dependencies.py`

---

## Phase 5: Docker & Infrastructure

### Task 5.1: Create .env.example
**Objective**: Document required environment variables

**Steps**:
1. Create `.env.example` in project root
2. Add all required variables with placeholder values

**Tests**: None (documentation task)

**Success Criteria**:
- [ ] File created
- [ ] All variables documented

**Files Created**: `.env.example`

**Content Template**:
```bash
# Application
APP_NAME=Film Concept Generator
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/filmmaking

# Google Cloud (for Vertex AI)
GOOGLE_CLOUD_PROJECT=your-gcp-project
```

---

### Task 5.2: Create Backend Dockerfile
**Objective**: Containerize Python application

**Steps**:
1. Create `backend/Dockerfile` (multi-stage build)
2. Use Python 3.12-slim base
3. Install uv and dependencies

**Tests**: None (infrastructure task)

**Success Criteria**:
- [ ] Dockerfile builds successfully
- [ ] Image size < 500MB

**Files Created**: `backend/Dockerfile`

**Implementation Hints**:
- Use template from architecture.md section 8.3
- Multi-stage: base → dependencies → production

---

### Task 5.3: Create docker-compose.yml
**Objective**: Orchestrate all services

**Steps**:
1. Create `docker-compose.yml` in project root
2. Define services: postgres, redis, api
3. Add health checks and dependencies

**Tests**: None (infrastructure task)

**Success Criteria**:
- [ ] `docker-compose up` works
- [ ] All services healthy
- [ ] API accessible on port 8000

**Files Created**: `docker-compose.yml`

**Implementation Hints**:
- Use template from architecture.md section 8.2
- Start with postgres + api only (add LiteLLM later)

---

### Task 5.4: Create Database Initialization Script
**Objective**: Setup PostgreSQL schema

**Steps**:
1. Create `database/init.sql`
2. Add sessions table creation
3. Add indexes

**Tests**: None (infrastructure task)

**Success Criteria**:
- [ ] Script runs without errors
- [ ] Tables created
- [ ] Indexes present

**Files Created**: `database/init.sql`

**Implementation Hints**:
- Use schema from architecture.md section 5.1
- Use `CREATE TABLE IF NOT EXISTS`

---

## Phase 6: Integration & End-to-End Testing

### Task 6.1: Create E2E Test for Film Creation
**Objective**: Test complete user workflow

**Steps**:
1. Create `backend/tests/e2e/test_film_creation_flow.py`
2. Test: Create session → Send message → Verify response

**Tests**:
```python
# tests/e2e/test_film_creation_flow.py
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_film_creation_workflow(client, db):
    # Create session
    response = client.post("/api/v1/sessions")
    session_id = response.json()["id"]

    # Send message
    response = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"message": "Create film about Ada Lovelace"}
    )

    assert response.status_code == 200
    assert "response" in response.json()

    # Verify state saved
    state_response = client.get(f"/api/v1/sessions/{session_id}/state")
    assert state_response.status_code == 200
```

**Success Criteria**:
- [ ] E2E test passes
- [ ] Database records created
- [ ] State persisted

**Files Created**: `backend/tests/e2e/test_film_creation_flow.py`

**Note**: Mark with `@pytest.mark.e2e` to run separately

---

### Task 6.2: Add Pytest Configuration
**Objective**: Configure test execution and coverage

**Steps**:
1. Create `pytest.ini`
2. Configure markers, coverage, async

**Tests**: None (configuration task)

**Success Criteria**:
- [ ] `pytest` runs all tests
- [ ] Coverage report generated
- [ ] Markers work (unit, integration, e2e)

**Files Created**: `pytest.ini`

**Content**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
addopts =
    --verbose
    --cov=backend/app
    --cov-report=term-missing
    --cov-report=html
```

---

## Phase 7: Documentation & Deployment

### Task 7.1: Create README.md
**Objective**: Document project setup and usage

**Steps**:
1. Create `README.md` in project root
2. Add sections: Features, Setup, Running, Testing

**Tests**: None (documentation task)

**Success Criteria**:
- [ ] README complete
- [ ] Setup instructions work

**Files Created**: `README.md`

---

### Task 7.2: Create Development Quick Start
**Objective**: Script for easy development setup

**Steps**:
1. Create `scripts/dev-setup.sh`
2. Automate: uv sync, docker-compose up, db init

**Tests**: None (tooling task)

**Success Criteria**:
- [ ] Script runs without errors
- [ ] Development environment ready

**Files Created**: `scripts/dev-setup.sh`

---

## Appendix: Testing Patterns

### Unit Test Template
```python
# tests/unit/module/test_feature.py
import pytest
from app.module.feature import Feature

def test_feature_does_something():
    """Test description following TDD."""
    # Arrange
    feature = Feature()

    # Act
    result = feature.do_something()

    # Assert
    assert result == expected_value
```

### Integration Test Template
```python
# tests/integration/test_api_feature.py
import pytest
from fastapi.testclient import TestClient

def test_api_endpoint(client: TestClient, db_session):
    """Test API endpoint with database."""
    # Arrange
    # ... setup test data

    # Act
    response = client.post("/api/endpoint", json={"data": "value"})

    # Assert
    assert response.status_code == 200
    # ... verify database state
```

### E2E Test Template
```python
# tests/e2e/test_workflow.py
import pytest

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_workflow(client, db):
    """Test complete user journey."""
    # ... multi-step workflow test
```

---

## Task Completion Checklist

For each task, verify:
- [ ] Tests written BEFORE implementation (TDD)
- [ ] All tests pass (`pytest -v`)
- [ ] Type hints on all functions
- [ ] 4-space indentation
- [ ] SOLID principles followed
- [ ] Code committed with conventional commit message
- [ ] Task marked as complete in this document

---

## Execution Order Summary

**Recommended sequence:**
1. Phase 0: Project Setup (Tasks 0.1-0.3)
2. Phase 1: Database Layer (Tasks 1.1-1.5)
3. Phase 2: Core Domain (Tasks 2.1-2.15)
4. Phase 3: Service Layer (Tasks 3.1-3.4)
5. Phase 4: API Layer (Tasks 4.1-4.4)
6. Phase 5: Docker (Tasks 5.1-5.4)
7. Phase 6: Integration Tests (Tasks 6.1-6.2)
8. Phase 7: Documentation (Tasks 7.1-7.2)

**Total Tasks**: 44 granular, testable tasks

**Estimated Time per Task**: 15-30 minutes

**Total MVP Time**: ~20-30 hours

---

## Notes for Engineering LLM

**After completing each task:**
1. Run `pytest tests/unit` for unit tests
2. Run `pytest tests/integration` for integration tests
3. Run `ruff check .` for linting
4. Run `mypy backend/app` for type checking
5. Commit with message format: `feat(scope): description` or `test(scope): description`

**Before moving to next task:**
- Wait for human verification
- Ensure all tests pass
- Confirm no regressions in existing tests

**If stuck:**
- Review architecture.md for implementation details
- Check Context7 ADK documentation
- Ask for clarification on requirements

---

**End of Task List**
**Version**: 1.0.0
**Last Updated**: 2025-11-25