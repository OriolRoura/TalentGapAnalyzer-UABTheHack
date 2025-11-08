"""
Motor de Recomendaciones Inteligentes
====================================

Genera recomendaciones personalizadas de desarrollo para empleados y
recomendaciones estratégicas para la organización.

Tipos de recomendaciones:
- Desarrollo individual por empleado
- Planes de carrera personalizados  
- Inversiones organizacionales
- Estrategias de contratación
- Programas de mentoring
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random

from .models import (
    Employee, Role, Skill, GapResult, GapBand, SkillLevel
)


class RecommendationEngine:
    """
    Motor de generación de recomendaciones personalizadas e inteligentes.
    """
    
    def __init__(self, skills_catalog: Dict[str, Skill]):
        """
        Args:
            skills_catalog: Catálogo completo de skills de la organización
        """
        self.skills_catalog = skills_catalog
        self.learning_paths = self._initialize_learning_paths()
        self.mentoring_programs = self._initialize_mentoring_programs()
    
    def generate_employee_recommendations(self,
                                        employee: Employee,
                                        gap_results: List[GapResult]) -> List[Dict]:
        """
        Genera recomendaciones personalizadas para un empleado específico.
        
        Args:
            employee: Empleado target
            gap_results: Resultados de gaps para sus roles de interés
            
        Returns:
            Lista de recomendaciones ordenadas por prioridad
        """
        recommendations = []
        
        # Priorizar por mejor score y banda
        sorted_results = sorted(
            gap_results, 
            key=lambda x: (x.band.value, -x.overall_score)
        )
        
        # Generar recomendaciones para top 3 opciones de carrera
        for i, result in enumerate(sorted_results[:3]):
            career_recs = self._generate_career_path_recommendations(
                employee, result, priority_rank=i+1
            )
            recommendations.extend(career_recs)
        
        # Recomendaciones de desarrollo general
        general_recs = self._generate_general_development_recommendations(employee)
        recommendations.extend(general_recs)
        
        # Filtrar duplicados y ordenar por prioridad
        unique_recs = self._deduplicate_recommendations(recommendations)
        return sorted(unique_recs, key=lambda x: x['priority_score'], reverse=True)[:10]
    
    def _generate_career_path_recommendations(self,
                                            employee: Employee,
                                            gap_result: GapResult,
                                            priority_rank: int) -> List[Dict]:
        """
        Genera recomendaciones específicas para una opción de carrera.
        """
        recommendations = []
        base_priority = 1.0 / priority_rank  # Primera opción tiene más prioridad
        
        # Recomendaciones basadas en banda
        if gap_result.band == GapBand.READY:
            recommendations.append({
                'type': 'career_action',
                'category': 'immediate_opportunity',
                'title': f'¡Oportunidad inmediata para {gap_result.role_id}!',
                'description': 'Ya tienes las competencias necesarias. Solicita la promoción.',
                'actions': [
                    'Hablar con tu manager sobre esta oportunidad',
                    'Preparar presentación de tu readiness',
                    'Solicitar feedback específico del rol'
                ],
                'timeline': '0-1 mes',
                'priority_score': base_priority * 1.0,
                'effort_level': 'LOW'
            })
        
        elif gap_result.band == GapBand.READY_WITH_SUPPORT:
            recommendations.append({
                'type': 'career_action',
                'category': 'supported_transition',
                'title': f'Transición con soporte a {gap_result.role_id}',
                'description': 'Estás muy cerca. Con soporte específico puedes hacer la transición.',
                'actions': [
                    'Identificar mentor interno en el rol',
                    'Solicitar shadowing de 2-4 semanas',
                    'Plan de onboarding estructurado'
                ],
                'timeline': '1-3 meses',
                'priority_score': base_priority * 0.9,
                'effort_level': 'MEDIUM'
            })
        
        elif gap_result.band == GapBand.NEAR:
            # Generar plan de desarrollo específico
            dev_plan = self._create_development_plan(employee, gap_result)
            recommendations.append({
                'type': 'development_plan',
                'category': 'structured_growth',
                'title': f'Plan de desarrollo hacia {gap_result.role_id}',
                'description': 'Plan estructurado de 3-6 meses para cerrar los gaps.',
                'actions': dev_plan['actions'],
                'timeline': dev_plan['timeline'],
                'priority_score': base_priority * 0.7,
                'effort_level': 'HIGH',
                'milestones': dev_plan['milestones']
            })
        
        # Recomendaciones específicas de skills
        skill_recs = self._generate_skill_recommendations(gap_result, base_priority * 0.6)
        recommendations.extend(skill_recs)
        
        return recommendations
    
    def _create_development_plan(self, employee: Employee, gap_result: GapResult) -> Dict:
        """
        Crea plan de desarrollo estructurado para cerrar gaps específicos.
        """
        actions = []
        milestones = []
        
        # Analizar gaps específicos
        skill_gaps = [gap for gap in gap_result.detailed_gaps if "Skill gap:" in gap]
        responsibility_gaps = len([gap for gap in gap_result.detailed_gaps if "responsabilidades" in gap])
        
        # Plan para skills gaps
        for skill_gap in skill_gaps[:3]:  # Top 3 skills
            skill_name = skill_gap.split(":")[1].split("(")[0].strip()
            skill_id = self._find_skill_id_by_name(skill_name)
            
            if skill_id:
                skill_plan = self._get_skill_learning_path(skill_id)
                actions.extend(skill_plan['actions'])
                milestones.append({
                    'month': skill_plan['duration_months'],
                    'milestone': f'Competencia en {skill_name}',
                    'success_criteria': f'Nivel mínimo: {skill_plan["target_level"]}'
                })
        
        # Plan para responsibility gaps
        if responsibility_gaps > 0:
            actions.extend([
                'Solicitar proyecto piloto con responsabilidades del rol objetivo',
                'Participar en comités de decisión relevantes',
                'Documentar y presentar resultados de nuevas responsabilidades'
            ])
            milestones.append({
                'month': 4,
                'milestone': 'Demostración de responsabilidades clave',
                'success_criteria': 'Feedback positivo en nuevas responsabilidades'
            })
        
        return {
            'actions': actions,
            'timeline': '3-6 meses',
            'milestones': milestones,
            'success_probability': self._estimate_success_probability(gap_result)
        }
    
    def _generate_skill_recommendations(self, gap_result: GapResult, base_priority: float) -> List[Dict]:
        """
        Genera recomendaciones específicas para desarrollar skills.
        """
        recommendations = []
        
        skill_gaps = [gap for gap in gap_result.detailed_gaps if "Skill gap:" in gap]
        
        for gap in skill_gaps[:3]:  # Top 3 skills más críticos
            skill_name = gap.split(":")[1].split("(")[0].strip()
            current_level = gap.split("(actual: ")[1].split(")")[0] if "(actual:" in gap else "novato"
            
            skill_id = self._find_skill_id_by_name(skill_name)
            if not skill_id:
                continue
            
            skill_info = self.skills_catalog[skill_id]
            learning_path = self._get_skill_learning_path(skill_id)
            
            recommendations.append({
                'type': 'skill_development',
                'category': 'technical_growth',
                'title': f'Desarrollar competencia en {skill_name}',
                'description': f'Pasar de {current_level} a {learning_path["target_level"]}',
                'actions': learning_path['actions'],
                'timeline': f'{learning_path["duration_months"]} meses',
                'priority_score': base_priority * skill_info.normalized_weight,
                'effort_level': learning_path['effort_level'],
                'resources': learning_path['resources'],
                'success_indicators': learning_path['success_indicators']
            })
        
        return recommendations
    
    def _generate_general_development_recommendations(self, employee: Employee) -> List[Dict]:
        """
        Genera recomendaciones generales de desarrollo profesional.
        """
        recommendations = []
        
        # Recomendación de networking
        recommendations.append({
            'type': 'networking',
            'category': 'professional_growth',
            'title': 'Expandir red profesional interna',
            'description': 'Conectar con profesionales de otros chapters',
            'actions': [
                'Participar en eventos internos cross-chapter',
                'Solicitar coffee chats con líderes de otros departamentos',
                'Unirse a grupos de trabajo interdisciplinarios'
            ],
            'timeline': 'Ongoing',
            'priority_score': 0.4,
            'effort_level': 'LOW'
        })
        
        # Recomendación de mentoring
        recommendations.append({
            'type': 'mentoring',
            'category': 'guidance',
            'title': 'Programa de mentoring',
            'description': 'Encontrar mentor para acelerar desarrollo',
            'actions': [
                'Identificar mentores potenciales en roles objetivo',
                'Estructurar sesiones de mentoring mensuales',
                'Definir objetivos específicos de mentoring'
            ],
            'timeline': '6-12 meses',
            'priority_score': 0.5,
            'effort_level': 'MEDIUM'
        })
        
        # Recomendación basada en ambiciones
        if employee.ambiciones:
            recommendations.append({
                'type': 'ambition_alignment',
                'category': 'career_planning',
                'title': 'Alinear proyectos con ambiciones',
                'description': 'Buscar proyectos que conecten con tus intereses',
                'actions': [
                    f'Proponer proyecto relacionado con: {employee.ambiciones[0]}',
                    'Documentar aprendizajes y resultados',
                    'Presentar resultados a stakeholders relevantes'
                ],
                'timeline': '2-4 meses',
                'priority_score': 0.6,
                'effort_level': 'MEDIUM'
            })
        
        return recommendations
    
    def generate_organizational_recommendations(self,
                                             gap_analysis: Dict,
                                             bottlenecks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Genera recomendaciones estratégicas para la organización.
        """
        recommendations = {
            'training_programs': self._recommend_training_programs(gap_analysis),
            'hiring_priorities': self._recommend_hiring_priorities(bottlenecks),
            'mentoring_programs': self._recommend_mentoring_programs(gap_analysis),
            'organizational_changes': self._recommend_org_changes(gap_analysis)
        }
        
        return recommendations
    
    def _recommend_training_programs(self, gap_analysis: Dict) -> List[Dict]:
        """Recomienda programas de training organizacionales."""
        programs = []
        
        # Identificar skills con alto impacto y ROI
        high_impact_skills = [
            (skill_id, data) for skill_id, data in gap_analysis.items()
            if data.get('priority_level', 0) > 0.7 and data.get('employees_with_gap', 0) >= 3
        ]
        
        for skill_id, data in high_impact_skills[:5]:  # Top 5
            programs.append({
                'program_type': 'group_training',
                'skill_focus': data['skill_name'],
                'target_employees': data['employees_with_gap'],
                'estimated_cost': data['employees_with_gap'] * 2000,  # €2k por persona
                'expected_roi': data.get('roi_estimate', {}).get('roi_ratio', 1.0),
                'timeline': '2-3 meses',
                'priority': 'HIGH' if data['priority_level'] > 0.8 else 'MEDIUM'
            })
        
        return programs
    
    def _recommend_hiring_priorities(self, bottlenecks: List[Dict]) -> List[Dict]:
        """Recomienda prioridades de contratación externa."""
        priorities = []
        
        # Skills imposibles de desarrollar internamente
        critical_bottlenecks = [b for b in bottlenecks if b['gap_percentage'] > 70]
        
        for bottleneck in critical_bottlenecks[:3]:  # Top 3
            priorities.append({
                'skill_required': bottleneck['skill_name'],
                'urgency_level': 'HIGH',
                'roles_blocked': bottleneck['affected_roles'],
                'recommended_level': 'Senior/Expert',
                'hiring_timeline': '1-2 meses',
                'budget_impact': 'HIGH'
            })
        
        return priorities
    
    def _initialize_learning_paths(self) -> Dict[str, Dict]:
        """Inicializa paths de aprendizaje para cada skill."""
        # Paths simplificados para demo
        return {
            'S-OKR': {
                'actions': [
                    'Curso online: OKRs Fundamentals (2 semanas)',
                    'Workshop interno: Implementación de OKRs (1 día)',
                    'Proyecto práctico: Definir OKRs para tu área (1 mes)',
                    'Mentoring con Head of Strategy (mensual)'
                ],
                'duration_months': 3,
                'target_level': 'avanzado',
                'effort_level': 'MEDIUM',
                'resources': ['Coursera', 'Internal workshop', 'Mentoring'],
                'success_indicators': ['Certificación completada', 'OKRs implementados', 'Feedback positivo']
            },
            'S-ANALISIS': {
                'actions': [
                    'Curso: Business Analytics (4 semanas)',
                    'Herramientas: Excel/PowerBI avanzado (2 semanas)',
                    'Proyecto: Análisis de datos cliente real (6 semanas)',
                    'Presentación: Insights a leadership team'
                ],
                'duration_months': 3,
                'target_level': 'avanzado',
                'effort_level': 'HIGH',
                'resources': ['External course', 'Software training', 'Real project'],
                'success_indicators': ['Proyecto completado', 'Insights implementados', 'Skills assessment']
            }
        }
    
    def _initialize_mentoring_programs(self) -> Dict[str, List[str]]:
        """Inicializa programas de mentoring disponibles."""
        return {
            'leadership_development': ['Head of Strategy', 'Senior Creative Lead'],
            'technical_skills': ['Martech Architect', 'Data Analyst'],
            'cross_chapter': ['Various department heads']
        }
    
    def _find_skill_id_by_name(self, skill_name: str) -> Optional[str]:
        """Encuentra skill_id por nombre."""
        for skill_id, skill in self.skills_catalog.items():
            if skill.nombre.lower() == skill_name.lower():
                return skill_id
        return None
    
    def _get_skill_learning_path(self, skill_id: str) -> Dict:
        """Obtiene path de aprendizaje para un skill."""
        if skill_id in self.learning_paths:
            return self.learning_paths[skill_id]
        
        # Path genérico si no existe específico
        skill = self.skills_catalog.get(skill_id)
        return {
            'actions': [
                f'Curso especializado en {skill.nombre if skill else skill_id}',
                'Proyecto práctico supervisado',
                'Evaluación de competencias'
            ],
            'duration_months': 2,
            'target_level': 'avanzado',
            'effort_level': 'MEDIUM',
            'resources': ['External training', 'Internal project'],
            'success_indicators': ['Course completion', 'Project success']
        }
    
    def _estimate_success_probability(self, gap_result: GapResult) -> float:
        """Estima probabilidad de éxito del plan de desarrollo."""
        if gap_result.overall_score >= 0.7:
            return 0.85
        elif gap_result.overall_score >= 0.5:
            return 0.65
        else:
            return 0.40
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Elimina recomendaciones duplicadas."""
        seen_titles = set()
        unique = []
        
        for rec in recommendations:
            if rec['title'] not in seen_titles:
                seen_titles.add(rec['title'])
                unique.append(rec)
        
        return unique
    
    def _recommend_mentoring_programs(self, gap_analysis: Dict) -> List[Dict]:
        """Recomienda programas de mentoring organizacionales."""
        return [
            {
                'program_name': 'Leadership Pipeline Mentoring',
                'target_group': 'High potential employees',
                'focus_areas': ['Strategic thinking', 'Team leadership'],
                'duration': '6 meses',
                'expected_participants': 10
            }
        ]
    
    def _recommend_org_changes(self, gap_analysis: Dict) -> List[Dict]:
        """Recomienda cambios organizacionales."""
        return [
            {
                'change_type': 'Role restructuring',
                'description': 'Crear roles intermedios para facilitar progresión',
                'rationale': 'Gaps muy grandes entre niveles actuales',
                'timeline': '3-6 meses',
                'impact': 'MEDIUM'
            }
        ]