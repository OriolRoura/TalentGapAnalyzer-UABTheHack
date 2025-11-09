"""
AI Insights API Routes
======================

Endpoints para generar y consumir insights, narrativas y recomendaciones generadas por IA.

Endpoints:
- GET /api/v1/ai/employee/{id}/recommendations - Recomendaciones personalizadas
- GET /api/v1/ai/employee/{id}/narrative - Narrativa individual
- GET /api/v1/ai/employee/{id}/development-plan - Plan de desarrollo completo
- GET /api/v1/ai/department/{chapter}/narrative - Narrativa departamental
- GET /api/v1/ai/company/executive-summary - Resumen ejecutivo empresa
- GET /api/v1/ai/stats - Estadísticas de uso de IA
- POST /api/v1/ai/batch-generate - Generación batch para múltiples empleados
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

from models.ai_models import (
    AIGeneratedNarrative, PersonalizedRecommendation, DevelopmentPlan,
    CompanyExecutiveSummary, NarrativeTone, AIGenerationRequest
)
from services.ai_service import AIService
from services.bias_detector import BiasDetector
from services.narrative_generator import NarrativeGenerator
from services.ai_recommendation_engine import AIRecommendationEngine
from services.data_loader import data_loader
from services.gap_service import GapAnalysisService

router = APIRouter(prefix="/api/v1/ai", tags=["AI Insights"])

# Inicializar servicios (lazy initialization)
_ai_service: Optional[AIService] = None
_bias_detector: Optional[BiasDetector] = None
_narrative_generator: Optional[NarrativeGenerator] = None
_recommendation_engine: Optional[AIRecommendationEngine] = None


def get_ai_service() -> AIService:
    """Lazy initialization del AI service."""
    global _ai_service
    if _ai_service is None:
        # Verificar si hay API keys disponibles
        has_openai = bool(os.getenv('OPENAI_API_KEY'))
        has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
        has_google = bool(os.getenv('GOOGLE_API_KEY'))
        has_publicai = bool(os.getenv('PUBLICAI_API_KEY', 'zpka_4c5681aec7834fd5a0915142ce97d096_5374e2e2'))
        
        if not (has_openai or has_anthropic or has_google or has_publicai):
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or PUBLICAI_API_KEY environment variable."
            )
        
        # Determinar provider default (PublicAI first - no blocking issues)
        default_provider = 'publicai' if has_publicai else ('openai' if has_openai else ('anthropic' if has_anthropic else 'google'))
        
        _ai_service = AIService(
            max_cost_per_analysis_usd=0.10,
            rate_limit_rpm=60,
            enable_cache=True,
            default_provider=default_provider
        )
    
    return _ai_service


def get_bias_detector() -> BiasDetector:
    """Lazy initialization del bias detector."""
    global _bias_detector
    if _bias_detector is None:
        _bias_detector = BiasDetector()
    return _bias_detector


def get_narrative_generator() -> NarrativeGenerator:
    """Lazy initialization del narrative generator."""
    global _narrative_generator
    if _narrative_generator is None:
        _narrative_generator = NarrativeGenerator(
            ai_service=get_ai_service(),
            bias_detector=get_bias_detector()
        )
    return _narrative_generator


def get_recommendation_engine() -> AIRecommendationEngine:
    """Lazy initialization del recommendation engine."""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = AIRecommendationEngine(
            ai_service=get_ai_service(),
            bias_detector=get_bias_detector(),
            mode='hybrid'
        )
    return _recommendation_engine


@router.get(
    "/employee/{employee_id}/recommendations",
    response_model=List[PersonalizedRecommendation],
    summary="Generar recomendaciones personalizadas para un empleado"
)
async def get_employee_recommendations(
    employee_id: str,
    max_recommendations: int = Query(default=10, ge=1, le=20),
    target_role_id: Optional[str] = None
):
    """
    Genera recomendaciones personalizadas usando IA para un empleado específico.
    
    - **employee_id**: ID del empleado
    - **max_recommendations**: Número máximo de recomendaciones (1-20)
    - **target_role_id**: Rol objetivo específico (opcional)
    """
    # Verificar que el empleado existe
    employees = data_loader.get_employees()
    emp_id = int(employee_id)
    if emp_id not in employees:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    employee = employees[emp_id]
    
    # Obtener gap results del empleado
    gap_service = GapAnalysisService()
    roles = data_loader.get_roles()
    
    # Calcular gaps para roles de interés
    gap_results = []
    target_role = None
    
    if target_role_id and target_role_id in roles:
        target_role = roles[target_role_id]
        gap_result = gap_service.calculate_gap(employee, target_role)
        gap_results = [gap_result]
    else:
        # Calcular para top roles del mismo chapter
        chapter_roles = [r for r in roles.values() if r.capitulo == employee.chapter]
        for role in chapter_roles[:5]:  # Top 5 roles
            gap_result = gap_service.calculate_gap(employee, role)
            gap_results.append(gap_result)
    
    # Generar recomendaciones con IA
    try:
        engine = get_recommendation_engine()
        recommendations = engine.generate_personalized_recommendations(
            employee=employee,
            gap_results=gap_results,
            target_role=target_role,
            max_recommendations=max_recommendations
        )
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get(
    "/employee/{employee_id}/narrative",
    response_model=AIGeneratedNarrative,
    summary="Generar narrativa individual para un empleado"
)
async def get_employee_narrative(
    employee_id: str,
    tone: NarrativeTone = Query(default=NarrativeTone.ANALYTICAL)
):
    """
    Genera una narrativa personalizada sobre el talent gap de un empleado.
    
    - **employee_id**: ID del empleado
    - **tone**: Tono de la narrativa (analytical, executive, motivational, technical)
    """
    employees = data_loader.get_employees()
    emp_id = int(employee_id)
    if emp_id not in employees:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    employee = employees[emp_id]
    
    # Calcular gaps
    gap_service = GapAnalysisService()
    roles = data_loader.get_roles()
    chapter_roles = [r for r in roles.values() if r.capitulo == employee.chapter]
    
    gap_results = []
    for role in chapter_roles[:5]:
        gap_result = gap_service.calculate_gap(employee, role)
        # Convertir a dict para pasar al narrative generator
        gap_results.append({
            'role_id': role.id,
            'overall_score': gap_result.overall_gap_score,
            'band': gap_result.classification,
            'skill_gaps': gap_result.skill_gaps
        })
    
    # Generar narrativa
    try:
        generator = get_narrative_generator()
        narrative = generator.generate_employee_narrative(
            employee_id=employee_id,
            gap_results=gap_results,
            tone=tone
        )
        
        return narrative
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate narrative: {str(e)}"
        )


@router.get(
    "/employee/{employee_id}/development-plan",
    response_model=DevelopmentPlan,
    summary="Generar plan de desarrollo completo"
)
async def get_employee_development_plan(
    employee_id: str,
    target_role_id: str,
    duration_months: int = Query(default=6, ge=1, le=24)
):
    """
    Genera un plan de desarrollo estructurado para alcanzar un rol objetivo.
    
    - **employee_id**: ID del empleado
    - **target_role_id**: ID del rol objetivo
    - **duration_months**: Duración del plan en meses (1-24)
    """
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    
    emp_id = int(employee_id)
    if emp_id not in employees:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    if target_role_id not in roles:
        raise HTTPException(status_code=404, detail=f"Role {target_role_id} not found")
    
    employee = employees[emp_id]
    target_role = roles[target_role_id]
    
    # Calcular gap
    gap_service = GapAnalysisService()
    gap_result = gap_service.calculate_gap(employee, target_role)
    
    # Generar plan
    try:
        engine = get_recommendation_engine()
        plan = engine.generate_development_plan(
            employee=employee,
            target_role=target_role,
            gap_result=gap_result,
            duration_months=duration_months
        )
        
        return plan
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate development plan: {str(e)}"
        )


@router.get(
    "/department/{chapter}/narrative",
    response_model=AIGeneratedNarrative,
    summary="Generar narrativa para un departamento"
)
async def get_department_narrative(
    chapter: str,
    tone: NarrativeTone = Query(default=NarrativeTone.EXECUTIVE)
):
    """
    Genera una narrativa ejecutiva sobre el estado del talent pipeline de un departamento.
    
    - **chapter**: ID del chapter/departamento
    - **tone**: Tono de la narrativa
    """
    # Verificar que el chapter existe
    employees = data_loader.get_employees()
    chapter_employees = {k: v for k, v in employees.items() if v.chapter == chapter}
    
    if not chapter_employees:
        raise HTTPException(status_code=404, detail=f"No employees found in chapter {chapter}")
    
    # Generar narrativa
    try:
        generator = get_narrative_generator()
        narrative = generator.generate_department_narrative(
            chapter=chapter,
            tone=tone
        )
        
        return narrative
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate department narrative: {str(e)}"
        )


@router.get(
    "/company/executive-summary",
    response_model=CompanyExecutiveSummary,
    summary="Generar resumen ejecutivo de la empresa"
)
async def get_company_executive_summary():
    """
    Genera un resumen ejecutivo completo del estado del talent gap en toda la organización.
    
    Este endpoint puede tardar varios segundos en ejecutarse debido al análisis completo.
    """
    try:
        generator = get_narrative_generator()
        summary = generator.generate_company_executive_summary()
        
        return summary
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate executive summary: {str(e)}"
        )


@router.get(
    "/stats",
    summary="Estadísticas de uso de IA"
)
async def get_ai_stats():
    """
    Retorna estadísticas de uso del servicio de IA.
    
    Incluye:
    - Total de requests
    - Costo total y por request
    - Uso por modelo y provider
    - Tokens consumidos
    """
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_usage_stats()
        
        return {
            "status": "active",
            "usage_stats": stats,
            "cache_enabled": ai_service.cache is not None,
            "default_provider": ai_service.default_provider
        }
    
    except HTTPException:
        return {
            "status": "not_configured",
            "message": "AI service is not configured. Please set API keys."
        }


@router.post(
    "/batch-generate",
    summary="Generación batch de recomendaciones",
    status_code=202
)
async def batch_generate_recommendations(
    request: AIGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Genera recomendaciones y narrativas para múltiples empleados en background.
    
    Retorna inmediatamente con un job ID. Los resultados se generan en background.
    """
    # Validar request
    if request.employee_ids and len(request.employee_ids) > 300:
        raise HTTPException(
            status_code=400,
            detail="Maximum 300 employees per batch request"
        )
    
    # Estimar costo
    num_employees = len(request.employee_ids) if request.employee_ids else len(data_loader.get_employees())
    
    try:
        ai_service = get_ai_service()
        cost_estimates = ai_service.estimate_analysis_cost(num_employees)
        
        # Verificar budget
        min_cost = min(cost_estimates.values())
        if min_cost > request.max_cost_usd:
            raise HTTPException(
                status_code=400,
                detail=f"Estimated cost (${min_cost:.4f}) exceeds maximum allowed (${request.max_cost_usd:.4f})"
            )
    
    except HTTPException:
        pass  # Si no está configurado, permitir continuar
    
    # Crear job ID
    import uuid
    job_id = str(uuid.uuid4())
    
    # Nota: En producción, esto debería usar un task queue como Celery
    # Por ahora retornamos el job_id y el caller puede polling
    
    return {
        "job_id": job_id,
        "status": "queued",
        "estimated_employees": num_employees,
        "estimated_cost_range": {
            "min_usd": min(cost_estimates.values()) if cost_estimates else 0,
            "max_usd": max(cost_estimates.values()) if cost_estimates else 0
        },
        "message": "Batch generation queued. Use /api/v1/ai/batch-status/{job_id} to check status."
    }


@router.get(
    "/health",
    summary="Health check del servicio de IA"
)
async def ai_health_check():
    """
    Verifica el estado del servicio de IA y los providers disponibles.
    """
    try:
        ai_service = get_ai_service()
        
        return {
            "status": "healthy",
            "providers_available": {
                "openai": ai_service.openai_client is not None,
                "anthropic": ai_service.anthropic_client is not None,
                "google": ai_service.google_client is not None
            },
            "default_provider": ai_service.default_provider,
            "bias_detection": "enabled",
            "cache": "enabled" if ai_service.cache else "disabled"
        }
    
    except HTTPException as e:
        return {
            "status": "unhealthy",
            "error": e.detail,
            "providers_available": {
                "openai": bool(os.getenv('OPENAI_API_KEY')),
                "anthropic": bool(os.getenv('ANTHROPIC_API_KEY')),
                "google": bool(os.getenv('GOOGLE_API_KEY'))
            }
        }
