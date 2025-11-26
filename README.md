# Agente Films - Multi-Agent Filmmaking System

Multi-agent filmmaking system using Google ADK, LiteLLM Proxy, FastAPI backend, and React/TypeScript frontend.

> **⚡ Quick Start**: Just run `./start.sh` to start everything! See [Quick Start](#quick-start) below.

## Features

- **Multi-Model LLM Support**: Switch between 9 models (Gemini, GPT, Claude) at will
- **LiteLLM Proxy**: Unified interface to multiple LLM providers
- **Google ADK Agents**: Specialized agents for screenplay, characters, and story development
- **FastAPI Backend**: Clean architecture with repository pattern
- **React Frontend**: TypeScript-based UI with hooks
- **Complete Testing**: Unit, integration, and E2E tests
- **Code Quality**: Ruff, MyPy, pre-commit hooks
- **Full Docker Stack**: Multi-container deployment with PostgreSQL
- **CI/CD**: GitHub Actions workflow

## Quick Start

### One-Command Startup ⚡

```bash
./start.sh
```

**That's it!** On first run, the script will:
1. Check Docker is running
2. Create `.env` from template (if needed)
3. Prompt you to add your `GOOGLE_CLOUD_PROJECT`
4. Build all Docker images
5. Start 4 services (API, LiteLLM, PostgreSQL, Frontend)
6. Wait for everything to be ready
7. Show you the URLs to access

**Stop everything:**
```bash
./stop.sh
```

### First Time: Edit .env

The script creates `.env` automatically. Edit it with your credentials:

```bash
nano .env

# Required (minimum for Gemini):
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional (for GPT models):
OPENAI_API_KEY=sk-...

# Optional (for Claude models):
ANTHROPIC_API_KEY=sk-ant-...
```

Then run `./start.sh` again.

### Access Your Services

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **LiteLLM Dashboard**: http://localhost:4000/ui

**🔄 Switch Models:**
```bash
make switch-model MODEL=gpt-4
make switch-model MODEL=claude-3-5-sonnet
```

**📚 Detailed Guide:** See [docs/QUICK_START.md](docs/QUICK_START.md)

### Local Development (Without Docker)

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env

# 3. Start database only
docker-compose up -d postgres

# 4. Run migrations
uv run alembic upgrade head

# 5. Start API
uv run uvicorn backend.app.api.main:app --reload --port 8000
```

### Available Commands

```bash
make help           # Show all commands
make up             # Start services
make down           # Stop services
make logs           # View logs
make test-models    # Test all models
make list-models    # List available models
make health         # Check service health
make shell-api      # Open API container shell
```

## Project Structure

```
agente-films/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes and endpoints
│   │   ├── core/             # ADK Runner, Session Manager
│   │   ├── db/               # Database models and repositories
│   │   └── services/         # Business logic services
│   └── tests/
│       ├── unit/             # Unit tests
│       └── integration/      # Integration tests
├── scripts/
│   ├── e2e_test.py           # End-to-end testing script
│   └── verify_setup.py       # Environment verification
├── docs/
│   ├── ARCHITECTURE.md       # System architecture with diagrams
│   ├── DEVELOPMENT.md        # Development guide
│   ├── TESTING.md            # Testing strategy
│   └── EXAMPLES.md           # Complete examples
├── alembic/                  # Database migrations
├── docker-compose.yml        # Docker services definition
└── pyproject.toml            # Project dependencies
```

## Documentation

- **[Quick Start](docs/QUICK_START.md)**: Get started in 3 steps ⚡
- **[LiteLLM Setup](docs/LITELLM_SETUP.md)**: Complete multi-model guide 🎯
- **[Architecture](docs/ARCHITECTURE.md)**: System design with diagrams 🏗️
- **[Development Guide](docs/DEVELOPMENT.md)**: Local setup, hot reloading, debugging 💻
- **[Testing Guide](docs/TESTING.md)**: Testing strategy, mocking LLMs, coverage 🧪
- **[Examples](docs/EXAMPLES.md)**: Complete working examples 📝

## Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit        # Unit tests only
make test-int         # Integration tests only

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/unit/test_screenplay_agent.py
```

## Code Quality

### Pre-commit Hooks

Automatically run on commit:
- Ruff linting and formatting
- MyPy type checking
- YAML/JSON validation

```bash
# Run manually
make pre-commit
```

### Linting

```bash
# Check code
make lint

# Auto-fix issues
make format
```

### Type Checking

```bash
# Run MyPy
make typecheck
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Generate Screenplay

```bash
curl -X POST http://localhost:8000/api/screenplay/generate \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "A detective who can see the future must prevent a crime",
    "model": "gemini-2.5-flash"
  }'
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Architecture

### ADK Agents

```python
from google.adk import Agent

agent = Agent(
    name="screenplay_writer",
    model="gemini-2.5-flash",
    description="Expert in screenplay structure",
    instruction="Create compelling three-act structure...",
)
```

### Repository Pattern

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

### FastAPI Integration

```python
@app.post("/api/screenplay/generate")
async def generate_screenplay(
    request: ScreenplayRequest,
) -> ScreenplayResponse:
    repository = get_repository()
    result = await repository.generate_outline(request.concept)
    return ScreenplayResponse(**result)
```

## Multi-Model LLM Support

Access 9 different models from 3 providers through unified LiteLLM proxy:

**Available Models:**
| Provider | Models | Use Cases |
|----------|--------|-----------|
| **Google** | gemini-2.5-flash, gemini-2.0-flash, gemini-pro | Fast, cost-effective, reasoning |
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-3.5-turbo | High quality, versatile |
| **Anthropic** | claude-3-5-sonnet, claude-3-opus, claude-3-haiku | Balanced, capable, fast |

**Switch Models:**
```bash
# Method 1: Make command
make switch-model MODEL=gpt-4

# Method 2: Environment variable
MODEL=claude-3-5-sonnet docker-compose up api

# Method 3: In code
from backend.app.services.litellm_client import LiteLLMClient
client = LiteLLMClient()
response = await client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-3-5-sonnet"
)
```

**Management UI:**
- LiteLLM UI: http://localhost:4000/ui
- API Docs: http://localhost:8000/docs
- Health Check: `make health`

**📚 Complete Guide:** See [docs/LITELLM_SETUP.md](docs/LITELLM_SETUP.md)

## CI/CD Pipeline

GitHub Actions workflow runs on push/PR:

1. **Lint**: Ruff linting and formatting
2. **Type Check**: MyPy validation
3. **Test**: Unit and integration tests
4. **Build**: Docker image build
5. **Coverage**: Upload to Codecov

See `.github/workflows/ci.yml` for configuration.

## Deployment

### Docker Compose

```bash
# Production deployment
docker-compose up -d

# Scale services
docker-compose up -d --scale api=3
```

### Environment Variables

Required:
- `GOOGLE_CLOUD_PROJECT`
- `LITELLM_MASTER_KEY`

Optional:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `LANGFUSE_PUBLIC_KEY` (observability)

## Performance

- Multi-stage Docker builds (optimized image size)
- Repository pattern (agent caching)
- Async/await throughout
- Connection pooling (LiteLLM proxy)

## Observability

### Langfuse Integration

Track agent executions:

```yaml
# litellm-config.yaml
litellm_settings:
  callbacks: ["langfuse"]
```

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Run pre-commit hooks
5. Submit pull request

## Best Practices

- Follow conventional commits format
- Write tests for new features
- Use 4 spaces for indentation
- Type hint all functions
- Document complex logic

## Troubleshooting

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

## Resources

- [Google ADK](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LiteLLM](https://docs.litellm.ai/)
- [Ruff](https://docs.astral.sh/ruff/)

## License

MIT License - See LICENSE file for details
