"""
Talent Gap Algorithm Module
===========================

Sistema de cálculo de gaps y matching para análisis de talento interno.
Diseñado específicamente para Quether Consulting.

Módulos principales:
- models: Modelos de datos (Employee, Role, Skill)
- gap_calculator: Motor de cálculo de compatibilidad
- ranking_engine: Sistema de ranking y bandas de readiness
- gap_analyzer: Análisis de gaps críticos
- recommendation_engine: Generación de recomendaciones
- talent_gap_algorithm: Clase principal orquestadora

Autor: Algorithm Engineer (Hackathon Team)
Fecha: 8 Nov 2025
"""

# Imports se harán dinámicamente para evitar errores circulares
__version__ = "1.0.0"

# Importar solo lo esencial
try:
    from .models import Employee, Role, Skill, SkillLevel, GapBand, Chapter
    from .gap_calculator import GapCalculator
    from .ranking_engine import RankingEngine
    from .gap_analyzer import GapAnalyzer
    from .recommendation_engine import RecommendationEngine
    from .talent_gap_algorithm import TalentGapAlgorithm
except ImportError:
    # Los imports se resolverán en tiempo de ejecución
    pass

__version__ = "1.0.0"
__all__ = [
    "Employee",
    "Role", 
    "Skill",
    "SkillLevel",
    "GapBand",
    "Chapter",
    "GapCalculator",
    "RankingEngine",
    "GapAnalyzer",
    "RecommendationEngine", 
    "TalentGapAlgorithm"
]