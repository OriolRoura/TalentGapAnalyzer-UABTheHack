"""
Talent Gap Analyzer API - Main Application
FastAPI application for managing company data, HR inputs, and feeding Samya's gap algorithm
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import employees, roles, company, hr_forms, health
from services.data_loader import DataLoader

# Initialize data loader
data_loader = DataLoader()

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
app.include_router(hr_forms.router, prefix="/api/v1/hr", tags=["HR Forms"])

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
