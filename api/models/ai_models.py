"""
AI-Generated Content Models
============================

Modelos Pydantic para contenido generado por IA:
- Narrativas automáticas
- Recomendaciones personalizadas
- Planes de desarrollo
- Insights ejecutivos

Todos los modelos incluyen metadata de explicabilidad y auditabilidad.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Nivel de confianza en la generación de IA."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReasoningType(str, Enum):
    """Tipo de razonamiento usado por la IA."""
    DATA_DRIVEN = "data_driven"  # Basado puramente en datos
    RULE_BASED = "rule_based"    # Basado en reglas predefinidas
    HYBRID = "hybrid"             # Combinación de datos y reglas
    GENERATIVE = "generative"     # Generado por LLM


class RecommendationType(str, Enum):
    """Tipos de recomendaciones."""
    SKILL_DEVELOPMENT = "skill_development"
    CAREER_PROGRESSION = "career_progression"
    MENTORING = "mentoring"
    TRAINING_PROGRAM = "training_program"
    PROJECT_ASSIGNMENT = "project_assignment"
    ROLE_TRANSITION = "role_transition"
    NETWORKING = "networking"


class EffortLevel(str, Enum):
    """Nivel de esfuerzo requerido."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AIMetadata(BaseModel):
    """Metadata de explicabilidad para contenido generado por IA."""
    model_used: str = Field(description="Modelo de IA usado (ej: gpt-4, claude-3-5-sonnet)")
    provider: str = Field(description="Provider de IA (openai, anthropic, google)")
    generated_at: datetime = Field(default_factory=datetime.now)
    confidence_level: ConfidenceLevel = Field(description="Nivel de confianza en la generación")
    reasoning_type: ReasoningType = Field(description="Tipo de razonamiento usado")
    reasoning_trace: Optional[str] = Field(default=None, description="Explicación del razonamiento")
    input_tokens: int = Field(default=0, description="Tokens de input")
    output_tokens: int = Field(default=0, description="Tokens de output")
    cost_usd: float = Field(default=0.0, description="Costo de generación en USD")
    bias_check_passed: bool = Field(default=True, description="Si pasó verificación de sesgos")
    human_review_required: bool = Field(default=False, description="Si requiere revisión humana")
    
    class Config:
        protected_namespaces = ()  # Permitir campos que empiezan con "model_"
        json_schema_extra = {
            "example": {
                "model_used": "gpt-3.5-turbo",
                "provider": "openai",
                "confidence_level": "high",
                "reasoning_type": "hybrid",
                "cost_usd": 0.003
            }
        }


class ActionItem(BaseModel):
    """Item de acción específica dentro de una recomendación."""
    action: str = Field(description="Descripción de la acción")
    timeline: str = Field(description="Timeline estimado (ej: '2-4 semanas')")
    resources_needed: List[str] = Field(default_factory=list, description="Recursos necesarios")
    success_criteria: Optional[str] = Field(default=None, description="Criterio de éxito")
    priority: Literal["high", "medium", "low"] = "medium"


class PersonalizedRecommendation(BaseModel):
    """Recomendación personalizada para un empleado."""
    id: str = Field(description="ID único de la recomendación")
    employee_id: str = Field(description="ID del empleado")
    type: RecommendationType = Field(description="Tipo de recomendación")
    title: str = Field(description="Título breve y accionable")
    description: str = Field(description="Descripción detallada")
    rationale: str = Field(description="Por qué esta recomendación es relevante")
    
    # Acciones específicas
    action_items: List[ActionItem] = Field(description="Items de acción específicos")
    
    # Esfuerzo y timeline
    effort_level: EffortLevel = Field(description="Nivel de esfuerzo requerido")
    estimated_duration: str = Field(description="Duración estimada total")
    
    # Impacto esperado
    expected_impact: Dict[str, float] = Field(
        description="Impacto esperado en diferentes áreas (0-1)",
        default_factory=dict
    )
    success_probability: float = Field(
        ge=0.0, le=1.0,
        description="Probabilidad de éxito (0-1)"
    )
    
    # Priorización
    priority_score: float = Field(
        ge=0.0, le=1.0,
        description="Score de prioridad (0-1, mayor = más prioritario)"
    )
    
    # Metadata IA
    ai_metadata: AIMetadata = Field(description="Metadata de generación por IA")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "REC-001",
                "employee_id": "1001",
                "type": "skill_development",
                "title": "Desarrollar competencia en OKRs",
                "description": "Curso estructurado de OKRs para mejorar capacidad estratégica",
                "rationale": "Gap identificado en skill estratégico crítico para rol objetivo",
                "effort_level": "medium",
                "estimated_duration": "3 meses",
                "priority_score": 0.85
            }
        }


class DevelopmentMilestone(BaseModel):
    """Milestone en un plan de desarrollo."""
    month: int = Field(ge=1, le=12, description="Mes del milestone")
    milestone: str = Field(description="Descripción del milestone")
    success_criteria: str = Field(description="Criterio de éxito")
    validation_method: Optional[str] = Field(default=None, description="Cómo validar el logro")


class DevelopmentPlan(BaseModel):
    """Plan de desarrollo personalizado completo."""
    employee_id: str = Field(description="ID del empleado")
    target_role_id: str = Field(description="Rol objetivo")
    current_score: float = Field(ge=0.0, le=1.0, description="Score actual (0-1)")
    target_score: float = Field(ge=0.0, le=1.0, description="Score objetivo (0-1)")
    
    # Plan estructurado
    duration_months: int = Field(ge=1, le=24, description="Duración del plan en meses")
    milestones: List[DevelopmentMilestone] = Field(description="Milestones del plan")
    
    # Recomendaciones agrupadas
    recommendations: List[PersonalizedRecommendation] = Field(description="Recomendaciones del plan")
    
    # Focus areas
    skill_priorities: List[Dict[str, str]] = Field(
        description="Skills prioritarios a desarrollar"
    )
    
    # Inversión requerida
    estimated_cost_eur: Optional[float] = Field(default=None, description="Costo estimado en EUR")
    time_investment_hours: int = Field(description="Inversión de tiempo en horas")
    
    # Success metrics
    success_probability: float = Field(ge=0.0, le=1.0, description="Probabilidad de éxito")
    risk_factors: List[str] = Field(default_factory=list, description="Factores de riesgo")
    
    # Metadata
    ai_metadata: AIMetadata = Field(description="Metadata de generación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "1001",
                "target_role_id": "R-STR-LEAD",
                "current_score": 0.55,
                "target_score": 0.75,
                "duration_months": 6,
                "success_probability": 0.72
            }
        }


class NarrativeTone(str, Enum):
    """Tono de la narrativa."""
    EXECUTIVE = "executive"      # Ejecutivo, estratégico
    ANALYTICAL = "analytical"    # Analítico, data-driven
    MOTIVATIONAL = "motivational"  # Motivacional, inspirador
    TECHNICAL = "technical"      # Técnico, detallado


class AIGeneratedNarrative(BaseModel):
    """Narrativa automática generada por IA."""
    id: str = Field(description="ID único de la narrativa")
    title: str = Field(description="Título de la narrativa")
    scope: Literal["employee", "department", "company"] = Field(
        description="Alcance de la narrativa"
    )
    scope_id: Optional[str] = Field(default=None, description="ID del scope (employee_id, chapter, etc)")
    
    # Contenido
    executive_summary: str = Field(description="Resumen ejecutivo (2-3 párrafos)")
    key_insights: List[str] = Field(description="Insights clave (bullets)")
    detailed_analysis: str = Field(description="Análisis detallado")
    recommendations_summary: str = Field(description="Resumen de recomendaciones")
    
    # Datos de soporte
    supporting_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Datos cuantitativos que soportan la narrativa"
    )
    
    # Trends y predicciones
    trends_identified: List[str] = Field(
        default_factory=list,
        description="Tendencias identificadas"
    )
    future_outlook: Optional[str] = Field(
        default=None,
        description="Perspectiva futura"
    )
    
    # Tone y estilo
    tone: NarrativeTone = Field(default=NarrativeTone.ANALYTICAL)
    
    # Metadata
    ai_metadata: AIMetadata = Field(description="Metadata de generación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "NAR-001",
                "title": "Análisis de Talent Gaps - Departamento Strategy",
                "scope": "department",
                "scope_id": "STR",
                "tone": "executive"
            }
        }


class ExecutiveInsight(BaseModel):
    """Insight ejecutivo de alto nivel."""
    insight_type: Literal["opportunity", "risk", "trend", "bottleneck"] = Field(
        description="Tipo de insight"
    )
    title: str = Field(description="Título del insight")
    description: str = Field(description="Descripción detallada")
    impact_level: Literal["critical", "high", "medium", "low"] = Field(
        description="Nivel de impacto"
    )
    
    # Datos cuantitativos
    affected_employees: int = Field(description="Empleados afectados")
    affected_roles: List[str] = Field(description="Roles afectados")
    
    # Recomendaciones estratégicas
    strategic_recommendations: List[str] = Field(description="Recomendaciones estratégicas")
    
    # Timeline
    urgency: Literal["immediate", "short_term", "medium_term", "long_term"] = Field(
        description="Urgencia de acción"
    )
    
    # Metadata
    ai_metadata: AIMetadata = Field(description="Metadata de generación")


class CompanyExecutiveSummary(BaseModel):
    """Resumen ejecutivo completo de la empresa."""
    generated_at: datetime = Field(default_factory=datetime.now)
    
    # Overview
    total_employees: int = Field(description="Total de empleados analizados")
    total_roles: int = Field(description="Total de roles en la organización")
    overall_readiness_score: float = Field(
        ge=0.0, le=1.0,
        description="Score de readiness general (0-1)"
    )
    
    # Narrativa principal
    narrative: AIGeneratedNarrative = Field(description="Narrativa ejecutiva principal")
    
    # Insights clave
    key_insights: List[ExecutiveInsight] = Field(description="Insights ejecutivos clave")
    
    # Métricas por departamento
    department_metrics: Dict[str, Dict] = Field(
        description="Métricas por departamento/chapter"
    )
    
    # Critical gaps
    critical_skill_gaps: List[Dict[str, Any]] = Field(
        description="Skills gaps más críticos"
    )
    critical_bottlenecks: List[Dict[str, Any]] = Field(
        description="Bottlenecks más críticos"
    )
    
    # Recomendaciones organizacionales
    organizational_recommendations: List[str] = Field(
        description="Recomendaciones a nivel organizacional"
    )
    investment_priorities: List[Dict[str, Any]] = Field(
        description="Prioridades de inversión"
    )
    
    # Metadata
    ai_metadata: AIMetadata = Field(description="Metadata de generación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_employees": 100,
                "total_roles": 25,
                "overall_readiness_score": 0.62
            }
        }


class BiasDetectionResult(BaseModel):
    """Resultado de detección de sesgos."""
    has_bias: bool = Field(description="Si se detectó algún sesgo")
    bias_types_detected: List[str] = Field(
        default_factory=list,
        description="Tipos de sesgo detectados"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confianza en la detección")
    flagged_content: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Contenido flaggeado con razón"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recomendaciones para mitigar sesgos"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "has_bias": False,
                "bias_types_detected": [],
                "confidence": 0.95
            }
        }


class AIGenerationRequest(BaseModel):
    """Request para generar contenido con IA."""
    employee_ids: Optional[List[str]] = Field(default=None, description="IDs de empleados")
    department: Optional[str] = Field(default=None, description="Departamento/chapter")
    include_narratives: bool = Field(default=True, description="Incluir narrativas")
    include_recommendations: bool = Field(default=True, description="Incluir recomendaciones")
    tone: NarrativeTone = Field(default=NarrativeTone.ANALYTICAL, description="Tono de narrativas")
    max_cost_usd: float = Field(default=0.10, description="Costo máximo por análisis")
    
    @field_validator('employee_ids')
    @classmethod
    def validate_employee_ids(cls, v):
        if v is not None and len(v) > 300:
            raise ValueError("Máximo 300 empleados por request")
        return v
