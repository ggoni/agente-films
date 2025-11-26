# LiteLLM Multi-Model Setup Guide

## Overview

This project uses **LiteLLM proxy** to provide unified access to multiple LLM providers:
- **Google Vertex AI** (Gemini models)
- **OpenAI** (GPT models)
- **Anthropic** (Claude models)

With this setup, you can **switch models at will** by simply changing an environment variable.

## Architecture

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│     FastAPI API      │
│  (uses LiteLLM       │
│   client service)    │
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────┐
│   LiteLLM Proxy         │
│   (Port 4000)           │
│   - Model routing       │
│   - API key management  │
│   - Usage tracking      │
└──────┬──────────────────┘
       │
       ├───────────────┬──────────────┬───────────────┐
       ▼               ▼              ▼               ▼
┌─────────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────┐
│  Vertex AI  │ │  OpenAI  │ │  Anthropic  │ │  Etc...  │
│   (Gemini)  │ │   (GPT)  │ │  (Claude)   │ │          │
└─────────────┘ └──────────┘ └─────────────┘ └──────────┘
```

## Quick Start

### 1. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Required for Gemini models
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional - only if using OpenAI models
OPENAI_API_KEY=sk-...

# Optional - only if using Anthropic models
ANTHROPIC_API_KEY=sk-ant-...

# Choose your default model
MODEL=gemini-2.5-flash
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (for app + LiteLLM)
- LiteLLM Proxy (port 4000)
- FastAPI Backend (port 8000)
- React Frontend (port 3000)

### 3. Verify Setup

```bash
# Check LiteLLM proxy health
curl http://localhost:4000/health

# List available models
curl http://localhost:4000/model/info \
  -H "Authorization: Bearer sk-1234"

# Test the API
curl http://localhost:8000/health
```

## Switching Models

### Method 1: Environment Variable (Persistent)

Edit `.env` and restart:

```bash
# Change model
MODEL=claude-3-5-sonnet

# Restart API service
docker-compose restart api
```

### Method 2: Docker Compose Override (Per Session)

```bash
# Run with different model
MODEL=gpt-4 docker-compose up api

# Or using environment override
docker-compose up -d
docker-compose exec api sh -c "MODEL=gpt-4-turbo uvicorn ..."
```

### Method 3: Runtime (In Code)

Use the `LiteLLMClient` service:

```python
from backend.app.services.litellm_client import LiteLLMClient

client = LiteLLMClient()

# Use specific model for this request
response = await client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="claude-3-5-sonnet"  # Override default
)
```

## Available Models

| Model Name | Provider | Description |
|------------|----------|-------------|
| `gemini-2.5-flash` | Google | Latest fast Gemini model |
| `gemini-2.0-flash` | Google | Experimental Gemini 2.0 |
| `gemini-pro` | Google | Gemini Pro 1.5 |
| `gpt-4` | OpenAI | GPT-4 baseline |
| `gpt-4-turbo` | OpenAI | GPT-4 Turbo |
| `gpt-3.5-turbo` | OpenAI | Fast, cost-effective |
| `claude-3-5-sonnet` | Anthropic | Claude 3.5 Sonnet |
| `claude-3-opus` | Anthropic | Most capable Claude |
| `claude-3-haiku` | Anthropic | Fast, efficient Claude |

## Adding New Models

Edit `litellm-config.yaml`:

```yaml
model_list:
  - model_name: my-new-model
    litellm_params:
      model: provider/model-id
      api_key: ${API_KEY_ENV_VAR}
```

Common providers:
- **Vertex AI**: `vertex_ai/model-name`
- **OpenAI**: `openai/model-name`
- **Anthropic**: `anthropic/model-name`
- **Azure OpenAI**: `azure/deployment-name`
- **Cohere**: `cohere/model-name`
- **Replicate**: `replicate/model-name`

Restart LiteLLM proxy:

```bash
docker-compose restart litellm-proxy
```

## Configuration Files

### litellm-config.yaml

Main configuration for LiteLLM proxy:
- Model routing
- API keys
- Provider settings
- Callbacks/observability

### .env

Runtime configuration:
- Default model selection
- API keys
- Database URLs
- Service endpoints

### docker-compose.yml

Service orchestration:
- Container definitions
- Port mappings
- Environment variables
- Health checks

## Usage Examples

### Basic Chat Completion

```python
from backend.app.services.litellm_client import LiteLLMClient

client = LiteLLMClient()

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Docker?"}
]

response = await client.chat_completion(
    messages=messages,
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=500
)

print(response["content"])
```

### Streaming Response

```python
messages = [{"role": "user", "content": "Tell me a story"}]

async for chunk in client.stream_chat_completion(messages):
    print(chunk, end="", flush=True)
```

### Model Comparison

```python
models = ["gemini-2.5-flash", "gpt-4", "claude-3-5-sonnet"]
results = {}

for model in models:
    response = await client.chat_completion(
        messages=messages,
        model=model
    )
    results[model] = {
        "content": response["content"],
        "tokens": response["usage"]["total_tokens"]
    }
```

## Monitoring

### LiteLLM Proxy UI

Access the web UI at: http://localhost:4000/ui

Features:
- Model usage statistics
- Request logs
- Error tracking
- Cost monitoring

### Logs

```bash
# View LiteLLM logs
docker-compose logs -f litellm-proxy

# View API logs
docker-compose logs -f api
```

### Database

LiteLLM stores usage data in PostgreSQL:

```bash
docker-compose exec postgres psql -U postgres -d litellm

# View model usage
SELECT model, count(*), avg(total_tokens)
FROM litellm_request_logs
GROUP BY model;
```

## Troubleshooting

### LiteLLM proxy not starting

```bash
# Check logs
docker-compose logs litellm-proxy

# Verify config
docker-compose exec litellm-proxy cat /app/config.yaml

# Ensure PostgreSQL is ready
docker-compose exec postgres pg_isready
```

### Model authentication errors

```bash
# Verify API keys in environment
docker-compose exec api env | grep API_KEY

# Test direct LiteLLM call
curl http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### Model not found

```bash
# List available models
curl http://localhost:4000/model/info \
  -H "Authorization: Bearer sk-1234"

# Check litellm-config.yaml syntax
docker-compose exec litellm-proxy cat /app/config.yaml
```

## Cost Optimization

### Model Selection Strategy

```python
# Use cheaper models for simple tasks
TASK_MODEL_MAP = {
    "greeting": "gpt-3.5-turbo",
    "research": "gemini-2.5-flash",
    "analysis": "gpt-4",
    "creative": "claude-3-5-sonnet"
}

model = TASK_MODEL_MAP.get(task_type, "gemini-2.5-flash")
```

### Token Management

```python
response = await client.chat_completion(
    messages=messages,
    model="gemini-2.5-flash",
    max_tokens=200,  # Limit response length
    temperature=0.3  # Lower = more focused, fewer tokens
)

# Track usage
print(f"Tokens used: {response['usage']['total_tokens']}")
```

## Security Best Practices

1. **Never commit API keys** - use environment variables
2. **Rotate LITELLM_MASTER_KEY** regularly
3. **Use least-privilege** service accounts for cloud providers
4. **Enable authentication** on LiteLLM proxy in production
5. **Monitor usage** to detect anomalies

## Production Considerations

### Scaling

```yaml
# docker-compose.yml
api:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '1'
        memory: 2G

litellm-proxy:
  deploy:
    replicas: 2
    resources:
      limits:
        cpus: '0.5'
        memory: 1G
```

### High Availability

- Use managed PostgreSQL (RDS, Cloud SQL)
- Deploy LiteLLM behind load balancer
- Configure retry logic in client
- Implement circuit breakers

### Observability

Add to `litellm-config.yaml`:

```yaml
litellm_settings:
  success_callback: ["langfuse", "prometheus"]
  failure_callback: ["sentry"]

environment_variables:
  LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
  LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
  SENTRY_DSN: ${SENTRY_DSN}
```

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Proxy](https://docs.litellm.ai/docs/proxy/quick_start)
- [Supported Models](https://docs.litellm.ai/docs/providers)
