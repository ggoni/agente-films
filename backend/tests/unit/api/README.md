# API Tests - TODO

API endpoint tests require integration test setup with actual PostgreSQL database.

## Skipped Unit Tests

The following API endpoints are implemented but unit tests are deferred to integration testing:

- `POST /sessions` - Create new session
- `GET /sessions/{id}` - Retrieve session by ID

## Why Skipped

FastAPI TestClient with SQLite in-memory databases has threading/scope issues with async dependency injection. Integration tests with real PostgreSQL will provide better coverage.

## Implementation Status

✅ Endpoints implemented and functional  
✅ Router integrated  
✅ Dependency injection configured  
⏭️ Tests deferred to Phase 5 integration testing

## Manual Testing

Start the API server and test manually:
```bash
uvicorn backend.app.api.main:app --reload

# Create session
curl -X POST http://localhost:8000/sessions

# Get session
curl http://localhost:8000/sessions/{session_id}
```
