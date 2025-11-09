"""
Gap Analysis Service
Integrates Samya's TalentGapAlgorithm with the API
"""

import sys
from pathlib import Path
from typing import Dict, List, TYPE_CHECKING

from models.employee import Employee
from models.role import Role
from models.hr_forms import EmployeeSkillGap, HRGapAnalysisRequest
from services.data_loader import data_loader
from services.model_adapter import ModelAdapter

# Lazy imports for algorithm to avoid import issues
GapCalculator = None
DEFAULT_WEIGHTS = {
    'skills': 0.50,
    'responsibilities': 0.25,
    'ambitions': 0.15,
    'dedication': 0.10
}

def _import_algorithm():
    """Lazy import of algorithm modules"""
    global GapCalculator, DEFAULT_WEIGHTS
    if GapCalculator is not None:
        return
    
    # Add parent directory to path so we can import 'algorithm' package
    parent_path = Path(__file__).parent.parent.parent
    if str(parent_path) not in sys.path:
        sys.path.append(str(parent_path))
    
    try:
        import algorithm.gap_calculator as gc
        import algorithm.models as am
        GapCalculator = gc.GapCalculator
        DEFAULT_WEIGHTS = am.DEFAULT_WEIGHTS.copy()
    except ImportError as e:
        print(f"Warning: Could not import algorithm: {e}")
        # Keep defaults


class GapAnalysisService:
    """
    Service for calculating talent gaps between current employees and future role requirements
    
    Implementation: Integrates Samya's TalentGapAlgorithm
    Algorithm calculates:
    - gap_score = 0.50 * skills_gap + 0.25 * responsibilities_gap + 0.15 * ambitions_gap + 0.10 * dedication_gap
    
    Classifications:
    - READY: gap < 20%
    - READY_WITH_SUPPORT: gap 20-40%
    - NEAR: gap 40-60%
    - FAR: gap 60-80%
    - NOT_VIABLE: gap > 80%
    """
    
    _gap_calculator = None
    _skills_catalog = None
    
    @classmethod
    def _get_gap_calculator(cls):
        """Get or create the gap calculator instance"""
        # Import algorithm on first use
        _import_algorithm()
        
        if cls._gap_calculator is None:
            # Build skills catalog from data_loader
            skills_data = data_loader.get_skills()
            cls._skills_catalog = {}
            
            for skill_id, skill_data in skills_data.items():
                algo_skill = ModelAdapter.api_skill_to_algo(skill_data)
                cls._skills_catalog[skill_id] = algo_skill
            
            # Initialize gap calculator with skills catalog
            cls._gap_calculator = GapCalculator(
                skills_catalog=cls._skills_catalog,
                weights=DEFAULT_WEIGHTS.copy()
            )
        
        return cls._gap_calculator
    
    @classmethod
    def calculate_gap(
        cls,
        employee: Employee,
        target_role: Role,
        weights: Dict[str, float] = None
    ) -> EmployeeSkillGap:
        """
        Calculate gap between employee and target role
        
        Args:
            employee: Current employee data
            target_role: Target role requirements
            weights: Custom weights for gap calculation (optional)
        
        Returns:
            EmployeeSkillGap with scores and classification
        """
        # Ensure algorithm models and skills catalog are loaded
        _import_algorithm()
        # If skills catalog is not built yet, build it (same logic as _get_gap_calculator)
        if cls._skills_catalog is None:
            skills_data = data_loader.get_skills()
            cls._skills_catalog = {}
            for skill_id, skill_data in skills_data.items():
                algo_skill = ModelAdapter.api_skill_to_algo(skill_data)
                cls._skills_catalog[skill_id] = algo_skill

        # Create a fresh GapCalculator for each calculation to avoid state carry-over
        calc_weights = weights if weights is not None else DEFAULT_WEIGHTS.copy()
        calculator = GapCalculator(
            skills_catalog=cls._skills_catalog,
            weights=calc_weights
        )

        # Convert API models to algorithm models
        algo_employee = ModelAdapter.api_employee_to_algo(employee)
        algo_role = ModelAdapter.api_role_to_algo(target_role, cls._skills_catalog)

        # Calculate gap using Samya's algorithm
        gap_result = calculator.calculate_gap(algo_employee, algo_role)
        
        # Convert score (0-1, higher is better) to gap percentage (0-100, lower is better)
        gap_percentage = ModelAdapter.score_to_gap_percentage(gap_result.overall_score)
        
        # Extract component gaps
        skills_gap = ModelAdapter.score_to_gap_percentage(gap_result.component_scores['skills'])
        responsibilities_gap = ModelAdapter.score_to_gap_percentage(gap_result.component_scores['responsibilities'])
        ambitions_gap = ModelAdapter.score_to_gap_percentage(gap_result.component_scores['ambitions'])
        dedication_gap = ModelAdapter.score_to_gap_percentage(gap_result.component_scores['dedication'])
        
        # Convert GapBand to classification string
        classification = ModelAdapter.gap_band_to_classification(gap_result.band)
        
        # Generate recommendations from gap details
        recommendations = []
        if gap_result.detailed_gaps:
            # detailed_gaps es una lista de strings con los gaps identificados
            for gap in gap_result.detailed_gaps[:3]:  # Top 3 gaps
                recommendations.append(f"Address gap: {gap}")
        
        # Agregar recomendaciones del algoritmo si existen
        if gap_result.recommendations:
            for rec in gap_result.recommendations[:2]:  # Top 2 recommendations
                if isinstance(rec, dict):
                    recommendations.append(rec.get('action', str(rec)))
                else:
                    recommendations.append(str(rec))
        
        if len(recommendations) == 0:
            recommendations.append("Employee is ready for this role!")
        
        # Build skill gaps dict from detailed_gaps
        skill_gaps_dict = {}
        if gap_result.detailed_gaps:
            for i, gap in enumerate(gap_result.detailed_gaps):
                skill_gaps_dict[f"gap_{i}"] = {
                    "description": gap,
                    "severity": "high" if i < 3 else "medium"
                }
        
        # Build EmployeeSkillGap response
        return EmployeeSkillGap(
            employee_id=employee.id_empleado,
            employee_name=employee.nombre,
            target_role_id=target_role.id,
            target_role_title=target_role.titulo,
            overall_gap_score=gap_percentage,
            skill_gaps=skill_gaps_dict,
            responsibilities_gap=responsibilities_gap,
            ambitions_alignment=100 - ambitions_gap,  # Convert to alignment (higher is better)
            dedication_availability=100 - dedication_gap,  # Convert to availability (higher is better)
            classification=classification,
            recommendations=recommendations
        )
    
    @classmethod
    def calculate_bulk_gaps(
        cls,
        employees: Dict[int, Employee],
        roles: Dict[str, Role],
        request: HRGapAnalysisRequest
    ) -> List[EmployeeSkillGap]:
        """
        Calculate gaps for multiple employees against multiple roles
        
        Args:
            employees: All employees to analyze
            roles: All target roles
            request: Analysis configuration
        
        Returns:
            List of EmployeeSkillGap results
        """
        print(f"📊 Starting bulk gap analysis...")
        print(f"   Total employees: {len(employees)}")
        print(f"   Total roles: {len(roles)}")
        print(f"   Target roles: {request.target_roles}")
        
        results = []
        
        # Filter employees
        filtered_employees = {}
        for emp_id, employee in employees.items():
            # Filter by employee IDs if specified
            if request.include_employees and emp_id not in request.include_employees:
                continue
            # Filter by chapters if specified
            if request.include_chapters and employee.chapter not in request.include_chapters:
                continue
            filtered_employees[emp_id] = employee
        
        print(f"   Filtered employees: {len(filtered_employees)}")
        
        # Filter roles
        filtered_roles = {}
        if request.target_roles:
            for role_id in request.target_roles:
                if role_id in roles:
                    filtered_roles[role_id] = roles[role_id]
                else:
                    print(f"   ⚠️  Role {role_id} not found in roles catalog")
        else:
            filtered_roles = roles
        
        print(f"   Filtered roles: {len(filtered_roles)}")
        
        # Calculate gap for each employee-role combination
        for employee in filtered_employees.values():
            for role in filtered_roles.values():
                try:
                    print(f"   🔍 Calculating: {employee.nombre} vs {role.titulo}")
                    gap_result = cls.calculate_gap(
                        employee=employee,
                        target_role=role,
                        weights=request.algorithm_weights
                    )
                    results.append(gap_result)
                    print(f"      ✅ Gap: {gap_result.overall_gap_score:.2f}% - {gap_result.classification}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Sort by overall gap score (ascending - best matches first)
        results.sort(key=lambda x: x.overall_gap_score)
        
        print(f"✅ Bulk analysis complete: {len(results)} results")
        return results
    
    @staticmethod
    def _estimate_readiness_time(gap_percentage: float, classification: str) -> str:
        """
        Estimate time to readiness based on gap
        
        Args:
            gap_percentage: Overall gap percentage
            classification: Gap classification
        
        Returns:
            Estimated time string
        """
        if classification == "READY":
            return "0-3 months"
        elif classification == "READY_WITH_SUPPORT":
            return "3-6 months"
        elif classification == "NEAR":
            return "6-12 months"
        elif classification == "FAR":
            return "12-18 months"
        else:  # NOT_VIABLE
            return ">18 months or role change recommended"
    
    @staticmethod
    def classify_gap(gap_score: float) -> str:
        """
        Classify gap score into bands
        
        Args:
            gap_score: Overall gap score (0-100)
        
        Returns:
            Classification: READY, READY_WITH_SUPPORT, NEAR, FAR, NOT_VIABLE
        """
        if gap_score < 20:
            return "READY"
        elif gap_score < 40:
            return "READY_WITH_SUPPORT"
        elif gap_score < 60:
            return "NEAR"
        elif gap_score < 80:
            return "FAR"
        else:
            return "NOT_VIABLE"
    
    @classmethod
    def generate_recommendations(
        cls,
        employee: Employee,
        target_role: Role,
        gap_details: Dict = None
    ) -> List[str]:
        """
        Generate development recommendations for employee
        
        Args:
            employee: Employee data
            target_role: Target role
            gap_details: Detailed gap analysis (optional)
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Skill-based recommendations
        employee_skills = set(employee.habilidades.keys())
        required_skills = set(target_role.habilidades_requeridas)
        missing_skills = required_skills - employee_skills
        
        if missing_skills:
            recommendations.append(f"Develop skills: {', '.join(list(missing_skills)[:3])}")
        
        # Level up existing skills
        low_skills = [skill_id for skill_id, level in employee.habilidades.items() 
                      if skill_id in required_skills and level < 7]
        if low_skills:
            recommendations.append(f"Improve proficiency in: {', '.join(low_skills[:2])}")
        
        # Responsibility recommendations
        if target_role.responsabilidades:
            recommendations.append(f"Gain experience in: {target_role.responsabilidades[0]}")
        
        # Level alignment
        current_level = employee.ambiciones.nivel_aspiracion.lower()
        target_level = target_role.nivel.value.lower()
        
        if target_level == "lead" and current_level != "lead":
            recommendations.append("Develop leadership skills and team management experience")
        elif target_level == "senior" and current_level in ["junior", "mid"]:
            recommendations.append("Focus on senior-level responsibilities and mentoring")
        
        # Chapter transition
        if employee.chapter != target_role.capitulo:
            recommendations.append(f"Consider cross-training in {target_role.capitulo} chapter")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    @classmethod
    def calculate_employee_gap_matrix(
        cls,
        employee_id: int,
        weights: Dict[str, float] = None
    ):
        """
        Calculate complete gap matrix for a single employee against all roles.
        Similar to main_challenge.py matrix generation.
        
        Args:
            employee_id: ID of the employee
            weights: Custom algorithm weights (optional)
        
        Returns:
            EmployeeGapMatrix with all role matches
        """
        from models.hr_forms import EmployeeGapMatrix, EmployeeGapMatrixRow
        
        # Get employee
        employee = data_loader.get_employee(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Get all roles
        roles = data_loader.get_roles()
        if not roles:
            raise ValueError("No roles found in system")
        
        print(f"📊 Calculating gap matrix for employee {employee.nombre} ({employee_id})")
        print(f"   Total roles to analyze: {len(roles)}")
        
        # Calculate gaps for all roles
        role_matches = []
        ready_count = 0
        total_score = 0.0
        
        for role_id, role in roles.items():
            try:
                # Calculate gap using the service
                gap_result = cls.calculate_gap(
                    employee=employee,
                    target_role=role,
                    weights=weights
                )
                
                # Convert gap percentages back to scores (0-1, higher is better)
                # gap_result returns gaps (lower is better), we need scores (higher is better)
                overall_score = (100 - gap_result.overall_gap_score) / 100.0
                
                # Get component scores - CORRECTLY extract from the gap_result
                # gap_result.responsibilities_gap is already a gap percentage (0-100)
                # We need to convert to score (0-1)
                skills_score = overall_score  # Will be calculated from detailed components
                responsibilities_score = (100 - gap_result.responsibilities_gap) / 100.0
                ambitions_score = gap_result.ambitions_alignment / 100.0
                dedication_score = gap_result.dedication_availability / 100.0
                
                # Note: skills_score is embedded in overall_score via the algorithm weights
                # To extract it properly, we'd need to reverse the weighted calculation
                # For now, we calculate it from the overall and other components
                # overall = 0.5*skills + 0.25*resp + 0.15*ambitions + 0.10*dedication
                # skills = (overall - 0.25*resp - 0.15*ambitions - 0.10*dedication) / 0.5
                w = weights if weights else DEFAULT_WEIGHTS
                skills_score = (overall_score - w['responsibilities']*responsibilities_score - 
                               w['ambitions']*ambitions_score - w['dedication']*dedication_score) / w['skills']
                # Clamp to valid range
                skills_score = max(0.0, min(1.0, skills_score))
                
                # Extract detailed gaps
                detailed_gaps = []
                for gap_key, gap_data in gap_result.skill_gaps.items():
                    if isinstance(gap_data, dict) and 'description' in gap_data:
                        detailed_gaps.append(gap_data['description'])
                
                # Create matrix row
                matrix_row = EmployeeGapMatrixRow(
                    employee_id=employee_id,
                    employee_name=employee.nombre,
                    role_id=role_id,
                    role_title=role.titulo,
                    overall_score=overall_score,
                    band=gap_result.classification,
                    skills_score=skills_score,
                    responsibilities_score=responsibilities_score,
                    ambitions_score=ambitions_score,
                    dedication_score=dedication_score,
                    detailed_gaps=detailed_gaps,
                    recommendations=gap_result.recommendations
                )
                
                role_matches.append(matrix_row)
                
                # Count ready roles
                if gap_result.classification in ["READY", "READY_WITH_SUPPORT"]:
                    ready_count += 1
                
                total_score += overall_score
                
                print(f"   ✓ {role.titulo}: {overall_score:.3f} ({gap_result.classification})")
                
            except Exception as e:
                print(f"   ✗ Error calculating gap for role {role_id}: {e}")
                continue
        
        # Sort by score (highest first)
        role_matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Get best match
        best_match = role_matches[0] if role_matches else None
        
        # Calculate average score
        avg_score = total_score / len(role_matches) if role_matches else 0.0
        
        # Build matrix response
        matrix = EmployeeGapMatrix(
            employee_id=employee_id,
            employee_name=employee.nombre,
            chapter=employee.chapter,
            current_role=employee.rol_actual,
            role_matches=role_matches,
            best_match=best_match,
            ready_roles_count=ready_count,
            avg_compatibility_score=avg_score
        )
        
        print(f"✅ Matrix complete: {len(role_matches)} roles analyzed")
        print(f"   Best match: {best_match.role_title} ({best_match.overall_score:.3f})") if best_match else None
        print(f"   Ready roles: {ready_count}")
        print(f"   Avg compatibility: {avg_score:.3f}")
        
        return matrix
    
    @classmethod
    def analyze_bottlenecks_by_role(cls) -> Dict[str, Dict]:
        """
        Analyzes critical skill gaps from the perspective of each role.
        Groups gaps by role to facilitate role-specific queries.
        
        Returns:
            Dict with structure:
            {
                "R-STR-LEAD": {
                    "role_id": "R-STR-LEAD",
                    "role_title": "Head of Strategy",
                    "critical_gaps": [
                        {
                            "skill_id": "S-ANALISIS",
                            "skill_name": "Análisis",
                            "avg_gap_percentage": 75.0,
                            "candidates_affected": 2,
                            "total_viable_candidates": 3,
                            "priority": "ALTA"
                        }
                    ],
                    "total_gaps": 3,
                    "highest_priority": "CRÍTICA"
                }
            }
        """
        from collections import defaultdict
        
        print("🔍 Analyzing critical bottlenecks by role...")
        
        employees = data_loader.get_employees()
        roles = data_loader.get_roles()
        
        if not employees or not roles:
            print("⚠️  No employees or roles data available")
            return {}
        
        role_gaps_dict = defaultdict(list)
        
        # Analyze each role
        for role_id, role in roles.items():
            print(f"📊 Analyzing role: {role.titulo}")
            
            # Get required skills for this role
            required_skills = role.habilidades_requeridas
            
            if not required_skills:
                print(f"   ⚠️  No required skills defined for {role.titulo}")
                continue
            
            # Analyze each employee against this role
            viable_candidates = []
            
            for emp_id, employee in employees.items():
                try:
                    # Calculate gap for this employee-role pair
                    gap_result = cls.calculate_gap(employee, role)
                    
                    # Only consider viable candidates (not NOT_VIABLE)
                    if gap_result.classification != "NOT_VIABLE":
                        viable_candidates.append({
                            'employee_id': emp_id,
                            'employee_name': employee.nombre,
                            'gap_result': gap_result,
                            'overall_gap': gap_result.overall_gap_score
                        })
                except Exception as e:
                    print(f"   ✗ Error calculating gap for employee {emp_id}: {e}")
                    continue
            
            # Sort candidates by gap (lower is better)
            viable_candidates.sort(key=lambda x: x['overall_gap'])
            
            total_viable = len(viable_candidates)
            print(f"   ✓ Found {total_viable} viable candidates")
            
            # Analyze skill gaps across top candidates (top 5 or all if less)
            top_candidates = viable_candidates[:min(5, total_viable)]
            
            if not top_candidates:
                print(f"   ⚠️  No viable candidates for {role.titulo}")
                continue
            
            # Identify critical skills that are missing/weak in top candidates
            skill_gap_analysis = defaultdict(lambda: {
                'total_gap': 0,
                'count': 0,
                'candidates_affected': []
            })
            
            for candidate in top_candidates:
                gap_result = candidate['gap_result']
                
                # Analyze skill gaps from the gap_result
                for skill_id in required_skills:
                    # Check if employee has this skill
                    employee_skill_level = None
                    employee = employees[candidate['employee_id']]
                    
                    if skill_id in employee.habilidades:
                        employee_skill_level = employee.habilidades[skill_id]
                    
                    # Calculate gap for this specific skill
                    if employee_skill_level is None or employee_skill_level < 5:
                        # Significant gap (no skill or low level)
                        gap_percentage = 100 if employee_skill_level is None else (10 - employee_skill_level) * 10
                        
                        skill_gap_analysis[skill_id]['total_gap'] += gap_percentage
                        skill_gap_analysis[skill_id]['count'] += 1
                        skill_gap_analysis[skill_id]['candidates_affected'].append({
                            'employee_id': candidate['employee_id'],
                            'employee_name': candidate['employee_name'],
                            'current_level': employee_skill_level if employee_skill_level is not None else 0,
                            'required_level': 7  # Typical requirement
                        })
            
            # Process skill gaps for this role
            for skill_id, gap_data in skill_gap_analysis.items():
                if gap_data['count'] == 0:
                    continue
                
                avg_gap = gap_data['total_gap'] / gap_data['count']
                candidates_affected = len(gap_data['candidates_affected'])
                
                # Determine priority based on gap and number of candidates affected
                if avg_gap >= 80 or candidates_affected >= 4:
                    priority = 'CRÍTICA'
                    criticality_score = avg_gap * 1.5
                elif avg_gap >= 60 or candidates_affected >= 3:
                    priority = 'ALTA'
                    criticality_score = avg_gap * 1.2
                elif avg_gap >= 40 or candidates_affected >= 2:
                    priority = 'MEDIA'
                    criticality_score = avg_gap
                else:
                    priority = 'BAJA'
                    criticality_score = avg_gap * 0.8
                
                # Get skill name - skills_data contains Skill objects, not dicts
                skills_data = data_loader.get_skills()
                skill_obj = skills_data.get(skill_id)
                skill_name = skill_obj.nombre if skill_obj else skill_id
                
                role_gaps_dict[role_id].append({
                    'skill_id': skill_id,
                    'skill_name': skill_name,
                    'avg_gap_percentage': round(avg_gap, 1),
                    'candidates_affected': candidates_affected,
                    'total_viable_candidates': total_viable,
                    'priority': priority,
                    'criticality_score': criticality_score,
                    'candidates_details': gap_data['candidates_affected'][:3]  # Top 3
                })
        
        # Build final result structure
        result = {}
        priority_order = ['CRÍTICA', 'ALTA', 'MEDIA', 'BAJA']
        
        for role_id, gaps in role_gaps_dict.items():
            if not gaps:
                continue
            
            # Sort by criticality
            gaps.sort(key=lambda x: x['criticality_score'], reverse=True)
            
            # Determine highest priority
            highest_priority = 'BAJA'
            for gap in gaps:
                gap_priority = gap.get('priority', 'MEDIA')
                if priority_order.index(gap_priority) < priority_order.index(highest_priority):
                    highest_priority = gap_priority
            
            # Get role title
            role = roles.get(role_id)
            role_title = role.titulo if role else role_id
            
            result[role_id] = {
                'role_id': role_id,
                'role_title': role_title,
                'critical_gaps': gaps,
                'total_gaps': len(gaps),
                'highest_priority': highest_priority
            }
        
        print(f"✅ Bottleneck analysis complete: {len(result)} roles with gaps identified")
        
        return result
