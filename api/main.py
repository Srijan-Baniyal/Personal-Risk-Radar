"""FastAPI application with all routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.data_input import router as data_input_router
from api.risks import router as risks_router
from api.signals import router as signals_router
from persistence.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Personal Risk Radar API",
    description="API for modeling, tracking, and reasoning about risk over time",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(risks_router)
app.include_router(signals_router)
app.include_router(data_input_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Personal Risk Radar API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
