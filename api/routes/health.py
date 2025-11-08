"""
Health Check Routes
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Talent Gap Analyzer API",
        "version": "1.0.0"
    }


@router.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Talent Gap Analyzer API",
        "version": "1.0.0",
        "description": "API for managing employee data, roles, and HR inputs for talent gap analysis",
        "endpoints": {
            "health": "/api/v1/health",
            "employees": "/api/v1/employees",
            "roles": "/api/v1/roles",
            "company": "/api/v1/company",
            "hr_forms": "/api/v1/hr",
            "docs": "/docs"
        }
    }
