"""
Pydantic models for HR Forms and Input
For collecting data from HR department to feed into gap analysis
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Dict, Optional
from datetime import date
from models.role import SeniorityLevel


class HREmployeeSkillForm(BaseModel):
    """Form for HR to input employee skills"""
    employee_id: int
    skill_id: str
    skill_name: str
    current_level: int = Field(..., ge=0, le=10, description="Current proficiency 0-10")
    evidence_url: Optional[str] = None
    last_assessment_date: Optional[date] = None
    notes: Optional[str] = None


class HREmployeeEvaluationForm(BaseModel):
    """Form for HR to input employee evaluation data"""
    employee_id: int
    evaluation_date: date
    performance_rating: str = Field(..., description="A, A-, B+, B, C")
    retention_risk: str = Field(..., description="Baja, Media, Alta")
    career_aspirations: List[str] = Field(default_factory=list)
    desired_seniority: SeniorityLevel
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    training_completed: List[str] = Field(default_factory=list)
    manager_comments: Optional[str] = None


class HRProjectDedicationForm(BaseModel):
    """Form for HR to input project dedication"""
    employee_id: int
    project_name: str
    dedication_percentage: int = Field(..., ge=0, le=100)
    start_date: date
    end_date: Optional[date] = None
    role_in_project: str


class HRBulkProjectDedication(BaseModel):
    """Form for updating all dedications for an employee"""
    employee_id: int
    dedications: Dict[str, int] = Field(..., description="Project name to percentage mapping")
    effective_date: date

    @field_validator('dedications')
    @classmethod
    def validate_dedication_sum(cls, v):
        """Validate that dedication percentages sum to 100"""
        total = sum(v.values())
        if total != 100:
            raise ValueError(f"Dedication percentages must sum to 100%, got {total}%")
        return v


class HRNewEmployeeForm(BaseModel):
    """Form for HR to add a new employee"""
    nombre: str
    email: EmailStr
    chapter: str
    rol_actual: str
    manager: Optional[str] = None
    start_date: date
    contract_type: str = Field(..., description="FT, PT, Freelance")
    initial_skills: List[HREmployeeSkillForm] = Field(default_factory=list)
    initial_dedication: Dict[str, int] = Field(default_factory=dict)


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


class HRBulkSkillUpdate(BaseModel):
    """Form for bulk updating skills for multiple employees"""
    updates: List[HREmployeeSkillForm]
    update_reason: str
    updated_by: str


class HRValidationResponse(BaseModel):
    """Response for validation checks"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    summary: Optional[Dict] = None
