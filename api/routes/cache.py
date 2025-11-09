"""
Cache Management Routes
=======================

Endpoints para gestionar y monitorear el caché de respuestas LLM
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from services.llm_cache import get_llm_cache

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """
    Obtiene estadísticas del caché de LLM.
    
    Returns:
        Estadísticas completas incluyendo hit rate, tamaño y costos ahorrados
    """
    cache = get_llm_cache()
    stats = cache.get_stats()
    
    return {
        "status": "success",
        "cache_stats": stats,
        "description": {
            "hit_rate_percent": "Porcentaje de requests servidas desde caché",
            "cost_saved_usd": "Costo total ahorrado en llamadas a LLM",
            "cache_size_mb": "Tamaño actual del caché en disco",
            "total_entries": "Número de respuestas en caché"
        }
    }


@router.post("/clear")
async def clear_cache():
    """
    Limpia completamente el caché de LLM.
    
    ⚠️ Esta operación elimina todas las respuestas cacheadas y reinicia estadísticas.
    """
    cache = get_llm_cache()
    cache.clear()
    
    return {
        "status": "success",
        "message": "Cache cleared successfully"
    }


@router.post("/invalidate/{pattern}")
async def invalidate_cache_pattern(pattern: str):
    """
    Invalida entradas del caché que coincidan con un patrón.
    
    Args:
        pattern: Patrón de búsqueda (ej: 'narrative', 'employee_1001', 'recommendations')
    
    Examples:
        - `/api/v1/cache/invalidate/narrative` - Invalida todas las narrativas
        - `/api/v1/cache/invalidate/employee_1001` - Invalida caché del empleado 1001
        - `/api/v1/cache/invalidate/gemini` - Invalida respuestas de Gemini
    """
    cache = get_llm_cache()
    cache.invalidate_pattern(pattern)
    
    return {
        "status": "success",
        "message": f"Invalidated cache entries matching pattern: {pattern}"
    }


@router.get("/health")
async def cache_health():
    """
    Verifica el estado del caché.
    
    Returns:
        Estado de salud del caché con métricas clave
    """
    cache = get_llm_cache()
    stats = cache.get_stats()
    
    # Determinar health status
    health_status = "healthy"
    warnings = []
    
    # Check cache size
    if stats['cache_size_mb'] > stats['max_size_mb'] * 0.9:
        warnings.append("Cache is nearly full (>90%)")
        health_status = "warning"
    
    # Check hit rate
    if stats['total_hits'] + stats['total_misses'] > 100:  # Min requests for meaningful rate
        if stats['hit_rate_percent'] < 30:
            warnings.append("Low cache hit rate (<30%)")
            health_status = "warning"
    
    return {
        "status": health_status,
        "cache_enabled": True,
        "total_entries": stats['total_entries'],
        "hit_rate_percent": stats['hit_rate_percent'],
        "cache_utilization_percent": round(
            (stats['cache_size_mb'] / stats['max_size_mb']) * 100, 2
        ),
        "cost_saved_usd": stats['cost_saved_usd'],
        "warnings": warnings
    }
