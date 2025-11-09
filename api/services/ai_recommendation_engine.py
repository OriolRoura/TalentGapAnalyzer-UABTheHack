"""
AI-Enhanced Recommendation Engine
==================================

Integra IA generativa para crear recomendaciones personalizadas e inteligentes.

Modos de operación:
1. AI-ENHANCED: Usa IA para enriquecer recomendaciones basadas en reglas
2. HYBRID: Combina reglas + IA generativa
3. FALLBACK: Solo reglas si IA no disponible

Características:
- Recomendaciones contextualizadas y personalizadas
- Fallback automático a recomendaciones basadas en reglas
- Validación de sesgos en todas las recomendaciones
"""

import json
import re
from typing import Dict, List, Optional
from datetime import datetime

# Importar tipos del algorithm
import sys
from pathlib import Path
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.append(str(parent_path))

try:
    from algorithm.models import Employee, Role, Skill, GapResult, GapBand
except ImportError:
    # Fallback types si no se puede importar
    Employee = Dict
    Role = Dict
    Skill = Dict
    GapResult = Dict
    GapBand = str

from models.ai_models import (
    PersonalizedRecommendation, DevelopmentPlan, ActionItem,
    RecommendationType, EffortLevel, AIMetadata,
    ConfidenceLevel, ReasoningType, DevelopmentMilestone
)
from services.ai_service import AIService
from services.bias_detector import BiasDetector


class AIRecommendationEngine:
    """
    Motor de recomendaciones mejorado con IA generativa.
    """
    
    def __init__(self,
                 ai_service: Optional[AIService] = None,
                 bias_detector: Optional[BiasDetector] = None,
                 mode: str = 'hybrid'):
        """
        Args:
            ai_service: Servicio de IA (opcional)
            bias_detector: Detector de sesgos (opcional)
            mode: 'ai-enhanced', 'hybrid', 'fallback'
        """
        self.ai_service = ai_service
        self.bias_detector = bias_detector or BiasDetector()
        self.mode = mode
        
        # Fallback a modo fallback si no hay AI service
        if not ai_service and mode != 'fallback':
            print("⚠️ AI Service not available. Falling back to rule-based recommendations.")
            self.mode = 'fallback'
    
    def generate_personalized_recommendations(self,
                                             employee: Employee,
                                             gap_results: List[GapResult],
                                             target_role: Optional[Role] = None,
                                             max_recommendations: int = 10) -> List[PersonalizedRecommendation]:
        """
        Genera recomendaciones personalizadas para un empleado.
        
        Args:
            employee: Empleado target
            gap_results: Resultados de gap analysis
            target_role: Rol objetivo específico (opcional)
            max_recommendations: Número máximo de recomendaciones
            
        Returns:
            Lista de recomendaciones personalizadas
        """
        if self.mode == 'fallback':
            return self._generate_rule_based_recommendations(
                employee, gap_results, target_role, max_recommendations
            )
        
        # Construir contexto
        context = self._build_recommendation_context(employee, gap_results, target_role)
        
        # Generar con IA
        try:
            print(f"🤖 Generating AI recommendations for employee {context['employee'].get('id')}...")
            ai_recommendations = self._generate_ai_recommendations(context, max_recommendations)
            print(f"✅ AI generated {len(ai_recommendations)} recommendations")
            
            # Si AI no generó nada, hacer fallback a reglas
            if len(ai_recommendations) == 0:
                print(f"⚠️ AI returned 0 recommendations. Falling back to rule-based.")
                return self._generate_rule_based_recommendations(
                    employee, gap_results, target_role, max_recommendations
                )
            
            # Si modo hybrid, combinar con reglas
            if self.mode == 'hybrid':
                rule_recommendations = self._generate_rule_based_recommendations(
                    employee, gap_results, target_role, max_recommendations
                )
                ai_recommendations = self._merge_recommendations(
                    ai_recommendations, rule_recommendations
                )
            
            # Validar sesgos
            ai_recommendations = self._validate_and_filter_biases(ai_recommendations)
            print(f"✅ Returning {len(ai_recommendations)} AI recommendations after bias validation")
            
            return ai_recommendations[:max_recommendations]
        
        except Exception as e:
            print(f"⚠️ AI generation failed: {type(e).__name__}: {e}. Falling back to rules.")
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()
            return self._generate_rule_based_recommendations(
                employee, gap_results, target_role, max_recommendations
            )
    
    def generate_development_plan(self,
                                 employee: Employee,
                                 target_role: Role,
                                 gap_result: GapResult,
                                 duration_months: int = 6) -> DevelopmentPlan:
        """
        Genera plan de desarrollo completo personalizado.
        
        Args:
            employee: Empleado
            target_role: Rol objetivo
            gap_result: Resultado de gap analysis
            duration_months: Duración del plan en meses
            
        Returns:
            Plan de desarrollo estructurado
        """
        if self.mode == 'fallback' or not self.ai_service:
            return self._generate_rule_based_plan(
                employee, target_role, gap_result, duration_months
            )
        
        # Construir contexto para el plan
        context = self._build_plan_context(employee, target_role, gap_result, duration_months)
        
        # Generar plan con IA
        try:
            plan = self._generate_ai_development_plan(context)
            
            # Validar sesgos
            bias_check = self.bias_detector.detect_bias(
                json.dumps(plan.dict(), default=str)
            )
            
            plan.ai_metadata.bias_check_passed = not bias_check['has_bias']
            plan.ai_metadata.human_review_required = bias_check['requires_human_review']
            
            return plan
        
        except Exception as e:
            print(f"⚠️ AI plan generation failed: {e}. Using rule-based plan.")
            return self._generate_rule_based_plan(
                employee, target_role, gap_result, duration_months
            )
    
    def _build_recommendation_context(self,
                                     employee: Employee,
                                     gap_results: List[GapResult],
                                     target_role: Optional[Role]) -> Dict:
        """Construye contexto para generación de recomendaciones CON VISIÓN FUTURA."""
        # Import data_loader here to avoid circular import
        from services.data_loader import data_loader
        
        # Get future roles and vision data
        future_roles = data_loader.get_future_roles()
        vision_data = data_loader.data_store.vision_data or {}
        
        # Extraer datos relevantes del empleado
        ambitions_obj = getattr(employee, 'ambiciones', None)
        ambitions_data = {}
        if ambitions_obj:
            ambitions_data = {
                'especialidades_preferidas': ambitions_obj.especialidades_preferidas[:3] if ambitions_obj.especialidades_preferidas else [],
                'nivel_aspiracion': ambitions_obj.nivel_aspiracion
            }
        
        employee_data = {
            'id': getattr(employee, 'id_empleado', 'unknown'),
            'skills': self._format_skills(employee),
            'ambitions': ambitions_data,
            'current_chapter': getattr(employee, 'chapter', 'unknown')
        }
        
        # Analizar gap results
        gaps_summary = self._summarize_gaps(gap_results)
        
        # NEW: Identify which of their best roles are future roles
        future_role_ids = set(future_roles.keys())
        gaps_summary['best_future_roles'] = [
            gap_results[i] for i in range(min(3, len(gap_results)))
            if getattr(gap_results[i], 'role_id', None) in future_role_ids
        ]
        
        # Target role info
        target_role_data = None
        if target_role:
            target_role_id = getattr(target_role, 'id', 'unknown')
            is_future_role = target_role_id in future_role_ids
            target_role_data = {
                'id': target_role_id,
                'title': getattr(target_role, 'titulo', 'unknown'),
                'required_skills': getattr(target_role, 'habilidades_requeridas', []),
                'is_future_role': is_future_role,
                'strategic_importance': 'HIGH' if is_future_role else 'MEDIUM'
            }
        
        # Extract rich company vision data from correct JSON structure
        timeline = vision_data.get('timeline', {})
        timeline_horizons = []
        kpis = {}
        risks = []
        
        for period in ['12_meses', '18_meses', '24_meses']:
            if period in timeline:
                period_data = timeline[period]
                timeline_horizons.extend(period_data.get('hitos', []))
                if 'kpis_objetivo' in period_data:
                    kpis[period] = period_data['kpis_objetivo']
                risks.extend(period_data.get('riesgos_clave', []))
        
        # Get strategic priorities (critical + desirable)
        prioridades = vision_data.get('prioridades', {})
        critical_priorities = prioridades.get('critico', [])
        desirable_priorities = prioridades.get('deseable', [])
        
        # Get transformations
        transformations = vision_data.get('transformaciones', [])
        
        return {
            'employee': employee_data,
            'gaps': gaps_summary,
            'target_role': target_role_data,
            'company_vision': {  # Rich company strategic context with correct JSON keys
                'horizon': '12-24 meses',
                'timeline_milestones': timeline_horizons[:5],  # Top 5 milestones across all periods
                'kpis_12m': kpis.get('12_meses', {}),
                'kpis_24m': kpis.get('24_meses', {}),
                'critical_priorities': critical_priorities,  # 5 critical priorities
                'desirable_priorities': desirable_priorities,  # 4 desirable priorities
                'key_risks': list(set(risks))[:3],  # Top 3 unique risks
                'transformations': [
                    {
                        'area': t.get('área', ''),
                        'change': t.get('cambio', ''),
                        'impact': t.get('impacto_esperado', ''),
                        'kpis': t.get('kpis', [])
                    } for t in transformations[:4]
                ],  # Top 4 transformations with full context
                'total_future_roles': len(future_roles),
                'organization': vision_data.get('organization', {}).get('descripcion', '')
            }
        }
    
    def _build_plan_context(self,
                           employee: Employee,
                           target_role: Role,
                           gap_result: GapResult,
                           duration_months: int) -> Dict:
        """Construye contexto ENRIQUECIDO para plan de desarrollo."""
        # Extract employee details
        ambitions_obj = getattr(employee, 'ambiciones', None)
        ambitions_list = []
        if ambitions_obj:
            ambitions_list = ambitions_obj.especialidades_preferidas[:3] if ambitions_obj.especialidades_preferidas else []
        
        employee_data = {
            'id': getattr(employee, 'id_empleado', getattr(employee, 'id', 'unknown')),
            'chapter': getattr(employee, 'chapter', 'unknown'),
            'skills': self._extract_structured_skills(employee),
            'ambitions': ambitions_list,
            'skill_count': len(getattr(employee, 'habilidades', {}))
        }
        
        # Extract target role details
        target_role_data = {
            'id': getattr(target_role, 'id', 'unknown'),
            'title': getattr(target_role, 'titulo', 'unknown'),
            'chapter': getattr(target_role, 'chapter', 'unknown'),
            'required_skills': getattr(target_role, 'habilidades_requeridas', []),
            'responsibilities': getattr(target_role, 'responsabilidades', [])
        }
        
        # Extract detailed gap information
        detailed_gaps = getattr(gap_result, 'detailed_gaps', [])
        gap_summary = {
            'skill_gaps': [g for g in detailed_gaps if isinstance(g, dict) and g.get('type') == 'skill'][:5],
            'responsibility_gaps': [g for g in detailed_gaps if isinstance(g, dict) and g.get('type') == 'responsibility'][:3],
            'total_gaps': len(detailed_gaps)
        }
        
        return {
            'employee_id': employee_data['id'],
            'employee': employee_data,
            'target_role_id': target_role_data['id'],
            'target_role': target_role_data,
            'current_score': getattr(gap_result, 'overall_score', 0.5),
            'gap_band': getattr(gap_result, 'band', 'NEAR'),
            'detailed_gaps': detailed_gaps[:5],  # Keep for backward compatibility
            'gap_summary': gap_summary,
            'duration_months': duration_months
        }
    
    def _generate_ai_recommendations(self,
                                    context: Dict,
                                    max_recommendations: int) -> List[PersonalizedRecommendation]:
        """Genera recomendaciones usando IA con structured output."""
        # Import structured output schema
        from models.ai_models import RecommendationsOutput
        
        # Construir prompt
        prompt = self._build_recommendations_prompt(context, max_recommendations)
        system_prompt = self.bias_detector.create_bias_free_prompt_template('recommendations')
        
        print(f"📝 Calling AI service with STRUCTURED OUTPUT...")
        
        # Try structured output first (uses default provider - OpenAI)
        try:
            structured_response = self.ai_service.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                response_schema=RecommendationsOutput,
                temperature=0.7
            )
            
            print(f"✅ Structured output returned {len(structured_response.get('recommendations', []))} recommendations")
            
            # Convert structured response to PersonalizedRecommendation objects
            recommendations = []
            for i, rec_data in enumerate(structured_response.get('recommendations', [])[:max_recommendations]):
                try:
                    # Build AI metadata
                    from models.ai_models import AIMetadata, ConfidenceLevel, ReasoningType
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
                    
                    # Convert action items
                    from models.ai_models import ActionItem
                    action_items = [
                        ActionItem(
                            action=item['action'],
                            timeline=item['timeline'],
                            priority=item.get('priority', 'medium'),
                            resources_needed=[],
                            success_criteria=None
                        )
                        for item in rec_data.get('action_items', [])
                    ]
                    
                    # Map type string to enum (handle any format)
                    from models.ai_models import PersonalizedRecommendation, RecommendationType, EffortLevel
                    type_str = rec_data.get('type', 'skill_development').lower().replace(' ', '_')
                    try:
                        rec_type = RecommendationType(type_str)
                    except ValueError:
                        rec_type = RecommendationType.SKILL_DEVELOPMENT
                    
                    # Map effort level (handle any format)
                    effort_str = rec_data.get('effort_level', 'medium').lower().replace(' ', '_')
                    try:
                        effort = EffortLevel(effort_str)
                    except ValueError:
                        effort = EffortLevel.MEDIUM
                    
                    # Create recommendation
                    recommendation = PersonalizedRecommendation(
                        id=f"REC-AI-{context['employee']['id']}-{i+1}",
                        employee_id=str(context['employee']['id']),
                        type=rec_type,
                        title=rec_data['title'],
                        description=rec_data['description'],
                        rationale=rec_data['rationale'],
                        action_items=action_items,
                        effort_level=effort,
                        estimated_duration=rec_data['estimated_duration'],
                        expected_impact={},
                        success_probability=0.75,
                        priority_score=float(rec_data.get('priority_score', 0.5)),
                        ai_metadata=ai_metadata
                    )
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    print(f"⚠️ Failed to convert recommendation {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"✅ Created {len(recommendations)} PersonalizedRecommendation objects from structured output")
            return recommendations
            
        except Exception as e:
            print(f"⚠️ Structured output failed: {type(e).__name__}: {e}")
            print(f"   Falling back to text parsing...")
            import traceback
            traceback.print_exc()
        
        # Fallback: original text-based generation
        print(f"📝 Using fallback text-based generation...")
        response = self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000,
            request_type='recommendations'
        )
        
        print(f"✅ AI service returned response ({len(response.content)} chars, provider: {response.provider})")
        
        # Parsear respuesta
        recommendations_data = self._parse_recommendations_response(response.content)
        print(f"✅ Parsed {len(recommendations_data)} recommendations from response")
        
        # Si no hay recomendaciones parseadas pero hay contenido, algo falló
        if len(recommendations_data) == 0 and len(response.content) > 50:
            print(f"⚠️ AI returned content but parser found 0 recommendations")
            print(f"   Response starts with: {response.content[:200]}")
            print(f"   This likely means AI didn't follow JSON format")
        
        # Convertir a objetos PersonalizedRecommendation
        recommendations = []
        for i, rec_data in enumerate(recommendations_data[:max_recommendations]):
            try:
                recommendation = self._create_recommendation_from_ai(
                    rec_data, context['employee']['id'], response, i
                )
                recommendations.append(recommendation)
            except Exception as e:
                print(f"⚠️ Failed to create recommendation {i}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Created {len(recommendations)} PersonalizedRecommendation objects")
        return recommendations
    
    def _generate_ai_development_plan(self, context: Dict) -> DevelopmentPlan:
        """Genera plan de desarrollo usando IA con structured output."""
        from models.ai_models import StructuredDevelopmentPlan
        
        prompt = self._build_plan_prompt(context)
        system_prompt = self.bias_detector.create_bias_free_prompt_template('recommendations')
        
        # Try structured output first (uses default provider - OpenAI)
        try:
            print(f"📝 Generating development plan with STRUCTURED OUTPUT...")
            
            structured_response = self.ai_service.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                response_schema=StructuredDevelopmentPlan,
                temperature=0.7
            )
            
            print(f"✅ Structured development plan generated successfully")
            
            # Convert to DevelopmentPlan format
            from models.ai_models import DevelopmentPlan, DevelopmentMilestone, AIMetadata, ConfidenceLevel, ReasoningType
            
            milestones = [
                DevelopmentMilestone(
                    month=m['month'],
                    milestone=m['milestone'],
                    success_criteria=m['success_criteria'],
                    validation_method=None
                )
                for m in structured_response.get('milestones', [])
            ]
            
            provider = self.ai_service.default_provider
            model_used = self.ai_service._get_default_model(provider)
            
            # Build skill priorities from focus areas
            skill_priorities = [
                {'skill': area, 'priority': 'high'} 
                for area in structured_response.get('focus_areas', [])
            ]
            
            plan = DevelopmentPlan(
                employee_id=str(context['employee']['id']),
                target_role_id=structured_response.get('target_role', context.get('target_role', {}).get('id', 'unknown')),
                current_score=context.get('gap_result', {}).get('overall_gap_score', 0.5),
                target_score=0.8,  # Default target
                duration_months=int(structured_response.get('duration', '6').split()[0]) if structured_response.get('duration') else 6,
                milestones=milestones,
                recommendations=[],  # Will be populated separately
                skill_priorities=skill_priorities if skill_priorities else [{'skill': 'General', 'priority': 'high'}],
                estimated_cost_eur=None,
                time_investment_hours=len(structured_response.get('focus_areas', [])) * 40,  # 40h per area
                success_probability=0.75,
                risk_factors=structured_response.get('resources_needed', []),
                ai_metadata=AIMetadata(
                    model_used=model_used,
                    provider=provider,
                    confidence_level=ConfidenceLevel.HIGH,
                    reasoning_type=ReasoningType.GENERATIVE,
                    reasoning_trace='Generated via structured output schema',
                    bias_check_passed=True,
                    human_review_required=False
                )
            )
            
            return plan
            
        except Exception as e:
            print(f"⚠️ Structured output failed: {type(e).__name__}: {e}")
            print(f"   Falling back to text-based generation...")
            import traceback
            traceback.print_exc()
        
        # Fallback: original text-based generation
        response = self.ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3500,
            request_type='plan'
        )
        
        # Parsear
        plan_data = self._parse_plan_response(response.content)
        
        # Crear plan estructurado
        plan = self._create_plan_from_ai(plan_data, context, response)
        
        return plan
    
    def _build_recommendations_prompt(self, context: Dict, max_recs: int) -> str:
        """Construye prompt OPTIMIZADO para recomendaciones con visión futura."""
        employee = context['employee']
        gaps = context['gaps']
        company_vision = context.get('company_vision', {})
        target_role = context.get('target_role', {})
        
        # Determine if target is a future role
        is_future_role = target_role.get('is_future_role', False) if target_role else False
        strategic_importance = target_role.get('strategic_importance', 'MEDIUM') if target_role else 'MEDIUM'
        
        # Build CONCISE vision context (avoiding safety filters)
        vision_context = ""
        if company_vision and is_future_role:
            critical = company_vision.get('critical_priorities', [])[:2]  # Only top 2
            transformations = company_vision.get('transformations', [])[:2]  # Only top 2
            
            vision_parts = []
            if critical:
                vision_parts.append(f"Prioridades críticas empresa: {'; '.join(critical)}")
            if transformations:
                trans_compact = [f"{t['area']}" for t in transformations]
                vision_parts.append(f"Transformaciones clave: {', '.join(trans_compact)}")
            
            if vision_parts:
                vision_context = f"\n\nCONTEXTO ESTRATÉGICO:\n- Rol objetivo es FUTURO (alta prioridad)\n- {chr(10).join(['- ' + p for p in vision_parts])}"
        
        # Get top skills to develop (concise)
        top_skills = ', '.join(gaps['top_skill_gaps'][:3]) if gaps['top_skill_gaps'] else 'N/A'
        
        # Get ambitions (concise)
        ambitions = employee.get('ambitions', {})
        ambitions_str = ', '.join(ambitions.get('especialidades_preferidas', [])[:2]) if ambitions else 'No especificadas'
        
        # Check if we have minimal data
        has_minimal_data = (
            employee.get('current_chapter') not in ['unknown', None, ''] and
            len(employee.get('skills', {})) > 0
        )
        
        prompt = f"""Genera {max_recs} recomendaciones desarrollo para empleado:

PERFIL:
- Chapter: {employee['current_chapter']} | Skills: {len(employee.get('skills', {}))}
- Ambiciones: {ambitions_str}

GAP ANALYSIS:
- Rol objetivo: {gaps['best_role']} (score: {gaps['best_gap_score']:.2f})
- Skills a desarrollar: {top_skills}
- Importancia estratégica: {strategic_importance}{vision_context}

{"⚠️ DATOS LIMITADOS: Genera recomendaciones generales para desarrollo en " + employee['current_chapter'] if not has_minimal_data else ""}

FORMATO JSON (OBLIGATORIO - RESPONDE SOLO CON JSON, SIN EXPLICACIONES):
[{{"type":"skill_development","title":"Título específico <60 chars","description":"Qué hacer","rationale":"Por qué relevante","action_items":[{{"action":"Acción 1","timeline":"X semanas","resources_needed":["R1"],"success_criteria":"Medible","priority":"high"}}],"effort_level":"medium","estimated_duration":"3 meses","priority_score":0.8}}]

REQUISITOS CRÍTICOS:
1. DEVUELVE SOLO JSON - NO agregues explicaciones antes o después
2. Genera exactamente {max_recs} recomendaciones
3. Si faltan datos, usa recomendaciones genéricas de {employee['current_chapter']}
4. Alineado con ambiciones: {ambitions_str}
5. Usa solo tipos válidos: skill_development, career_progression, mentoring, training
"""
        return prompt
    
    def _build_plan_prompt(self, context: Dict) -> str:
        """Construye prompt ENRIQUECIDO para plan de desarrollo."""
        employee = context.get('employee', {})
        target_role = context.get('target_role', {})
        gap_summary = context.get('gap_summary', {})
        
        # Format skills compactly
        skills_str = ', '.join([f"{s['skill_name']} ({s['level']})" for s in employee.get('skills', [])[:8]])
        ambitions_str = ', '.join(employee.get('ambitions', []))
        
        # Format gap summary
        skill_gaps_str = '\n'.join([
            f"  • {g.get('skill_name', 'Unknown')}: actual {g.get('current_level', 0)}/10, requiere {g.get('required_level', 0)}/10"
            for g in gap_summary.get('skill_gaps', [])[:5]
        ]) if gap_summary.get('skill_gaps') else '  (No hay gaps de skills críticos)'
        
        prompt = f"""
Genera un PLAN DE DESARROLLO COMPLETO Y ESTRUCTURADO:

PERFIL DEL EMPLEADO:
- ID: {employee.get('id', 'unknown')}
- Chapter actual: {employee.get('chapter', 'unknown')}
- Skills actuales ({employee.get('skill_count', 0)}): {skills_str}
- Ambiciones profesionales: {ambitions_str if ambitions_str else 'No especificadas'}

ROL OBJETIVO:
- ID: {target_role.get('id', 'unknown')}
- Título: {target_role.get('title', 'unknown')}
- Chapter: {target_role.get('chapter', 'unknown')}
- Skills requeridas: {len(target_role.get('required_skills', []))} competencias
- Responsabilidades: {len(target_role.get('responsibilities', []))} áreas clave

ANÁLISIS DE GAP:
- Score actual: {context.get('current_score', 0.5):.2f}/1.00
- Clasificación: {context.get('gap_band', 'NEAR')}
- Duración objetivo: {context.get('duration_months', 6)} meses
- Total gaps identificados: {gap_summary.get('total_gaps', 0)}

GAPS DE SKILLS PRIORITARIOS:
{skill_gaps_str}

FORMATO REQUERIDO (JSON):
{{
  "skill_priorities": [
    {{"skill_id": "S-XXX", "skill_name": "Nombre", "priority": "high|medium|low", "target_level": "avanzado", "current_level": "básico"}}
  ],
  "milestones": [
    {{
      "month": 2,
      "milestone": "Descripción del milestone",
      "success_criteria": "Criterio de éxito medible",
      "validation_method": "Cómo validar",
      "deliverables": ["Entregable 1", "Entregable 2"]
    }}
  ],
  "estimated_cost_eur": 2000,
  "time_investment_hours": 120,
  "success_probability": 0.75,
  "risk_factors": ["Factor de riesgo 1", "Factor 2"],
  "recommended_resources": ["Recurso 1", "Recurso 2"]
}}

REQUISITOS DEL PLAN:
1. Ser progresivo (milestones incrementales mes a mes)
2. Incluir validación específica en cada milestone
3. Ser realista en tiempo y costo (considerar jornada laboral)
4. Identificar riesgos específicos al empleado y rol
5. Alinearse con ambiciones profesionales del empleado
6. Priorizar gaps más críticos primero
7. Incluir deliverables medibles en cada milestone
"""
        return prompt
    
    def _parse_recommendations_response(self, response_text: str) -> List[Dict]:
        """Parsea respuesta de recomendaciones con sanitización mejorada."""
        print(f"🔍 Parsing AI response ({len(response_text)} chars)")
        print(f"📝 First 500 chars: {response_text[:500]}")
        print(f"📝 Last 200 chars: {response_text[-200:]}")
        
        # Remove common markdown code fences that AIs add
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            # Buscar JSON array
            start = cleaned_text.find('[')
            end = cleaned_text.rfind(']') + 1
            
            print(f"🔍 JSON array search: start={start}, end={end}")
            
            if start != -1 and end > start:
                json_str = cleaned_text[start:end]
                print(f"✅ Found JSON array ({len(json_str)} chars)")
                try:
                    recs = json.loads(json_str)
                    if isinstance(recs, list) and len(recs) > 0:
                        print(f"✅ Parsed {len(recs)} recommendations")
                        # Sanitize expected_impact to ensure all values are floats
                        return self._sanitize_recommendations(recs)
                    else:
                        print(f"⚠️ Parsed JSON but got empty list or non-list: {type(recs)}")
                except json.JSONDecodeError as je:
                    print(f"⚠️ JSON parse failed on extracted array: {je}")
                    print(f"📝 Extracted JSON: {json_str[:200]}...")
            
            # Intentar parsear directo
            if cleaned_text.startswith('['):
                print(f"🔍 Trying direct parse (starts with [)")
                recs = json.loads(cleaned_text)
                if isinstance(recs, list):
                    print(f"✅ Parsed {len(recs)} recommendations (direct)")
                    return self._sanitize_recommendations(recs)
            
            # Si la respuesta es muy corta, probablemente sea un mensaje de error
            if len(response_text) < 100:
                print(f"⚠️ Response too short ({len(response_text)} chars), likely an error message:")
                print(f"   '{response_text}'")
            else:
                print(f"❌ No valid JSON array found in response")
            
            return []
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse recommendations JSON: {e}")
            print(f"📝 Problematic section around position {e.pos}:")
            print(f"   {cleaned_text[max(0, e.pos-100):e.pos+100]}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error parsing recommendations: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _sanitize_recommendations(self, recs: List[Dict]) -> List[Dict]:
        """Sanitiza datos de recomendaciones para asegurar tipos correctos."""
        for rec in recs:
            # Sanitize expected_impact - convert strings to floats
            if 'expected_impact' in rec and isinstance(rec['expected_impact'], dict):
                sanitized_impact = {}
                for key, value in rec['expected_impact'].items():
                    if isinstance(value, str):
                        # Try to extract number from strings like "20-30%" or "high"
                        if '%' in value:
                            # Extract first number from percentage
                            import re
                            match = re.search(r'(\d+)', value)
                            sanitized_impact[key] = float(match.group(1)) / 100 if match else 0.5
                        elif value.lower() in ['high', 'alto', 'alta']:
                            sanitized_impact[key] = 0.8
                        elif value.lower() in ['medium', 'medio', 'media', 'medium-high']:
                            sanitized_impact[key] = 0.6
                        elif value.lower() in ['low', 'bajo', 'baja']:
                            sanitized_impact[key] = 0.3
                        else:
                            # Try to parse as float
                            try:
                                sanitized_impact[key] = float(value)
                            except ValueError:
                                sanitized_impact[key] = 0.5  # Default
                    else:
                        sanitized_impact[key] = float(value) if value is not None else 0.0
                rec['expected_impact'] = sanitized_impact
        return recs
    
    def _parse_plan_response(self, response_text: str) -> Dict:
        """Parsea respuesta de plan con manejo robusto de errores."""
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                
                # Intentar limpiar JSON malformado
                # Eliminar trailing commas antes de ] o }
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                
                # Intentar parsear
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse plan JSON: {e}")
                    print(f"📄 Problematic JSON (first 500 chars): {json_str[:500]}")
                    
                    # Intentar reparar JSON común
                    json_str_fixed = self._repair_json(json_str)
                    if json_str_fixed:
                        try:
                            return json.loads(json_str_fixed)
                        except:
                            pass
            
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            return {}
        except Exception as e:
            print(f"⚠️ Failed to parse plan JSON: {e}")
            return {}
    
    def _repair_json(self, json_str: str) -> Optional[str]:
        """Intenta reparar JSON malformado común."""
        try:
            # Eliminar trailing commas antes de } o ]
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Eliminar commas duplicadas
            json_str = re.sub(r',\s*,', r',', json_str)
            
            # Añadir commas faltantes entre elementos de objetos
            # Patrón: "key": "value" "key2" -> "key": "value", "key2"
            json_str = re.sub(r'"\s*\n\s*"(?=[a-zA-Z_])', '",\n  "', json_str)
            
            # Añadir commas faltantes entre } y siguiente elemento
            json_str = re.sub(r'}\s*\n\s*{', '},\n  {', json_str)
            json_str = re.sub(r'}\s*\n\s*"', '},\n  "', json_str)
            
            # Arreglar commas faltantes después de valores
            json_str = re.sub(r'(["\d\]}])\s*\n\s*"(?=[a-zA-Z_])', r'\1,\n  "', json_str)
            
            return json_str
        except:
            return None
    
    def _create_recommendation_from_ai(self,
                                      rec_data: Dict,
                                      employee_id: str,
                                      response,
                                      index: int) -> PersonalizedRecommendation:
        """Crea objeto PersonalizedRecommendation desde datos de IA."""
        # Parsear action items
        action_items = []
        for item_data in rec_data.get('action_items', []):
            action_items.append(ActionItem(
                action=item_data.get('action', ''),
                timeline=item_data.get('timeline', ''),
                resources_needed=item_data.get('resources_needed', []),
                success_criteria=item_data.get('success_criteria'),
                priority=item_data.get('priority', 'medium')
            ))
        
        # Parse type field - handle multiple types separated by |
        type_value = rec_data.get('type', 'skill_development')
        if '|' in str(type_value):
            # Take first type when multiple provided
            type_value = type_value.split('|')[0].strip()
        
        # Crear recomendación
        recommendation = PersonalizedRecommendation(
            id=f"REC-{employee_id}-{datetime.now().strftime('%Y%m%d')}-{index}",
            employee_id=employee_id,
            type=RecommendationType(type_value),
            title=rec_data.get('title', 'Recomendación de desarrollo'),
            description=rec_data.get('description', ''),
            rationale=rec_data.get('rationale', ''),
            action_items=action_items,
            effort_level=EffortLevel(rec_data.get('effort_level', 'medium')),
            estimated_duration=rec_data.get('estimated_duration', ''),
            expected_impact=rec_data.get('expected_impact', {}),
            success_probability=rec_data.get('success_probability', 0.7),
            priority_score=rec_data.get('priority_score', 0.5),
            ai_metadata=AIMetadata(
                model_used=response.model,
                provider=response.provider,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace=f"AI-generated recommendation #{index}",
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd / max(len(rec_data), 1)  # Prorratear costo
            )
        )
        
        return recommendation
    
    def _create_plan_from_ai(self, plan_data: Dict, context: Dict, response) -> DevelopmentPlan:
        """Crea DevelopmentPlan desde datos de IA."""
        # Parsear milestones
        milestones = []
        for ms_data in plan_data.get('milestones', []):
            milestones.append(DevelopmentMilestone(
                month=ms_data.get('month', 1),
                milestone=ms_data.get('milestone', ''),
                success_criteria=ms_data.get('success_criteria', ''),
                validation_method=ms_data.get('validation_method')
            ))
        
        # Crear plan
        plan = DevelopmentPlan(
            employee_id=context['employee_id'],
            target_role_id=context['target_role_id'],
            current_score=context['current_score'],
            target_score=min(context['current_score'] + 0.25, 1.0),
            duration_months=context['duration_months'],
            milestones=milestones,
            recommendations=[],  # Se llenarían por separado
            skill_priorities=plan_data.get('skill_priorities', []),
            estimated_cost_eur=plan_data.get('estimated_cost_eur'),
            time_investment_hours=plan_data.get('time_investment_hours', 0),
            success_probability=plan_data.get('success_probability', 0.7),
            risk_factors=plan_data.get('risk_factors', []),
            ai_metadata=AIMetadata(
                model_used=response.model,
                provider=response.provider,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning_type=ReasoningType.GENERATIVE,
                reasoning_trace=f"AI-generated development plan",
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd
            )
        )
        
        return plan
    
    def _generate_rule_based_recommendations(self,
                                            employee,
                                            gap_results: List,
                                            target_role,
                                            max_recommendations: int) -> List[PersonalizedRecommendation]:
        """Fallback MEJORADO: genera recomendaciones basadas en reglas + visión futura."""
        from services.data_loader import data_loader
        
        recommendations = []
        employee_id = getattr(employee, 'id', 'unknown')
        target_role_id = getattr(target_role, 'id', 'unknown') if target_role else None
        
        # Check if target role is a future role
        future_roles = data_loader.get_future_roles()
        is_future_role = target_role_id in future_roles if target_role_id else False
        
        # Get vision data for context (access data_store attribute directly)
        vision_data = data_loader.data_store.vision_data or {}
        critical_priorities = vision_data.get('prioridades', {}).get('critico', [])[:2] if vision_data else []
        
        # Get best gap result for analysis
        best_gap = gap_results[0] if gap_results else None
        gap_score = getattr(best_gap, 'overall_score', 0.5) if best_gap else 0.5
        
        # 1. Skill Development (always relevant)
        title = f"Desarrollar skills para {getattr(target_role, 'titulo', 'rol objetivo')}" if target_role else "Desarrollar competencias clave"
        if is_future_role:
            title += " (Rol Futuro - Alta Prioridad)"
        
        description = f"Programa de desarrollo enfocado en cerrar gaps identificados (gap score actual: {gap_score:.2f})."
        if is_future_role and critical_priorities:
            description += f" Alineado con prioridades estratégicas: {critical_priorities[0]}"
        
        rec1 = PersonalizedRecommendation(
            id=f"REC-RULE-SKILL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            employee_id=employee_id,
            type=RecommendationType.SKILL_DEVELOPMENT,
            title=title,
            description=description,
            rationale=f"Gap score de {gap_score:.2f} indica oportunidades de desarrollo" + (" en rol estratégico futuro" if is_future_role else ""),
            action_items=[
                ActionItem(
                    action="Realizar autoevaluación detallada de skills requeridos",
                    timeline="1 semana",
                    resources_needed=["Gap analysis report", "Descripción del rol objetivo"],
                    priority="high" if is_future_role else "medium",
                    success_criteria="Lista priorizada de top 5 skills a desarrollar"
                ),
                ActionItem(
                    action="Inscribirse en cursos/certificaciones relevantes",
                    timeline="2-4 semanas",
                    resources_needed=["Budget aprobado", "Plataformas de learning (Coursera, LinkedIn Learning)"],
                    priority="high",
                    success_criteria="Al menos 2 cursos iniciados"
                ),
                ActionItem(
                    action="Aplicar skills en proyecto real",
                    timeline="6-8 semanas",
                    resources_needed=["Proyecto piloto", "Mentor asignado"],
                    priority="high",
                    success_criteria="Proyecto completado con feedback positivo"
                )
            ],
            effort_level=EffortLevel.MEDIUM if gap_score > 0.5 else EffortLevel.HIGH,
            estimated_duration="3-6 meses",
            expected_impact={"gap_reduction": 0.15, "readiness_improvement": 0.25},
            success_probability=0.75 if gap_score > 0.5 else 0.65,
            priority_score=0.9 if is_future_role else 0.7,
            ai_metadata=AIMetadata(
                model_used="rule-based-enhanced",
                provider="internal",
                confidence_level=ConfidenceLevel.MEDIUM,
                reasoning_type=ReasoningType.RULE_BASED,
                reasoning_trace=f"Generated using enhanced rule-based fallback. Future role: {is_future_role}"
            )
        )
        recommendations.append(rec1)
        
        # 2. Mentoring (if gap score suggests need)
        if gap_score < 0.7:
            rec2 = PersonalizedRecommendation(
                id=f"REC-RULE-MENTOR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                employee_id=employee_id,
                type=RecommendationType.MENTORING,
                title="Programa de mentoría con experto en el rol",
                description=f"Asignación de mentor con experiencia en {getattr(target_role, 'titulo', 'el rol objetivo')} para acelerar desarrollo",
                rationale=f"Gap score de {gap_score:.2f} se beneficiaría de guía directa y experiencia práctica",
                action_items=[
                    ActionItem(
                        action="Identificar y asignar mentor adecuado",
                        timeline="1-2 semanas",
                        resources_needed=["Aprobación manager", "Base de mentores disponibles"],
                        priority="high",
                        success_criteria="Mentor asignado con match confirmado"
                    ),
                    ActionItem(
                        action="Establecer plan de sesiones regulares (bi-weekly)",
                        timeline="2 semanas",
                        resources_needed=["Calendario compartido", "Objetivos definidos"],
                        priority="high",
                        success_criteria="Calendario de 6 meses establecido"
                    )
                ],
                effort_level=EffortLevel.MEDIUM,
                estimated_duration="6 meses",
                expected_impact={"skill_acceleration": 0.35, "confidence_boost": 0.8},
                success_probability=0.80,
                priority_score=0.85,
                ai_metadata=AIMetadata(
                    model_used="rule-based-enhanced",
                    provider="internal",
                    confidence_level=ConfidenceLevel.MEDIUM,
                    reasoning_type=ReasoningType.RULE_BASED,
                    reasoning_trace="Mentoring recommended due to gap score < 0.7"
                )
            )
            recommendations.append(rec2)
        
        # 3. Career Progression planning
        rec3 = PersonalizedRecommendation(
            id=f"REC-RULE-CAREER-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            employee_id=employee_id,
            type=RecommendationType.CAREER_PROGRESSION,
            title="Planificación de carrera hacia " + (getattr(target_role, 'titulo', 'rol objetivo') if target_role else "siguiente nivel"),
            description=f"Desarrollo de plan de carrera estructurado con milestones claros" + (" alineado con la visión estratégica de la empresa" if is_future_role else ""),
            rationale="Roadmap claro aumenta motivación y dirección del desarrollo" + (" en rol clave para el futuro" if is_future_role else ""),
            action_items=[
                ActionItem(
                    action="Reunión con manager para alinear expectativas",
                    timeline="1 semana",
                    resources_needed=["Disponibilidad manager", "Gap analysis report"],
                    priority="high",
                    success_criteria="Plan de carrera validado por ambas partes"
                ),
                ActionItem(
                    action="Definir milestones trimestrales",
                    timeline="2 semanas",
                    resources_needed=["Template de plan de carrera"],
                    priority="medium",
                    success_criteria="4 milestones definidos con criterios de éxito"
                )
            ],
            effort_level=EffortLevel.LOW,
            estimated_duration="Ongoing",
            expected_impact={"clarity": 0.9, "motivation": 0.75},
            success_probability=0.85,
            priority_score=0.75,
            ai_metadata=AIMetadata(
                model_used="rule-based-enhanced",
                provider="internal",
                confidence_level=ConfidenceLevel.MEDIUM,
                reasoning_type=ReasoningType.RULE_BASED,
                reasoning_trace="Career planning recommended for structured progression"
            )
        )
        recommendations.append(rec3)
        
        return recommendations[:max_recommendations]
    
    def _generate_rule_based_plan(self, employee, target_role, gap_result, duration_months) -> DevelopmentPlan:
        """Fallback: plan basado en reglas."""
        plan = DevelopmentPlan(
            employee_id=getattr(employee, 'id', 'unknown'),
            target_role_id=getattr(target_role, 'id', 'unknown'),
            current_score=getattr(gap_result, 'overall_score', 0.5),
            target_score=0.75,
            duration_months=duration_months,
            milestones=[
                DevelopmentMilestone(
                    month=2,
                    milestone="Completar training inicial",
                    success_criteria="Cursos completados"
                ),
                DevelopmentMilestone(
                    month=4,
                    milestone="Aplicar skills en proyecto",
                    success_criteria="Proyecto completado exitosamente"
                ),
                DevelopmentMilestone(
                    month=6,
                    milestone="Evaluación final",
                    success_criteria="Assessment aprobado"
                )
            ],
            recommendations=[],
            skill_priorities=[],
            time_investment_hours=120,
            success_probability=0.65,
            risk_factors=["Disponibilidad de tiempo", "Recursos limitados"],
            ai_metadata=AIMetadata(
                model_used="rule-based",
                provider="internal",
                confidence_level=ConfidenceLevel.MEDIUM,
                reasoning_type=ReasoningType.RULE_BASED,
                reasoning_trace="Generated using rule-based fallback"
            )
        )
        
        return plan
    
    def _format_skills(self, employee) -> str:
        """Formatea skills del empleado para prompt (string)."""
        try:
            skills = getattr(employee, 'skills', {})
            if isinstance(skills, dict):
                return ', '.join([f"{k}: {v}" for k, v in list(skills.items())[:5]])
            return str(skills)[:100]
        except:
            return "N/A"
    
    def _extract_structured_skills(self, employee) -> List[Dict]:
        """Extrae skills en formato estructurado (lista de dicts)."""
        try:
            skills = getattr(employee, 'habilidades', {})
            if not skills:
                skills = getattr(employee, 'skills', {})
            
            if isinstance(skills, dict):
                return [
                    {
                        'skill_id': k,
                        'skill_name': k.replace('S-', '').replace('_', ' ').title(),
                        'level': v
                    }
                    for k, v in skills.items()
                ]
            return []
        except:
            return []
    
    def _summarize_gaps(self, gap_results: List) -> Dict:
        """Resume gap results para contexto."""
        if not gap_results:
            return {
                'best_role': 'N/A',
                'best_gap_score': 0.0,
                'skill_gaps_count': 0,
                'top_skill_gaps': []
            }
        
        best = max(gap_results, key=lambda x: getattr(x, 'overall_score', 0))
        
        return {
            'best_role': getattr(best, 'role_id', 'unknown'),
            'best_gap_score': getattr(best, 'overall_score', 0.0),
            'skill_gaps_count': len(getattr(best, 'detailed_gaps', [])),
            'top_skill_gaps': getattr(best, 'detailed_gaps', [])[:3]
        }
    
    def _validate_and_filter_biases(self,
                                   recommendations: List[PersonalizedRecommendation]) -> List[PersonalizedRecommendation]:
        """Valida y filtra recomendaciones con sesgos."""
        validated = []
        
        for rec in recommendations:
            # Validar contenido completo
            full_text = f"{rec.title} {rec.description} {rec.rationale}"
            bias_check = self.bias_detector.detect_bias(full_text)
            
            # Actualizar metadata
            rec.ai_metadata.bias_check_passed = not bias_check['has_bias']
            rec.ai_metadata.human_review_required = bias_check['requires_human_review']
            
            # Solo incluir si no tiene sesgos de alta severidad
            if not bias_check['requires_human_review']:
                validated.append(rec)
            else:
                print(f"⚠️ Recommendation filtered due to bias: {rec.title}")
        
        return validated
    
    def _merge_recommendations(self,
                              ai_recs: List[PersonalizedRecommendation],
                              rule_recs: List[PersonalizedRecommendation]) -> List[PersonalizedRecommendation]:
        """Combina recomendaciones de IA y reglas, eliminando duplicados."""
        # Usar títulos como clave de deduplicación
        seen_titles = set()
        merged = []
        
        # Priorizar IA recs
        for rec in ai_recs:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                merged.append(rec)
        
        # Agregar rule recs únicas
        for rec in rule_recs:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                merged.append(rec)
        
        return merged
