# Quick Start Guide

## 🚀 Get Started in 1 Step

### Just Run This:

```bash
./start.sh
```

**That's it!** The script handles everything:
- ✓ Checks Docker is running
- ✓ Creates .env from template (if needed)
- ✓ Builds all Docker images
- ✓ Starts 4 services (API, LiteLLM, PostgreSQL, Frontend)
- ✓ Waits for all services to be ready
- ✓ Shows you the URLs to access

### Stop Everything:

```bash
./stop.sh
```

## 📝 First Time Setup

The `start.sh` script will create `.env` for you. Edit it with your credentials:

```bash
# Required (minimum for Gemini):
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional (for other models):
OPENAI_API_KEY=sk-...              # For GPT models
ANTHROPIC_API_KEY=sk-ant-...        # For Claude models
```

Then run `./start.sh` again.

## 🎯 Switch Models On-The-Fly

### Quick Switch

```bash
# Using Make
make switch-model MODEL=gpt-4

# Manual method
echo "MODEL=gpt-4" >> .env
docker-compose restart api
```

### Available Models

```bash
# List all configured models
make list-models
```

**Default Models:**
- `gemini-2.5-flash` (Google - Fast)
- `gemini-pro` (Google - Powerful)
- `gpt-4` (OpenAI)
- `gpt-4-turbo` (OpenAI - Faster)
- `claude-3-5-sonnet` (Anthropic)
- `claude-3-haiku` (Anthropic - Fast)

## 📊 Check Health

```bash
# Check all services
make health

# View logs
make logs

# API logs only
make logs-api

# LiteLLM logs only
make logs-litellm
```

## 🔧 Common Commands

```bash
make help           # Show all commands
make up             # Start services
make down           # Stop services
make restart        # Restart all
make restart-api    # Restart API only
make clean          # Clean everything
```

## 🌐 Service URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LiteLLM**: http://localhost:4000
- **LiteLLM UI**: http://localhost:4000/ui
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5433

## 📖 Detailed Documentation

- [LiteLLM Setup](./LITELLM_SETUP.md) - Complete multi-model guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🐛 Troubleshooting

### Services won't start

```bash
# Check what's running
docker-compose ps

# View logs for errors
docker-compose logs

# Clean and restart
make clean
make setup
```

### Model not working

```bash
# Verify model is configured
make list-models

# Check API keys in .env
cat .env | grep API_KEY

# View LiteLLM logs
make logs-litellm
```

### Database issues

```bash
# Access database
make shell-db

# Reset database
docker-compose down -v
docker-compose up -d
```

## 💡 Pro Tips

1. **Use Make** - Simplifies common operations
2. **Check logs** - First step in debugging
3. **Test early** - Run `make test-models` after setup
4. **Monitor usage** - Use LiteLLM UI at http://localhost:4000/ui
5. **Read docs** - Check [LITELLM_SETUP.md](./LITELLM_SETUP.md) for advanced features

## 🎓 Next Steps

1. **Add your API keys** to `.env`
2. **Test models** with `make test-models`
3. **Build your agents** using `backend/app/services/litellm_client.py`
4. **Monitor usage** at http://localhost:4000/ui
5. **Switch models** anytime with `make switch-model MODEL=...`

Happy building! 🎬
