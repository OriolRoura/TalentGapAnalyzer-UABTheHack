"""
Tests Unitarios para el Algoritmo de Talent Gap
==============================================

Suite básica de tests para validar funcionamiento del algoritmo.
Incluye tests para cada componente principal y casos edge.
"""

import unittest
from typing import Dict, List
import json
import os

# Importar módulos del algoritmo
from .models import Employee, Role, Skill, SkillLevel, GapBand, Chapter
from .gap_calculator import GapCalculator
from .ranking_engine import RankingEngine
from .gap_analyzer import GapAnalyzer
from .recommendation_engine import RecommendationEngine
from .talent_gap_algorithm import TalentGapAlgorithm


class TestModels(unittest.TestCase):
    """Tests para modelos de datos."""
    
    def test_skill_level_numeric_values(self):
        """Test conversión de niveles a valores numéricos."""
        self.assertEqual(SkillLevel.NOVATO.numeric_value, 0.25)
        self.assertEqual(SkillLevel.INTERMEDIO.numeric_value, 0.50)
        self.assertEqual(SkillLevel.AVANZADO.numeric_value, 0.75)
        self.assertEqual(SkillLevel.EXPERTO.numeric_value, 1.0)
    
    def test_skill_normalized_weight(self):
        """Test normalización de pesos de skills."""
        skill = Skill(
            id="TEST-SKILL",
            nombre="Test Skill",
            categoria="Test",
            peso=3.0,
            herramientas_asociadas=["Tool1"]
        )
        self.assertEqual(skill.normalized_weight, 0.6)  # 3/5
    
    def test_employee_skill_methods(self):
        """Test métodos de empleado para skills."""
        employee = Employee(
            id="EMP-001",
            nombre="Test Employee",
            chapter_actual="Strategy",
            skills={"S-OKR": SkillLevel.AVANZADO, "S-ANALISIS": SkillLevel.INTERMEDIO},
            responsabilidades_actuales=["Ejecutar OKRs"],
            ambiciones=["Liderar estrategia"],
            dedicacion_actual="30-40h/semana"
        )
        
        # Test get_skill_level
        self.assertEqual(employee.get_skill_level("S-OKR"), SkillLevel.AVANZADO)
        self.assertEqual(employee.get_skill_level("INEXISTENTE"), SkillLevel.NOVATO)
        
        # Test has_skill_at_level
        self.assertTrue(employee.has_skill_at_level("S-OKR", SkillLevel.INTERMEDIO))
        self.assertFalse(employee.has_skill_at_level("S-ANALISIS", SkillLevel.AVANZADO))
        
        # Test parse_dedication_hours
        min_hours, max_hours = employee.parse_dedication_hours()
        self.assertEqual((min_hours, max_hours), (30, 40))


class TestGapCalculator(unittest.TestCase):
    """Tests para el calculador de gaps."""
    
    def setUp(self):
        """Configurar datos de test."""
        self.skills_catalog = {
            "S-OKR": Skill("S-OKR", "OKRs y Roadmapping", "Estrategia", 5.0, ["Miro"]),
            "S-ANALISIS": Skill("S-ANALISIS", "Análisis Estratégico", "Estrategia", 3.0, ["Excel"])
        }
        
        self.calculator = GapCalculator(self.skills_catalog)
        
        self.employee = Employee(
            id="EMP-001",
            nombre="Juan Pérez",
            chapter_actual="Strategy",
            skills={"S-OKR": SkillLevel.INTERMEDIO, "S-ANALISIS": SkillLevel.AVANZADO},
            responsabilidades_actuales=["Ejecutar OKRs trimestrales", "Análisis de mercado"],
            ambiciones=["Liderar estrategia", "Definir OKRs"],
            dedicacion_actual="35-45h/semana"
        )
        
        self.role = Role(
            id="R-STR-LEAD",
            titulo="Head of Strategy",
            nivel="Lead",
            chapter="Strategy",
            habilidades_requeridas=["S-OKR", "S-ANALISIS"],
            responsabilidades=["Definir visión estratégica", "Liderar OKRs"],
            dedicacion_esperada="40-50h/semana"
        )
    
    def test_calculate_gap_basic(self):
        """Test cálculo básico de gap."""
        result = self.calculator.calculate_gap(self.employee, self.role)
        
        self.assertIsInstance(result.overall_score, float)
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 1.0)
        self.assertIn(result.band, list(GapBand))
        
        # Verificar componentes
        self.assertIn('skills', result.component_scores)
        self.assertIn('responsibilities', result.component_scores)
        self.assertIn('ambitions', result.component_scores)
        self.assertIn('dedication', result.component_scores)
    
    def test_skills_match_calculation(self):
        """Test específico del cálculo de skills match."""
        # Employee con skills perfectos
        perfect_employee = Employee(
            id="PERFECT",
            nombre="Perfect Employee",
            chapter_actual="Strategy",
            skills={"S-OKR": SkillLevel.EXPERTO, "S-ANALISIS": SkillLevel.EXPERTO},
            responsabilidades_actuales=["Test"],
            ambiciones=["Test"],
            dedicacion_actual="40h/semana"
        )
        
        skills_score = self.calculator._calculate_skills_match(perfect_employee, self.role)
        self.assertGreater(skills_score, 0.8)  # Debería ser muy alto
    
    def test_band_classification(self):
        """Test clasificación en bandas."""
        # Test diferentes scores
        self.assertEqual(self.calculator._classify_band(0.9), GapBand.READY)
        self.assertEqual(self.calculator._classify_band(0.75), GapBand.READY_WITH_SUPPORT)
        self.assertEqual(self.calculator._classify_band(0.55), GapBand.NEAR)
        self.assertEqual(self.calculator._classify_band(0.35), GapBand.FAR)
        self.assertEqual(self.calculator._classify_band(0.15), GapBand.NOT_VIABLE)


class TestRankingEngine(unittest.TestCase):
    """Tests para el motor de ranking."""
    
    def setUp(self):
        """Configurar datos de test."""
        self.ranking_engine = RankingEngine()
        
        # Crear matriz de compatibilidad mock
        from .models import CompatibilityMatrix, GapResult
        
        results = {
            "EMP-001": {
                "ROLE-001": GapResult("EMP-001", "ROLE-001", 0.85, GapBand.READY, {}, [], []),
                "ROLE-002": GapResult("EMP-001", "ROLE-002", 0.65, GapBand.NEAR, {}, [], [])
            },
            "EMP-002": {
                "ROLE-001": GapResult("EMP-002", "ROLE-001", 0.75, GapBand.READY_WITH_SUPPORT, {}, [], []),
                "ROLE-002": GapResult("EMP-002", "ROLE-002", 0.90, GapBand.READY, {}, [], [])
            }
        }
        
        self.compatibility_matrix = CompatibilityMatrix(results)
    
    def test_generate_role_rankings(self):
        """Test generación de rankings por rol."""
        roles = {
            "ROLE-001": Role("ROLE-001", "Test Role 1", "Senior", "Test", [], [], "40h/semana"),
            "ROLE-002": Role("ROLE-002", "Test Role 2", "Lead", "Test", [], [], "40h/semana")
        }
        
        rankings = self.ranking_engine.generate_role_rankings(
            self.compatibility_matrix, roles
        )
        
        self.assertIn("ROLE-001", rankings)
        self.assertIn("ROLE-002", rankings)
        
        # Verificar orden correcto para ROLE-001 (EMP-001 tiene mejor score)
        role1_candidates = rankings["ROLE-001"]
        self.assertGreater(len(role1_candidates), 0)
        self.assertEqual(role1_candidates[0].employee_id, "EMP-001")  # Mejor score
    
    def test_detect_conflicts(self):
        """Test detección de conflictos de asignación."""
        rankings = {
            "ROLE-001": [
                self.compatibility_matrix.results["EMP-001"]["ROLE-001"],
                self.compatibility_matrix.results["EMP-002"]["ROLE-001"]
            ],
            "ROLE-002": [
                self.compatibility_matrix.results["EMP-002"]["ROLE-002"],
                self.compatibility_matrix.results["EMP-001"]["ROLE-002"]
            ]
        }
        
        conflicts = self.ranking_engine.detect_assignment_conflicts(rankings, top_n=2)
        
        # Ambos empleados aparecen en top de ambos roles
        self.assertIn("EMP-001", conflicts)
        self.assertIn("EMP-002", conflicts)


class TestIntegration(unittest.TestCase):
    """Tests de integración completa."""
    
    def setUp(self):
        """Configurar datos de integración."""
        # Crear configuración mock
        self.org_config = {
            "organization": {
                "nombre": "Test Org",
                "direccion": "Test Address",
                "descripcion": "Test Description"
            },
            "chapters": [
                {
                    "nombre": "Strategy",
                    "descripción": "Strategy chapter",
                    "role_templates": ["R-STR-LEAD"]
                }
            ],
            "roles": [
                {
                    "id": "R-STR-LEAD",
                    "título": "Head of Strategy",
                    "nivel": "Lead",
                    "responsabilidades": ["Definir estrategia"],
                    "habilidades_requeridas": ["S-OKR"],
                    "dedicación_esperada": "40h/semana"
                }
            ],
            "skills": [
                {
                    "id": "S-OKR",
                    "nombre": "OKRs y Roadmapping",
                    "categoría": "Estrategia",
                    "peso": 5,
                    "herramientas_asociadas": ["Miro"]
                }
            ]
        }
        
        self.vision_futura = {
            "organization": {"nombre": "Test Org"},
            "roles_necesarios": [
                {
                    "id": "R-STR-LEAD",
                    "título": "Head of Strategy",
                    "nivel": "Lead",
                    "capítulo": "Strategy"
                }
            ]
        }
        
        self.employees_data = [
            {
                "id": "EMP-001",
                "nombre": "Juan Pérez",
                "chapter_actual": "Strategy",
                "skills": {"S-OKR": SkillLevel.AVANZADO},
                "responsabilidades_actuales": ["Ejecutar OKRs"],
                "ambiciones": ["Liderar estrategia"],
                "dedicacion_actual": "35-45h/semana"
            }
        ]
    
    def test_full_algorithm_workflow(self):
        """Test del flujo completo del algoritmo."""
        # Inicializar algoritmo
        algorithm = TalentGapAlgorithm(self.org_config, self.vision_futura)
        
        # Cargar empleados
        algorithm.load_employees_data(self.employees_data)
        self.assertEqual(len(algorithm.employees), 1)
        
        # Ejecutar análisis completo
        results = algorithm.run_full_analysis()
        
        # Verificar estructura de resultados
        self.assertIn('metadata', results)
        self.assertIn('compatibility_matrix', results)
        self.assertIn('rankings', results)
        self.assertIn('gap_analysis', results)
        self.assertIn('recommendations', results)
        self.assertIn('executive_summary', results)
        
        # Verificar métricas básicas
        metadata = results['metadata']
        self.assertEqual(metadata['total_employees'], 1)
        self.assertGreater(metadata['total_roles'], 0)
        self.assertGreater(metadata['total_skills'], 0)
    
    def test_employee_specific_analysis(self):
        """Test análisis específico de empleado."""
        algorithm = TalentGapAlgorithm(self.org_config, self.vision_futura)
        algorithm.load_employees_data(self.employees_data)
        algorithm.run_full_analysis()
        
        # Análisis específico de empleado
        emp_analysis = algorithm.get_employee_analysis("EMP-001")
        
        self.assertIn('employee_info', emp_analysis)
        self.assertIn('career_options', emp_analysis)
        self.assertIn('recommendations', emp_analysis)
        self.assertIn('development_priority', emp_analysis)
        
        # Verificar datos del empleado
        emp_info = emp_analysis['employee_info']
        self.assertEqual(emp_info['id'], "EMP-001")
        self.assertEqual(emp_info['nombre'], "Juan Pérez")
    
    def test_role_specific_analysis(self):
        """Test análisis específico de rol."""
        algorithm = TalentGapAlgorithm(self.org_config, self.vision_futura)
        algorithm.load_employees_data(self.employees_data)
        algorithm.run_full_analysis()
        
        # Análisis específico de rol
        role_analysis = algorithm.get_role_analysis("R-STR-LEAD")
        
        self.assertIn('role_info', role_analysis)
        self.assertIn('candidates', role_analysis)
        self.assertIn('hiring_recommendation', role_analysis)
        self.assertIn('succession_plan', role_analysis)


class TestDataValidation(unittest.TestCase):
    """Tests de validación de datos."""
    
    def test_invalid_employee_data(self):
        """Test manejo de datos inválidos de empleados."""
        invalid_data = [
            {
                "id": "INVALID",
                # Faltan campos requeridos
            }
        ]
        
        algorithm = TalentGapAlgorithm({}, {})
        
        # No debería crashear, pero tampoco debería cargar empleados inválidos
        algorithm.load_employees_data(invalid_data)
        self.assertEqual(len(algorithm.employees), 0)
    
    def test_empty_analysis(self):
        """Test análisis sin empleados."""
        algorithm = TalentGapAlgorithm({}, {})
        
        with self.assertRaises(ValueError):
            algorithm.run_full_analysis()


def run_tests():
    """Ejecutar todos los tests."""
    print("🧪 Running Algorithm Tests...")
    
    # Crear test suite
    test_suite = unittest.TestSuite()
    
    # Agregar test cases
    test_classes = [
        TestModels,
        TestGapCalculator,
        TestRankingEngine,
        TestIntegration,
        TestDataValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Resumen
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()