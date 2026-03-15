"""
FastAPI backend application for Red Team Operations Dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_database
from backend.routes import router
from backend.routes.ai_chat import router as ai_chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: Initialize database
    init_database()
    print("Database initialized successfully!")
    yield
    # Shutdown: Cleanup if needed
    print("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="Red Team Operations Dashboard API",
    description="Backend API for Red Team Operations Dashboard with Nmap and Metasploit integration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")
app.include_router(ai_chat_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Red Team Operations Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
