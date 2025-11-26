# Documentation Index

Complete documentation for the agente-films multi-agent filmmaking system.

## Getting Started

1. **[QUICK_START.md](QUICK_START.md)** - Get started in 3 steps ⚡
   - Full Docker setup
   - Model switching
   - Service access
   - Quick commands

2. **[LITELLM_SETUP.md](LITELLM_SETUP.md)** - Complete multi-model guide 🎯
   - Architecture overview
   - 9 available models
   - Configuration
   - Usage examples
   - Monitoring & troubleshooting

3. **[README.md](../README.md)** - Project overview
   - Features and capabilities
   - Quick start instructions
   - Project structure
   - API usage examples

## Core Documentation

### Development

**[DEVELOPMENT.md](DEVELOPMENT.md)** - Complete development guide

Topics covered:
- Local development setup
- Hot reloading (backend, agents, frontend)
- Debugging ADK agents locally
- Testing LiteLLM proxy integration
- Environment variables
- Architecture patterns
- Common issues and solutions

Key sections:
- Project Setup
- Development Workflow
- Code Quality Tools
- Testing Strategy
- Docker Development
- Performance Tips

### Testing

**[TESTING.md](TESTING.md)** - Comprehensive testing guide

Topics covered:
- Testing philosophy and best practices
- Unit tests for ADK agents
- Mocking LLM responses
- Integration tests for API endpoints
- E2E tests for complete workflows
- Coverage reporting
- Fixtures and test utilities

Key sections:
- Testing ADK Agents
- Integration Testing
- E2E Testing
- Mock Strategies
- Async Testing
- Performance Testing

### Examples

**[EXAMPLES.md](EXAMPLES.md)** - Complete working examples

Included examples:
1. **ADK Agent with Tests**
   - CharacterAgent implementation
   - Tool integration
   - Unit tests with mocks
   - State management

2. **FastAPI Endpoint with Repository Pattern**
   - Repository implementation
   - FastAPI routes
   - Dependency injection
   - Integration tests

3. **Multi-Agent Workflow**
   - Sequential workflow
   - Agent composition
   - Workflow tests

4. **React Component**
   - Custom hooks
   - API integration
   - Component tests
   - TypeScript types

### Architecture

**[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and patterns

Topics covered:
- System architecture diagram
- Component descriptions
- Data flow diagrams
- Design patterns (Repository, DI, Strategy, Factory)
- Testing strategy overview
- Security considerations
- Performance optimization
- Scalability approaches
- Error handling
- Future enhancements

### Summary

**[SUMMARY.md](SUMMARY.md)** - Quick reference guide

Everything in one place:
- Project structure
- Quick commands
- Code quality tools
- Testing strategy
- Architecture patterns
- ADK agent development
- Local development
- Docker development
- CI/CD pipeline
- Common issues
- Best practices
- Key files
- Resources

## Configuration Files

### Python Configuration

**pyproject.toml** - Python project configuration
- Dependencies (main and dev)
- Ruff configuration (linting and formatting)
- MyPy configuration (type checking)
- pytest configuration (test settings)
- Coverage configuration

**pytest.ini** - pytest-specific settings
- Test discovery patterns
- Default options
- Test markers
- Asyncio settings

### Pre-commit Hooks

**.pre-commit-config.yaml** - Pre-commit hook configuration
- Trailing whitespace removal
- YAML/JSON/TOML validation
- Ruff linting and formatting
- MyPy type checking

### Docker Configuration

**Dockerfile** - Container image definition
- Multi-stage build
- Python 3.12 slim base
- Non-root user
- Health checks

**docker-compose.yml** - Multi-container setup
- API service
- LiteLLM proxy
- PostgreSQL database
- Frontend service

**litellm-config.yaml** - LiteLLM proxy configuration
- Model definitions (Gemini, GPT-4, Claude)
- General settings
- Callbacks and observability

**.dockerignore** - Files excluded from Docker build

### Environment

**.env.example** - Environment variable template
- Google Cloud configuration
- LiteLLM settings
- API keys
- Optional services

### CI/CD

**.github/workflows/ci.yml** - GitHub Actions workflow
- Linting jobs
- Testing jobs
- Docker build jobs
- Coverage reporting

### Build Tools

**Makefile** - Common development commands
- Installation
- Testing
- Linting
- Docker management
- Development server

## File Organization

```
docs/
├── INDEX.md             # This file - documentation index
├── QUICK_START.md       # Get started in 3 steps
├── LITELLM_SETUP.md     # Multi-model LLM setup guide
├── SUMMARY.md           # Quick reference for everything
├── DEVELOPMENT.md       # Detailed development guide
├── TESTING.md           # Complete testing strategies
├── EXAMPLES.md          # Working code examples
└── ARCHITECTURE.md      # System design and patterns

Root:
├── README.md                    # Project overview
├── LITELLM_IMPLEMENTATION.md    # LiteLLM implementation summary
└── Makefile                     # Common commands
```

## How to Use This Documentation

### If you're new to the project:
1. Start with **[QUICK_START.md](QUICK_START.md)** - 3 steps to get running
2. Read **[LITELLM_SETUP.md](LITELLM_SETUP.md)** - Understand multi-model support
3. Check **[README.md](../README.md)** for overview
4. Review **[DEVELOPMENT.md](DEVELOPMENT.md)** for setup details
5. See **[EXAMPLES.md](EXAMPLES.md)** for working code

### If you're writing tests:
1. Read **[TESTING.md](TESTING.md)** for strategies
2. Check **[EXAMPLES.md](EXAMPLES.md)** for test examples
3. Use **[SUMMARY.md](SUMMARY.md)** as quick reference

### If you're debugging:
1. Check **[DEVELOPMENT.md](DEVELOPMENT.md)** for debugging tools
2. Review **[ARCHITECTURE.md](ARCHITECTURE.md)** for system design
3. See **[SUMMARY.md](SUMMARY.md)** for common issues

### If you need a quick reference:
1. **[SUMMARY.md](SUMMARY.md)** has everything condensed
2. Use `make help` for available commands
3. Check **[QUICKSTART.md](../QUICKSTART.md)** for basics

## Documentation Standards

### Code Examples
All code examples in documentation are:
- Tested and working
- Type-hinted
- Properly formatted with ruff
- Include necessary imports

### Commands
All shell commands are:
- Tested on macOS and Linux
- Use absolute paths when needed
- Include descriptions
- Show expected output

### Structure
All documents include:
- Clear headings
- Table of contents (when long)
- Cross-references to related docs
- Examples and code snippets
- Common issues and solutions

## Additional Resources

### External Documentation
- [Google ADK](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LiteLLM](https://docs.litellm.ai/)
- [Ruff](https://docs.astral.sh/ruff/)
- [pytest](https://docs.pytest.org/)
- [uv](https://docs.astral.sh/uv/)

### Code Examples Repository
All examples from **[EXAMPLES.md](EXAMPLES.md)** are implemented in:
- `src/agents/` - Agent implementations
- `src/api/` - API implementations
- `tests/` - Test examples

### Project Files
Key implementation files:
- `src/agents/screenplay_agent.py` - Example ADK agent
- `src/api/main.py` - FastAPI application
- `src/api/repository.py` - Repository pattern
- `tests/unit/test_screenplay_agent.py` - Unit test examples
- `tests/integration/test_api.py` - Integration test examples

## Maintenance

### Keeping Documentation Updated
When making changes:
1. Update relevant documentation files
2. Test all code examples
3. Update version numbers
4. Add to changelog (if exists)

### Documentation Review
Before release:
1. Verify all links work
2. Test all code examples
3. Check formatting consistency
4. Update timestamps/versions

## Quick Navigation

| Need | Go To |
|------|-------|
| Quick setup | [QUICK_START.md](QUICK_START.md) ⚡ |
| Multi-model setup | [LITELLM_SETUP.md](LITELLM_SETUP.md) 🎯 |
| Project overview | [README.md](../README.md) |
| Development setup | [DEVELOPMENT.md](DEVELOPMENT.md) |
| Testing guide | [TESTING.md](TESTING.md) |
| Code examples | [EXAMPLES.md](EXAMPLES.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Quick reference | [SUMMARY.md](SUMMARY.md) |
| All commands | [Makefile](../Makefile) |

## Support

For questions or issues:
1. Search documentation (use Ctrl+F)
2. Check [EXAMPLES.md](EXAMPLES.md) for patterns
3. Review test files for usage examples
4. Check [DEVELOPMENT.md](DEVELOPMENT.md) troubleshooting section

---

Last Updated: 2025-11-25
Version: 0.1.0
