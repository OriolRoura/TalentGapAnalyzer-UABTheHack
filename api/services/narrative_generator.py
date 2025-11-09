"""
AI Narrative Generator
======================

Genera narrativas automáticas inteligentes usando LLMs para:
- Análisis individuales de empleados
- Narrativas por departamento/chapter
- Executive summaries a nivel empresa

Utiliza prompts estructurados para asegurar coherencia y accionabilidad.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add algorithm path for Samya's advanced analytics
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.append(str(parent_path))

from models.ai_models import (
    AIGeneratedNarrative, ExecutiveInsight, CompanyExecutiveSummary,
    NarrativeTone, AIMetadata, ConfidenceLevel, ReasoningType
)
from services.ai_service import AIService, AIResponse
from services.bias_detector import BiasDetector
from services.data_loader import data_loader

# Import Samya's advanced gap analysis
try:
    from algorithm.gap_analyzer import GapAnalyzer
    from algorithm.models import CompatibilityMatrix, Employee as AlgoEmployee, Role as AlgoRole, Skill as AlgoSkill
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False
    print("⚠️ Advanced gap analytics not available")


class NarrativeGenerator:
    """
    Generador de narrativas automáticas usando IA.
    """
    
    def __init__(self, ai_service: AIService, bias_detector: BiasDetector):
        """
        Args:
            ai_service: Servicio de IA configurado
            bias_detector: Detector de sesgos
        """
        self.ai_service = ai_service
        self.bias_detector = bias_detector
    
    def generate_employee_narrative(self,
                                   employee_id: str,
                                   gap_results: List[Dict],
                                   tone: NarrativeTone = NarrativeTone.ANALYTICAL) -> AIGeneratedNarrative:
        """
        Genera narrativa personalizada para un empleado.
        
        Args:
            employee_id: ID del empleado
            gap_results: Resultados de gap analysis
            tone: Tono de la narrativa
            
        Returns:
            Narrativa generada
        """
        # Obtener datos del empleado
        employees = data_loader.get_employees()
        emp_id = int(employee_id) if isinstance(employee_id, str) else employee_id
        if emp_id not in employees:
            raise ValueError(f"Employee {employee_id} not found")
        
        employee = employees[emp_id]
        
        # Construir contexto
        context = self._build_employee_context(employee, gap_results)
        
        # Construir prompt
        prompt = self._build_employee_narrative_prompt(context, tone)
        system_prompt = self.bias_detector.create_bias_free_prompt_template('narrative')
        
        # Validar prompt
        validation = self.bias_detector.validate_prompt(prompt)
        if not validation['is_valid']:
            print(f"⚠️ Prompt tiene warnings: {validation['warnings']}")
        
        # Try structured output first (uses default provider - OpenAI)
        try:
            from models.ai_models import StructuredNarrative
            print(f"📝 Generating narrative with STRUCTURED OUTPUT...")
            
            structured_response = self.ai_service.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                response_schema=StructuredNarrative,
                temperature=0.7
            )
            
            print(f"✅ Structured narrative generated successfully")
            
            # Convert to narrative_data format
            narrative_data = {
                'title': structured_response['title'],
                'executive_summary': structured_response['executive_summary'],
                'detailed_analysis': f"{structured_response['current_situation']}\n\n{structured_response['gap_analysis']}\n\n{structured_response['opportunities']}\n\n{structured_response['challenges']}",
                'recommendations_summary': structured_response['recommended_path'],
                'key_insights': structured_response['key_takeaways'],
                'trends': []
            }
            
            # Create mock response for metadata
            from services.ai_service import AIResponse
            response = AIResponse(
                content=str(structured_response),
                model='gemini-2.5-pro',
                provider='google',
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                latency_ms=0.0
            )
            
        except Exception as e:
            print(f"⚠️ Structured output failed: {type(e).__name__}: {e}")
            print(f"   Falling back to text-based generation...")
            
            # Fallback to text-based generation
            response = self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=3000,
                request_type='narrative'
            )
            
            # Parsear respuesta
            narrative_data = self._parse_narrative_response(response.content)
        
        # Validar sesgos en respuesta
        bias_check = self.bias_detector.detect_bias(response.content)
        
        # Construir narrativa
        narrative = AIGeneratedNarrative(
            id=f"NAR-EMP-{employee_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=narrative_data.get('title', f"Análisis de Talent Gap - {employee.nombre}"),
            scope='employee',
            scope_id=employee_id,
            executive_summary=narrative_data.get('executive_summary', ''),
            key_insights=narrative_data.get('key_insights', []),
            detailed_analysis=narrative_data.get('detailed_analysis', ''),
            recommendations_summary=narrative_data.get('recommendations_summary', ''),
            supporting_data={
                'employee_name': employee.nombre,
                'current_chapter': employee.chapter,
                'num_gap_results': len(gap_results),
                'best_role_score': max([r.get('overall_score', 0) for r in gap_results]) if gap_results else 0
            },
            trends_identified=narrative_data.get('trends', []),
            tone=tone,
            ai_metadata=AIMetadata(
                model_used=response.model,
                provider=response.provider,
                confidence_level=ConfidenceLevel.HIGH if not bias_check['has_bias'] else ConfidenceLevel.MEDIUM,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace=f"Generated narrative for employee {employee_id} based on {len(gap_results)} gap results",
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
                bias_check_passed=not bias_check['has_bias'],
                human_review_required=bias_check['requires_human_review']
            )
        )
        
        return narrative
    
    def generate_department_narrative(self,
                                     chapter: str,
                                     tone: NarrativeTone = NarrativeTone.EXECUTIVE) -> AIGeneratedNarrative:
        """
        Genera narrativa para un departamento/chapter.
        
        Args:
            chapter: ID del chapter
            tone: Tono de la narrativa
            
        Returns:
            Narrativa generada
        """
        from services.gap_service import GapAnalysisService
        
        # Obtener datos del departamento
        employees = data_loader.get_employees()
        roles = data_loader.get_roles()
        
        # Filtrar empleados del chapter
        chapter_employees = {
            emp_id: emp for emp_id, emp in employees.items()
            if emp.chapter == chapter
        }
        
        if not chapter_employees:
            raise ValueError(f"No employees found in chapter {chapter}")
        
        # Obtener roles del chapter (usar 'capitulo' que es el nombre del campo en el modelo)
        chapter_roles = {
            role_id: role for role_id, role in roles.items()
            if role.capitulo == chapter
        }
        
        # Calculate gap analysis for all employees in this chapter
        gap_service = GapAnalysisService()
        chapter_gap_results = {}
        
        print(f"📊 Calculating gap analysis for {len(chapter_employees)} employees in {chapter}...")
        for emp_id in chapter_employees.keys():
            try:
                gap_matrix = gap_service.calculate_employee_gap_matrix(emp_id)
                chapter_gap_results[emp_id] = gap_matrix
            except Exception as e:
                print(f"⚠️ Error calculating gap for employee {emp_id}: {e}")
        
        # Construir contexto agregado CON DATOS REALES
        context = self._build_department_context(chapter, chapter_employees, chapter_roles, chapter_gap_results)
        
        # Construir prompt
        prompt = self._build_department_narrative_prompt(context, tone)
        system_prompt = self.bias_detector.create_bias_free_prompt_template('narrative')
        
        # Generar con IA
        response = self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3500,  # Aumentado para narrativas departamentales más completas
            request_type='narrative'  # Cache TTL: 1 hour
        )
        
        # Parsear respuesta
        narrative_data = self._parse_narrative_response(response.content)
        
        # Validar sesgos
        bias_check = self.bias_detector.detect_bias(response.content)
        
        # Construir narrativa
        narrative = AIGeneratedNarrative(
            id=f"NAR-DEPT-{chapter}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=narrative_data.get('title', f"Análisis de Talent Gap - Departamento {chapter}"),
            scope='department',
            scope_id=chapter,
            executive_summary=narrative_data.get('executive_summary', ''),
            key_insights=narrative_data.get('key_insights', []),
            detailed_analysis=narrative_data.get('detailed_analysis', ''),
            recommendations_summary=narrative_data.get('recommendations_summary', ''),
            supporting_data=context['metrics'],
            trends_identified=narrative_data.get('trends', []),
            future_outlook=narrative_data.get('future_outlook'),
            tone=tone,
            ai_metadata=AIMetadata(
                model_used=response.model,
                provider=response.provider,
                confidence_level=ConfidenceLevel.HIGH if not bias_check['has_bias'] else ConfidenceLevel.MEDIUM,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace=f"Generated narrative for chapter {chapter} with {len(chapter_employees)} employees",
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
                bias_check_passed=not bias_check['has_bias'],
                human_review_required=bias_check['requires_human_review']
            )
        )
        
        return narrative
    
    def generate_company_executive_summary(self) -> CompanyExecutiveSummary:
        """
        Genera resumen ejecutivo completo de la empresa.
        
        Returns:
            Resumen ejecutivo con narrativa, insights y métricas
        """
        from services.gap_service import GapAnalysisService
        
        # Obtener todos los datos
        employees = data_loader.get_employees()
        roles = data_loader.get_roles()
        
        # Calculate actual gap analysis for all employees
        gap_service = GapAnalysisService()
        all_gap_results = {}
        
        print(f"📊 Calculating gap analysis for {len(employees)} employees...")
        for emp_id, employee in employees.items():
            try:
                gap_matrix = gap_service.calculate_employee_gap_matrix(emp_id)
                all_gap_results[emp_id] = gap_matrix
            except Exception as e:
                print(f"⚠️ Error calculating gap for employee {emp_id}: {e}")
        
        # Construir contexto global CON DATOS REALES
        context = self._build_company_context(employees, roles, all_gap_results)
        
        # Construir prompt
        prompt = self._build_company_narrative_prompt(context)
        system_prompt = self.bias_detector.create_bias_free_prompt_template('narrative')
        
        # Try structured output first
        from models.ai_models import StructuredCompanyExecutiveSummary
        
        print(f"📝 Generating company executive summary with STRUCTURED OUTPUT...")
        try:
            structured_response = self.ai_service.generate_structured(
                prompt=prompt,
                response_schema=StructuredCompanyExecutiveSummary,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            print(f"✅ Structured company executive summary generated successfully")
            
            # Convert structured response to dict
            narrative_data = {
                'title': structured_response['title'],
                'executive_summary': structured_response['executive_summary'],
                'key_insights': structured_response['key_insights'],
                'detailed_analysis': structured_response['detailed_analysis'],
                'recommendations_summary': structured_response['recommendations_summary'],
                'trends': structured_response['trends'],
                'future_outlook': structured_response['future_outlook'],
                'org_recommendations': structured_response['org_recommendations'],
                'investment_priorities': [
                    {
                        'area': ip['area'],
                        'priority': ip['priority'],
                        'rationale': ip['rationale']
                    }
                    for ip in structured_response.get('investment_priorities', [])
                ]
            }
            
            # Build AI metadata for structured response
            provider = self.ai_service.default_provider
            model_used = self.ai_service._get_default_model(provider)
            
            ai_metadata = AIMetadata(
                model_used=model_used,
                provider=provider,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace='Generated via structured output schema',
                bias_check_passed=True,
                human_review_required=False
            )
            
            # No need for bias check on structured output (no free text)
            use_structured = True
            
        except Exception as e:
            print(f"⚠️ Structured output failed: {e}")
            print(f"   Falling back to text parsing...")
            
            # Fallback to text-based generation
            response = self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=4000,
                request_type='summary'
            )
            
            # Parsear respuesta
            narrative_data = self._parse_narrative_response(response.content)
            
            # Validar sesgos
            bias_check = self.bias_detector.detect_bias(response.content)
            
            # Build AI metadata from response
            ai_metadata = AIMetadata(
                model_used=response.model,
                provider=response.provider,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace=f"Company-wide analysis with {len(employees)} employees and {len(roles)} roles",
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
                bias_check_passed=not bias_check['has_bias'],
                human_review_required=bias_check['requires_human_review']
            )
            
            use_structured = False
        
        # Crear narrativa principal (using ai_metadata built above)
        main_narrative = AIGeneratedNarrative(
            id=f"NAR-COMPANY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="Executive Summary - Talent Gap Analysis",
            scope='company',
            executive_summary=narrative_data.get('executive_summary', ''),
            key_insights=narrative_data.get('key_insights', []),
            detailed_analysis=narrative_data.get('detailed_analysis', ''),
            recommendations_summary=narrative_data.get('recommendations_summary', ''),
            supporting_data=context['metrics'],
            trends_identified=narrative_data.get('trends', []),
            future_outlook=narrative_data.get('future_outlook'),
            tone=NarrativeTone.EXECUTIVE,
            ai_metadata=ai_metadata
        )
        
        # Generar insights ejecutivos
        key_insights = self._generate_executive_insights(context)
        
        # Construir summary completo
        summary = CompanyExecutiveSummary(
            total_employees=len(employees),
            total_roles=len(roles),
            overall_readiness_score=context['metrics']['overall_readiness_score'],
            narrative=main_narrative,
            key_insights=key_insights,
            department_metrics=context['metrics']['by_chapter'],
            critical_skill_gaps=context['critical_gaps']['skills'][:5],
            critical_bottlenecks=context['critical_gaps']['bottlenecks'][:5],
            organizational_recommendations=narrative_data.get('org_recommendations', []),
            investment_priorities=narrative_data.get('investment_priorities', []),
            ai_metadata=main_narrative.ai_metadata
        )
        
        return summary
    
    def _build_employee_context(self, employee, gap_results: List[Dict]) -> Dict:
        """Construye contexto para narrativa de empleado."""
        return {
            'employee': {
                'id': employee.id_empleado,
                'nombre': employee.nombre,
                'chapter': employee.chapter,
                'skills_count': len(employee.habilidades),
                'ambiciones': employee.ambiciones.especialidades_preferidas[:3] if employee.ambiciones.especialidades_preferidas else []
            },
            'gap_analysis': {
                'num_roles_analyzed': len(gap_results),
                'best_role': max(gap_results, key=lambda x: x.get('overall_score', 0)) if gap_results else None,
                'ready_roles': [r for r in gap_results if r.get('band') == 'READY'],
                'near_roles': [r for r in gap_results if r.get('band') == 'NEAR']
            }
        }
    
    def _build_department_context(self, chapter: str, employees: Dict, roles: Dict, gap_results: Dict) -> Dict:
        """Construye contexto agregado para departamento CON DATOS REALES de gap analysis."""
        # Calculate real metrics from gap analysis
        total_ready = 0
        role_demand = {}
        skill_gaps = {}
        
        for emp_id, gap_matrix in gap_results.items():
            # Count ready roles
            ready_roles = [r for r in gap_matrix.role_matches if r.band in ['READY', 'READY_WITH_SUPPORT']]
            if ready_roles:
                total_ready += 1
            
            # Track role demand (which roles employees are ready for)
            for role_match in gap_matrix.role_matches:
                if role_match.band in ['READY', 'READY_WITH_SUPPORT']:
                    role_id = role_match.role_id
                    if role_id not in role_demand:
                        role_demand[role_id] = {'ready_count': 0, 'avg_score': 0.0}
                    role_demand[role_id]['ready_count'] += 1
                    role_demand[role_id]['avg_score'] += role_match.overall_score
            
            # Aggregate skill gaps from role scores
            for role_match in gap_matrix.role_matches[:2]:  # Top 2 roles per employee
                # Use skill score as proxy for gap detection
                if role_match.skills_score < 0.7:  # Significant skill gap
                    gap_key = f"{role_match.role_title}_skills"
                    if gap_key not in skill_gaps:
                        skill_gaps[gap_key] = {'count': 0, 'avg_gap': 0.0}
                    gap_percentage = (1.0 - role_match.skills_score) * 100
                    skill_gaps[gap_key]['count'] += 1
                    skill_gaps[gap_key]['avg_gap'] += gap_percentage
        
        # Calculate averages for role demand
        for role_id in role_demand:
            if role_demand[role_id]['ready_count'] > 0:
                role_demand[role_id]['avg_score'] /= role_demand[role_id]['ready_count']
        
        # Identify critical skill gaps
        critical_skills = []
        for skill_name, data in skill_gaps.items():
            avg_gap = data['avg_gap'] / data['count'] if data['count'] > 0 else 0
            critical_skills.append({
                'skill_name': skill_name,
                'affected_employees': data['count'],
                'avg_gap_score': round(avg_gap, 2)
            })
        critical_skills.sort(key=lambda x: x['avg_gap_score'] * x['affected_employees'], reverse=True)
        
        readiness_rate = total_ready / len(employees) if employees else 0.0
        
        return {
            'chapter': chapter,
            'num_employees': len(employees),
            'num_roles': len(roles),
            'metrics': {
                'avg_skills_per_employee': sum(len(e.habilidades) for e in employees.values()) / len(employees) if employees else 0,
                'readiness_rate': round(readiness_rate, 3),
                'employees_ready': total_ready,
                'roles_list': list(roles.keys())[:5],  # Top 5 roles
                'most_demanded_roles': sorted(
                    [(rid, data['ready_count'], round(data['avg_score'], 3)) 
                     for rid, data in role_demand.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                'critical_skill_gaps': critical_skills[:5]
            },
            'gap_analysis_summary': {
                'employees_analyzed': len(gap_results),
                'total_role_matches': sum(len(gm.role_matches) for gm in gap_results.values())
            }
        }
    
    def _build_company_context(self, employees: Dict, roles: Dict, all_gap_results: Dict) -> Dict:
        """Construye contexto global de la empresa CON DATOS REALES de gap analysis + VISIÓN FUTURA."""
        # Get future roles and vision data
        future_roles = data_loader.get_future_roles()
        current_roles = data_loader.get_current_roles()
        vision_data = data_loader.data_store.vision_data or {}
        
        # Agrupar por chapter
        by_chapter = {}
        for emp in employees.values():
            chapter = emp.chapter
            if chapter not in by_chapter:
                by_chapter[chapter] = []
            by_chapter[chapter].append(emp)
        
        # Calculate REAL metrics from gap analysis
        total_ready_count = 0
        total_employees_analyzed = 0
        chapter_readiness = {}
        skill_gap_counts = {}
        future_role_readiness = {}  # NEW: Track readiness for future roles specifically
        
        for emp_id, gap_matrix in all_gap_results.items():
            total_employees_analyzed += 1
            employee = employees.get(emp_id)
            if not employee:
                continue
            
            chapter = employee.chapter
            if chapter not in chapter_readiness:
                chapter_readiness[chapter] = {'ready': 0, 'total': 0, 'avg_score': 0.0}
            
            # Count ready roles for this employee
            ready_roles = [r for r in gap_matrix.role_matches if r.band in ['READY', 'READY_WITH_SUPPORT']]
            if ready_roles:
                total_ready_count += 1
                chapter_readiness[chapter]['ready'] += 1
            
            # NEW: Track readiness for future roles specifically
            for role_match in gap_matrix.role_matches:
                if role_match.role_id in future_roles:
                    if role_match.role_id not in future_role_readiness:
                        future_role_readiness[role_match.role_id] = {
                            'role_title': role_match.role_title,
                            'total_candidates': 0,
                            'ready_candidates': 0,
                            'avg_score': 0.0,
                            'best_score': 0.0
                        }
                    future_role_readiness[role_match.role_id]['total_candidates'] += 1
                    future_role_readiness[role_match.role_id]['avg_score'] += role_match.overall_score
                    future_role_readiness[role_match.role_id]['best_score'] = max(
                        future_role_readiness[role_match.role_id]['best_score'],
                        role_match.overall_score
                    )
                    if role_match.band in ['READY', 'READY_WITH_SUPPORT']:
                        future_role_readiness[role_match.role_id]['ready_candidates'] += 1
            
            chapter_readiness[chapter]['total'] += 1
            
            # Get best score
            if gap_matrix.role_matches:
                best_score = max(r.overall_score for r in gap_matrix.role_matches)
                chapter_readiness[chapter]['avg_score'] += best_score
            
            # Aggregate skill gaps from role scores
            for role_match in gap_matrix.role_matches[:3]:  # Top 3 roles
                # Use skill score as a proxy for gap detection
                # Lower skill_score means larger gap
                if role_match.skills_score < 0.7:  # Significant skill gap
                    gap_key = f"{role_match.role_title}_skills"
                    if gap_key not in skill_gap_counts:
                        skill_gap_counts[gap_key] = {'count': 0, 'avg_gap': 0.0, 'employees': set()}
                    
                    # Convert score back to gap percentage
                    gap_percentage = (1.0 - role_match.skills_score) * 100
                    skill_gap_counts[gap_key]['count'] += 1
                    skill_gap_counts[gap_key]['avg_gap'] += gap_percentage
                    skill_gap_counts[gap_key]['employees'].add(emp_id)
        
        # Calculate averages for future role readiness
        for role_id, data in future_role_readiness.items():
            if data['total_candidates'] > 0:
                data['avg_score'] /= data['total_candidates']
                data['avg_score'] = round(data['avg_score'], 3)
                data['best_score'] = round(data['best_score'], 3)
        
        # Calculate averages
        for chapter in chapter_readiness:
            if chapter_readiness[chapter]['total'] > 0:
                chapter_readiness[chapter]['avg_score'] /= chapter_readiness[chapter]['total']
                chapter_readiness[chapter]['readiness_rate'] = (
                    chapter_readiness[chapter]['ready'] / chapter_readiness[chapter]['total']
                )
        
        # Identify critical skill gaps (most common and largest gaps)
        critical_skills = []
        for skill_name, data in skill_gap_counts.items():
            avg_gap = data['avg_gap'] / data['count'] if data['count'] > 0 else 0
            critical_skills.append({
                'skill_name': skill_name,
                'affected_employees': len(data['employees']),
                'avg_gap_score': round(avg_gap, 2),
                'priority': 'HIGH' if avg_gap > 50 and len(data['employees']) > 3 else 'MEDIUM'
            })
        
        # Sort by impact (gap size * number of employees)
        critical_skills.sort(key=lambda x: x['avg_gap_score'] * x['affected_employees'], reverse=True)
        
        # Calculate overall readiness (% of employees with at least 1 ready role)
        overall_readiness_score = (total_ready_count / total_employees_analyzed) if total_employees_analyzed > 0 else 0.0
        
        # NEW: Use Samya's advanced gap analysis for critical bottlenecks
        advanced_bottlenecks = self._calculate_advanced_bottlenecks(employees, roles, all_gap_results)
        
        # Extract rich vision data from correct JSON structure
        timeline = vision_data.get('timeline', {})
        timeline_milestones = []
        kpis = {}
        risks = []
        
        for period in ['12_meses', '18_meses', '24_meses']:
            if period in timeline:
                period_data = timeline[period]
                timeline_milestones.extend(period_data.get('hitos', []))
                if 'kpis_objetivo' in period_data:
                    kpis[period] = period_data['kpis_objetivo']
                risks.extend(period_data.get('riesgos_clave', []))
        
        # Get strategic priorities (critical + desirable)
        prioridades = vision_data.get('prioridades', {})
        critical_priorities = prioridades.get('critico', [])
        desirable_priorities = prioridades.get('deseable', [])
        
        # Get transformations with full context
        transformations = vision_data.get('transformaciones', [])
        transformation_details = [
            {
                'area': t.get('área', ''),
                'change': t.get('cambio', ''),
                'impact': t.get('impacto_esperado', ''),
                'kpis': t.get('kpis', [])
            } for t in transformations
        ]
        
        return {
            'total_employees': len(employees),
            'total_roles': len(roles),
            'num_chapters': len(by_chapter),
            'future_vision': {  # Rich strategic vision with correct JSON structure
                'total_future_roles': len(future_roles),
                'total_current_roles': len(current_roles),
                'horizon': '12-24 meses',
                'organization': vision_data.get('organization', {}).get('descripcion', ''),
                'timeline_milestones': timeline_milestones,  # All milestones across periods
                'kpis_12m': kpis.get('12_meses', {}),
                'kpis_18m': kpis.get('18_meses', {}),
                'kpis_24m': kpis.get('24_meses', {}),
                'critical_priorities': critical_priorities,  # 5 critical priorities from JSON
                'desirable_priorities': desirable_priorities,  # 4 desirable priorities from JSON
                'key_risks': list(set(risks)),  # Unique risks across all periods
                'transformations': transformation_details,  # Full transformation context
                'future_role_readiness': future_role_readiness
            },
            'metrics': {
                'overall_readiness_score': round(overall_readiness_score, 3),
                'employees_analyzed': total_employees_analyzed,
                'employees_with_ready_roles': total_ready_count,
                'by_chapter': {
                    ch: {
                        'employees': data['total'],
                        'ready_employees': data['ready'],
                        'readiness_rate': round(data['readiness_rate'], 3),
                        'avg_best_score': round(data['avg_score'], 3),
                        'avg_skills': sum(len(e.habilidades) for e in by_chapter[ch]) / len(by_chapter[ch])
                    } for ch, data in chapter_readiness.items()
                }
            },
            'critical_gaps': {
                'skills': critical_skills[:10],  # Top 10 critical skill gaps
                'bottlenecks': advanced_bottlenecks[:10]  # Use Samya's advanced calculation
            },
            'gap_analysis_summary': {
                'total_gaps_analyzed': sum(len(gm.role_matches) for gm in all_gap_results.values()),
                'avg_roles_per_employee': sum(len(gm.role_matches) for gm in all_gap_results.values()) / len(all_gap_results) if all_gap_results else 0
            }
        }
    
    def _build_employee_narrative_prompt(self, context: Dict, tone: NarrativeTone) -> str:
        """Construye prompt para narrativa de empleado."""
        employee = context['employee']
        gap_analysis = context['gap_analysis']
        
        prompt = f"""
Genera una narrativa profesional de análisis de talent gap para el siguiente empleado:

EMPLEADO:
- ID: {employee['id']}
- Chapter actual: {employee['chapter']}
- Número de skills: {employee['skills_count']}
- Ambiciones: {', '.join(employee['ambiciones']) if employee['ambiciones'] else 'No especificadas'}

ANÁLISIS DE GAPS:
- Roles analizados: {gap_analysis['num_roles_analyzed']}
- Roles READY: {len(gap_analysis['ready_roles'])}
- Roles NEAR: {len(gap_analysis['near_roles'])}

TONO: {tone.value}

FORMATO REQUERIDO (JSON):
{{
    "title": "Título conciso y profesional",
    "executive_summary": "Resumen ejecutivo de 2-3 párrafos sobre la situación actual del empleado, sus fortalezas, y oportunidades identificadas",
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "detailed_analysis": "Análisis detallado de los gaps identificados, explicando las áreas de desarrollo prioritarias",
    "recommendations_summary": "Resumen de las recomendaciones clave para cerrar gaps",
    "trends": ["Trend 1", "Trend 2"]
}}

IMPORTANTE:
- Ser específico y accionable
- Basar análisis SOLO en datos proporcionados
- NO hacer suposiciones sobre características personales
- Mantener tono profesional y motivador
- Resaltar tanto fortalezas como áreas de desarrollo
"""
        return prompt
    
    def _build_department_narrative_prompt(self, context: Dict, tone: NarrativeTone) -> str:
        """Construye prompt para narrativa de departamento."""
        metrics = context['metrics']
        gap_summary = context.get('gap_analysis_summary', {})
        
        # Format most demanded roles
        demanded_roles_str = "\n".join([
            f"  - {role_id}: {count} employees ready (avg score: {score})"
            for role_id, count, score in metrics.get('most_demanded_roles', [])
        ]) if metrics.get('most_demanded_roles') else "  (No data)"
        
        # Format critical skill gaps
        skill_gaps_str = "\n".join([
            f"  - {sg['skill_name']}: {sg['affected_employees']} employees affected (avg gap: {sg['avg_gap_score']})"
            for sg in metrics.get('critical_skill_gaps', [])
        ]) if metrics.get('critical_skill_gaps') else "  (No critical gaps)"
        
        prompt = f"""
Genera una narrativa ejecutiva sobre el estado del talent pipeline del departamento:

DEPARTAMENTO: {context['chapter']}
- Empleados: {context['num_employees']}
- Roles disponibles: {context['num_roles']}
- Skills promedio por empleado: {metrics['avg_skills_per_employee']:.1f}

GAP ANALYSIS RESULTS:
- Readiness rate: {metrics['readiness_rate']*100:.1f}% ({metrics['employees_ready']}/{context['num_employees']} employees ready)
- Total role matches analyzed: {gap_summary.get('total_role_matches', 0)}

MOST DEMANDED ROLES (employees ready for):
{demanded_roles_str}

CRITICAL SKILL GAPS:
{skill_gaps_str}

TONO: {tone.value}

FORMATO REQUERIDO (JSON):
{{
    "title": "Título ejecutivo",
    "executive_summary": "Resumen ejecutivo sobre el estado del departamento, capacidad actual vs. futura",
    "key_insights": ["Insight estratégico 1", "Insight 2", "Insight 3"],
    "detailed_analysis": "Análisis detallado de gaps, fortalezas, y oportunidades del departamento",
    "recommendations_summary": "Recomendaciones estratégicas para el departamento",
    "trends": ["Tendencia identificada 1", "Tendencia 2"],
    "future_outlook": "Perspectiva futura y recomendaciones estratégicas"
}}

Enfócate en:
- Capacidad del departamento para cubrir roles futuros
- Gaps críticos que requieren atención
- Fortalezas a capitalizar
- Recomendaciones estratégicas (hiring, training, desarrollo)
"""
        return prompt
    
    def _build_company_narrative_prompt(self, context: Dict) -> str:
        """Construye prompt para narrativa ejecutiva de empresa CON VISIÓN FUTURA."""
        metrics = context['metrics']
        critical_gaps = context['critical_gaps']
        gap_summary = context.get('gap_analysis_summary', {})
        future_vision = context.get('future_vision', {})
        
        # Format chapter breakdown
        chapter_breakdown = "\n".join([
            f"  - {ch}: {data['employees']} employees, {data['readiness_rate']*100:.1f}% ready, avg score: {data['avg_best_score']:.3f}"
            for ch, data in metrics['by_chapter'].items()
        ])
        
        # Format top critical skills
        critical_skills_str = "\n".join([
            f"  - {sg['skill_name']}: {sg['affected_employees']} employees, avg gap: {sg['avg_gap_score']}"
            for sg in critical_gaps['skills'][:5]
        ])
        
        # Format bottlenecks (now with advanced analytics from Samya)
        bottleneck_list = []
        for b in critical_gaps['bottlenecks'][:8]:
            if 'description' in b:
                bottleneck_list.append(f"  - {b['description']}")
            else:
                skill_name = b.get('skill_name', 'Unknown')
                priority = b.get('priority', 'MEDIUM')
                bottleneck_list.append(f"  - {skill_name}: {priority} priority")
        bottlenecks_str = "\n".join(bottleneck_list)
        
        # NEW: Format future role readiness
        future_roles_readiness = future_vision.get('future_role_readiness', {})
        future_roles_str = "\n".join([
            f"  - {data['role_title']}: {data['ready_candidates']}/{data['total_candidates']} candidates ready (avg score: {data['avg_score']:.3f})"
            for role_id, data in sorted(future_roles_readiness.items(), key=lambda x: x[1]['ready_candidates'], reverse=True)[:8]
        ]) if future_roles_readiness else "  No se ha calculado readiness para roles futuros"
        
        # NEW: Format strategic priorities
        priorities_str = "\n".join([f"  - {p}" for p in future_vision.get('strategic_priorities', [])[:5]])
        if not priorities_str:
            priorities_str = "  No se han definido prioridades estratégicas"
        
        prompt = f"""
Genera un EXECUTIVE SUMMARY completo del estado del talent gap en la organización:

ORGANIZACIÓN ACTUAL:
- Total empleados: {context['total_employees']}
- Total roles definidos: {context['total_roles']} ({future_vision.get('total_current_roles', 0)} actuales, {future_vision.get('total_future_roles', 0)} futuros)
- Chapters/Departamentos: {context['num_chapters']}
- Employees analyzed: {metrics['employees_analyzed']}
- Employees with at least 1 ready role: {metrics['employees_with_ready_roles']} ({metrics['overall_readiness_score']*100:.1f}%)

VISIÓN FUTURA DE LA EMPRESA:
- Organización: {future_vision.get('organization', 'Quether Consulting')}
- Horizonte temporal: {future_vision.get('horizon', '12-24 meses')}
- Roles futuros necesarios: {future_vision.get('total_future_roles', 0)}

PRIORIDADES ESTRATÉGICAS CRÍTICAS:
{chr(10).join([f"  {i+1}. {p}" for i, p in enumerate(future_vision.get('critical_priorities', []))])}

PRIORIDADES DESEABLES:
{chr(10).join([f"  • {p}" for p in future_vision.get('desirable_priorities', [])])}

HITOS CLAVE (próximos 12-24 meses):
{chr(10).join([f"  • {h}" for h in future_vision.get('timeline_milestones', [])[:5]])}

TRANSFORMACIONES EN CURSO:
{chr(10).join([f"  • {t['area']}: {t['change']}" + (f" (Impacto: {t['impact']})" if t.get('impact') else '') for t in future_vision.get('transformations', [])[:4]])}

RIESGOS CLAVE A MITIGAR:
{chr(10).join([f"  ⚠️ {r}" for r in future_vision.get('key_risks', [])])}

KPIs OBJETIVO 12 MESES:
{chr(10).join([f"  • {k}: {v}" for k, v in future_vision.get('kpis_12m', {}).items()])}

KPIs OBJETIVO 24 MESES:
{chr(10).join([f"  • {k}: {v}" for k, v in future_vision.get('kpis_24m', {}).items()])}

READINESS PARA ROLES FUTUROS (Top 8):
{future_roles_str}

GAP ANALYSIS SUMMARY:
- Total gaps analyzed: {gap_summary.get('total_gaps_analyzed', 0)}
- Avg roles analyzed per employee: {gap_summary.get('avg_roles_per_employee', 0):.1f}

CHAPTER BREAKDOWN (Readiness):
{chapter_breakdown}

TOP 5 CRITICAL SKILL GAPS:
{critical_skills_str}

CRITICAL BOTTLENECKS (Skills que bloquean múltiples transiciones):
{bottlenecks_str}

**IMPORTANTE sobre BOTTLENECKS**: Estos son los skills críticos que están bloqueando a múltiples candidatos viables 
de avanzar a roles específicos. Cada bottleneck representa un skill gap que afecta a varios empleados que de otra 
manera estarían listos para promoción. La prioridad indica cuán crítico es para la estrategia de la empresa.

FORMATO REQUERIDO (JSON):
{{
    "title": "Executive Summary - Talent Gap Analysis",
    "executive_summary": "Resumen ejecutivo de alto nivel sobre el estado organizacional, readiness para el futuro, y prioridades estratégicas (3-4 párrafos)",
    "key_insights": ["Insight estratégico crítico 1", "Insight 2", "Insight 3", "Insight 4"],
    "detailed_analysis": "Análisis detallado del talent pipeline organizacional, identificando patterns, fortalezas, y gaps críticos",
    "recommendations_summary": "Recomendaciones estratégicas prioritarias para el liderazgo",
    "trends": ["Tendencia organizacional 1", "Tendencia 2", "Tendencia 3"],
    "future_outlook": "Perspectiva futura y recomendaciones estratégicas de largo plazo",
    "org_recommendations": ["Recomendación organizacional 1", "Recomendación 2", "Recomendación 3"],
    "investment_priorities": [
        {{"area": "Training Programs", "priority": "HIGH", "rationale": "Razón"}},
        {{"area": "External Hiring", "priority": "MEDIUM", "rationale": "Razón"}}
    ]
}}

Este resumen será leído por el C-level. Debe ser:
- Estratégico y de alto nivel, alineado con las PRIORIDADES CRÍTICAS de la empresa
- Basado en datos y métricas REALES proporcionados arriba
- Accionable con próximos pasos claros que apoyen los HITOS CLAVE
- Balanceado (oportunidades Y riesgos, incluyendo los RIESGOS CLAVE mencionados)
- **CRÍTICO**: Enfocarse en la READINESS para los ROLES FUTUROS, no solo roles actuales
- Analizar si la empresa está preparada para las TRANSFORMACIONES EN CURSO
- Identificar gaps críticos que pueden frenar los KPIs OBJETIVO (12m y 24m)
- Conectar los bottlenecks de skills con las necesidades de las transformaciones
- Priorizar recomendaciones según las PRIORIDADES ESTRATÉGICAS CRÍTICAS
- Evaluar si la organización tiene el talento necesario para ejecutar el plan estratégico

CONTEXTO IMPORTANTE:
La empresa está en proceso de transformación hacia profesionalización, digitalización y crecimiento.
Las prioridades críticas (CRM, PMO, productización, contrataciones clave) son BLOQUEANTES.
Los gaps en roles futuros clave como {', '.join([r for r in list(future_roles_readiness.keys())[:3]])} 
pueden retrasar significativamente los KPIs objetivo.
"""
        return prompt
    
    def _parse_narrative_response(self, response_text: str) -> Dict:
        """Parsea respuesta de la IA en formato JSON."""
        try:
            # Clean up markdown code blocks if present
            cleaned_text = response_text.strip()
            
            # Remove markdown code block markers (```json or ``` at start/end)
            if cleaned_text.startswith('```'):
                # Find the first newline after opening ```
                first_newline = cleaned_text.find('\n')
                if first_newline != -1:
                    cleaned_text = cleaned_text[first_newline + 1:]
                
                # Remove closing ```
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                
                cleaned_text = cleaned_text.strip()
            
            # Intentar parsear JSON directamente
            if cleaned_text.startswith('{'):
                return json.loads(cleaned_text)
            
            # Buscar JSON dentro del texto
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = cleaned_text[start:end]
                return json.loads(json_str)
            
            # Fallback: estructura básica
            return {
                'title': 'Análisis de Talent Gap',
                'executive_summary': response_text[:500],
                'key_insights': ['Análisis generado por IA'],
                'detailed_analysis': response_text,
                'recommendations_summary': 'Ver análisis detallado',
                'trends': []
            }
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse narrative JSON: {e}")
            # Fallback si no se puede parsear
            return {
                'title': 'Análisis de Talent Gap',
                'executive_summary': response_text[:500],
                'key_insights': ['Análisis generado por IA'],
                'detailed_analysis': response_text,
                'recommendations_summary': 'Ver análisis detallado',
                'trends': []
            }
    
    def _generate_executive_insights(self, context: Dict) -> List[ExecutiveInsight]:
        """Genera insights ejecutivos de alto nivel."""
        # Placeholder - en producción se generarían con IA también
        insights = []
        
        # Ejemplo de insight
        insights.append(ExecutiveInsight(
            insight_type='opportunity',
            title='Alta capacidad de movilidad interna',
            description='El 40% de los empleados están READY o NEAR para roles de mayor responsabilidad',
            impact_level='high',
            affected_employees=int(context['total_employees'] * 0.4),
            affected_roles=['Varios roles senior'],
            strategic_recommendations=[
                'Acelerar programas de desarrollo interno',
                'Crear roles intermedios para facilitar progresión',
                'Implementar mentoring estructurado'
            ],
            urgency='short_term',
            ai_metadata=AIMetadata(
                model_used='rule-based',
                provider='internal',
                confidence_level=ConfidenceLevel.HIGH,
                reasoning_type=ReasoningType.DATA_DRIVEN,
                reasoning_trace='Based on gap analysis statistics'
            )
        ))
        
        return insights
    
    def _calculate_advanced_bottlenecks(self, employees: Dict, roles: Dict, all_gap_results: Dict) -> List[Dict]:
        """
        Calcula bottlenecks críticos usando el algoritmo avanzado de Samya.
        
        Returns:
            Lista de bottlenecks críticos con métricas detalladas
        """
        if not ADVANCED_ANALYTICS_AVAILABLE:
            # Fallback to simple calculation
            print("⚠️ Advanced analytics not available, using simple bottleneck calculation")
            return self._calculate_simple_bottlenecks(all_gap_results)
        
        try:
            # Build compatibility matrix from gap results
            compatibility_matrix = self._build_compatibility_matrix_from_results(all_gap_results)
            
            # Initialize Samya's gap analyzer
            gap_analyzer = GapAnalyzer()
            
            # Get skills catalog
            skills = data_loader.get_skills()
            algo_skills = {}
            for skill_id, skill in skills.items():
                algo_skills[skill_id] = AlgoSkill(
                    id=skill.id,
                    nombre=skill.nombre,
                    categoria=skill.categoria,
                    peso=getattr(skill, 'peso', 1.0),  # Default weight
                    herramientas_asociadas=getattr(skill, 'herramientas_asociadas', [])
                )
            
            # Convert employees to algo format (needed for some analytics)
            # Convert employees to algo format using ModelAdapter to ensure field names match
            algo_employees = []
            try:
                from services.model_adapter import ModelAdapter
            except Exception:
                ModelAdapter = None

            for emp_id, emp in employees.items():
                try:
                    if ModelAdapter:
                        algo_employees.append(ModelAdapter.api_employee_to_algo(emp))
                    else:
                        # Fallback: build minimal AlgoEmployee-compatible dict/object
                        algo_employees.append(AlgoEmployee(
                            id=str(emp_id),
                            nombre=getattr(emp, 'nombre', ''),
                            chapter_actual=getattr(emp, 'chapter', getattr(emp, 'chapter_actual', '')),
                            skills={k: None for k in getattr(emp, 'habilidades', {})},
                            responsabilidades_actuales=getattr(emp, 'responsabilidades_actuales', []),
                            ambiciones=getattr(emp, 'ambiciones', []) or [] ,
                            dedicacion_actual=getattr(emp, 'dedicacion_actual', 'full-time')
                        ))
                except Exception as e:
                    print(f"⚠️ Could not convert employee {emp_id} to algo model: {e}")
            
            # Convert roles to algo format using ModelAdapter when available
            algo_roles = {}
            try:
                from services.model_adapter import ModelAdapter
            except Exception:
                ModelAdapter = None

            for role_id, role in roles.items():
                try:
                    if ModelAdapter:
                        algo_roles[role_id] = ModelAdapter.api_role_to_algo(role, data_loader.get_skills())
                    else:
                        algo_roles[role_id] = AlgoRole(
                            id=role.id,
                            titulo=getattr(role, 'titulo', ''),
                            nivel=getattr(role, 'nivel', ''),
                            capitulo=getattr(role, 'capitulo', ''),
                            habilidades_requeridas=getattr(role, 'habilidades_requeridas', []),
                            responsabilidades=getattr(role, 'responsabilidades', []),
                            dedicacion_esperada=getattr(role, 'dedicacion_esperada', '40-40h')
                        )
                except Exception as e:
                    print(f"⚠️ Could not convert role {role_id} to algo model: {e}")
            
            # Calculate critical bottlenecks using Samya's algorithm
            bottlenecks = gap_analyzer.identify_bottleneck_skills(
                compatibility_matrix=compatibility_matrix,
                roles_catalog=algo_roles,
                employees=algo_employees,
                score_threshold=0.5  # Only consider viable candidates
            )
            
            # Format bottlenecks for API response
            formatted_bottlenecks = []
            for bottleneck in bottlenecks[:15]:  # Top 15 critical bottlenecks
                formatted_bottlenecks.append({
                    'type': 'skill_gap',
                    'role_id': bottleneck['role_id'],
                    'role_title': bottleneck['role_title'],
                    'skill_id': bottleneck['skill_id'],
                    'skill_name': bottleneck['skill_name'],
                    'avg_gap_percentage': round(bottleneck['avg_gap_percentage'], 2),
                    'candidates_affected': bottleneck['candidates_affected'],
                    'total_viable_candidates': bottleneck['total_viable_candidates'],
                    'criticality_score': round(bottleneck['criticality_score'], 2),
                    'priority': bottleneck['priority'],
                    'description': f"{bottleneck['role_title']}: {bottleneck['skill_name']} - {bottleneck['candidates_affected']}/{bottleneck['total_viable_candidates']} candidates affected ({bottleneck['avg_gap_percentage']:.0f}% gap)",
                    'no_viable_candidates': bottleneck.get('no_viable_candidates', False)
                })
            
            print(f"✅ Calculated {len(formatted_bottlenecks)} critical bottlenecks using advanced analytics")
            return formatted_bottlenecks
            
        except Exception as e:
            print(f"⚠️ Error calculating advanced bottlenecks: {e}")
            return self._calculate_simple_bottlenecks(all_gap_results)
    
    def _build_compatibility_matrix_from_results(self, all_gap_results: Dict) -> 'CompatibilityMatrix':
        """Construye una CompatibilityMatrix desde los resultados de gap analysis."""
        # Import algorithm models and CompatibilityMatrix
        from algorithm.models import GapResult as AlgoGapResult, GapBand as AlgoBand, CompatibilityMatrix as AlgoCompatibilityMatrix

        # Build a plain results dict first: employee_id -> role_id -> AlgoGapResult
        results: Dict[str, Dict[str, AlgoGapResult]] = {}

        # Convert our gap results to algo format
        for emp_id, gap_matrix in all_gap_results.items():
            emp_key = str(emp_id)
            if emp_key not in results:
                results[emp_key] = {}

            for role_match in gap_matrix.role_matches:
                # Map our band to algo band
                band_mapping = {
                    'READY': AlgoBand.READY,
                    'READY_WITH_SUPPORT': AlgoBand.READY_WITH_SUPPORT,
                    'NEAR': AlgoBand.NEAR,
                    'FAR': AlgoBand.FAR,
                    'NOT_VIABLE': AlgoBand.NOT_VIABLE
                }
                algo_band = band_mapping.get(role_match.band, AlgoBand.FAR)

                # Component scores expected by algorithm GapResult
                comp_scores = {
                    'skills': getattr(role_match, 'skills_score', 0.0),
                    'responsibilities': getattr(role_match, 'responsibilities_score', 0.0),
                    'ambitions': getattr(role_match, 'ambitions_score', 0.0),
                    'dedication': getattr(role_match, 'dedication_score', 0.0)
                }

                detailed_gaps = getattr(role_match, 'detailed_gaps', []) or []
                recommendations = getattr(role_match, 'recommendations', []) or []

                # Create algo gap result using the correct dataclass signature
                algo_result = AlgoGapResult(
                    employee_id=emp_key,
                    role_id=role_match.role_id,
                    overall_score=getattr(role_match, 'overall_score', 0.0),
                    band=algo_band,
                    component_scores=comp_scores,
                    detailed_gaps=detailed_gaps,
                    recommendations=recommendations
                )

                results[emp_key][role_match.role_id] = algo_result

        # Instantiate and return the CompatibilityMatrix with the built results dict
        compatibility_matrix = AlgoCompatibilityMatrix(results=results)
        return compatibility_matrix
    
    def _calculate_simple_bottlenecks(self, all_gap_results: Dict) -> List[Dict]:
        """Fallback simple calculation when advanced analytics not available."""
        chapter_readiness = {}
        for emp_id, gap_matrix in all_gap_results.items():
            employees = data_loader.get_employees()
            employee = employees.get(emp_id)
            if not employee:
                continue
            
            chapter = employee.chapter
            if chapter not in chapter_readiness:
                chapter_readiness[chapter] = {'ready': 0, 'total': 0}
            
            ready_roles = [r for r in gap_matrix.role_matches if r.band in ['READY', 'READY_WITH_SUPPORT']]
            if ready_roles:
                chapter_readiness[chapter]['ready'] += 1
            chapter_readiness[chapter]['total'] += 1
        
        # Calculate readiness rates
        for chapter, data in chapter_readiness.items():
            if data['total'] > 0:
                data['readiness_rate'] = data['ready'] / data['total']
        # Build list of bottlenecks, filter out zero-impact chapters (no employees_not_ready)
        bottlenecks = []
        for ch, data in sorted(chapter_readiness.items(), key=lambda x: x[1]['readiness_rate']):
            employees_not_ready = data['total'] - data['ready']
            readiness_rate = data.get('readiness_rate', 0.0)

            # Skip chapters where there is no gap (all employees have at least one READY role)
            if employees_not_ready <= 0:
                continue

            # Priority mapping: lower readiness -> higher priority
            if readiness_rate < 0.3:
                priority = 'HIGH'
            elif readiness_rate < 0.7:
                priority = 'MEDIUM'
            else:
                priority = 'LOW'

            bottlenecks.append({
                'type': 'chapter_bottleneck',
                'chapter': ch,
                'employees_not_ready': employees_not_ready,
                'readiness_rate': round(readiness_rate, 3),
                'priority': priority,
                'description': f"Chapter {ch}: {employees_not_ready} employees not ready ({round((1-readiness_rate)*100, 1)}%)"
            })

            # Limit results to top 5 by worst readiness
            if len(bottlenecks) >= 5:
                break

        return bottlenecks
