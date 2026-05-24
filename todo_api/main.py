"""
Main FastAPI application entry point.
Implements Clean Architecture with dependency injection.
"""

from datetime import datetime
from fastapi import FastAPI

from app.presentation.api import user_router, project_router, task_router


# Create FastAPI application
app = FastAPI(
    title="Todo API with Timers",
    description="High-performance Todo API with Clean Architecture",
    version="2.0.0"
)

# Include routers
app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
