"""
API Monitoring Routes
=====================

Endpoints for monitoring API calls, tracing, and debugging.
"""

from fastapi import APIRouter, Query
from typing import Optional, List, Dict
from services.api_tracer import get_tracer

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


@router.get(
    "/traces/recent",
    summary="Get recent API call traces"
)
async def get_recent_traces(
    limit: int = Query(default=20, ge=1, le=100, description="Number of recent traces to return")
):
    """
    Returns recent API call traces for debugging.
    
    Includes:
    - Request/response details
    - Timing information
    - Error details if any
    - Token usage and costs
    """
    tracer = get_tracer()
    traces = tracer.get_recent_traces(limit=limit)
    
    return {
        "count": len(traces),
        "traces": traces
    }


@router.get(
    "/stats",
    summary="Get API statistics"
)
async def get_api_stats():
    """
    Returns comprehensive API usage statistics.
    
    Includes:
    - Total calls and success rate
    - Breakdown by provider
    - Breakdown by endpoint
    - Total costs and tokens
    """
    tracer = get_tracer()
    stats = tracer.get_stats()
    
    return {
        "status": "active",
        "statistics": stats
    }


@router.get(
    "/errors/recent",
    summary="Get recent API errors"
)
async def get_recent_errors(
    limit: int = Query(default=20, ge=1, le=50, description="Number of recent errors to return")
):
    """
    Returns recent API errors for debugging.
    
    Useful for:
    - Identifying recurring issues
    - Debugging provider-specific problems
    - Monitoring error patterns
    """
    tracer = get_tracer()
    errors = tracer.get_errors(limit=limit)
    
    return {
        "count": len(errors),
        "errors": errors
    }


@router.get(
    "/health",
    summary="Monitoring service health check"
)
async def monitoring_health():
    """
    Health check for the monitoring service.
    """
    tracer = get_tracer()
    stats = tracer.get_stats()
    
    # Determine health status
    success_rate = stats.get('success_rate', 0)
    health_status = "healthy"
    
    if success_rate < 50:
        health_status = "critical"
    elif success_rate < 80:
        health_status = "degraded"
    
    return {
        "status": health_status,
        "success_rate": f"{success_rate:.1f}%",
        "total_calls": stats.get('total_calls', 0),
        "total_errors": stats.get('failed_calls', 0),
        "logging_enabled": tracer.enable_file_logging,
        "log_directory": str(tracer.log_dir)
    }


@router.post(
    "/summary",
    summary="Print monitoring summary to console"
)
async def print_monitoring_summary():
    """
    Prints a formatted summary of API monitoring to the server console.
    
    Useful for:
    - Quick overview during development
    - Debugging sessions
    - Performance analysis
    """
    tracer = get_tracer()
    tracer.print_summary()
    
    return {
        "message": "Summary printed to console",
        "status": "success"
    }
