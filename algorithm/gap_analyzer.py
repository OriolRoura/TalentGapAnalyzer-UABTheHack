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
                                 skill_gaps: Dict[str, Dict],
                                 employees: List[Employee] = None,
                                 threshold_percentage: float = 20.0) -> List[Dict]:
        """
        Identifica skills que actúan como bottlenecks organizacionales.
        
        Args:
            skill_gaps: Resultado de analyze_skill_gaps
            employees: Lista de empleados para cálculos reales
            threshold_percentage: % mínimo de gap para considerar bottleneck
            
        Returns:
            Lista de skills bottleneck ordenados por impacto
        """
        # Guardar empleados como atributo temporal para uso en vision_bottlenecks
        self.employees = employees or []
        
        bottlenecks = []
        
        # Intentar usar datos de vision_futura primero
        vision_bottlenecks = self._identify_bottlenecks_from_vision()
        if vision_bottlenecks:
            return vision_bottlenecks
        
        # Fallback al método original
        for skill_id, analysis in skill_gaps.items():
            if analysis['gap_percentage'] >= threshold_percentage:
                bottleneck_impact = (
                    analysis['gap_percentage'] * 
                    analysis['skill_weight'] * 
                    analysis['required_in_roles']
                ) / 100.0
                
                bottlenecks.append({
                    'skill_id': skill_id,
                    'skill_name': analysis['skill_name'],
                    'gap_percentage': analysis['gap_percentage'],
                    'affected_roles': analysis['required_in_roles'],
                    'blocked_transitions': analysis['blocked_transitions'],
                    'bottleneck_impact': bottleneck_impact,
                    'priority_level': analysis['priority_level']
                })
        
        # Ordenar por impacto descendente
        bottlenecks.sort(key=lambda x: x['bottleneck_impact'], reverse=True)
        
        return bottlenecks
    
    def _identify_bottlenecks_from_vision(self) -> List[Dict]:
        """
        Identifica bottlenecks basándose en vision_futura.json capacidad_requerida.
        Calcula transiciones bloqueadas REALES desde la matriz de compatibilidad.
        """
        try:
            from pathlib import Path
            import json
            
            vision_path = Path("dataSet/talent-gap-analyzer-main/vision_futura.json")
            with open(vision_path, 'r', encoding='utf-8') as f:
                vision_data = json.load(f)
            
            capacidad_requerida = vision_data.get('capacidad_requerida', {})
            skills_criticos = capacidad_requerida.get('skills_criticos', [])
            
            bottlenecks = []
            for skill_critico in skills_criticos:
                if skill_critico.get('gap_critico', False):
                    skill_id = skill_critico['skill_id']
                    demanda = skill_critico.get('demanda_proyectada', 0)
                    capacidad = skill_critico.get('capacidad_actual', 0)
                    
                    gap_percentage = ((demanda - capacidad) / demanda * 100) if demanda > 0 else 0
                    
                    # Calcular transiciones bloqueadas REALES:
                    # Contar empleados sin este skill × roles que lo requieren
                    affected_roles = self._get_roles_requiring_skill(skill_id)
                    
                    # Contar cuántos empleados NO tienen este skill
                    employees_without_skill = sum(
                        1 for emp in self.employees 
                        if skill_id not in emp.skills or 
                        emp.skills.get(skill_id, SkillLevel.NOVATO) == SkillLevel.NOVATO
                    )
                    
                    # Transiciones bloqueadas = empleados sin skill × roles que lo requieren
                    blocked_transitions_real = employees_without_skill * len(affected_roles)
                    
                    bottlenecks.append({
                        'skill_id': skill_id,
                        'skill_name': skill_id.replace('S-', '').replace('-', ' ').title(),
                        'gap_percentage': gap_percentage,
                        'affected_roles': affected_roles,
                        'blocked_transitions': blocked_transitions_real,  # CÁLCULO REAL
                        'bottleneck_impact': gap_percentage * demanda / 100,
                        'priority_level': 'HIGH' if gap_percentage > 60 else 'MEDIUM',
                        'demanda_proyectada': demanda,
                        'capacidad_actual': capacidad,
                        'employees_without_skill': employees_without_skill,
                        'roles_requiring_skill': len(affected_roles),
                        'descripcion': skill_critico.get('descripcion', '')
                    })
            
            # Ordenar por gap_percentage descendente
            bottlenecks.sort(key=lambda x: x['gap_percentage'], reverse=True)
            
            return bottlenecks
            
        except Exception as e:
            print(f"Warning: Could not load bottlenecks from vision_futura: {e}")
            return []
    
    def _get_roles_requiring_skill(self, skill_id: str) -> List[str]:
        """Helper para obtener roles que requieren un skill específico."""
        # Mapeo básico skill -> roles (puede expandirse)
        skill_to_roles = {
            'S-ANALISIS': ['R-STR-LEAD', 'R-STR-SR'],
            'S-CRM': ['R-MTX-ARCH', 'R-CRM-ADMIN'],
            'S-UIUX': ['R-DSN-SR'],
            'S-DATA': ['R-MTX-ARCH', 'R-DATA-ANL'],
            'S-STAKE': ['R-STR-LEAD', 'R-PM'],
        }
        return skill_to_roles.get(skill_id, [])
    
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
            recommendations['immediate_actions'].append(
                f"Urgente: Programa intensivo de {bottleneck['skill_name']} "
                f"({bottleneck['blocked_transitions']} transiciones bloqueadas)"
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