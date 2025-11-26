# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                  (React + TypeScript)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │─▶│  Repository  │─▶│  ADK Agents  │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
└─────────────────────────────────────────────┼──────────────┘
                                              │
                       ┌──────────────────────┼──────────────┐
                       │                      ▼              │
                       │            LiteLLM Proxy            │
                       │                      │              │
                       └──────────────────────┼──────────────┘
                                              │
                    ┌─────────────────────────┼──────────────┐
                    │                         ▼              │
                    │  ┌──────────┐  ┌──────────┐           │
                    │  │  Gemini  │  │  GPT-4   │  ...      │
                    │  └──────────┘  └──────────┘           │
                    └───────────────────────────────────────┘
```

## Components

### 1. ADK Agents Layer

**Purpose**: Specialized agents for filmmaking tasks

**Components**:
- `ScreenplayAgent`: Creates screenplay outlines
- `CharacterAgent`: Develops characters
- `WorkflowAgent`: Orchestrates multi-agent workflows

**Key Features**:
- Model-agnostic (configurable LLM backend)
- Session state management
- Tool integration
- Agent composition (Sequential, Loop, Parallel)

**Example**:
```python
agent = Agent(
    name="screenplay_writer",
    model="gemini-2.5-flash",
    description="Expert in screenplay structure",
    instruction="Create three-act structure...",
    tools=[save_to_state],
)
```

### 2. FastAPI Backend

**Purpose**: HTTP API for agent interaction

**Layers**:

#### a. Routes Layer (`src/api/main.py`)
- HTTP endpoint definitions
- Request/response handling
- Error handling
- CORS configuration

#### b. Repository Layer (`src/api/repository.py`)
- Abstract data access
- Agent lifecycle management
- Caching strategies
- Model selection

#### c. Models Layer (`src/api/models.py`)
- Pydantic schemas
- Request validation
- Response serialization
- Type safety

**Pattern**: Repository Pattern
- Decouples business logic from data access
- Easy to test with mocks
- Swappable implementations

**Example**:
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

### 3. LiteLLM Proxy

**Purpose**: Unified interface for multiple LLM providers

**Features**:
- Model abstraction
- Load balancing
- Rate limiting
- Cost tracking
- Observability (Langfuse integration)

**Configuration**:
```yaml
model_list:
  - model_name: gemini-2.5-flash
    litellm_params:
      model: vertex_ai/gemini-2.5-flash
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
```

### 4. Frontend (React)

**Purpose**: User interface for agent interaction

**Components**:
- `ScreenplayGenerator`: Main form component
- `useScreenplay`: Custom hook for API calls
- Type-safe API clients

**Example**:
```typescript
const { screenplay, loading, generateScreenplay } = useScreenplay();

await generateScreenplay({
  concept: "Story idea...",
  model: "gemini-2.5-flash"
});
```

## Data Flow

### Screenplay Generation Flow

1. **User Input**: Frontend submits concept
2. **API Validation**: Pydantic validates request
3. **Repository**: Selects/creates agent
4. **Agent Execution**: ADK agent processes request
5. **LLM Call**: Via LiteLLM proxy to provider
6. **Response Processing**: Agent structures output
7. **API Response**: Returns to frontend

```
User → Frontend → FastAPI → Repository → ADK Agent → LiteLLM → LLM Provider
                                           ↓
                                    Session State
```

### Multi-Agent Workflow

1. **Workflow Definition**: SequentialAgent with sub-agents
2. **Sequential Execution**: Each agent runs in order
3. **State Sharing**: Via session state dictionary
4. **Tool Calls**: Agents use tools to save data
5. **Final Output**: Aggregated results

```
Concept Analyzer → Character Developer → Screenplay Writer
        ↓                  ↓                    ↓
    [state]            [state]              [state]
```

## Design Patterns

### 1. Repository Pattern

**Problem**: Tight coupling between API and data source

**Solution**: Abstract interface for data access

**Benefits**:
- Easy to test (mock repository)
- Swappable implementations
- Clean separation of concerns

### 2. Dependency Injection

**Problem**: Hard-coded dependencies

**Solution**: FastAPI's Depends()

**Benefits**:
- Testable (inject mocks)
- Flexible configuration
- Clear dependencies

### 3. Strategy Pattern

**Problem**: Multiple algorithm variants

**Solution**: Agent composition (Sequential, Loop, Parallel)

**Benefits**:
- Flexible workflows
- Reusable agents
- Easy to extend

### 4. Factory Pattern

**Problem**: Complex object creation

**Solution**: Repository creates/caches agents

**Benefits**:
- Centralized agent management
- Efficient resource usage
- Consistent configuration

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Fast execution (<1s)

### Integration Tests
- Test component interactions
- Mock LLM responses
- Medium execution (~5s)

### E2E Tests
- Test complete workflows
- May use real LLM (marked as slow)
- Slow execution (>30s)

## Security

### API Security
- CORS configuration
- Request validation
- Rate limiting (via LiteLLM)

### Environment Variables
- Secrets in .env (never committed)
- Example file (.env.example) for reference
- Docker secrets support

### Docker Security
- Non-root user
- Multi-stage builds
- Minimal base images
- Health checks

## Performance

### Optimization Strategies

1. **Agent Caching**: Repository caches agent instances
2. **Async/Await**: Non-blocking I/O throughout
3. **Connection Pooling**: LiteLLM handles connections
4. **Docker Multi-stage**: Smaller images, faster deploys

### Monitoring

- **Health Checks**: `/health` endpoint
- **Logging**: Structured logging throughout
- **Observability**: Langfuse for LLM calls
- **Metrics**: Prometheus support (via LiteLLM)

## Scalability

### Horizontal Scaling
```bash
docker-compose up -d --scale api=3
```

### Load Balancing
- LiteLLM handles LLM provider balancing
- Reverse proxy for API instances

### State Management
- Session state per request
- Stateless API design
- Database for persistence (future)

## Configuration

### Environment-based
- Development: `.env` file
- Production: Environment variables
- Docker: `.env` + `docker-compose.yml`

### Model Configuration
- LiteLLM config file
- Agent model parameter
- Repository model selection

## Error Handling

### API Level
- HTTP status codes
- Error response models
- Exception handling

### Agent Level
- Graceful degradation
- Retry logic (via LiteLLM)
- Timeout handling

### Frontend Level
- Error states
- User feedback
- Retry mechanisms

## Future Enhancements

### Short Term
- [ ] Database persistence
- [ ] User authentication
- [ ] Rate limiting per user
- [ ] Caching layer (Redis)

### Medium Term
- [ ] Streaming responses
- [ ] WebSocket support
- [ ] Agent marketplace
- [ ] Version control for scripts

### Long Term
- [ ] Collaborative editing
- [ ] Real-time agent monitoring
- [ ] Custom agent training
- [ ] Integration with production tools
