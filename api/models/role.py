"""
Pydantic models for Roles and Role Requirements
Based on vision_futura.json and org_config.json schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class SeniorityLevel(str, Enum):
    """Seniority levels"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"


class Modality(str, Enum):
    """Employment modality"""
    FT = "FT"  # Full Time
    PT = "PT"  # Part Time
    FREELANCE = "Freelance"


class RoleRequirement(BaseModel):
    """Role requirement with skill and level"""
    skill_id: str
    skill_name: str
    required_level: int = Field(..., ge=0, le=10)
    weight: float = Field(default=1.0, ge=0, le=1)


class Role(BaseModel):
    """Complete role definition"""
    id: str = Field(..., description="Role ID, e.g., R-STR-LEAD")
    titulo: str = Field(..., description="Role title")
    nivel: SeniorityLevel
    capitulo: str = Field(..., description="Chapter/Department")
    modalidad: Modality = Field(default=Modality.FT)
    cantidad: int = Field(default=1, ge=1, description="Number of positions needed")
    inicio_estimado: str = Field(..., description="Estimated start, e.g., '0-3m'")
    responsabilidades: List[str] = Field(default_factory=list)
    habilidades_requeridas: List[str] = Field(default_factory=list)
    objetivos_asociados: List[str] = Field(default_factory=list)
    dedicacion_esperada: str = Field(default="40h/semana")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "R-STR-LEAD",
                "titulo": "Head of Strategy",
                "nivel": "lead",
                "capitulo": "Strategy",
                "modalidad": "FT",
                "cantidad": 1,
                "inicio_estimado": "0-3m",
                "responsabilidades": [
                    "Definir visión y prioridades estratégicas",
                    "Alinear roadmap de capítulos"
                ],
                "habilidades_requeridas": [
                    "S-OKR",
                    "S-ANALISIS",
                    "S-STAKE"
                ],
                "objetivos_asociados": [
                    "OKRs y gobierno",
                    "Propuesta de valor"
                ],
                "dedicacion_esperada": "30-40h/semana"
            }
        }


class RoleCreate(BaseModel):
    """Model for creating a new role"""
    titulo: str
    nivel: SeniorityLevel
    capitulo: str
    modalidad: Modality = Modality.FT
    cantidad: int = 1
    inicio_estimado: str
    responsabilidades: List[str] = Field(default_factory=list)
    habilidades_requeridas: List[str] = Field(default_factory=list)
    objetivos_asociados: List[str] = Field(default_factory=list)
    dedicacion_esperada: str = "40h/semana"


class RoleUpdate(BaseModel):
    """Model for updating a role"""
    titulo: Optional[str] = None
    nivel: Optional[SeniorityLevel] = None
    capitulo: Optional[str] = None
    modalidad: Optional[Modality] = None
    cantidad: Optional[int] = None
    inicio_estimado: Optional[str] = None
    responsabilidades: Optional[List[str]] = None
    habilidades_requeridas: Optional[List[str]] = None
    objetivos_asociados: Optional[List[str]] = None
    dedicacion_esperada: Optional[str] = None


class RoleListResponse(BaseModel):
    """Response model for role list"""
    total: int
    roles: List[Role]


class Chapter(BaseModel):
    """Chapter/Department definition"""
    nombre: str
    descripcion: str
    role_templates: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Skill definition"""
    id: str
    nombre: str
    categoria: str
    descripcion: Optional[str] = Field(default="", description="Skill description")
    peso: int = Field(default=1, ge=1, le=10)
    herramientas_asociadas: List[str] = Field(default_factory=list)


class SkillCreate(BaseModel):
    """Model for creating a new skill"""
    nombre: str
    categoria: str
    descripcion: Optional[str] = ""
    peso: int = Field(default=1, ge=1, le=10)
    herramientas_asociadas: List[str] = Field(default_factory=list)


class SkillListResponse(BaseModel):
    """Response model for skill list"""
    total: int
    skills: List[Skill]
