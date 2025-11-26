# Development Guidelines Summary

## Overview

Complete development setup for multi-agent filmmaking system with:
- **Multi-Model LLM Support**: 9 models across 3 providers (Gemini, GPT, Claude)
- **LiteLLM Proxy**: Unified interface with model switching at will
- Google ADK agents
- FastAPI backend with repository pattern
- React/TypeScript frontend
- Comprehensive testing (unit, integration, E2E)
- CI/CD pipeline
- Full Docker stack deployment

## Project Structure

```
agente-films/
├── src/
│   ├── agents/              # ADK agents (screenplay, characters)
│   ├── api/                 # FastAPI (routes, models, repository)
│   └── tools/               # Custom ADK tools
├── tests/
│   ├── unit/                # Fast, isolated tests
│   ├── integration/         # Component interaction tests
│   └── e2e/                 # Full workflow tests
├── docs/
│   ├── DEVELOPMENT.md       # Local dev setup, hot reload, debugging
│   ├── TESTING.md           # Testing strategies, mocking LLMs
│   ├── EXAMPLES.md          # Complete working examples
│   └── ARCHITECTURE.md      # System design and patterns
├── .github/workflows/       # CI/CD pipeline
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Multi-container setup
├── pyproject.toml           # Dependencies and tool config
└── Makefile                 # Common commands
```

## Quick Commands

```bash
# Setup
make setup                # First-time setup (copy .env, build, start)
make up                   # Start all services
make down                 # Stop all services

# Model Management
make test-models          # Test all configured models
make list-models          # List available models
make switch-model MODEL=gpt-4  # Switch to different model

# Development
make logs                 # View all logs
make logs-api             # API logs only
make logs-litellm         # LiteLLM logs only
make health               # Check service health

# Testing
make test                 # Run all tests
make format               # Format code
make lint                 # Check code quality
make fix                  # Auto-fix linting issues

# Utilities
make shell-api            # Open API container shell
make shell-db             # Open PostgreSQL shell
make clean                # Clean containers and volumes
```

## Code Quality Tools

### Ruff (Linter & Formatter)
- Line length: 100 chars
- Python 3.12 target
- Auto-fixes for most issues
- Configured in `pyproject.toml`

```bash
uv run ruff check .        # Check code
uv run ruff check --fix .  # Auto-fix
uv run ruff format .       # Format code
```

### MyPy (Type Checker)
- Strict mode enabled
- Disallow untyped definitions
- Check all function signatures

```bash
uv run mypy src
```

### Pre-commit Hooks
Run automatically on commit:
- Trailing whitespace removal
- YAML/JSON/TOML validation
- Ruff linting and formatting
- MyPy type checking

```bash
uv run pre-commit run --all-files
```

## Testing Strategy

### 1. Unit Tests (Fast, Isolated)

**Location**: `tests/unit/`
**Purpose**: Test individual components
**Markers**: `@pytest.mark.unit`

**Example**:
```python
@pytest.mark.unit
def test_agent_initialization():
    agent = ScreenplayAgent(model="gemini-2.5-flash")
    assert agent.model == "gemini-2.5-flash"
```

**Mocking LLM Responses**:
```python
@pytest.fixture
def mock_llm_response():
    return {
        "title": "Test Title",
        "logline": "Test story",
        "three_act_structure": {...},
        "characters": [...]
    }

@pytest.mark.unit
async def test_with_mock(mock_llm_response):
    with patch.object(agent, 'create_outline', return_value=mock_llm_response):
        result = await agent.create_outline("concept")
        assert result["title"] == "Test Title"
```

### 2. Integration Tests (Component Interaction)

**Location**: `tests/integration/`
**Purpose**: Test API endpoints, repository pattern
**Markers**: `@pytest.mark.integration`

**Example**:
```python
@pytest.mark.integration
async def test_api_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/screenplay/generate",
            json={"concept": "Story idea"}
        )
        assert response.status_code == 201
```

### 3. E2E Tests (Full Workflows)

**Location**: `tests/e2e/`
**Purpose**: Test complete user workflows
**Markers**: `@pytest.mark.e2e`, `@pytest.mark.slow`

**Example**:
```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_complete_workflow():
    # Test from API request to final response
    pass
```

### Running Tests

```bash
# All tests
uv run pytest

# By marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific file
uv run pytest tests/unit/test_screenplay_agent.py

# Specific test
uv run pytest tests/unit/test_screenplay_agent.py::test_agent_initialization
```

## Architecture Patterns

### 1. Repository Pattern

**Purpose**: Abstract data access layer

```python
class ScreenplayRepository(ABC):
    @abstractmethod
    async def generate_outline(self, concept: str) -> dict:
        pass

class ADKScreenplayRepository(ScreenplayRepository):
    async def generate_outline(self, concept: str) -> dict:
        agent = self._get_agent()
        return await agent.create_outline(concept)
```

**Benefits**:
- Easy to test (mock repository)
- Swappable implementations
- Clean separation of concerns

### 2. Dependency Injection

**Purpose**: Manage dependencies cleanly

```python
def get_repository() -> ScreenplayRepository:
    return ADKScreenplayRepository()

@app.post("/api/screenplay/generate")
async def generate_screenplay(
    request: ScreenplayRequest,
    repository: ScreenplayRepository = Depends(get_repository)
):
    return await repository.generate_outline(request.concept)
```

**Benefits**:
- Testable (inject mocks)
- Flexible configuration
- Clear dependencies

## ADK Agent Development

### Basic Agent

```python
from google.adk import Agent

agent = Agent(
    name="agent_name",
    model="gemini-2.5-flash",
    description="What the agent does",
    instruction="""
    Detailed instructions for the agent.
    Use {state_key?} to read from session state.
    """,
    tools=[tool_function],
)
```

### Agent with Tools

```python
def save_to_state(
    tool_context: ToolContext,
    key: str,
    value: str,
) -> dict[str, str]:
    """Save data to session state."""
    tool_context.state[key] = value
    return {"status": "success"}

agent = Agent(
    name="agent_with_tool",
    model="gemini-2.5-flash",
    tools=[save_to_state],
)
```

### Multi-Agent Workflows

**Sequential** (one after another):
```python
workflow = SequentialAgent(
    name="workflow",
    sub_agents=[agent1, agent2, agent3],
)
```

**Loop** (iterative refinement):
```python
workflow = LoopAgent(
    name="iterative_workflow",
    sub_agents=[researcher, writer, critic],
    max_iterations=5,
)
```

**Parallel** (concurrent execution):
```python
workflow = ParallelAgent(
    name="parallel_workflow",
    sub_agents=[research_agent, analysis_agent],
)
```

## Local Development

### Hot Reloading

**Backend**:
```bash
uv run uvicorn src.api.main:app --reload
```

**Agents**:
```bash
uv run adk web --reload_agents
```

**Frontend**:
```bash
cd frontend
npm run dev
```

### Debugging

**ADK CLI**:
```bash
uv run adk run src.agents.screenplay_agent
```

**ADK Web UI**:
```bash
uv run adk web --port 8001
# Visit http://localhost:8001
```

**LiteLLM Proxy**:
```bash
# Check health
curl http://localhost:4000/health

# List models
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

## Docker Development

### Local Docker

```bash
# Build
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Services

- `api`: FastAPI backend (port 8000) - http://localhost:8000/docs
- `litellm-proxy`: LLM proxy (port 4000) - http://localhost:4000/ui
- `postgres`: PostgreSQL (port 5433) - filmdb + litellm databases
- `frontend`: React app (port 3000) - http://localhost:3000

### Multi-Model Support

**Available Models (9 total):**
- Google: gemini-2.5-flash, gemini-2.0-flash, gemini-pro
- OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- Anthropic: claude-3-5-sonnet, claude-3-opus, claude-3-haiku

**Switch Models:**
```bash
make switch-model MODEL=gpt-4
make switch-model MODEL=claude-3-5-sonnet
```

## CI/CD Pipeline

GitHub Actions runs on push/PR:

1. **Lint**: Ruff check and format validation
2. **Type Check**: MyPy validation
3. **Test**: Unit and integration tests
4. **Coverage**: Upload to Codecov
5. **Build**: Docker image build

**Configuration**: `.github/workflows/ci.yml`

## Common Issues

### Port in Use
```bash
lsof -i :8000
kill -9 <PID>
```

### Docker Issues
```bash
docker system prune -a
docker-compose build --no-cache
```

### uv Lock Issues
```bash
rm -rf .venv
uv sync --all-extras
```

### Pre-commit Issues
```bash
uv run pre-commit clean
uv run pre-commit install
```

## Best Practices

### Code Style
- 4 spaces indentation (Python)
- Type hints on all functions
- Docstrings with Args/Returns
- Max line length: 100 chars

### Git Commits
- Conventional Commits format
- Example: `feat: add character agent`
- Example: `fix: resolve API timeout issue`
- Example: `test: add integration tests for workflow`

### Testing
- Test behavior, not implementation
- Mock external dependencies
- Keep tests fast (<1s for unit)
- Use fixtures for shared setup
- Aim for 80%+ coverage

### Documentation
- Update docs with code changes
- Include examples in docstrings
- Keep README.md current
- Document complex logic

## Environment Variables

**Required (minimum for Gemini):**
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
MODEL=gemini-2.5-flash
```

**Optional (for other models):**
```bash
OPENAI_API_KEY=sk-your-key        # For GPT models
ANTHROPIC_API_KEY=sk-your-key     # For Claude models
```

**LiteLLM Configuration:**
```bash
LITELLM_BASE_URL=http://litellm-proxy:4000
LITELLM_MASTER_KEY=sk-1234
```

**See:** `.env.example` for complete list

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Dependencies, tool config |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container setup |
| `litellm-config.yaml` | LLM proxy configuration |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.github/workflows/ci.yml` | CI/CD pipeline |
| `Makefile` | Common commands |

## Documentation

- **[QUICK_START.md](QUICK_START.md)**: Get started in 3 steps ⚡
- **[LITELLM_SETUP.md](LITELLM_SETUP.md)**: Complete multi-model guide 🎯
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Detailed development guide
- **[TESTING.md](TESTING.md)**: Complete testing strategies
- **[EXAMPLES.md](EXAMPLES.md)**: Working code examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System design patterns
- **[README.md](../README.md)**: Project overview

## Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review examples in `docs/EXAMPLES.md`
3. Check existing tests for patterns
4. Run `make help` for available commands
