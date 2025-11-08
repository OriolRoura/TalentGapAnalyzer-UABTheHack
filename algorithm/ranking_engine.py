"""
Sistema de Ranking y Clasificación
==================================

Genera rankings de candidatos por rol y identifica los mejores matches
bidireccionales. Maneja conflictos cuando múltiples roles compiten por
los mismos candidatos top.

Funcionalidades principales:
- Ranking de candidatos por rol objetivo
- Mejores opciones de carrera por empleado  
- Detección de conflictos en asignaciones
- Distribución óptima de talento
- Identificación de roles "huérfanos"
"""

from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import numpy as np

from .models import (
    Employee, Role, GapResult, CompatibilityMatrix, GapBand
)


class RankingEngine:
    """
    Motor de ranking y clasificación para optimizar matches empleado-rol.
    """
    
    def __init__(self, min_viable_score: float = 0.25):
        """
        Args:
            min_viable_score: Score mínimo para considerar un match viable
        """
        self.min_viable_score = min_viable_score
    
    def generate_role_rankings(self, 
                             compatibility_matrix: CompatibilityMatrix,
                             roles: Dict[str, Role]) -> Dict[str, List[GapResult]]:
        """
        Genera ranking de candidatos para cada rol.
        
        Args:
            compatibility_matrix: Matriz de compatibilidad completa
            roles: Diccionario de roles disponibles
            
        Returns:
            Dict[role_id, List[GapResult]] ordenado por score descendente
        """
        rankings = {}
        
        for role_id in roles.keys():
            candidates = compatibility_matrix.get_role_candidates(role_id)
            
            # Filtrar candidatos viables
            viable_candidates = [
                result for result in candidates 
                if result.overall_score >= self.min_viable_score
            ]
            
            rankings[role_id] = viable_candidates
        
        return rankings
    
    def generate_employee_career_paths(self,
                                     compatibility_matrix: CompatibilityMatrix,
                                     employees: Dict[str, Employee]) -> Dict[str, List[GapResult]]:
        """
        Genera las mejores opciones de carrera para cada empleado.
        
        Returns:
            Dict[employee_id, List[GapResult]] con top opciones ordenadas
        """
        career_paths = {}
        
        for employee_id in employees.keys():
            employee_results = compatibility_matrix.get_employee_results(employee_id)
            
            # Ordenar por score y filtrar viables
            viable_paths = [
                result for result in employee_results.values()
                if result.overall_score >= self.min_viable_score
            ]
            
            viable_paths.sort(key=lambda x: x.overall_score, reverse=True)
            
            # Tomar top 5 opciones
            career_paths[employee_id] = viable_paths[:5]
        
        return career_paths
    
    def detect_assignment_conflicts(self,
                                  role_rankings: Dict[str, List[GapResult]],
                                  top_n: int = 3) -> Dict[str, List[str]]:
        """
        Detecta empleados que aparecen como top candidatos para múltiples roles.
        
        Args:
            role_rankings: Rankings por rol
            top_n: Considerar solo top N candidatos por rol
            
        Returns:
            Dict[employee_id, List[role_id]] con conflictos detectados
        """
        employee_appearances = defaultdict(list)
        
        # Mapear en qué roles aparece cada empleado como top candidato
        for role_id, candidates in role_rankings.items():
            top_candidates = candidates[:top_n]
            for result in top_candidates:
                employee_appearances[result.employee_id].append(role_id)
        
        # Filtrar solo empleados con conflictos (aparecen en múltiples roles)
        conflicts = {
            emp_id: roles for emp_id, roles in employee_appearances.items()
            if len(roles) > 1
        }
        
        return conflicts
    
    def suggest_optimal_distribution(self,
                                   role_rankings: Dict[str, List[GapResult]],
                                   priority_roles: List[str] = None) -> Dict[str, str]:
        """
        Sugiere distribución óptima de empleados a roles considerando conflictos.
        
        Utiliza algoritmo greedy que prioriza:
        1. Roles críticos/prioritarios
        2. Matches con scores más altos
        3. Minimizar roles sin candidatos
        
        Args:
            role_rankings: Rankings de candidatos por rol
            priority_roles: Lista de roles con prioridad alta
            
        Returns:
            Dict[employee_id, role_id] con asignación sugerida
        """
        assignments = {}
        assigned_employees = set()
        priority_roles = priority_roles or []
        
        # Crear lista ordenada de roles (prioritarios primero)
        ordered_roles = priority_roles + [
            role_id for role_id in role_rankings.keys() 
            if role_id not in priority_roles
        ]
        
        # Asignar empleados empezando por roles prioritarios
        for role_id in ordered_roles:
            candidates = role_rankings.get(role_id, [])
            
            # Buscar el mejor candidato no asignado
            for result in candidates:
                if result.employee_id not in assigned_employees:
                    # Solo asignar si está en banda READY o READY_WITH_SUPPORT
                    if result.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]:
                        assignments[result.employee_id] = role_id
                        assigned_employees.add(result.employee_id)
                        break
        
        return assignments
    
    def identify_orphan_roles(self,
                            role_rankings: Dict[str, List[GapResult]],
                            min_ready_candidates: int = 1) -> List[str]:
        """
        Identifica roles sin suficientes candidatos ready.
        
        Args:
            role_rankings: Rankings por rol
            min_ready_candidates: Mínimo de candidatos ready requeridos
            
        Returns:
            Lista de role_ids con déficit de candidatos
        """
        orphan_roles = []
        
        for role_id, candidates in role_rankings.items():
            ready_candidates = [
                result for result in candidates
                if result.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]
            ]
            
            if len(ready_candidates) < min_ready_candidates:
                orphan_roles.append(role_id)
        
        return orphan_roles
    
    def calculate_readiness_distribution(self,
                                       compatibility_matrix: CompatibilityMatrix) -> Dict[GapBand, int]:
        """
        Calcula distribución de empleados por banda de readiness.
        """
        distribution = defaultdict(int)
        
        for employee_results in compatibility_matrix.results.values():
            for result in employee_results.values():
                distribution[result.band] += 1
        
        return dict(distribution)
    
    def identify_high_potential_employees(self,
                                        career_paths: Dict[str, List[GapResult]],
                                        min_ready_options: int = 2) -> List[str]:
        """
        Identifica empleados con alto potencial (múltiples opciones de carrera ready).
        
        Args:
            career_paths: Opciones de carrera por empleado
            min_ready_options: Mínimo de opciones ready para considerar alto potencial
            
        Returns:
            Lista de employee_ids con alto potencial
        """
        high_potential = []
        
        for employee_id, paths in career_paths.items():
            ready_paths = [
                path for path in paths
                if path.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]
            ]
            
            if len(ready_paths) >= min_ready_options:
                high_potential.append(employee_id)
        
        return high_potential
    
    def generate_succession_planning(self,
                                   role_rankings: Dict[str, List[GapResult]],
                                   leadership_roles: List[str]) -> Dict[str, List[str]]:
        """
        Genera plan de sucesión para roles de liderazgo.
        
        Args:
            role_rankings: Rankings de candidatos
            leadership_roles: Lista de roles considerados de liderazgo
            
        Returns:
            Dict[role_id, List[employee_id]] con candidatos de sucesión ordenados
        """
        succession_plan = {}
        
        for role_id in leadership_roles:
            if role_id not in role_rankings:
                succession_plan[role_id] = []
                continue
            
            candidates = role_rankings[role_id]
            
            # Filtrar candidatos viable para sucesión (NEAR o mejor)
            succession_candidates = [
                result.employee_id for result in candidates
                if result.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT, GapBand.NEAR]
            ]
            
            succession_plan[role_id] = succession_candidates[:3]  # Top 3
        
        return succession_plan
    
    def calculate_transition_timeline(self,
                                    result: GapResult) -> Dict[str, int]:
        """
        Estima timeline de desarrollo para alcanzar readiness.
        
        Returns:
            Dict con estimaciones en meses para diferentes hitos
        """
        if result.band == GapBand.READY:
            return {"ready_now": 0, "fully_ready": 0}
        elif result.band == GapBand.READY_WITH_SUPPORT:
            return {"ready_now": 0, "fully_ready": 1}
        elif result.band == GapBand.NEAR:
            return {"ready_now": 3, "fully_ready": 6}
        elif result.band == GapBand.FAR:
            return {"ready_now": 9, "fully_ready": 12}
        else:  # NOT_VIABLE
            return {"ready_now": -1, "fully_ready": -1}  # No viable
    
    def generate_ranking_summary(self,
                               role_rankings: Dict[str, List[GapResult]],
                               employees: Dict[str, Employee],
                               roles: Dict[str, Role]) -> Dict:
        """
        Genera resumen ejecutivo de los rankings.
        """
        total_positions = len(roles)
        total_employees = len(employees)
        
        # Contar posiciones con candidatos ready
        positions_with_ready = 0
        total_ready_matches = 0
        
        for candidates in role_rankings.values():
            ready_candidates = [
                c for c in candidates 
                if c.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]
            ]
            if ready_candidates:
                positions_with_ready += 1
            total_ready_matches += len(ready_candidates)
        
        # Identificar roles críticos sin candidatos
        orphan_roles = self.identify_orphan_roles(role_rankings)
        
        # Calcular distribución de readiness
        all_results = [
            result for candidates in role_rankings.values()
            for result in candidates
        ]
        
        readiness_dist = defaultdict(int)
        for result in all_results:
            readiness_dist[result.band] += 1
        
        return {
            "total_positions": total_positions,
            "positions_with_ready_candidates": positions_with_ready,
            "coverage_percentage": (positions_with_ready / total_positions * 100) if total_positions > 0 else 0,
            "total_ready_matches": total_ready_matches,
            "orphan_roles_count": len(orphan_roles),
            "orphan_roles": orphan_roles,
            "readiness_distribution": dict(readiness_dist),
            "avg_candidates_per_role": len(all_results) / total_positions if total_positions > 0 else 0
        }