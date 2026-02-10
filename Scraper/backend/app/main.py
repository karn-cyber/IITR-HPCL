"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, leads, dashboard, products, sources, territories, alerts, feedback

# Initialize FastAPI app
app = FastAPI(
    title="HPCL Lead Intelligence API",
    description="RESTful backend API for the HPCL Lead Intelligence system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(sources.router)
app.include_router(territories.router)
app.include_router(alerts.router)
app.include_router(feedback.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "HPCL Lead Intelligence API",
        "version": "1.0.0",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
