"""
Modelos de datos para el sistema de Talent Gap Analysis
======================================================

Define las estructuras de datos principales utilizadas en el algoritmo:
- Employee: Representa un empleado actual con skills y ambiciones
- Role: Representa un rol objetivo con requirements
- Skill: Habilidad con peso y categoría  
- Chapter: Departamento/área de la organización
- Enums: Niveles de skill, bandas de gap, etc.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum


class SkillLevel(str, Enum):
    """Niveles de habilidad de un empleado en un skill específico."""
    NOVATO = "novato"
    INTERMEDIO = "intermedio" 
    AVANZADO = "avanzado"
    EXPERTO = "experto"
    
    @property
    def numeric_value(self) -> float:
        """Convierte el nivel a valor numérico para cálculos."""
        mapping = {
            self.NOVATO: 0.25,
            self.INTERMEDIO: 0.50,
            self.AVANZADO: 0.75,
            self.EXPERTO: 1.0
        }
        return mapping[self]


class GapBand(str, Enum):
    """Bandas de clasificación de gap entre empleado y rol objetivo."""
    READY = "READY"  # Listo para promoción inmediata (score >= 0.75)
    READY_WITH_SUPPORT = "READY_WITH_SUPPORT"  # Listo con soporte (score >= 0.60)
    NEAR = "NEAR"  # Cerca, necesita desarrollo (score >= 0.40)
    FAR = "FAR"  # Lejos, desarrollo significativo (score >= 0.20)
    NOT_VIABLE = "NOT_VIABLE"  # No viable para este rol (score < 0.20)


@dataclass
class Skill:
    """Representa una habilidad en la organización."""
    id: str
    nombre: str
    categoria: str
    peso: float  # 1-5, importancia relativa del skill
    herramientas_asociadas: List[str]
    
    @property
    def normalized_weight(self) -> float:
        """Peso normalizado (0-1) para usar en cálculos."""
        return min(self.peso / 5.0, 1.0)


@dataclass
class Role:
    """Representa un rol objetivo en la organización."""
    id: str
    titulo: str
    nivel: str  # Lead, Senior, Mid, Junior
    chapter: str
    habilidades_requeridas: List[str]  # IDs de skills
    responsabilidades: List[str]
    dedicacion_esperada: str  # e.g., "30-40h/semana"
    
    def parse_dedication_hours(self) -> tuple[int, int]:
        """Extrae el rango de horas de dedicación."""
        import re
        match = re.search(r'(\d+)-(\d+)h', self.dedicacion_esperada)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 40, 40  # Default fallback


@dataclass 
class Chapter:
    """Representa un departamento/área de la organización."""
    nombre: str
    descripcion: str
    role_templates: List[str]  # IDs de roles disponibles


@dataclass
class Employee:
    """Representa un empleado actual en la organización."""
    id: str
    nombre: str
    chapter_actual: str
    skills: Dict[str, SkillLevel]  # skill_id -> nivel
    responsabilidades_actuales: List[str]
    ambiciones: List[str]  # Qué quiere hacer/aprender
    dedicacion_actual: str  # e.g., "30-40h/semana"
    
    def get_skill_level(self, skill_id: str) -> SkillLevel:
        """Obtiene el nivel de un skill, devuelve NOVATO si no lo tiene."""
        return self.skills.get(skill_id, SkillLevel.NOVATO)
    
    def has_skill_at_level(self, skill_id: str, min_level: SkillLevel) -> bool:
        """Verifica si tiene un skill al nivel mínimo requerido."""
        current_level = self.get_skill_level(skill_id)
        return current_level.numeric_value >= min_level.numeric_value
    
    def parse_dedication_hours(self) -> tuple[int, int]:
        """Extrae el rango de horas de dedicación actual."""
        import re
        match = re.search(r'(\d+)-(\d+)h', self.dedicacion_actual)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 40, 40  # Default fallback
    
    def get_skills_by_level(self, min_level: SkillLevel) -> Set[str]:
        """Obtiene todos los skills que tiene al nivel mínimo o superior."""
        return {
            skill_id for skill_id, level in self.skills.items()
            if level.numeric_value >= min_level.numeric_value
        }


@dataclass
class GapResult:
    """Resultado del análisis de gap entre empleado y rol."""
    employee_id: str
    role_id: str
    overall_score: float  # 0-1, donde 1 = perfect match
    band: GapBand
    component_scores: Dict[str, float]  # skills, responsibilities, ambitions, dedication
    detailed_gaps: List[str]  # Lista de gaps específicos identificados
    recommendations: List[Dict]  # Recomendaciones de desarrollo
    
    @property
    def is_ready(self) -> bool:
        """True si está en banda READY o READY_WITH_SUPPORT."""
        return self.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]
    
    @property
    def development_needed(self) -> bool:
        """True si necesita desarrollo significativo."""
        return self.band in [GapBand.NEAR, GapBand.FAR]


@dataclass
class CompatibilityMatrix:
    """Matriz completa de compatibilidad empleado × rol."""
    results: Dict[str, Dict[str, GapResult]]  # employee_id -> role_id -> result
    
    def get_result(self, employee_id: str, role_id: str) -> Optional[GapResult]:
        """Obtiene el resultado para un par empleado-rol específico."""
        return self.results.get(employee_id, {}).get(role_id)
    
    def get_employee_results(self, employee_id: str) -> Dict[str, GapResult]:
        """Obtiene todos los resultados para un empleado."""
        return self.results.get(employee_id, {})
    
    def get_role_candidates(self, role_id: str) -> List[GapResult]:
        """Obtiene todos los candidatos para un rol, ordenados por score."""
        candidates = []
        for employee_results in self.results.values():
            if role_id in employee_results:
                candidates.append(employee_results[role_id])
        
        return sorted(candidates, key=lambda x: x.overall_score, reverse=True)
    
    def get_ready_candidates(self) -> List[GapResult]:
        """Obtiene todos los candidatos en banda READY o READY_WITH_SUPPORT."""
        ready = []
        for employee_results in self.results.values():
            for result in employee_results.values():
                if result.is_ready:
                    ready.append(result)
        
        return sorted(ready, key=lambda x: x.overall_score, reverse=True)


# Configuración por defecto de pesos del algoritmo
DEFAULT_WEIGHTS = {
    'skills': 0.50,        # 50% - Importancia de las habilidades técnicas
    'responsibilities': 0.25,  # 25% - Alineación de responsabilidades
    'ambitions': 0.15,     # 15% - Match con ambiciones del empleado
    'dedication': 0.10     # 10% - Compatibilidad de dedicación horaria
}

# Umbrales por defecto para clasificación en bandas
DEFAULT_BAND_THRESHOLDS = {
    GapBand.READY: 0.75,
    GapBand.READY_WITH_SUPPORT: 0.60,
    GapBand.NEAR: 0.40,
    GapBand.FAR: 0.20,
    # NOT_VIABLE: < 0.20
}