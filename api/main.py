"""
Talent Gap Analyzer API - Main Application
FastAPI application for managing company data, HR inputs, and feeding Samya's gap algorithm
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
print(f"🔧 Loading environment from: {env_path}")
print(f"🔧 .env file exists: {env_path.exists()}")

# Add PARENT directory to path (so we can import 'algorithm' as a package)
# This is safer than adding algorithm directly as it won't shadow 'models'
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.append(str(parent_path))  # Use append, not insert(0)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import employees, roles, company, hr_forms, health, skills, ai_insights, monitoring, cache
from services.data_loader import data_loader  # Use the global instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown events"""
    # Startup: Load initial data from CSV/JSON files
    print("🚀 Loading initial data...")
    data_loader.load_all_data()
    print("✅ Data loaded successfully")
    yield
    # Shutdown
    print("👋 Shutting down API...")

# Create FastAPI app
app = FastAPI(
    title="Talent Gap Analyzer API",
    description="API for managing employee data, roles, and HR inputs for talent gap analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(company.router, prefix="/api/v1/company", tags=["Company"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(skills.router, tags=["Skills"])
app.include_router(hr_forms.router, prefix="/api/v1/hr", tags=["HR Forms"])
app.include_router(ai_insights.router, tags=["AI Insights"])  # AI-generated content
app.include_router(monitoring.router, tags=["Monitoring"])  # API monitoring and tracing
app.include_router(cache.router, prefix="/api/v1/cache", tags=["Cache Management"])  # LLM cache management

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Talent Gap Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
