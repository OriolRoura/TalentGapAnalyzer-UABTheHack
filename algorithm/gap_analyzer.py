"""
Analizador de Gaps Críticos
===========================

Identifica vacíos críticos en la organización que pueden bloquear el crecimiento.
Analiza gaps por skill, chapter y impacto organizacional.

Funcionalidades principales:
- Gap analysis por skill específico
- Gap analysis por chapter/departamento  
- Identificación de bottlenecks críticos
- Priorización de inversiones en desarrollo
- ROI de entrenamiento por skill
"""

from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
import numpy as np

from .models import (
    Employee, Role, Skill, SkillLevel, CompatibilityMatrix, GapResult, GapBand, Chapter
)


class GapAnalyzer:
    """
    Analizador de gaps críticos para identificar bloqueos organizacionales.
    """
    
    def __init__(self):
        pass
    
    def analyze_skill_gaps(self,
                          compatibility_matrix: CompatibilityMatrix,
                          skills_catalog: Dict[str, Skill],
                          roles: Dict[str, Role]) -> Dict[str, Dict]:
        """
        Analiza gaps por skill específico.
        
        Returns:
            Dict[skill_id, analysis] con métricas detalladas por skill
        """
        skill_analysis = {}
        
        # Mapear qué roles requieren cada skill
        skill_to_roles = defaultdict(list)
        for role in roles.values():
            for skill_id in role.habilidades_requeridas:
                skill_to_roles[skill_id].append(role.id)
        
        for skill_id, skill_info in skills_catalog.items():
            required_in_roles = skill_to_roles[skill_id]
            
            if not required_in_roles:
                continue  # Skip skills no requeridos
            
            # Analizar empleados que necesitan este skill
            employees_needing_skill = []
            blocked_transitions = 0
            
            for emp_id, roles_results in compatibility_matrix.results.items():
                for role_id, result in roles_results.items():
                    if role_id in required_in_roles:
                        # Verificar si este skill es un gap
                        skill_gap = self._is_skill_blocking_transition(
                            result, skill_id, skill_info
                        )
                        if skill_gap and skill_gap.get('blocking', False):
                            employees_needing_skill.append({
                                'employee_id': emp_id,
                                'role_id': role_id,
                                'overall_score': result.overall_score,
                                'skill_impact': skill_gap.get('impact', 0.0)
                            })
                            blocked_transitions += 1
            
            # Calcular métricas del skill
            total_demand = len(required_in_roles) * len(compatibility_matrix.results)
            gap_percentage = (blocked_transitions / total_demand * 100) if total_demand > 0 else 0
            
            skill_analysis[skill_id] = {
                'skill_name': skill_info.nombre,
                'skill_weight': skill_info.peso,
                'categoria': skill_info.categoria,
                'required_in_roles': len(required_in_roles),
                'role_ids': required_in_roles,
                'employees_with_gap': len(employees_needing_skill),
                'blocked_transitions': blocked_transitions,
                'gap_percentage': gap_percentage,
                'priority_level': self._calculate_skill_priority(
                    skill_info.peso, gap_percentage, len(required_in_roles)
                ),
                'roi_estimate': self._estimate_skill_training_roi(
                    employees_needing_skill, skill_info.peso
                ),
                'affected_employees': employees_needing_skill[:10]  # Top 10
            }
        
        # Ordenar por criticidad
        sorted_skills = sorted(
            skill_analysis.items(),
            key=lambda x: (x[1]['priority_level'], x[1]['gap_percentage']),
            reverse=True
        )
        
        return dict(sorted_skills)
    
    def analyze_chapter_gaps(self,
                           compatibility_matrix: CompatibilityMatrix,
                           employees: Dict[str, Employee],
                           roles: Dict[str, Role],
                           chapters: Dict[str, Chapter]) -> Dict[str, Dict]:
        """
        Analiza gaps por chapter/departamento.
        """
        chapter_analysis = {}
        
        # Agrupar empleados por chapter
        employees_by_chapter = defaultdict(list)
        for emp in employees.values():
            employees_by_chapter[emp.chapter_actual].append(emp)
        
        # Agrupar roles por chapter
        roles_by_chapter = defaultdict(list)
        for role in roles.values():
            roles_by_chapter[role.chapter].append(role)
        
        for chapter_name in chapters.keys():
            chapter_employees = employees_by_chapter[chapter_name]
            chapter_roles = roles_by_chapter[chapter_name]
            
            if not chapter_employees or not chapter_roles:
                continue
            
            # Analizar readiness del chapter
            ready_transitions = 0
            total_transitions = 0
            skill_gaps_in_chapter = defaultdict(int)
            
            for emp in chapter_employees:
                emp_results = compatibility_matrix.get_employee_results(emp.id)
                
                for role in chapter_roles:
                    if role.id in emp_results:
                        result = emp_results[role.id]
                        total_transitions += 1
                        
                        if result.band in [GapBand.READY, GapBand.READY_WITH_SUPPORT]:
                            ready_transitions += 1
                        
                        # Contar skill gaps específicos
                        for gap in result.detailed_gaps:
                            if "Skill gap:" in gap:
                                skill_name = gap.split(":")[1].split("(")[0].strip()
                                skill_gaps_in_chapter[skill_name] += 1
            
            readiness_percentage = (ready_transitions / total_transitions * 100) if total_transitions > 0 else 0
            
            # Identificar skills críticos del chapter
            critical_skills = dict(Counter(skill_gaps_in_chapter).most_common(5))
            
            chapter_analysis[chapter_name] = {
                'total_employees': len(chapter_employees),
                'total_roles': len(chapter_roles),
                'total_possible_transitions': total_transitions,
                'ready_transitions': ready_transitions,
                'readiness_percentage': readiness_percentage,
                'critical_skills': critical_skills,
                'health_status': self._assess_chapter_health(readiness_percentage),
                'recommended_actions': self._generate_chapter_recommendations(
                    readiness_percentage, critical_skills
                )
            }
        
        return chapter_analysis
    
    def identify_bottleneck_skills(self,
                                 compatibility_matrix: 'CompatibilityMatrix',
                                 roles_catalog: Dict,
                                 employees: List[Employee] = None,
                                 score_threshold: float = 0.5) -> List[Dict]:
        """
        Identifica VACÍOS CRÍTICOS por rol: skills faltantes en los mejores candidatos.
        
        Este es el análisis correcto de bottlenecks:
        - Para cada rol, encuentra candidatos con score > threshold
        - Identifica qué skills requeridos les faltan
        - Calcula el % de gap de cada skill
        - Prioriza según criticidad (% gap × candidatos afectados)
        
        Args:
            compatibility_matrix: Objeto CompatibilityMatrix con resultados
            roles_catalog: Catálogo de roles con skills requeridos
            employees: Lista de empleados
            score_threshold: Score mínimo para considerar candidato viable (default: 0.5)
            
        Returns:
            Lista de vacíos críticos por rol
        """
        critical_gaps = []
        
        # Obtener empleados si no se proporcionaron
        if not employees:
            employees = []
        employees_dict = {emp.id: emp for emp in employees}
        
        # Analizar gaps para cada rol
        for role_id, role in roles_catalog.items():
            # Obtener candidatos para este rol ordenados por score
            candidates_results = compatibility_matrix.get_role_candidates(role_id)
            
            # Filtrar solo candidatos viables (score > threshold)
            viable_candidates = [
                result for result in candidates_results
                if result.overall_score >= score_threshold
            ]
            
            # Si no hay candidatos viables, reportar TODOS los skills como gaps críticos
            if not viable_candidates:
                required_skills_list = role.habilidades_requeridas
                
                # Solo reportar si el rol tiene skills requeridos
                if required_skills_list:
                    for skill_id in required_skills_list:
                        critical_gaps.append({
                            'role_id': role_id,
                            'role_title': role.titulo,
                            'skill_id': skill_id,
                            'skill_name': self._get_skill_name(skill_id),
                            'avg_gap_percentage': 100.0,  # Gap total - nadie viable
                            'candidates_affected': 0,
                            'total_viable_candidates': 0,
                            'affected_ratio': 1.0,
                            'criticality_score': 100.0,  # Máxima criticidad
                            'priority': 'CRÍTICA',
                            'candidates_details': [],
                            'no_viable_candidates': True  # Flag especial
                        })
                
                continue
            
            required_skills_list = role.habilidades_requeridas  # List[skill_id]
            
            # Analizar cada skill requerido
            # Asumimos nivel AVANZADO como requerido (0.75)
            required_level_default = SkillLevel.AVANZADO
            
            skill_gaps_in_role = {}
            
            for skill_id in required_skills_list:
                candidates_missing_skill = []
                total_gap_percentage = 0
                
                for result in viable_candidates:
                    employee_id = result.employee_id
                    employee = employees_dict.get(employee_id)
                    
                    if not employee:
                        continue
                    
                    current_level = employee.get_skill_level(skill_id)
                    
                    # Calcular gap individual
                    required_value = required_level_default.numeric_value
                    current_value = current_level.numeric_value
                    
                    if current_value < required_value:
                        gap_pct = ((required_value - current_value) / required_value) * 100
                        total_gap_percentage += gap_pct
                        candidates_missing_skill.append({
                            'employee_id': employee_id,
                            'employee_name': employee.nombre,
                            'current_level': current_level.value,
                            'required_level': required_level_default.value,
                            'gap_percentage': gap_pct,
                            'overall_score': result.overall_score
                        })
                
                # Si hay candidatos con gap en este skill, es un vacío crítico
                if candidates_missing_skill:
                    avg_gap = total_gap_percentage / len(candidates_missing_skill)
                    affected_ratio = len(candidates_missing_skill) / len(viable_candidates)
                    
                    skill_gaps_in_role[skill_id] = {
                        'avg_gap_percentage': avg_gap,
                        'candidates_affected': len(candidates_missing_skill),
                        'total_candidates': len(viable_candidates),
                        'affected_ratio': affected_ratio,
                        'candidates_details': candidates_missing_skill
                    }
            
            # Agregar vacíos críticos de este rol
            if skill_gaps_in_role:
                # Ordenar skills por criticidad (gap × ratio de afectados)
                sorted_gaps = sorted(
                    skill_gaps_in_role.items(),
                    key=lambda x: x[1]['avg_gap_percentage'] * x[1]['affected_ratio'],
                    reverse=True
                )
                
                for skill_id, gap_info in sorted_gaps:
                    critical_gaps.append({
                        'role_id': role_id,
                        'role_title': role.titulo,
                        'skill_id': skill_id,
                        'skill_name': self._get_skill_name(skill_id),
                        'avg_gap_percentage': gap_info['avg_gap_percentage'],
                        'candidates_affected': gap_info['candidates_affected'],
                        'total_viable_candidates': gap_info['total_candidates'],
                        'affected_ratio': gap_info['affected_ratio'],
                        'criticality_score': gap_info['avg_gap_percentage'] * gap_info['affected_ratio'],
                        'priority': self._calculate_priority(
                            gap_info['avg_gap_percentage'],
                            gap_info['affected_ratio'],
                            gap_info['total_candidates']
                        ),
                        'candidates_details': gap_info['candidates_details']
                    })
        
        # Ordenar por criticidad descendente
        critical_gaps.sort(key=lambda x: x['criticality_score'], reverse=True)
        
        return critical_gaps
    
    def _get_skill_name(self, skill_id: str) -> str:
        """Obtiene el nombre legible de un skill."""
        # Convertir S-ANALISIS → Análisis, S-CRM → CRM, etc.
        return skill_id.replace('S-', '').replace('-', ' ').title()
    
    def _calculate_priority(self, gap_pct: float, affected_ratio: float, total_candidates: int) -> str:
        """
        Calcula la prioridad de un vacío crítico.
        
        CRÍTICA: Gap alto + muchos candidatos afectados + pocos candidatos totales
        ALTA: Gap alto o muchos candidatos afectados
        MEDIA: Gap moderado
        BAJA: Gap bajo
        """
        criticality = gap_pct * affected_ratio
        
        if criticality > 60 and total_candidates <= 2:
            return 'CRÍTICA'
        elif criticality > 50 or (gap_pct > 70):
            return 'ALTA'
        elif criticality > 30:
            return 'MEDIA'
        else:
            return 'BAJA'
    
    def calculate_training_roi(self,
                             skill_gaps: Dict[str, Dict],
                             training_cost_per_skill: float = 2000.0,
                             promotion_value: float = 15000.0) -> Dict[str, Dict]:
        """
        Calcula ROI de invertir en training de cada skill.
        
        Args:
            skill_gaps: Análisis de gaps por skill
            training_cost_per_skill: Costo promedio de entrenar un skill
            promotion_value: Valor de una promoción exitosa
            
        Returns:
            Dict[skill_id, roi_analysis] con métricas de ROI
        """
        roi_analysis = {}
        
        for skill_id, analysis in skill_gaps.items():
            employees_affected = len(analysis['affected_employees'])
            
            if employees_affected == 0:
                continue
            
            # Estimar empleados que se beneficiarían del training
            high_potential_employees = len([
                emp for emp in analysis['affected_employees']
                if emp['overall_score'] >= 0.6  # Ya están cerca
            ])
            
            # Costos
            total_training_cost = employees_affected * training_cost_per_skill
            
            # Beneficios (promociones desbloqueadas)
            estimated_promotions = high_potential_employees * 0.7  # 70% éxito estimado
            total_value = estimated_promotions * promotion_value
            
            # ROI
            roi_ratio = (total_value - total_training_cost) / total_training_cost if total_training_cost > 0 else 0
            
            roi_analysis[skill_id] = {
                'skill_name': analysis['skill_name'],
                'employees_to_train': employees_affected,
                'high_potential_employees': high_potential_employees,
                'training_cost': total_training_cost,
                'estimated_promotions': estimated_promotions,
                'estimated_value': total_value,
                'roi_ratio': roi_ratio,
                'roi_percentage': roi_ratio * 100,
                'payback_months': self._estimate_payback_period(roi_ratio),
                'priority_recommendation': self._classify_training_priority(roi_ratio)
            }
        
        # Ordenar por ROI
        sorted_roi = sorted(
            roi_analysis.items(),
            key=lambda x: x[1]['roi_ratio'],
            reverse=True
        )
        
        return dict(sorted_roi)
    
    def generate_strategic_recommendations(self,
                                         skill_gaps: Dict[str, Dict],
                                         chapter_gaps: Dict[str, Dict],
                                         bottlenecks: List[Dict]) -> Dict[str, List[str]]:
        """
        Genera recomendaciones estratégicas basadas en el análisis completo.
        """
        recommendations = {
            'immediate_actions': [],
            'short_term_investments': [],
            'long_term_strategy': [],
            'hiring_priorities': []
        }
        
        # Acciones inmediatas (bottlenecks críticos)
        critical_bottlenecks = [b for b in bottlenecks[:3]]  # Top 3
        for bottleneck in critical_bottlenecks:
            affected = bottleneck.get('candidates_affected', 0)
            total = bottleneck.get('total_viable_candidates', 0)
            role_title = bottleneck.get('role_title', 'Unknown')
            recommendations['immediate_actions'].append(
                f"Urgente: {role_title} - {bottleneck['skill_name']} "
                f"({affected}/{total} candidatos viables afectados)"
            )
        
        # Inversiones a corto plazo (skills con alto ROI)
        high_roi_skills = [
            skill for skill, analysis in skill_gaps.items()
            if analysis.get('roi_estimate', {}).get('roi_ratio', 0) > 2.0
        ]
        
        for skill_id in high_roi_skills[:5]:  # Top 5
            skill_name = skill_gaps[skill_id]['skill_name']
            recommendations['short_term_investments'].append(
                f"Invertir en training de {skill_name} (ROI estimado alto)"
            )
        
        # Estrategia a largo plazo (chapters con baja readiness)
        unhealthy_chapters = [
            chapter for chapter, analysis in chapter_gaps.items()
            if analysis['readiness_percentage'] < 30
        ]
        
        if unhealthy_chapters:
            recommendations['long_term_strategy'].append(
                f"Reestructurar chapters con baja readiness: {', '.join(unhealthy_chapters)}"
            )
        
        # Prioridades de contratación (skills imposibles de desarrollar internamente)
        impossible_skills = [
            skill for skill, analysis in skill_gaps.items()
            if analysis['gap_percentage'] > 80 and analysis['employees_with_gap'] > 5
        ]
        
        for skill_id in impossible_skills:
            skill_name = skill_gaps[skill_id]['skill_name']
            recommendations['hiring_priorities'].append(
                f"Contratar externamente: {skill_name} (gap crítico no cubierto internamente)"
            )
        
        return recommendations
    
    def _is_skill_blocking_transition(self, result: GapResult, skill_id: str, skill_info: Skill) -> Dict:
        """Verifica si un skill específico está bloqueando una transición."""
        for gap in result.detailed_gaps:
            if f"Skill gap: {skill_info.nombre}" in gap:
                # Estimar impacto del gap en el score total
                impact = skill_info.normalized_weight * 0.5  # Máximo impacto posible
                return {
                    'blocking': True,
                    'impact': impact,
                    'gap_description': gap
                }
        return {
            'blocking': False,
            'impact': 0.0,
            'gap_description': None
        }
    
    def _calculate_skill_priority(self, weight: float, gap_percentage: float, roles_count: int) -> float:
        """Calcula prioridad de un skill basado en peso, gap y demanda."""
        return (weight / 5.0) * (gap_percentage / 100.0) * min(roles_count / 5.0, 1.0)
    
    def _estimate_skill_training_roi(self, affected_employees: List[Dict], skill_weight: float) -> Dict:
        """Estima ROI básico de entrenar un skill."""
        if not affected_employees:
            return {'roi_ratio': 0, 'estimated_impact': 0}
        
        # Empleados con alto potencial (score > 0.6)
        high_potential = len([emp for emp in affected_employees if emp['overall_score'] > 0.6])
        
        # ROI estimado basado en peso del skill y potencial
        roi_ratio = (high_potential * skill_weight) / max(len(affected_employees), 1)
        
        return {
            'roi_ratio': roi_ratio,
            'estimated_impact': high_potential
        }
    
    def _assess_chapter_health(self, readiness_percentage: float) -> str:
        """Evalúa la salud de un chapter basado en su % de readiness."""
        if readiness_percentage >= 60:
            return "HEALTHY"
        elif readiness_percentage >= 30:
            return "NEEDS_ATTENTION"
        else:
            return "CRITICAL"
    
    def _generate_chapter_recommendations(self, readiness_pct: float, critical_skills: Dict) -> List[str]:
        """Genera recomendaciones específicas para un chapter."""
        recommendations = []
        
        if readiness_pct < 30:
            recommendations.append("Urgente: Plan de desarrollo acelerado")
            recommendations.append("Considerar contratación externa para roles críticos")
        elif readiness_pct < 60:
            recommendations.append("Programa de desarrollo estructurado")
        
        # Recomendaciones por skills críticos
        top_skills = list(critical_skills.keys())[:2]
        for skill in top_skills:
            recommendations.append(f"Reforzar training en: {skill}")
        
        return recommendations
    
    def _estimate_payback_period(self, roi_ratio: float) -> int:
        """Estima período de recuperación en meses."""
        if roi_ratio <= 0:
            return -1  # No se recupera
        elif roi_ratio >= 2.0:
            return 6   # 6 meses
        elif roi_ratio >= 1.0:
            return 12  # 12 meses
        else:
            return 24  # 24 meses
    
    def _classify_training_priority(self, roi_ratio: float) -> str:
        """Clasifica prioridad de training basado en ROI."""
        if roi_ratio >= 3.0:
            return "HIGH"
        elif roi_ratio >= 1.5:
            return "MEDIUM" 
        elif roi_ratio >= 0.5:
            return "LOW"
        else:
            return "NOT_RECOMMENDED"