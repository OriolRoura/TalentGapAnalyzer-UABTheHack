"""
Model Adapter Service
Converts between API Pydantic models and Algorithm dataclass models
"""

import sys
from pathlib import Path
from typing import Dict, List

from models.employee import Employee as APIEmployee
from models.role import Role as APIRole, Skill as APISkill

# Lazy import algorithm models to avoid path issues
AlgoEmployee = None
AlgoRole = None
AlgoSkill = None
AlgoSkillLevel = None
GapBand = None

def _import_algorithm_models():
    """Lazy import of algorithm models"""
    global AlgoEmployee, AlgoRole, AlgoSkill, AlgoSkillLevel, GapBand
    
    if AlgoEmployee is not None:
        return
    
    # Add parent directory to path so we can import 'algorithm' package
    parent_path = Path(__file__).parent.parent.parent
    if str(parent_path) not in sys.path:
        sys.path.append(str(parent_path))
    
    try:
        from algorithm.models import (
            Employee as _AlgoEmployee,
            Role as _AlgoRole,
            Skill as _AlgoSkill,
            SkillLevel as _AlgoSkillLevel,
            GapBand as _GapBand
        )
        AlgoEmployee = _AlgoEmployee
        AlgoRole = _AlgoRole
        AlgoSkill = _AlgoSkill
        AlgoSkillLevel = _AlgoSkillLevel
        GapBand = _GapBand
    except ImportError as e:
        print(f"Warning: Could not import algorithm models: {e}")


class ModelAdapter:
    """
    Adapter to convert between API models (Pydantic) and Algorithm models (dataclasses)
    """
    
    @staticmethod
    def api_employee_to_algo(api_employee: APIEmployee):
        """
        Convert API Employee model to Algorithm Employee model
        
        Args:
            api_employee: Pydantic Employee from API
            
        Returns:
            AlgoEmployee: Dataclass Employee for algorithm
        """
        _import_algorithm_models()
        
        # Convert skills from Dict[str, int] to Dict[str, SkillLevel]
        # Use same thresholds as main_challenge.py for consistency
        algo_skills = {}
        for skill_id, level in api_employee.habilidades.items():
            # Map numeric level (0-10) to SkillLevel enum
            # Thresholds match main_challenge.py: >= 8: EXPERTO, >= 6: AVANZADO, >= 4: INTERMEDIO, < 4: NOVATO
            if level >= 8:
                algo_skills[skill_id] = AlgoSkillLevel.EXPERTO
            elif level >= 6:
                algo_skills[skill_id] = AlgoSkillLevel.AVANZADO
            elif level >= 4:
                algo_skills[skill_id] = AlgoSkillLevel.INTERMEDIO
            else:
                algo_skills[skill_id] = AlgoSkillLevel.NOVATO
        
        # Extract ambitions - match main_challenge.py format exactly
        # Include especialidades_preferidas + "nivel {nivel_aspiracion}" if exists
        ambiciones = api_employee.ambiciones.especialidades_preferidas.copy()
        if api_employee.ambiciones.nivel_aspiracion:
            ambiciones.append(f"nivel {api_employee.ambiciones.nivel_aspiracion}")
        
        # Convert dedication dict to string format
        # main_challenge.py uses the raw CSV value which could be JSON string or "full-time"
        # For now, convert dict to simple string representation
        # Example: {"Project A": 60, "Project B": 40} -> "full-time" or similar
        if api_employee.dedicacion_actual:
            total_dedication = sum(api_employee.dedicacion_actual.values())
            hours_per_week = int(total_dedication * 40 / 100)  # Assuming 100% = 40h/week
            dedicacion_str = f"{hours_per_week}h/semana"
        else:
            dedicacion_str = "full-time"
        
        return AlgoEmployee(
            id=str(api_employee.id_empleado),
            nombre=api_employee.nombre,
            chapter_actual=api_employee.chapter,
            skills=algo_skills,
            responsabilidades_actuales=api_employee.responsabilidades_actuales,
            ambiciones=ambiciones,
            dedicacion_actual=dedicacion_str
        )
    
    @staticmethod
    def api_role_to_algo(api_role: APIRole, skills_catalog: Dict):
        """
        Convert API Role model to Algorithm Role model
        
        Args:
            api_role: Pydantic Role from API
            skills_catalog: Catalog of skills for the algorithm
            
        Returns:
            AlgoRole: Dataclass Role for algorithm
        """
        _import_algorithm_models()
        
        return AlgoRole(
            id=api_role.id,
            titulo=api_role.titulo,
            nivel=api_role.nivel.value,  # Convert enum to string
            chapter=api_role.capitulo,
            habilidades_requeridas=api_role.habilidades_requeridas,
            responsabilidades=api_role.responsabilidades,
            dedicacion_esperada=api_role.dedicacion_esperada
        )
    
    @staticmethod
    def api_skill_to_algo(api_skill: APISkill):
        """
        Convert API Skill model to Algorithm Skill model
        
        Args:
            api_skill: Pydantic Skill from API
            
        Returns:
            AlgoSkill: Dataclass Skill for algorithm
        """
        _import_algorithm_models()
        
        return AlgoSkill(
            id=api_skill.id,
            nombre=api_skill.nombre,
            categoria=api_skill.categoria if hasattr(api_skill, 'categoria') else 'general',
            peso=api_skill.peso if hasattr(api_skill, 'peso') else 3.0,
            herramientas_asociadas=api_skill.herramientas if hasattr(api_skill, 'herramientas') else []
        )
    
    @staticmethod
    def gap_band_to_classification(gap_band) -> str:
        """
        Convert GapBand enum to API classification string
        
        Args:
            gap_band: GapBand from algorithm
            
        Returns:
            str: Classification string for API
        """
        _import_algorithm_models()
        
        mapping = {
            GapBand.READY: "READY",
            GapBand.READY_WITH_SUPPORT: "READY_WITH_SUPPORT",
            GapBand.NEAR: "NEAR",
            GapBand.FAR: "FAR",
            GapBand.NOT_VIABLE: "NOT_VIABLE"
        }
        return mapping.get(gap_band, "NOT_VIABLE")
    
    @staticmethod
    def score_to_gap_percentage(score: float) -> float:
        """
        Convert algorithm score (0-1, higher is better) to gap percentage (0-100, lower is better)
        
        Args:
            score: Compatibility score from algorithm (0-1)
            
        Returns:
            float: Gap percentage (0-100)
        """
        # Score of 1.0 (perfect match) = 0% gap
        # Score of 0.0 (no match) = 100% gap
        return (1.0 - score) * 100
