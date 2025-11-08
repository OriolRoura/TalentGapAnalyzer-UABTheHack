"""
Talent Gap Algorithm - Clase Principal Orquestadora
==================================================

Esta es la clase principal que orquesta todos los componentes del sistema
de análisis de talent gaps. Proporciona una interfaz unificada y flujo
de trabajo completo desde datos de entrada hasta insights finales.

Funcionalidades principales:
- Coordina todos los módulos del algoritmo
- Gestiona el flujo de datos entre componentes  
- Proporciona API simplificada para integración
- Maneja configuración y parámetros
- Genera outputs estructurados
"""

from typing import Dict, List, Tuple, Optional
import json
import pandas as pd
from datetime import datetime

from .models import (
    Employee, Role, Skill, Chapter, CompatibilityMatrix, 
    GapResult, DEFAULT_WEIGHTS
)
from .gap_calculator import GapCalculator
from .ranking_engine import RankingEngine
from .gap_analyzer import GapAnalyzer
from .recommendation_engine import RecommendationEngine


class TalentGapAlgorithm:
    """
    Clase principal que orquesta el análisis completo de talent gaps.
    
    Workflow:
    1. Inicialización con configuración organizacional
    2. Carga de datos de empleados
    3. Cálculo de matriz de compatibilidad
    4. Generación de rankings
    5. Análisis de gaps críticos
    6. Generación de recomendaciones
    7. Output de resultados estructurados
    """
    
    def __init__(self, 
                 org_config: Dict,
                 vision_futura: Dict,
                 algorithm_weights: Dict[str, float] = None):
        """
        Inicializa el algoritmo con la configuración organizacional.
        
        Args:
            org_config: Configuración desde org_config.json
            vision_futura: Visión futura desde vision_futura.json  
            algorithm_weights: Pesos personalizados para el algoritmo
        """
        self.org_config = org_config
        self.vision_futura = vision_futura
        self.weights = algorithm_weights or DEFAULT_WEIGHTS.copy()
        
        # Parsear configuración organizacional
        self.skills_catalog = self._parse_skills_catalog()
        self.roles_catalog = self._parse_roles_catalog()
        self.chapters_catalog = self._parse_chapters_catalog()
        self.future_roles = self._parse_future_roles()
        
        # Inicializar componentes del algoritmo
        self.gap_calculator = GapCalculator(
            skills_catalog=self.skills_catalog,
            weights=self.weights
        )
        self.ranking_engine = RankingEngine()
        self.gap_analyzer = GapAnalyzer()
        self.recommendation_engine = RecommendationEngine(self.skills_catalog)
        
        # Estado interno
        self.employees = {}
        self.compatibility_matrix = None
        self.analysis_results = {}
        
    def load_employees_data(self, employees_data: List[Dict]) -> None:
        """
        Carga datos de empleados actuales.
        
        Args:
            employees_data: Lista de diccionarios con datos de empleados
        """
        self.employees = {}
        
        for emp_data in employees_data:
            try:
                employee = Employee(**emp_data)
                self.employees[employee.id] = employee
            except Exception as e:
                print(f"Warning: Error loading employee {emp_data.get('id', 'unknown')}: {e}")
        
        print(f"✓ Loaded {len(self.employees)} employees successfully")
    
    def run_full_analysis(self) -> Dict:
        """
        Ejecuta el análisis completo de talent gaps.
        
        Returns:
            Diccionario con todos los resultados del análisis
        """
        if not self.employees:
            raise ValueError("No employees loaded. Call load_employees_data() first.")
        
        print("🚀 Starting full talent gap analysis...")
        
        # Paso 0: Inicializar sistema de keywords dinámicas
        print("🧠 Step 0: Learning keywords from data...")
        try:
            self.gap_calculator.initialize_dynamic_keywords(
                list(self.employees.values()), 
                list(self.roles_catalog.values())
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize dynamic keywords ({e}), using fallback system")
            # El sistema usará automáticamente el método fallback
        
        # Paso 1: Calcular matriz de compatibilidad
        print("📊 Step 1: Calculating compatibility matrix...")
        self.compatibility_matrix = self._calculate_compatibility_matrix()
        
        # Paso 2: Generar rankings
        print("🏆 Step 2: Generating rankings...")
        role_rankings = self.ranking_engine.generate_role_rankings(
            self.compatibility_matrix, 
            self.roles_catalog
        )
        
        career_paths = self.ranking_engine.generate_employee_career_paths(
            self.compatibility_matrix,
            self.employees
        )
        
        # Paso 3: Detectar conflictos y optimizar distribución
        print("⚖️ Step 3: Analyzing conflicts and optimization...")
        conflicts = self.ranking_engine.detect_assignment_conflicts(role_rankings)
        optimal_distribution = self.ranking_engine.suggest_optimal_distribution(role_rankings)
        orphan_roles = self.ranking_engine.identify_orphan_roles(role_rankings)
        
        # Paso 4: Análisis de gaps críticos
        print("🔍 Step 4: Critical gap analysis...")
        skill_gaps = self.gap_analyzer.analyze_skill_gaps(
            self.compatibility_matrix,
            self.skills_catalog,
            self.roles_catalog
        )
        
        chapter_gaps = self.gap_analyzer.analyze_chapter_gaps(
            self.compatibility_matrix,
            self.employees,
            self.roles_catalog,
            self.chapters_catalog
        )
        
        bottlenecks = self.gap_analyzer.identify_bottleneck_skills(skill_gaps)
        training_roi = self.gap_analyzer.calculate_training_roi(skill_gaps)
        
        # Paso 5: Generar recomendaciones
        print("💡 Step 5: Generating recommendations...")
        strategic_recommendations = self.gap_analyzer.generate_strategic_recommendations(
            skill_gaps, chapter_gaps, bottlenecks
        )
        
        organizational_recommendations = self.recommendation_engine.generate_organizational_recommendations(
            skill_gaps, bottlenecks
        )
        
        # Generar recomendaciones individuales para empleados top
        individual_recommendations = self._generate_individual_recommendations(career_paths)
        
        # Paso 6: Compilar resultados finales
        print("📋 Step 6: Compiling final results...")
        results = {
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_employees': len(self.employees),
                'total_roles': len(self.roles_catalog),
                'total_skills': len(self.skills_catalog),
                'algorithm_version': '1.0.0',
                'weights_used': self.weights
            },
            
            'compatibility_matrix': {
                'summary': self._summarize_compatibility_matrix(),
                'detailed_results': self._export_compatibility_matrix_data()
            },
            
            'rankings': {
                'role_rankings': role_rankings,
                'career_paths': career_paths,
                'conflicts': conflicts,
                'optimal_distribution': optimal_distribution,
                'orphan_roles': orphan_roles,
                'ranking_summary': self.ranking_engine.generate_ranking_summary(
                    role_rankings, self.employees, self.roles_catalog
                )
            },
            
            'gap_analysis': {
                'skill_gaps': skill_gaps,
                'chapter_gaps': chapter_gaps,
                'bottlenecks': bottlenecks,
                'training_roi': training_roi
            },
            
            'recommendations': {
                'strategic': strategic_recommendations,
                'organizational': organizational_recommendations,
                'individual': individual_recommendations
            },
            
            'executive_summary': self._generate_executive_summary(
                role_rankings, skill_gaps, chapter_gaps, bottlenecks
            )
        }
        
        self.analysis_results = results
        print("✅ Analysis completed successfully!")
        
        return results
    
    def get_employee_analysis(self, employee_id: str) -> Dict:
        """
        Obtiene análisis detallado para un empleado específico.
        """
        if employee_id not in self.employees:
            raise ValueError(f"Employee {employee_id} not found")
        
        if not self.compatibility_matrix:
            raise ValueError("No analysis run yet. Call run_full_analysis() first.")
        
        employee = self.employees[employee_id]
        employee_results = self.compatibility_matrix.get_employee_results(employee_id)
        
        # Generar recomendaciones específicas
        gap_results = list(employee_results.values())
        recommendations = self.recommendation_engine.generate_employee_recommendations(
            employee, gap_results
        )
        
        return {
            'employee_info': {
                'id': employee.id,
                'nombre': employee.nombre,
                'chapter_actual': employee.chapter_actual,
                'skills_actuales': dict(employee.skills),
                'ambiciones': employee.ambiciones
            },
            'career_options': [
                {
                    'role_id': result.role_id,
                    'score': result.overall_score,
                    'band': result.band.value,
                    'component_scores': result.component_scores,
                    'gaps': result.detailed_gaps
                }
                for result in sorted(gap_results, key=lambda x: x.overall_score, reverse=True)
            ],
            'recommendations': recommendations,
            'development_priority': self._calculate_development_priority(gap_results)
        }
    
    def get_role_analysis(self, role_id: str) -> Dict:
        """
        Obtiene análisis detallado para un rol específico.
        """
        if role_id not in self.roles_catalog:
            raise ValueError(f"Role {role_id} not found")
        
        if not self.compatibility_matrix:
            raise ValueError("No analysis run yet. Call run_full_analysis() first.")
        
        role = self.roles_catalog[role_id]
        candidates = self.compatibility_matrix.get_role_candidates(role_id)
        
        return {
            'role_info': {
                'id': role.id,
                'titulo': role.titulo,
                'nivel': role.nivel,
                'chapter': role.chapter,
                'habilidades_requeridas': role.habilidades_requeridas,
                'responsabilidades': role.responsabilidades
            },
            'candidates': [
                {
                    'employee_id': result.employee_id,
                    'employee_name': self.employees[result.employee_id].nombre,
                    'score': result.overall_score,
                    'band': result.band.value,
                    'readiness_timeline': self.ranking_engine.calculate_transition_timeline(result)
                }
                for result in candidates
            ],
            'hiring_recommendation': self._should_hire_external(candidates),
            'succession_plan': candidates[:3] if candidates else []  # Top 3 successors
        }
    
    def export_results(self, format: str = 'json', include_detailed: bool = True) -> str:
        """
        Exporta resultados del análisis en formato especificado.
        
        Args:
            format: 'json', 'csv', 'excel'
            include_detailed: Si incluir datos detallados o solo summary
            
        Returns:
            String con datos exportados o path al archivo
        """
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analysis first.")
        
        if format == 'json':
            return json.dumps(self.analysis_results, indent=2, ensure_ascii=False, default=str)
        
        elif format == 'csv':
            return self._export_csv()
        
        elif format == 'excel':
            return self._export_excel()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _parse_skills_catalog(self) -> Dict[str, Skill]:
        """Parsea catálogo de skills desde org_config."""
        skills = {}
        
        for skill_data in self.org_config.get('skills', []):
            skill = Skill(
                id=skill_data['id'],
                nombre=skill_data['nombre'],
                categoria=skill_data.get('categoría', 'General'),
                peso=skill_data.get('peso', 1.0),
                herramientas_asociadas=skill_data.get('herramientas_asociadas', [])
            )
            skills[skill.id] = skill
        
        return skills
    
    def _parse_roles_catalog(self) -> Dict[str, Role]:
        """Parsea catálogo de roles desde org_config.json (roles definidos en la organización)."""
        roles = {}
        
        # Usar roles definidos en org_config.json
        org_roles = self.org_config.get('roles', [])
        
        for role_data in org_roles:
            role = Role(
                id=role_data['id'],
                titulo=role_data.get('título', role_data.get('titulo', role_data['id'])),
                nivel=role_data.get('nivel', 'Mid'),
                chapter=self._get_chapter_for_role(role_data['id']),
                habilidades_requeridas=role_data.get('habilidades_requeridas', []),
                responsabilidades=role_data.get('responsabilidades', []),
                dedicacion_esperada=role_data.get('dedicación_esperada', '35-45h/semana')
            )
            roles[role.id] = role
        
        return roles
    
    def _get_chapter_for_role(self, role_id: str) -> str:
        """Obtiene el chapter al que pertenece un rol basándose en org_config.json."""
        for chapter in self.org_config.get('chapters', []):
            if role_id in chapter.get('role_templates', []):
                return chapter['nombre']
        return 'Unknown'
    
    def _infer_skills_for_future_role(self, role_data: dict) -> List[str]:
        """Infiere las habilidades requeridas basado en el tipo de rol futuro."""
        role_id = role_data.get('id', '')
        
        # Mapeo de roles futuros a skills principales
        skill_mapping = {
            'R-STR-LEAD': ['S-OKR', 'S-ANALISIS', 'S-STAKE'],
            'R-PM': ['S-PM', 'S-ANALYTICS', 'S-STAKE'], 
            'R-MTX-ARCH': ['S-CRM', 'S-AUTOM', 'S-DATA'],
            'R-CRM-ADMIN': ['S-CRM', 'S-AUTOM', 'S-EMAIL'],
            'R-DATA-ANL': ['S-ANALYTICS', 'S-SQLPY', 'S-DATA'],
            'R-CRT-LEAD': ['S-STORY', 'S-COPY', 'S-BRAND'],
            'R-CON-WRI': ['S-COPY', 'S-STORY', 'S-EMAIL'],
            'R-DEV-LEAD': ['S-SQLPY', 'S-DATA', 'S-PM'],
            'R-DEV-FE': ['S-FIGMA', 'S-UIUX', 'S-DATA'],
            'R-DEV-BE': ['S-SQLPY', 'S-DATA', 'S-AUTOM'],
            'R-REV-OPS': ['S-CRM', 'S-ANALYTICS', 'S-AUTOM'],
            'R-CUS-SUC': ['S-CRM', 'S-STAKE', 'S-EMAIL']
        }
        
        return skill_mapping.get(role_id, ['S-PM', 'S-ANALYTICS', 'S-STAKE'])  # Default skills
    
    def _parse_chapters_catalog(self) -> Dict[str, Chapter]:
        """Parsea catálogo de chapters desde org_config."""
        chapters = {}
        
        for chapter_data in self.org_config.get('chapters', []):
            chapter = Chapter(
                nombre=chapter_data['nombre'],
                descripcion=chapter_data.get('descripción', ''),
                role_templates=chapter_data.get('role_templates', [])
            )
            chapters[chapter.nombre] = chapter
        
        return chapters
    
    def _parse_future_roles(self) -> Dict[str, Role]:
        """Parsea roles futuros desde vision_futura."""
        future_roles = {}
        
        roles_necesarios = self.vision_futura.get('roles_necesarios', [])
        
        for role_data in roles_necesarios:
            # Buscar definición completa en org_config
            role_id = role_data['id']
            base_role = self.roles_catalog.get(role_id)
            
            if base_role:
                future_role = Role(
                    id=role_id,
                    titulo=role_data.get('título', base_role.titulo),
                    nivel=role_data.get('nivel', base_role.nivel),
                    chapter=role_data.get('capítulo', base_role.chapter),
                    habilidades_requeridas=base_role.habilidades_requeridas,
                    responsabilidades=base_role.responsabilidades,
                    dedicacion_esperada=base_role.dedicacion_esperada
                )
                future_roles[role_id] = future_role
        
        return future_roles
    
    def _calculate_compatibility_matrix(self) -> CompatibilityMatrix:
        """Calcula la matriz completa de compatibilidad."""
        results = {}
        
        for emp_id, employee in self.employees.items():
            results[emp_id] = {}
            
            # Calcular gaps para roles relevantes (del mismo chapter + roles futuros)
            relevant_roles = self._get_relevant_roles_for_employee(employee)
            
            for role_id, role in relevant_roles.items():
                gap_result = self.gap_calculator.calculate_gap(employee, role)
                results[emp_id][role_id] = gap_result
        
        return CompatibilityMatrix(results)
    
    def _get_relevant_roles_for_employee(self, employee: Employee) -> Dict[str, Role]:
        """Obtiene roles relevantes para un empleado específico."""
        relevant = {}
        
        # Roles del mismo chapter
        for role_id, role in self.roles_catalog.items():
            if role.chapter == employee.chapter_actual:
                relevant[role_id] = role
        
        # Roles futuros especificados
        for role_id, role in self.future_roles.items():
            relevant[role_id] = role
        
        return relevant
    
    def _generate_individual_recommendations(self, career_paths: Dict) -> Dict[str, List[Dict]]:
        """Genera recomendaciones individuales para empleados key."""
        individual_recs = {}
        
        # Generar para empleados con alto potencial
        high_potential_employees = self.ranking_engine.identify_high_potential_employees(career_paths)
        
        for emp_id in high_potential_employees[:10]:  # Top 10
            if emp_id in self.employees:
                employee = self.employees[emp_id]
                gap_results = list(career_paths[emp_id])
                
                recommendations = self.recommendation_engine.generate_employee_recommendations(
                    employee, gap_results
                )
                
                individual_recs[emp_id] = recommendations
        
        return individual_recs
    
    def _generate_executive_summary(self, role_rankings, skill_gaps, chapter_gaps, bottlenecks) -> Dict:
        """Genera resumen ejecutivo del análisis."""
        
        # Calcular métricas clave
        total_ready_matches = sum(
            len([c for c in candidates if c.band.value in ['READY', 'READY_WITH_SUPPORT']])
            for candidates in role_rankings.values()
        )
        
        total_possible_matches = sum(len(candidates) for candidates in role_rankings.values())
        readiness_rate = (total_ready_matches / total_possible_matches * 100) if total_possible_matches > 0 else 0
        
        critical_bottlenecks = [b for b in bottlenecks if b['gap_percentage'] > 50]
        
        return {
            'overall_readiness': f"{readiness_rate:.1f}%",
            'employees_analyzed': len(self.employees),
            'roles_analyzed': len(self.roles_catalog),
            'ready_transitions': total_ready_matches,
            'critical_bottlenecks': len(critical_bottlenecks),
            'chapters_needing_attention': len([
                ch for ch, data in chapter_gaps.items()
                if data['health_status'] != 'HEALTHY'
            ]),
            'key_insights': [
                f"Readiness rate: {readiness_rate:.1f}% of analyzed transitions are ready",
                f"Critical bottlenecks: {len(critical_bottlenecks)} skills blocking multiple transitions",
                f"Investment priority: {bottlenecks[0]['skill_name'] if bottlenecks else 'No major bottlenecks'}"
            ],
            'next_steps': [
                "Review individual development plans for high-potential employees",
                "Implement training programs for bottleneck skills",
                "Consider external hiring for critical gaps"
            ]
        }
    
    def _summarize_compatibility_matrix(self) -> Dict:
        """Genera resumen de la matriz de compatibilidad."""
        if not self.compatibility_matrix:
            return {}
        
        total_combinations = sum(len(roles) for roles in self.compatibility_matrix.results.values())
        ready_combinations = len(self.compatibility_matrix.get_ready_candidates())
        
        return {
            'total_employee_role_combinations': total_combinations,
            'ready_combinations': ready_combinations,
            'readiness_percentage': (ready_combinations / total_combinations * 100) if total_combinations > 0 else 0
        }
    
    def _export_compatibility_matrix_data(self) -> List[Dict]:
        """Exporta datos de matriz de compatibilidad para análisis externo."""
        if not self.compatibility_matrix:
            return []
        
        data = []
        for emp_id, roles in self.compatibility_matrix.results.items():
            employee = self.employees.get(emp_id)
            
            for role_id, result in roles.items():
                role = self.roles_catalog.get(role_id)
                
                data.append({
                    'employee_id': emp_id,
                    'employee_name': employee.nombre if employee else emp_id,
                    'role_id': role_id,
                    'role_title': role.titulo if role else role_id,
                    'overall_score': result.overall_score,
                    'band': result.band.value,
                    'skills_score': result.component_scores['skills'],
                    'responsibilities_score': result.component_scores['responsibilities'],
                    'ambitions_score': result.component_scores['ambitions'],
                    'dedication_score': result.component_scores['dedication'],
                    'gaps_count': len(result.detailed_gaps)
                })
        
        return data
    
    def _calculate_development_priority(self, gap_results: List[GapResult]) -> str:
        """Calcula prioridad de desarrollo para un empleado."""
        best_score = max(result.overall_score for result in gap_results) if gap_results else 0
        
        if best_score >= 0.8:
            return "HIGH"  # Ya está cerca de estar ready
        elif best_score >= 0.6:
            return "MEDIUM"  # Desarrollo factible
        else:
            return "LOW"  # Necesita desarrollo significativo
    
    def _should_hire_external(self, candidates: List[GapResult]) -> Dict:
        """Determina si se debería contratar externamente para un rol."""
        ready_candidates = [c for c in candidates if c.band.value in ['READY', 'READY_WITH_SUPPORT']]
        
        if len(ready_candidates) >= 2:
            return {'recommend_external': False, 'reason': 'Sufficient internal candidates'}
        elif len(ready_candidates) == 1:
            return {'recommend_external': False, 'reason': 'One strong internal candidate available'}
        else:
            return {'recommend_external': True, 'reason': 'No ready internal candidates'}
    
    def _export_csv(self) -> str:
        """Exporta resultados principales a CSV."""
        # Implementación simplificada para demo
        data = self._export_compatibility_matrix_data()
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    
    def _export_excel(self) -> str:
        """Exporta resultados a Excel con múltiples hojas."""
        # Implementación simplificada para demo  
        return "Excel export functionality - to be implemented with pandas ExcelWriter"