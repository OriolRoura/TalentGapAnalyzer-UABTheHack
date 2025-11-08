"""
Pydantic models for Company and Organization Configuration
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Organization(BaseModel):
    """Organization basic information"""
    nombre: str
    direccion: Optional[str] = None
    descripcion: Optional[str] = None
    industry: Optional[str] = None
    max_employees: int = Field(default=300, ge=1, le=300)


class Timeline(BaseModel):
    """Timeline with KPIs and milestones"""
    hitos: List[str]
    kpis_objetivo: Dict[str, float]
    riesgos_clave: List[str]


class Vision(BaseModel):
    """Future vision with timelines"""
    timeline_12_meses: Optional[Timeline] = None
    timeline_18_meses: Optional[Timeline] = None
    timeline_24_meses: Optional[Timeline] = None


class GapCalculationWeights(BaseModel):
    """Weights for gap calculation algorithm"""
    skills: float = Field(default=0.50, ge=0, le=1)
    responsibilities: float = Field(default=0.25, ge=0, le=1)
    ambitions: float = Field(default=0.15, ge=0, le=1)
    dedication: float = Field(default=0.10, ge=0, le=1)

    def validate_sum(self) -> bool:
        """Validate that weights sum to 1.0"""
        total = self.skills + self.responsibilities + self.ambitions + self.dedication
        return abs(total - 1.0) < 0.001


class CompanyConfig(BaseModel):
    """Complete company configuration"""
    organization: Organization
    chapters: List[Dict]
    gap_calculation_weights: GapCalculationWeights = Field(default_factory=GapCalculationWeights)


class CompanyStatus(BaseModel):
    """Current company status snapshot"""
    organization: Organization
    total_employees: int
    total_roles: int
    total_chapters: int
    employees_by_chapter: Dict[str, int]
    roles_by_chapter: Dict[str, int]
    avg_skills_per_employee: float
    data_completeness: Dict[str, float]
    last_updated: str


class CompanyHealthCheck(BaseModel):
    """Company data health check"""
    total_employees: int
    total_roles: int
    validation_errors: List[str]
    validation_warnings: List[str]
    data_quality_score: float = Field(..., ge=0, le=100)
    missing_data: Dict[str, List[str]]
    recommendations: List[str]


class CompanyProject(BaseModel):
    """Company project information"""
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None  # client_project, internal_project, internal_operations, marketing
    status: str = "active"  # active, paused, completed
    priority: str = "medium"  # low, medium, high, critical
    estimated_duration: Optional[str] = None
    metadata: Optional[Dict] = None
    # Stats populated from employee data
    total_employees: int = 0
    avg_dedication_percentage: float = 0.0
    employees: List[str] = Field(default_factory=list)


class CompanyProjectsResponse(BaseModel):
    """Response with all company projects"""
    projects: List[CompanyProject]
    total_projects: int
    last_updated: str
