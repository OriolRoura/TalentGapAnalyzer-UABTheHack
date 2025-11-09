"""
Debug script to compare algorithm inputs between main_challenge.py and API
"""
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent))

from services.data_loader import data_loader
from services.model_adapter import ModelAdapter
from algorithm.models import SkillLevel

# Load data
print("=" * 80)
print("DEBUGGING ALGORITHM INPUTS")
print("=" * 80)

employees = data_loader.get_employees()
roles = data_loader.get_roles()

# Test employee 1001
emp = employees[1001]
print(f"\n📋 API Employee 1001 - {emp.nombre}")
print(f"   ID: {emp.id_empleado}")
print(f"   Chapter: {emp.chapter}")
print(f"   Skills (raw): {emp.habilidades}")
print(f"   Responsabilidades: {emp.responsabilidades_actuales}")
print(f"   Ambiciones: {emp.ambiciones}")
print(f"   Dedicación: {emp.dedicacion_actual}")

# Convert to algorithm format
algo_emp = ModelAdapter.api_employee_to_algo(emp)
print(f"\n🔄 Algorithm Employee (converted):")
print(f"   ID: {algo_emp.id}")
print(f"   Nombre: {algo_emp.nombre}")
print(f"   Chapter: {algo_emp.chapter_actual}")
print(f"   Skills (converted):")
for skill_id, level in algo_emp.skills.items():
    print(f"      {skill_id}: {level.value} (numeric: {level.numeric_value})")
print(f"   Responsabilidades: {algo_emp.responsabilidades_actuales}")
print(f"   Ambiciones: {algo_emp.ambiciones}")
print(f"   Dedicación: {algo_emp.dedicacion_actual}")

# Test 2 roles
print(f"\n📊 Testing Roles:")
role1 = roles['R-STR-LEAD']
role2 = roles['R-PM']

print(f"\n   Role 1: {role1.titulo} ({role1.id})")
print(f"      Habilidades requeridas: {role1.habilidades_requeridas}")
print(f"      Responsabilidades: {role1.responsabilidades}")
print(f"      Dedicación esperada: {role1.dedicacion_esperada}")

print(f"\n   Role 2: {role2.titulo} ({role2.id})")
print(f"      Habilidades requeridas: {role2.habilidades_requeridas}")
print(f"      Responsabilidades: {role2.responsabilidades}")
print(f"      Dedicación esperada: {role2.dedicacion_esperada}")

# Now run the algorithm
from services.gap_service import GapAnalysisService

print(f"\n🧮 Running Algorithm...")
print("=" * 80)

gap1 = GapAnalysisService.calculate_gap(emp, role1)
print(f"\nGap for {role1.titulo}:")
print(f"   Overall score: {gap1.overall_gap_score:.1f}% gap")
print(f"   Classification: {gap1.classification}")
print(f"   Skills gap: {gap1.skill_gaps}")
print(f"   Responsibilities gap: {gap1.responsibilities_gap:.1f}%")
print(f"   Ambitions alignment: {gap1.ambitions_alignment:.1f}%")
print(f"   Dedication availability: {gap1.dedication_availability:.1f}%")

gap2 = GapAnalysisService.calculate_gap(emp, role2)
print(f"\nGap for {role2.titulo}:")
print(f"   Overall score: {gap2.overall_gap_score:.1f}% gap")
print(f"   Classification: {gap2.classification}")
print(f"   Skills gap: {gap2.skill_gaps}")
print(f"   Responsibilities gap: {gap2.responsibilities_gap:.1f}%")
print(f"   Ambitions alignment: {gap2.ambitions_alignment:.1f}%")
print(f"   Dedication availability: {gap2.dedication_availability:.1f}%")

print("\n" + "=" * 80)
print("EXPECTED FROM main_challenge.py CSV:")
print("   Jordi -> R-STR-LEAD: overall=0.88, skills=1.0, resp=1.0, amb=0.2, ded=1.0")
print("   Jordi -> R-PM: overall=0.225, skills=0.0, resp=0.5, amb=0.0, ded=1.0")
print("=" * 80)
