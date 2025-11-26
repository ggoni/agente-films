"""FastAPI application main module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import Settings

# Initialize settings
settings = Settings()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent filmmaking system using Google ADK",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status message indicating API is running
    """
    return {"status": "healthy", "service": "agente-films-api"}


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.

    Returns:
        Welcome message and API details
    """
    return {
        "message": "Film Concept Generator API",
        "version": "1.0.0",
        "docs": "/docs",
    }
