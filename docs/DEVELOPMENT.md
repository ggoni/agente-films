# Development Guide

## Project Setup

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Docker and Docker Compose
- Node.js 20+ (for frontend)

### Initial Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd agente-films

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

## Development Workflow

```mermaid
graph LR
    Code[Write Code] --> Lint[Lint & Format]
    Lint --> Test[Run Tests]
    Test --> Local[Local Verify]
    Local --> Commit[Commit & Push]
    Commit --> CI[CI Pipeline]
    
    subgraph "Inner Loop (Fast)"
    Code
    Lint
    Test
    end
    
    style Code fill:#bbdefb
    style Lint fill:#fff9c4
    style Test fill:#c8e6c9
```

### Local Development

```bash
# Run backend API with hot reload
uv run uvicorn src.api.main:app --reload --port 8000

# Run tests with coverage
uv run pytest

# Run specific test markers
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e

# Run linting
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy src
```

### Docker Development

```bash
# Build and start all services
docker-compose up --build

# Start specific service
docker-compose up api

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Clean volumes
docker-compose down -v
```

### Testing ADK Agents Locally

```bash
# Test agent in CLI
uv run adk run src.agents.screenplay_agent

# Test agent with web UI
uv run adk web --port 8001 --reload_agents
```

### Debugging LiteLLM Proxy

```bash
# Check proxy health
curl http://localhost:4000/health

# Test model endpoint
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# View proxy logs
docker-compose logs -f litellm-proxy
```

## Code Quality

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

- Trailing whitespace removal
- YAML/JSON/TOML validation
- Ruff linting and formatting
- MyPy type checking

```bash
# Run pre-commit manually
uv run pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

### Linting Configuration

Ruff configuration in `pyproject.toml`:

- Line length: 100 characters
- Python version: 3.12
- Enabled rules: pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- Auto-fixes available for most issues

### Type Checking

MyPy configuration in `pyproject.toml`:

- Strict mode enabled
- Disallow untyped definitions
- Warn on unused configs and redundant casts
- Check untyped definitions

## Testing Strategy

### Unit Tests

Located in `tests/unit/`

Test individual components in isolation:

```python
# Example: Testing ADK agent
@pytest.mark.unit
async def test_agent_creation():
    agent = ScreenplayAgent(model="gemini-2.5-flash")
    assert agent.model == "gemini-2.5-flash"
```

Mock LLM responses:

```python
@pytest.fixture
def mock_llm_response():
    return {
        "title": "Test Title",
        "logline": "Test logline",
        # ...
    }

async def test_with_mock(mock_llm_response):
    with patch.object(agent, 'create_outline', return_value=mock_llm_response):
        result = await agent.create_outline("concept")
```

### Integration Tests

Located in `tests/integration/`

Test component interactions:

```python
@pytest.mark.integration
async def test_api_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/screenplay/generate", json={...})
        assert response.status_code == 201
```

### E2E Tests

Located in `tests/e2e/`

Test complete workflows:

```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_full_screenplay_workflow():
    # Test entire flow from API request to agent response
    pass
```

### Coverage Reports

```bash
# Generate coverage report
uv run pytest --cov=src --cov-report=html

# View HTML report
open htmlcov/index.html
```

## Environment Variables

Create `.env` file:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_LOCATION=global

# LiteLLM
LITELLM_MASTER_KEY=sk-your-key
DATABASE_URL=postgresql://litellm:litellm@localhost:5432/litellm

# OpenAI (optional)
OPENAI_API_KEY=sk-your-key

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-your-key

# Langfuse (optional)
LANGFUSE_PUBLIC_KEY=pk-your-key
LANGFUSE_SECRET_KEY=sk-your-key
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Architecture Patterns

### Repository Pattern

Abstracts data access logic:

```python
class ScreenplayRepository(ABC):
    @abstractmethod
    async def generate_outline(self, concept: str, model: str) -> dict:
        pass

class ADKScreenplayRepository(ScreenplayRepository):
    async def generate_outline(self, concept: str, model: str) -> dict:
        agent = self._get_agent(model)
        return await agent.create_outline(concept)
```

Benefits:
- Easy to mock in tests
- Swap implementations without changing API
- Cleaner separation of concerns

### Dependency Injection

Use FastAPI's dependency injection:

```python
def get_repository() -> ScreenplayRepository:
    return ADKScreenplayRepository()

@app.post("/api/screenplay/generate")
async def generate_screenplay(
    request: ScreenplayRequest,
    repository: ScreenplayRepository = Depends(get_repository)
):
    return await repository.generate_outline(...)
```

## Hot Reloading

### Backend Hot Reload

```bash
# Auto-reload on code changes
uv run uvicorn src.api.main:app --reload
```

### Agent Hot Reload

```bash
# Reload agents when files change
uv run adk web --reload_agents
```

### Frontend Hot Reload

```bash
# Vite dev server (in frontend directory)
npm run dev
```

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker Issues

```bash
# Clean Docker system
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### uv Lock Issues

```bash
# Update lock file
uv lock --upgrade

# Force reinstall
rm -rf .venv
uv sync --all-extras
```

## Performance Tips

### Docker Build Optimization

- Multi-stage builds reduce image size
- Layer caching speeds up rebuilds
- `.dockerignore` excludes unnecessary files

### Test Optimization

- Run unit tests first (fastest feedback)
- Use `pytest-xdist` for parallel execution
- Mark slow tests with `@pytest.mark.slow`

## Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
