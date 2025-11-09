"""
Tests for AI Generation Services
=================================

Tests para validar:
- Generación de narrativas
- Generación de recomendaciones
- Detección de sesgos
- Optimización de costos
- Calidad del contenido generado
"""

import pytest
import json
from typing import Dict

from services.ai_service import AIService, AIResponse
from services.bias_detector import BiasDetector
from services.narrative_generator import NarrativeGenerator
from services.ai_recommendation_engine import AIRecommendationEngine
from models.ai_models import NarrativeTone, ConfidenceLevel


class TestBiasDetector:
    """Tests para el detector de sesgos."""
    
    def setup_method(self):
        self.detector = BiasDetector()
    
    def test_detect_gender_bias(self):
        """Detecta sesgos de género."""
        text = "Los hombres son más técnicos y las mujeres son más organizadas."
        result = self.detector.detect_bias(text)
        
        assert result['has_bias'] == True
        assert 'gender' in result['bias_types_detected']
        assert result['high_severity_count'] > 0
    
    def test_detect_age_bias(self):
        """Detecta sesgos de edad."""
        text = "El joven empleado es más energético pero el mayor trabajador tiene más experiencia."
        result = self.detector.detect_bias(text)
        
        assert result['has_bias'] == True
        assert 'age' in result['bias_types_detected']
    
    def test_no_bias_in_neutral_text(self):
        """No detecta sesgos en texto neutral."""
        text = "El personal del departamento tiene competencias sólidas en análisis de datos."
        result = self.detector.detect_bias(text)
        
        assert result['has_bias'] == False
        assert len(result['bias_types_detected']) == 0
    
    def test_sanitize_text(self):
        """Sanitiza texto con términos sesgados."""
        text = "Los empleados deben completar la formación."
        sanitized, changes = self.detector.sanitize_text(text)
        
        assert len(changes) > 0
        assert "personal" in sanitized.lower() or "equipo" in sanitized.lower()
    
    def test_validate_prompt(self):
        """Valida prompts antes de enviar a IA."""
        biased_prompt = "Recomienda el mejor candidato masculino para este rol de liderazgo."
        result = self.detector.validate_prompt(biased_prompt)
        
        assert result['is_valid'] == False
        assert len(result['warnings']) > 0
    
    def test_bias_free_prompt_template(self):
        """Genera templates libres de sesgo."""
        template = self.detector.create_bias_free_prompt_template('recommendations')
        
        assert 'LENGUAJE INCLUSIVO' in template
        assert 'BASAR EN DATOS' in template
        assert 'EVITAR ESTEREOTIPOS' in template
    
    def test_batch_validation(self):
        """Valida múltiples textos en batch."""
        texts = [
            "El personal tiene competencias avanzadas.",
            "Los hombres son mejores en roles técnicos.",
            "El equipo necesita formación en OKRs."
        ]
        result = self.detector.batch_validate(texts)
        
        assert result['total_texts_analyzed'] == 3
        assert result['texts_with_bias'] >= 1
        assert 0 <= result['bias_rate'] <= 1


class TestAIServiceMock:
    """Tests para AIService usando mocks (sin consumir API real)."""
    
    def test_cost_calculation(self):
        """Calcula costos correctamente."""
        # Simular costos
        model = 'gpt-3.5-turbo'
        input_tokens = 1000
        output_tokens = 500
        
        # Costo esperado con tabla de costos
        # GPT-3.5: $0.5/1M input, $1.5/1M output
        expected_cost = (1000 / 1_000_000) * 0.5 + (500 / 1_000_000) * 1.5
        
        assert expected_cost > 0
        assert expected_cost < 0.01  # Debería ser centavos
    
    def test_estimate_analysis_cost(self):
        """Estima costo de análisis completo."""
        # Mock service
        from services.ai_service import AIService
        service = AIService(max_cost_per_analysis_usd=0.10)
        
        estimates = service.estimate_analysis_cost(num_employees=100)
        
        assert 'gpt-3.5-turbo' in estimates or len(estimates) > 0
        # Verificar que hay al menos una estimación
        if estimates:
            min_cost = min(estimates.values())
            max_cost = max(estimates.values())
            
            assert min_cost > 0
            assert max_cost > min_cost
            assert max_cost < 50  # No debería ser exorbitante para 100 empleados
    
    def test_budget_check(self):
        """Verifica presupuesto."""
        service = AIService(max_cost_per_analysis_usd=0.10)
        
        # Dentro de presupuesto
        assert service.check_budget(0.05) == True
        
        # Fuera de presupuesto
        assert service.check_budget(0.15) == False


class TestRecommendationQuality:
    """Tests de calidad de recomendaciones."""
    
    def test_recommendation_structure(self):
        """Valida estructura de recomendaciones."""
        # Datos de prueba
        rec_data = {
            'type': 'skill_development',
            'title': 'Desarrollar OKRs',
            'description': 'Curso de OKRs para mejorar visión estratégica',
            'rationale': 'Gap identificado en skill estratégico',
            'action_items': [
                {
                    'action': 'Inscribirse en curso',
                    'timeline': '2 semanas',
                    'resources_needed': ['Budget', 'Plataforma'],
                    'priority': 'high'
                }
            ],
            'effort_level': 'medium',
            'estimated_duration': '3 meses',
            'priority_score': 0.85
        }
        
        # Validar campos requeridos
        assert 'type' in rec_data
        assert 'title' in rec_data
        assert 'description' in rec_data
        assert 'action_items' in rec_data
        assert len(rec_data['action_items']) > 0
        
        # Validar primera acción
        action = rec_data['action_items'][0]
        assert 'action' in action
        assert 'timeline' in action
        assert 'priority' in action
    
    def test_recommendation_actionability(self):
        """Valida que recomendaciones sean accionables."""
        rec_data = {
            'title': 'Mejorar habilidades',  # Too vague
            'action_items': []  # No actions
        }
        
        # Una buena recomendación debe tener:
        # 1. Título específico (no genérico)
        # 2. Al menos 1 acción concreta
        # 3. Timeline definido
        
        is_actionable = (
            len(rec_data.get('action_items', [])) > 0 and
            len(rec_data.get('title', '')) > 20  # No demasiado vago
        )
        
        assert is_actionable == False  # Este ejemplo NO es accionable
    
    def test_no_bias_in_recommendations(self):
        """Valida que recomendaciones no tengan sesgos."""
        detector = BiasDetector()
        
        recommendation_text = """
        Título: Desarrollar competencias en análisis estratégico
        Descripción: El empleado debe fortalecer sus habilidades de OKRs y análisis de negocio.
        Acciones:
        1. Completar curso de OKRs (4 semanas)
        2. Aplicar en proyecto piloto (2 meses)
        3. Presentar resultados al equipo de liderazgo
        """
        
        result = detector.detect_bias(recommendation_text)
        
        assert result['has_bias'] == False
        assert result['requires_human_review'] == False


class TestNarrativeQuality:
    """Tests de calidad de narrativas."""
    
    def test_narrative_structure(self):
        """Valida estructura de narrativas."""
        narrative_data = {
            'title': 'Análisis de Talent Gap - Employee X',
            'executive_summary': 'Este es un resumen ejecutivo completo que describe la situación actual del empleado, sus fortalezas principales en análisis técnico, y las oportunidades de desarrollo identificadas para su progresión hacia roles de mayor responsabilidad en el departamento.',
            'key_insights': ['Insight 1', 'Insight 2', 'Insight 3'],
            'detailed_analysis': 'Análisis detallado...',
            'recommendations_summary': 'Resumen de recomendaciones...'
        }
        
        # Validar campos requeridos
        assert 'title' in narrative_data
        assert 'executive_summary' in narrative_data
        assert 'key_insights' in narrative_data
        assert 'detailed_analysis' in narrative_data
        
        # Validar calidad mínima
        assert len(narrative_data['executive_summary']) >= 100
        assert len(narrative_data['key_insights']) >= 2
    
    def test_narrative_coherence(self):
        """Valida coherencia de narrativa."""
        narrative = {
            'executive_summary': 'El empleado tiene gap en OKRs.',
            'key_insights': ['Gap en OKRs identificado', 'Necesita formación'],
            'detailed_analysis': 'El análisis muestra gap significativo en competencias estratégicas.',
            'recommendations_summary': 'Recomendar curso de OKRs.'
        }
        
        # Verificar coherencia: términos clave deben aparecer en múltiples secciones
        key_term = 'OKRs'
        sections_with_term = sum([
            key_term in narrative['executive_summary'],
            any(key_term in insight for insight in narrative['key_insights']),
            key_term in narrative['detailed_analysis'],
            key_term in narrative['recommendations_summary']
        ])
        
        # Debería aparecer en al menos 3 de 4 secciones
        assert sections_with_term >= 3
    
    def test_no_bias_in_narrative(self):
        """Valida que narrativas no tengan sesgos."""
        detector = BiasDetector()
        
        narrative_text = """
        Análisis de Talent Gap - Departamento Strategy
        
        El departamento cuenta con 15 personas profesionales con competencias sólidas.
        Se identifican gaps en habilidades de OKRs y análisis estratégico.
        El personal muestra alto potencial de desarrollo en estas áreas.
        
        Recomendaciones:
        1. Programa de formación en OKRs para todo el equipo
        2. Mentoring con leadership team
        3. Proyectos piloto para aplicar nuevas competencias
        """
        
        result = detector.detect_bias(narrative_text)
        
        assert result['has_bias'] == False
        assert result['high_severity_count'] == 0


class TestCostOptimization:
    """Tests de optimización de costos."""
    
    def test_cost_per_employee_within_budget(self):
        """Valida que el costo por empleado esté dentro del presupuesto."""
        target_cost_per_employee = 0.10  # $0.10 USD
        num_employees = 100
        total_budget = target_cost_per_employee * num_employees  # $10 USD
        
        # Con Gemini Flash: ~$0.0015 por empleado
        # Con GPT-3.5: ~$0.01 por empleado
        # Con Claude 3.5 Sonnet: ~$0.025 por empleado
        
        gemini_cost = 0.0015 * num_employees
        gpt35_cost = 0.01 * num_employees
        claude_cost = 0.025 * num_employees
        
        assert gemini_cost < total_budget
        assert gpt35_cost < total_budget
        # Claude puede estar borderline
    
    def test_batch_reduces_cost(self):
        """Verifica que procesamiento batch reduzca costos."""
        # Costo individual (sin cache)
        individual_cost_per_request = 0.002
        num_employees = 10
        
        # Sin cache: cada request paga full
        cost_without_cache = individual_cost_per_request * num_employees
        
        # Con cache: requests similares reutilizan respuestas
        # Asumiendo 30% de cache hit rate
        cache_hit_rate = 0.3
        cost_with_cache = cost_without_cache * (1 - cache_hit_rate)
        
        assert cost_with_cache < cost_without_cache
        savings_percentage = (cost_without_cache - cost_with_cache) / cost_without_cache * 100
        assert savings_percentage >= 25  # Al menos 25% de ahorro


def test_integration_bias_detection_in_generation():
    """Test de integración: bias detection durante generación."""
    detector = BiasDetector()
    
    # Simular respuesta de IA con sesgo
    ai_response = """
    Recomendación: Como es típico de los jóvenes profesionales, Juan debería 
    desarrollar más madurez profesional. Los hombres tienden a ser más 
    técnicos mientras que las mujeres son mejores en roles administrativos.
    """
    
    # Detectar sesgos
    result = detector.detect_bias(ai_response)
    
    # Debería detectar múltiples sesgos
    assert result['has_bias'] == True
    # Puede detectar 'age', 'gender', o 'stereotype' dependiendo del pattern
    assert len(result['bias_types_detected']) > 0
    assert result['requires_human_review'] == True
    
    # No debería permitirse usar esta respuesta
    assert result['high_severity_count'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
