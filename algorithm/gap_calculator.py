"""
Motor de Cálculo de Gaps - Core del Algoritmo
============================================

Implementa la lógica principal para calcular la compatibilidad entre
empleados actuales y roles objetivo. Utiliza un sistema de scoring
multinivel que combina:

1. Skills Match (50%): Compatibilidad de habilidades técnicas
2. Responsibilities Alignment (25%): Alineación de responsabilidades 
3. Ambitions Match (15%): Match con aspiraciones del empleado
4. Dedication Compatibility (10%): Compatibilidad horaria

El resultado es un score 0-1 donde 1 significa match perfecto.
"""

import re
import numpy as np
from typing import Dict, List, Set
from .models import (
    Employee, Role, Skill, SkillLevel, GapResult, GapBand,
    DEFAULT_WEIGHTS, DEFAULT_BAND_THRESHOLDS
)


class GapCalculator:
    """
    Motor principal de cálculo de gaps entre empleados y roles objetivo.
    """
    
    def __init__(self, 
                 skills_catalog: Dict[str, Skill],
                 weights: Dict[str, float] = None,
                 band_thresholds: Dict[GapBand, float] = None):
        """
        Inicializar el calculador.
        
        Args:
            skills_catalog: Diccionario skill_id -> Skill object
            weights: Pesos personalizados para componentes del score
            band_thresholds: Umbrales personalizados para bandas
        """
        self.skills_catalog = skills_catalog
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self.band_thresholds = band_thresholds or DEFAULT_BAND_THRESHOLDS.copy()
        
        # Validar que los pesos sumen 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            # Normalizar automáticamente
            for key in self.weights:
                self.weights[key] /= total_weight
    
    def calculate_gap(self, employee: Employee, role: Role) -> GapResult:
        """
        Calcular el gap completo entre un empleado y un rol objetivo.
        
        Args:
            employee: Empleado a evaluar
            role: Rol objetivo
            
        Returns:
            GapResult con score, banda y detalles del análisis
        """
        # Calcular scores por componente
        skills_score = self._calculate_skills_match(employee, role)
        responsibilities_score = self._calculate_responsibilities_alignment(employee, role)
        ambitions_score = self._calculate_ambitions_match(employee, role)
        dedication_score = self._calculate_dedication_compatibility(employee, role)
        
        # Score total ponderado
        overall_score = (
            skills_score * self.weights['skills'] +
            responsibilities_score * self.weights['responsibilities'] +
            ambitions_score * self.weights['ambitions'] +
            dedication_score * self.weights['dedication']
        )
        
        # Determinar banda
        band = self._classify_band(overall_score)
        
        # Identificar gaps específicos
        detailed_gaps = self._identify_detailed_gaps(employee, role, {
            'skills': skills_score,
            'responsibilities': responsibilities_score,
            'ambitions': ambitions_score,
            'dedication': dedication_score
        })
        
        return GapResult(
            employee_id=employee.id,
            role_id=role.id,
            overall_score=overall_score,
            band=band,
            component_scores={
                'skills': skills_score,
                'responsibilities': responsibilities_score,
                'ambitions': ambitions_score,
                'dedication': dedication_score
            },
            detailed_gaps=detailed_gaps,
            recommendations=[]  # Se llenarán en RecommendationEngine
        )
    
    def _calculate_skills_match(self, employee: Employee, role: Role) -> float:
        """
        Calcula el match de skills considerando niveles y pesos.
        
        Algoritmo:
        1. Para cada skill requerido, obtener nivel del empleado
        2. Convertir nivel a score numérico (novato=0.25, experto=1.0)
        3. Aplicar peso del skill desde catalog
        4. Promediar scores ponderados
        """
        if not role.habilidades_requeridas:
            return 1.0  # Si no requiere skills específicos, match perfecto
        
        skill_scores = []
        total_weight = 0.0
        
        for skill_id in role.habilidades_requeridas:
            # Obtener información del skill
            skill_info = self.skills_catalog.get(skill_id)
            if not skill_info:
                continue  # Skip skills desconocidos
            
            # Nivel actual del empleado en este skill
            employee_level = employee.get_skill_level(skill_id)
            level_score = employee_level.numeric_value
            
            # Aplicar peso del skill
            skill_weight = skill_info.normalized_weight
            weighted_score = level_score * skill_weight
            
            skill_scores.append(weighted_score)
            total_weight += skill_weight
        
        if not skill_scores:
            return 0.0  # No tiene ningún skill requerido
        
        # Promedio ponderado
        if total_weight > 0:
            return sum(skill_scores) / total_weight
        else:
            return np.mean(skill_scores)
    
    def _calculate_responsibilities_alignment(self, employee: Employee, role: Role) -> float:
        """
        Calcula alineación entre responsabilidades actuales y futuras.
        
        Utiliza matching de palabras clave y conceptos para determinar overlap.
        """
        current_resp = [r.lower() for r in employee.responsabilidades_actuales]
        target_resp = [r.lower() for r in role.responsabilidades]
        
        if not target_resp:
            return 1.0  # Sin responsabilidades específicas = match perfecto
        
        if not current_resp:
            return 0.0  # Sin experiencia previa
        
        # Extraer palabras clave importantes de ambas listas
        current_keywords = self._extract_keywords(current_resp)
        target_keywords = self._extract_keywords(target_resp)
        
        if not target_keywords:
            return 0.5  # Fallback si no se pueden extraer keywords
        
        # Calcular overlap de keywords
        overlap = len(current_keywords.intersection(target_keywords))
        total_target = len(target_keywords)
        
        base_score = overlap / total_target if total_target > 0 else 0.0
        
        # Bonus por responsabilidades progresivas
        progression_bonus = self._detect_responsibility_progression(current_resp, target_resp)
        
        return min(base_score + progression_bonus, 1.0)
    
    def _extract_keywords(self, responsibilities: List[str]) -> Set[str]:
        """
        Extrae palabras clave importantes de una lista de responsabilidades.
        """
        # Palabras clave importantes en el contexto de Quether Consulting
        important_keywords = {
            'okr', 'okrs', 'estrategia', 'estratégica', 'estratégicas',
            'análisis', 'analítica', 'datos', 'crm', 'automatización',
            'campaign', 'campañas', 'creative', 'copy', 'narrativa',
            'diseño', 'design', 'ui', 'visual', 'identidad',
            'social', 'media', 'influencer', 'kol', 'creators',
            'performance', 'seo', 'sem', 'growth', 'captación',
            'workshop', 'discovery', 'roadmap', 'gobierno',
            'cliente', 'clientes', 'proyecto', 'proyectos',
            'lider', 'liderar', 'dirigir', 'gestión', 'management'
        }
        
        keywords = set()
        
        for resp in responsibilities:
            # Limpiar texto y extraer palabras
            words = re.findall(r'\b\w{4,}\b', resp.lower())
            for word in words:
                if word in important_keywords:
                    keywords.add(word)
        
        return keywords
    
    def _detect_responsibility_progression(self, current: List[str], target: List[str]) -> float:
        """
        Detecta si hay progresión lógica entre responsabilidades actuales y futuras.
        
        Examples:
        - "ejecutar OKRs" -> "definir OKRs" = progresión positiva
        - "análisis básico" -> "análisis estratégico" = progresión
        """
        progression_patterns = [
            (r'ejecutar.*okr', r'definir.*okr', 0.2),
            (r'apoyar.*análisis', r'liderar.*análisis', 0.15),
            (r'gestionar.*proyecto', r'dirigir.*estrategia', 0.2),
            (r'crear.*contenido', r'dirigir.*creative', 0.15),
            (r'configurar.*crm', r'arquitectura.*datos', 0.2)
        ]
        
        current_text = ' '.join(current).lower()
        target_text = ' '.join(target).lower()
        
        bonus = 0.0
        for current_pattern, target_pattern, bonus_value in progression_patterns:
            if re.search(current_pattern, current_text) and re.search(target_pattern, target_text):
                bonus += bonus_value
        
        return min(bonus, 0.3)  # Max 30% bonus
    
    def _calculate_ambitions_match(self, employee: Employee, role: Role) -> float:
        """
        Calcula qué tan bien el rol se alinea con las ambiciones del empleado.
        """
        if not employee.ambiciones:
            return 0.5  # Neutral si no especifica ambiciones
        
        ambitions_text = ' '.join(employee.ambiciones).lower()
        role_context = f"{role.titulo} {' '.join(role.responsabilidades)}".lower()
        
        # Extraer keywords de ambiciones
        ambition_keywords = self._extract_keywords(employee.ambiciones)
        role_keywords = self._extract_keywords([role_context])
        
        if not ambition_keywords:
            return 0.5
        
        # Match directo de keywords
        overlap = len(ambition_keywords.intersection(role_keywords))
        base_score = overlap / len(ambition_keywords) if ambition_keywords else 0.0
        
        # Bonus por menciones explícitas del nivel del rol
        level_bonus = 0.0
        role_level = role.nivel.lower()
        if role_level in ambitions_text:
            level_bonus = 0.2
        elif 'lead' in ambitions_text and 'lead' in role_level:
            level_bonus = 0.2
        elif 'senior' in ambitions_text and 'senior' in role_level:
            level_bonus = 0.15
        
        return min(base_score + level_bonus, 1.0)
    
    def _calculate_dedication_compatibility(self, employee: Employee, role: Role) -> float:
        """
        Calcula compatibilidad de dedicación horaria.
        """
        try:
            emp_min, emp_max = employee.parse_dedication_hours()
            role_min, role_max = role.parse_dedication_hours()
        except:
            return 0.8  # Fallback si no se puede parsear
        
        # Calcular overlap de rangos
        overlap_min = max(emp_min, role_min)
        overlap_max = min(emp_max, role_max)
        
        if overlap_min > overlap_max:
            # Sin overlap - calcular qué tan lejos están
            distance = min(abs(emp_max - role_min), abs(role_max - emp_min))
            return max(0.0, 1.0 - (distance / 20.0))  # Penalizar por distancia
        
        # Con overlap - calcular qué porcentaje del rango objetivo está cubierto
        role_range = role_max - role_min
        overlap_range = overlap_max - overlap_min
        
        if role_range == 0:
            return 1.0  # Dedicación exacta
        
        return overlap_range / role_range
    
    def _classify_band(self, score: float) -> GapBand:
        """Clasifica el score en una banda de readiness."""
        if score >= self.band_thresholds[GapBand.READY]:
            return GapBand.READY
        elif score >= self.band_thresholds[GapBand.READY_WITH_SUPPORT]:
            return GapBand.READY_WITH_SUPPORT
        elif score >= self.band_thresholds[GapBand.NEAR]:
            return GapBand.NEAR
        elif score >= self.band_thresholds[GapBand.FAR]:
            return GapBand.FAR
        else:
            return GapBand.NOT_VIABLE
    
    def _identify_detailed_gaps(self, employee: Employee, role: Role, 
                              component_scores: Dict[str, float]) -> List[str]:
        """
        Identifica gaps específicos para feedback detallado.
        """
        gaps = []
        
        # Skills gaps
        if component_scores['skills'] < 0.7:
            missing_skills = []
            for skill_id in role.habilidades_requeridas:
                emp_level = employee.get_skill_level(skill_id)
                if emp_level.numeric_value < 0.75:  # Menos que avanzado
                    skill_info = self.skills_catalog.get(skill_id)
                    skill_name = skill_info.nombre if skill_info else skill_id
                    gaps.append(f"Skill gap: {skill_name} (actual: {emp_level.value})")
        
        # Responsibilities gaps  
        if component_scores['responsibilities'] < 0.6:
            gaps.append("Gap significativo en responsabilidades similares")
        
        # Ambitions mismatch
        if component_scores['ambitions'] < 0.5:
            gaps.append("Rol no alineado con ambiciones expresadas")
        
        # Dedication gap
        if component_scores['dedication'] < 0.7:
            gaps.append("Gap en disponibilidad horaria")
        
        return gaps