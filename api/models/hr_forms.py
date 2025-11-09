"""
Pydantic models for HR Forms and Input
For collecting data from HR department to feed into gap analysis
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Dict, Optional, Any
from datetime import date
from models.role import SeniorityLevel


class HRRoleDefinitionForm(BaseModel):
    """Form for HR to define a future role requirement"""
    role_title: str
    chapter: str
    seniority_level: SeniorityLevel
    positions_needed: int = Field(default=1, ge=1)
    estimated_start: str = Field(..., description="e.g., 0-3m, 3-6m, 6-12m")
    key_responsibilities: List[str]
    required_skills: List[str]
    required_skill_levels: Dict[str, int] = Field(
        ...,
        description="Mapping of skill_id to required level (0-10)"
    )
    priority: str = Field(default="medium", description="low, medium, high, critical")


class HRGapAnalysisRequest(BaseModel):
    """Request form for initiating gap analysis"""
    analysis_name: str
    description: Optional[str] = None
    include_chapters: Optional[List[str]] = None  # None means all
    include_employees: Optional[List[int]] = None  # None means all
    target_roles: List[str] = Field(..., description="List of role IDs to analyze against")
    timeline: str = Field(..., description="12_meses, 18_meses, 24_meses")
    algorithm_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom weights for gap calculation. Defaults: skills=0.5, responsibilities=0.25, ambitions=0.15, dedication=0.1"
    )


class HRGapAnalysisResponse(BaseModel):
    """Response after initiating gap analysis"""
    analysis_id: str
    status: str = Field(default="queued", description="queued, processing, completed, failed")
    created_at: str
    estimated_completion: Optional[str] = None
    message: str


class EmployeeSkillGap(BaseModel):
    """Skill gap for a single employee"""
    employee_id: int
    employee_name: str
    target_role_id: str
    target_role_title: str
    overall_gap_score: float = Field(..., ge=0, le=100)
    classification: str = Field(
        ...,
        description="READY, READY_WITH_SUPPORT, NEAR, FAR, NOT_VIABLE"
    )
    skill_gaps: Dict[str, Dict] = Field(
        ...,
        description="Skill-level gaps with current vs required levels"
    )
    responsibilities_gap: float
    ambitions_alignment: float
    dedication_availability: float
    recommendations: List[str] = Field(default_factory=list)


class HRValidationResponse(BaseModel):
    """Response for validation checks"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    summary: Optional[Dict] = None


class HREmployeeSkillSubmit(BaseModel):
    """Skill data for employee submission"""
    nombre: str
    nivel: int = Field(..., ge=0, le=10)
    experiencia_años: int = Field(..., ge=0)


class HREmployeeAmbitionsSubmit(BaseModel):
    """Ambitions data for employee submission"""
    especialidades_preferidas: List[str] = Field(default_factory=list)
    nivel_aspiracion: str
    interes_liderazgo: bool = False
    areas_interes: List[str] = Field(default_factory=list)


class EmployeeGapMatrixRow(BaseModel):
    """Single row in employee gap matrix - represents one employee-role match"""
    employee_id: int
    employee_name: str
    role_id: str
    role_title: str
    overall_score: float = Field(..., description="Overall compatibility score (0-1, higher is better)")
    band: str = Field(..., description="READY, READY_WITH_SUPPORT, NEAR, FAR, NOT_VIABLE")
    skills_score: float = Field(..., ge=0, le=1)
    responsibilities_score: float = Field(..., ge=0, le=1)
    ambitions_score: float = Field(..., ge=0, le=1)
    dedication_score: float = Field(..., ge=0, le=1)
    detailed_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class EmployeeGapMatrix(BaseModel):
    """Complete gap matrix for an employee against all roles"""
    employee_id: int
    employee_name: str
    chapter: str
    current_role: str
    role_matches: List[EmployeeGapMatrixRow] = Field(
        default_factory=list,
        description="List of all role matches for this employee"
    )
    best_match: Optional[EmployeeGapMatrixRow] = Field(
        default=None,
        description="Best role match for this employee"
    )
    ready_roles_count: int = Field(
        default=0,
        description="Number of roles where employee is READY or READY_WITH_SUPPORT"
    )
    avg_compatibility_score: float = Field(
        default=0.0,
        description="Average compatibility across all roles"
    )


class HREmployeeDedicationSubmit(BaseModel):
    """
    Dedication data for employee submission.
    Use GET /company/projects to retrieve available company projects.
    """
    proyecto_actual: str = Field(
        ..., 
        description="Name of the project. Use GET /company/projects to see available options."
    )
    porcentaje_dedicacion: int = Field(..., ge=0, le=100, description="Percentage of time dedicated to this project")
    horas_semana: int = Field(..., ge=0, description="Hours per week dedicated to this project")


class HREmployeeSubmitForm(BaseModel):
    """
    Form for submitting complete employee profile.
    
    To get available options for form fields, use these endpoints:
    - GET /company/projects - Get list of current company projects
    - GET /company/chapters - Get list of chapters
    - GET /roles - Get available roles and skills
    
    Note: Responsibilities are automatically loaded from the role definition
    based on the 'rol_actual' field (role title). They are fetched from org_config.json
    and you don't need to provide them manually.
    """
    employee_id: Optional[str] = None
    nombre: str
    email: EmailStr
    chapter: str = Field(..., description="Employee's chapter. Use GET /company/chapters for available options.")
    rol_actual: str = Field(..., description="Current role/position name (e.g., 'Consultor de Estrategia', 'Project Manager'). Responsibilities will be loaded automatically from org_config.json based on this role title.")
    seniority: str = Field(..., description="Seniority level (e.g., 'Junior', 'Mid', 'Senior', 'Lead')")
    modalidad: str
    skills: List[HREmployeeSkillSubmit]
    ambiciones: HREmployeeAmbitionsSubmit
    dedicacion_actual: List[HREmployeeDedicationSubmit] = Field(
        ..., 
        description="List of project dedications. Multiple projects allowed. Total percentages must sum to 100%. Use GET /company/projects to see available projects."
    )
    
    @field_validator('dedicacion_actual')
    @classmethod
    def validate_dedication_sum(cls, v):
        """Validate that dedication percentages sum to 100%"""
        total = sum(d.porcentaje_dedicacion for d in v)
        if total != 100:
            raise ValueError(f"Total dedication must sum to 100%, got {total}%")
        return v


class HREmployeeSubmitResponse(BaseModel):
    """Response for employee submission"""
    status: str
    message: str
    employee_id: str
    validation: Dict[str, Any]
