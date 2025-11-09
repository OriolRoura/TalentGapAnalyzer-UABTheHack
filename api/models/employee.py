"""
Pydantic models for Employee data
Based on talento_actual.csv schema
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime


class SkillLevel(BaseModel):
    """Skill with proficiency level"""
    skill_id: str
    skill_name: str
    level: int = Field(..., ge=0, le=10, description="Proficiency level 0-10")


class Dedication(BaseModel):
    """Employee dedication percentage per project/client"""
    project_name: str
    percentage: int = Field(..., ge=0, le=100)


class Ambitions(BaseModel):
    """Employee career ambitions"""
    especialidades_preferidas: List[str] = Field(default_factory=list)
    nivel_aspiracion: str = Field(..., description="junior, mid, mid-senior, senior, lead")


class Metadata(BaseModel):
    """Employee performance and trajectory metadata"""
    performance_rating: str = Field(..., description="A, A-, B+, B, C")
    retention_risk: str = Field(..., description="Baja, Media, Alta")
    trayectoria: str = Field(..., description="Career trajectory description")


class Employee(BaseModel):
    """Complete employee model"""
    id_empleado: int
    nombre: str
    email: EmailStr
    chapter: str
    rol_actual: str
    manager: Optional[str] = None
    antiguedad: str = Field(..., description="Tenure, e.g., '24m', '2m'")
    habilidades: Dict[str, int] = Field(..., description="Skills with levels 0-10")
    responsabilidades_actuales: List[str] = Field(default_factory=list)
    dedicacion_actual: Dict[str, int] = Field(..., description="Project dedication percentages")
    ambiciones: Ambitions
    metadata: Metadata

    @field_validator('dedicacion_actual')
    @classmethod
    def validate_dedication_sum(cls, v):
        """Validate that dedication percentages sum to 100"""
        total = sum(v.values())
        if total != 100:
            raise ValueError(f"Dedication percentages must sum to 100%, got {total}%")
        return v

    @field_validator('habilidades')
    @classmethod
    def validate_skill_levels(cls, v):
        """Validate that skill levels are between 0-10"""
        for skill, level in v.items():
            if not (0 <= level <= 10):
                raise ValueError(f"Skill level for {skill} must be between 0-10, got {level}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id_empleado": 1001,
                "nombre": "Jordi Casals",
                "email": "jordi.casals@quether.com",
                "chapter": "Strategy",
                "rol_actual": "Head of Strategy",
                "manager": None,
                "antiguedad": "24m",
                "habilidades": {
                    "S-OKR": 9,
                    "S-ANALISIS": 9,
                    "S-STAKE": 8
                },
                "responsabilidades_actuales": [
                    "OKRs y gobierno",
                    "Workshops C-level"
                ],
                "dedicacion_actual": {
                    "Royal": 40,
                    "Arquimbau": 25,
                    "Quether GTM": 20,
                    "I+D": 15
                },
                "ambiciones": {
                    "especialidades_preferidas": ["Estrategia", "Pricing"],
                    "nivel_aspiracion": "lead"
                },
                "metadata": {
                    "performance_rating": "A",
                    "retention_risk": "Baja",
                    "trayectoria": "Head of Strategy > Director Operaciones (12-24m)"
                }
            }
        }


class EmployeeCreate(BaseModel):
    """Model for creating a new employee"""
    nombre: str
    email: EmailStr
    chapter: str
    rol_actual: str
    manager: Optional[str] = None
    antiguedad: str
    habilidades: Dict[str, int]
    responsabilidades_actuales: List[str] = Field(default_factory=list)
    dedicacion_actual: Dict[str, int]
    ambiciones: Ambitions
    metadata: Metadata


class EmployeeUpdate(BaseModel):
    """Model for updating employee data"""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    chapter: Optional[str] = None
    rol_actual: Optional[str] = None
    manager: Optional[str] = None
    antiguedad: Optional[str] = None
    habilidades: Optional[Dict[str, int]] = None
    responsabilidades_actuales: Optional[List[str]] = None
    dedicacion_actual: Optional[Dict[str, int]] = None
    ambiciones: Optional[Ambitions] = None
    metadata: Optional[Metadata] = None


class EmployeeListResponse(BaseModel):
    """Response model for employee list"""
    total: int
    employees: List[Employee]


class EmployeeStats(BaseModel):
    """Employee statistics for dashboard"""
    total_employees: int
    by_chapter: Dict[str, int]
    by_performance: Dict[str, int]
    by_retention_risk: Dict[str, int]
    avg_skills_per_employee: float
    avg_tenure_months: float
