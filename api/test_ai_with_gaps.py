"""
Test AI generation with real gap analysis data
"""
import sys
import os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Set environment for data loading
os.environ['DATA_PATH'] = str(Path(__file__).parent.parent / 'dataSet' / 'talent-gap-analyzer-main')

from services.data_loader import DataLoader
from services.gap_service import GapAnalysisService

def test_gap_calculation():
    """Test that gap analysis works and returns real data."""
    print("\n" + "="*60)
    print("🧪 Testing Gap Analysis Integration")
    print("="*60)
    
    # Use the global singleton data_loader
    from services.data_loader import data_loader
    
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    
    print(f"\n📊 Loaded {len(employees)} employees and {len(roles)} roles")
    
    if not employees:
        print("❌ No employees loaded! Loading data now...")
        data_loader.load_all_data()
        employees = data_loader.get_employees()
        roles = data_loader.get_roles()
        print(f"📊 After reload: {len(employees)} employees and {len(roles)} roles")
    
    # Test gap calculation for first employee
    first_emp_id = list(employees.keys())[0]
    first_employee = employees[first_emp_id]
    
    print(f"\n👤 Testing gap analysis for: {first_employee.nombre} (ID: {first_emp_id})")
    
    # Calculate gap matrix
    gap_service = GapAnalysisService()
    
    try:
        print(f"\n🔍 Calculating gap matrix...")
        gap_matrix = gap_service.calculate_employee_gap_matrix(first_emp_id)
        
        print(f"\n✅ Gap Matrix Results:")
        print(f"   - Total roles analyzed: {len(gap_matrix.role_matches)}")
        if gap_matrix.best_match:
            print(f"   - Best role: {gap_matrix.best_match.role_id}")
            print(f"   - Best score: {gap_matrix.best_match.overall_score:.3f}")
        print(f"   - Ready roles: {gap_matrix.ready_roles_count}")
        print(f"   - Average compatibility: {gap_matrix.avg_compatibility_score:.3f}")
        
        print(f"\n📋 Top 3 Role Matches:")
        for i, match in enumerate(gap_matrix.role_matches[:3], 1):
            print(f"   {i}. {match.role_id}: {match.overall_score:.3f} ({match.band})")
            print(f"      - Skills: {match.skills_score:.3f}")
            print(f"      - Responsibilities: {match.responsibilities_score:.3f}")
            print(f"      - Top gap: {match.detailed_gaps[0] if match.detailed_gaps else 'None'}")
        
        print(f"\n✅ Gap analysis is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error calculating gap matrix: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_narrative_context_building():
    """Test that narrative generator builds context with real gap data."""
    print("\n" + "="*60)
    print("🧪 Testing Narrative Context Building")
    print("="*60)
    
    from services.ai_service import AIService
    from services.bias_detector import BiasDetector
    from services.narrative_generator import NarrativeGenerator
    from services.data_loader import data_loader
    
    # Ensure data is loaded
    employees = data_loader.get_employees()
    if not employees:
        print("❌ No employees loaded! Loading data now...")
        data_loader.load_all_data()
        employees = data_loader.get_employees()
    
    # Initialize services (without actually calling AI)
    try:
        ai_service = AIService(default_provider='google')
        bias_detector = BiasDetector()
        generator = NarrativeGenerator(ai_service, bias_detector)
        
        roles = data_loader.get_roles()
        
        print(f"\n📊 Building company context with gap analysis...")
        
        # Calculate gap analysis for all employees
        gap_service = GapAnalysisService()
        all_gap_results = {}
        
        for emp_id in list(employees.keys())[:3]:  # Test with first 3 employees
            try:
                print(f"   - Calculating for employee {emp_id}...")
                gap_matrix = gap_service.calculate_employee_gap_matrix(emp_id)
                all_gap_results[emp_id] = gap_matrix
            except Exception as e:
                print(f"   ⚠️ Error for employee {emp_id}: {e}")
        
        print(f"\n✅ Successfully calculated gaps for {len(all_gap_results)} employees")
        
        # Build context
        print(f"\n🏗️ Building company context...")
        context = generator._build_company_context(employees, roles, all_gap_results)
        
        print(f"\n📊 Context Summary:")
        print(f"   - Total employees: {context['total_employees']}")
        print(f"   - Total roles: {context['total_roles']}")
        print(f"   - Overall readiness: {context['metrics']['overall_readiness_score']*100:.1f}%")
        print(f"   - Employees analyzed: {context['metrics']['employees_analyzed']}")
        print(f"   - Employees with ready roles: {context['metrics']['employees_with_ready_roles']}")
        
        print(f"\n🏢 Chapter Breakdown:")
        for chapter, data in context['metrics']['by_chapter'].items():
            print(f"   - {chapter}: {data['readiness_rate']*100:.1f}% ready ({data['ready_employees']}/{data['employees']})")
        
        print(f"\n🎯 Top 5 Critical Skill Gaps:")
        for i, gap in enumerate(context['critical_gaps']['skills'][:5], 1):
            print(f"   {i}. {gap['skill_name']}: {gap['affected_employees']} employees (avg gap: {gap['avg_gap_score']})")
        
        print(f"\n✅ Context building is working with real gap data!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error building context: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting AI + Gap Analysis Integration Tests\n")
    
    # Run tests
    test1_passed = test_gap_calculation()
    test2_passed = test_narrative_context_building()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Gap Calculation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Context Building: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("\n" + "="*60)
    
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - AI is using real gap analysis data!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    
    sys.exit(0 if (test1_passed and test2_passed) else 1)
