"""
Bias Detection Service
======================

Detecta y mitiga sesgos en contenido generado por IA.

Tipos de sesgos detectados:
- Género (referencias desbalanceadas a géneros)
- Edad (suposiciones basadas en edad/antigüedad)
- Origen/Nacionalidad (referencias étnicas o geográficas)
- Discapacidad (lenguaje discriminatorio)
- Estereotipos profesionales (roles asociados a género/edad)

Estrategias:
1. Pre-generación: Guardrails en prompts
2. Post-generación: Análisis de contenido generado
3. Validación: Checks automáticos y manual review triggers
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BiasPattern:
    """Patrón de sesgo a detectar."""
    category: str
    pattern: str  # Regex pattern
    severity: str  # 'high', 'medium', 'low'
    description: str
    mitigation: str


class BiasDetector:
    """
    Detector de sesgos en contenido generado por IA.
    """
    
    def __init__(self):
        self.bias_patterns = self._initialize_bias_patterns()
        self.neutral_language_guide = self._initialize_neutral_language()
    
    def _initialize_bias_patterns(self) -> List[BiasPattern]:
        """Inicializa patrones de detección de sesgos."""
        patterns = []
        
        # GÉNERO
        patterns.extend([
            BiasPattern(
                category='gender',
                pattern=r'\b(él|ella|masculino|femenino)\b(?!.*\b(independientemente|sin importar|cualquier)\b)',
                severity='high',
                description='Referencias explícitas a género sin justificación',
                mitigation='Usar lenguaje neutral o inclusivo'
            ),
            BiasPattern(
                category='gender',
                pattern=r'\b(hombres|mujeres)\s+(son|tienden|suelen)\b',
                severity='high',
                description='Generalización por género',
                mitigation='Evitar generalizaciones basadas en género'
            ),
            BiasPattern(
                category='gender',
                pattern=r'\b(líder|ingeniero|secretaria|enfermera)\b.*\b(él|ella)\b',
                severity='medium',
                description='Asociación de roles con género específico',
                mitigation='Usar lenguaje neutro para roles profesionales'
            )
        ])
        
        # EDAD
        patterns.extend([
            BiasPattern(
                category='age',
                pattern=r'\b(joven|viejo|mayor|antiguo)\s+(empleado|profesional|trabajador)\b',
                severity='high',
                description='Referencias a edad de forma innecesaria',
                mitigation='Evitar mencionar edad salvo sea estrictamente relevante'
            ),
            BiasPattern(
                category='age',
                pattern=r'\b(millennials?|generación [XYZ]|boomers?)\b',
                severity='medium',
                description='Estereotipos generacionales',
                mitigation='Evitar categorizar por generación'
            ),
            BiasPattern(
                category='age',
                pattern=r'\b(demasiado (joven|viejo)|muy (senior|junior))\b',
                severity='high',
                description='Juicios basados en edad/antigüedad',
                mitigation='Basar evaluaciones en competencias, no edad'
            )
        ])
        
        # ORIGEN/NACIONALIDAD
        patterns.extend([
            BiasPattern(
                category='origin',
                pattern=r'\b(español|extranjero|latino|asiático|africano|europeo)\s+(empleado|trabajador)\b',
                severity='high',
                description='Referencias a origen étnico/nacional',
                mitigation='No mencionar origen salvo sea relevante para visas/permisos'
            ),
            BiasPattern(
                category='origin',
                pattern=r'\b(acento|cultura|tradición)\s+(de su país|nativa|extranjera)\b',
                severity='medium',
                description='Referencias a diferencias culturales',
                mitigation='Evitar mencionar diferencias culturales'
            )
        ])
        
        # DISCAPACIDAD
        patterns.extend([
            BiasPattern(
                category='disability',
                pattern=r'\b(limitación|impedimento|deficiencia|incapacidad)\b',
                severity='high',
                description='Lenguaje discriminatorio sobre capacidades',
                mitigation='Usar lenguaje inclusivo y respetuoso'
            ),
            BiasPattern(
                category='disability',
                pattern=r'\b(normal|anormal|sufre de|padece)\b',
                severity='high',
                description='Lenguaje que implica condiciones como defectos',
                mitigation='Usar lenguaje neutral y objetivo'
            )
        ])
        
        # ESTEREOTIPOS PROFESIONALES
        patterns.extend([
            BiasPattern(
                category='stereotype',
                pattern=r'\b(como es típico|como suele pasar|la mayoría de)\s+los?\s+(hombres|mujeres|jóvenes|mayores)\b',
                severity='high',
                description='Estereotipos profesionales',
                mitigation='Basar recomendaciones en datos individuales, no estereotipos'
            ),
            BiasPattern(
                category='stereotype',
                pattern=r'\b(apto para|ideal para|mejor suited para)\s+(hombres|mujeres|jóvenes)\b',
                severity='high',
                description='Roles asociados a grupos demográficos',
                mitigation='No asociar roles con características demográficas'
            )
        ])
        
        # LENGUAJE NO INCLUSIVO
        patterns.extend([
            BiasPattern(
                category='language',
                pattern=r'\b(los empleados|los profesionales|los trabajadores)\b(?!.*\b(y empleadas|y profesionales|y trabajadoras)\b)',
                severity='low',
                description='Lenguaje no inclusivo (masculino genérico)',
                mitigation='Usar lenguaje inclusivo: "el personal", "las personas"'
            ),
            BiasPattern(
                category='language',
                pattern=r'\b(padre de familia|ama de casa|cabeza de familia)\b',
                severity='medium',
                description='Términos con connotaciones de género',
                mitigation='Usar términos neutrales'
            )
        ])
        
        return patterns
    
    def _initialize_neutral_language(self) -> Dict[str, str]:
        """Guía de lenguaje neutral."""
        return {
            'los empleados': 'el personal / las personas empleadas',
            'los trabajadores': 'el personal / el equipo',
            'los profesionales': 'las personas profesionales / el equipo',
            'él/ella': 'la persona / el empleado/a',
            'líder masculino': 'líder',
            'ingeniero/a': 'profesional de ingeniería',
            'joven empleado': 'empleado en etapa temprana / empleado junior',
            'empleado senior': 'empleado con experiencia / empleado de nivel senior',
            'antigüedad': 'experiencia / trayectoria',
        }
    
    def detect_bias(self, text: str) -> Dict[str, any]:
        """
        Detecta sesgos en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con resultados de detección
        """
        detections = []
        text_lower = text.lower()
        
        for pattern in self.bias_patterns:
            matches = re.finditer(pattern.pattern, text_lower, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'category': pattern.category,
                    'severity': pattern.severity,
                    'matched_text': match.group(0),
                    'position': match.span(),
                    'description': pattern.description,
                    'mitigation': pattern.mitigation
                })
        
        # Calcular score de sesgo
        has_bias = len(detections) > 0
        high_severity_count = len([d for d in detections if d['severity'] == 'high'])
        
        # Confidence basado en número y severidad de detecciones
        if high_severity_count >= 2:
            confidence = 0.95
        elif high_severity_count == 1:
            confidence = 0.80
        elif len(detections) >= 3:
            confidence = 0.70
        elif len(detections) > 0:
            confidence = 0.60
        else:
            confidence = 0.95  # Alta confianza en ausencia de sesgo
        
        # Categorías únicas detectadas
        categories = list(set([d['category'] for d in detections]))
        
        # Recomendaciones
        recommendations = self._generate_bias_mitigation_recommendations(detections)
        
        return {
            'has_bias': has_bias,
            'bias_score': min(len(detections) / 10.0, 1.0),  # 0-1
            'confidence': confidence,
            'total_detections': len(detections),
            'high_severity_count': high_severity_count,
            'bias_types_detected': categories,
            'flagged_content': detections,
            'recommendations': recommendations,
            'requires_human_review': high_severity_count > 0
        }
    
    def _generate_bias_mitigation_recommendations(self, detections: List[Dict]) -> List[str]:
        """Genera recomendaciones específicas para mitigar sesgos detectados."""
        recommendations = []
        
        categories_found = set([d['category'] for d in detections])
        
        if 'gender' in categories_found:
            recommendations.append('Usar lenguaje inclusivo y neutro en género')
            recommendations.append('Basar recomendaciones en competencias, no en género')
        
        if 'age' in categories_found:
            recommendations.append('Evitar referencias a edad o antigüedad innecesarias')
            recommendations.append('Enfocarse en skills y experiencia relevante, no edad')
        
        if 'origin' in categories_found:
            recommendations.append('No mencionar origen étnico o nacional salvo sea legalmente relevante')
        
        if 'disability' in categories_found:
            recommendations.append('Usar lenguaje respetuoso e inclusivo respecto a capacidades')
        
        if 'stereotype' in categories_found:
            recommendations.append('Evitar estereotipos profesionales basados en demografía')
            recommendations.append('Personalizar recomendaciones basándose en datos individuales')
        
        if 'language' in categories_found:
            recommendations.append('Adoptar lenguaje inclusivo consistente')
        
        # Recomendación general
        if recommendations:
            recommendations.insert(0, 'GENERAL: Revisar todo el contenido para eliminar sesgos identificados')
        
        return recommendations
    
    def sanitize_text(self, text: str, strict_mode: bool = False) -> Tuple[str, List[str]]:
        """
        Intenta sanitizar un texto reemplazando términos sesgados.
        
        Args:
            text: Texto a sanitizar
            strict_mode: Si True, reemplaza todo. Si False, solo términos críticos.
            
        Returns:
            (texto_sanitizado, cambios_realizados)
        """
        sanitized = text
        changes = []
        
        # Aplicar reemplazos de lenguaje neutral
        for biased, neutral in self.neutral_language_guide.items():
            if biased in sanitized.lower():
                # Reemplazar manteniendo capitalización
                pattern = re.compile(re.escape(biased), re.IGNORECASE)
                matches = pattern.findall(sanitized)
                for match in matches:
                    sanitized = sanitized.replace(match, neutral)
                    changes.append(f'Reemplazado "{match}" por "{neutral}"')
        
        return sanitized, changes
    
    def validate_prompt(self, prompt: str) -> Dict[str, any]:
        """
        Valida un prompt antes de enviarlo a la IA para prevenir sesgos.
        
        Args:
            prompt: Prompt a validar
            
        Returns:
            Resultado de validación con warnings
        """
        result = self.detect_bias(prompt)
        
        warnings = []
        if result['has_bias']:
            warnings.append('⚠️ El prompt contiene potenciales sesgos que pueden propagarse a la respuesta')
            warnings.extend(result['recommendations'])
        
        # Checks adicionales en prompts
        if 'mejor candidato' in prompt.lower() and not any(
            word in prompt.lower() for word in ['competencias', 'skills', 'experiencia']
        ):
            warnings.append('⚠️ Asegurar que criterios de evaluación sean objetivos y basados en competencias')
        
        return {
            'is_valid': not result['requires_human_review'],
            'bias_detected': result['has_bias'],
            'warnings': warnings,
            'full_analysis': result
        }
    
    def create_bias_free_prompt_template(self, context: str = 'general') -> str:
        """
        Crea template de prompt con guardrails contra sesgos.
        
        Args:
            context: Contexto del análisis ('recommendations', 'narrative', 'general')
            
        Returns:
            Template de prompt con guardrails incorporados
        """
        base_guardrails = """
INSTRUCCIONES CRÍTICAS - NEUTRALIDAD Y EQUIDAD:

1. LENGUAJE INCLUSIVO: Usar siempre lenguaje neutral en género (ej: "el personal", "las personas")
2. NO ASUMIR GÉNERO: No hacer suposiciones sobre género de personas
3. NO MENCIONAR EDAD: No referenciar edad o antigüedad de forma innecesaria
4. NO MENCIONAR ORIGEN: No hacer referencias a nacionalidad, origen étnico, o cultural
5. BASAR EN DATOS: Todas las recomendaciones deben basarse EXCLUSIVAMENTE en:
   - Competencias técnicas (skills)
   - Experiencia profesional relevante
   - Responsabilidades actuales
   - Ambiciones profesionales declaradas
   - Performance objetiva

6. EVITAR ESTEREOTIPOS: No usar estereotipos profesionales asociados a grupos demográficos
7. SER OBJETIVO: Usar métricas y datos cuantitativos cuando sea posible

Si no hay datos suficientes para una recomendación objetiva, indicarlo explícitamente.
"""
        
        if context == 'recommendations':
            specific = """
CONTEXTO: Recomendaciones de desarrollo profesional

FOCO: Personalizar recomendaciones basándose en:
- Gap específico de skills identificado
- Ambiciones profesionales del empleado
- Trayectoria de carrera individual
- Oportunidades de desarrollo disponibles

NO incluir suposiciones sobre capacidades basadas en características personales.
"""
        elif context == 'narrative':
            specific = """
CONTEXTO: Narrativa ejecutiva

FOCO: Análisis agregado y trends organizacionales
- Usar estadísticas y métricas agregadas
- Identificar patterns en datos, no en personas
- Hacer recomendaciones estratégicas objetivas
"""
        else:
            specific = ""
        
        return base_guardrails + specific
    
    def get_bias_report(self, detections: List[Dict]) -> str:
        """Genera reporte legible de sesgos detectados."""
        if not detections:
            return "✅ No se detectaron sesgos en el contenido analizado."
        
        report = "⚠️ REPORTE DE SESGOS DETECTADOS\n"
        report += "=" * 50 + "\n\n"
        
        by_category = {}
        for d in detections:
            cat = d['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(d)
        
        for category, items in by_category.items():
            report += f"\n📊 Categoría: {category.upper()}\n"
            report += f"   Detecciones: {len(items)}\n"
            for item in items:
                report += f"   - [{item['severity']}] {item['matched_text']}\n"
                report += f"     Razón: {item['description']}\n"
                report += f"     Mitigación: {item['mitigation']}\n"
        
        return report
    
    def batch_validate(self, texts: List[str]) -> Dict[str, any]:
        """
        Valida múltiples textos en batch.
        
        Args:
            texts: Lista de textos a validar
            
        Returns:
            Reporte agregado de validación
        """
        results = [self.detect_bias(text) for text in texts]
        
        total_texts = len(texts)
        texts_with_bias = sum(1 for r in results if r['has_bias'])
        total_detections = sum(r['total_detections'] for r in results)
        
        all_categories = set()
        for r in results:
            all_categories.update(r['bias_types_detected'])
        
        return {
            'total_texts_analyzed': total_texts,
            'texts_with_bias': texts_with_bias,
            'bias_rate': texts_with_bias / total_texts if total_texts > 0 else 0,
            'total_detections': total_detections,
            'categories_found': list(all_categories),
            'requires_review': any(r['requires_human_review'] for r in results),
            'individual_results': results
        }
