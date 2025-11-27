"""FastAPI application with screenplay generation endpoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import ErrorResponse, ScreenplayRequest, ScreenplayResponse
from src.api.repository import ADKScreenplayRepository, ScreenplayRepository

# Repository instance (injected in production)
_repository: ScreenplayRepository | None = None


def get_repository() -> ScreenplayRepository:
    """Get repository instance.

    Returns:
        ScreenplayRepository instance
    """
    global _repository
    if _repository is None:
        _repository = ADKScreenplayRepository()
    return _repository


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Args:
        _app: FastAPI application instance (unused)

    Yields:
        None
    """
    # Startup: Initialize services
    print("Starting agente-films API...")
    yield
    # Shutdown: Cleanup
    print("Shutting down agente-films API...")


app = FastAPI(
    title="Agente Films API",
    description="Multi-agent filmmaking system API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Agente Films API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


@app.post(
    "/api/screenplay/generate",
    response_model=ScreenplayResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def generate_screenplay(
    request: ScreenplayRequest,
) -> ScreenplayResponse:
    """Generate screenplay outline from concept.

    Args:
        request: Screenplay generation request

    Returns:
        Generated screenplay outline

    Raises:
        HTTPException: If generation fails
    """
    try:
        repository = get_repository()
        model = request.model or "gemini-2.5-flash"

        result = await repository.generate_outline(
            concept=request.concept,
            model=model,
        )

        return ScreenplayResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate screenplay",
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
