# 🚀 TALENT GAP ANALYZER - Documentación del Algoritmo

Sistema completo de análisis de brechas de talento para identificar la readiness de empleados hacia nuevos roles.

## 📁 Arquitectura del Sistema

```
algorithm/
├── __init__.py                 # 📦 Exports principales del módulo  
├── models.py                   # 🏗️  Estructuras de datos (Employee, Role, Skill, etc.)
├── gap_calculator.py           # ⚡ Motor de cálculo de gaps (CORE ENGINE)
├── ranking_engine.py           # 🏆 Sistema de rankings y bandas de readiness
├── gap_analyzer.py             # 🔍 Análisis de gaps críticos y bottlenecks
├── recommendation_engine.py    # 💡 Generación de recomendaciones
├── talent_gap_algorithm.py     # 🎯 Clase principal orquestadora (API)
├── test_algorithm.py           # ✅ Suite de tests unitarios
└── README.md                   # 📚 Esta documentación
```

---

## 🎯 API Principal - TalentGapAlgorithm

### **Inicialización**
```python
from algorithm import TalentGapAlgorithm

algorithm = TalentGapAlgorithm(
    org_config=org_config_dict,          # Configuración organizacional
    vision_futura=vision_futura_dict,    # Roles futuros deseados
    algorithm_weights={                   # Pesos del algoritmo (opcional)
        'skills': 0.50,
        'responsibilities': 0.25, 
        'ambitions': 0.15,
        'dedication': 0.10
    }
)
```

### **Métodos Principales**

#### 🔄 `load_employees_data(employees_data: List[Dict])`
**Función:** Carga datos de empleados desde lista de diccionarios
**Input:** Lista de empleados con formato:
```json
[{
  "id": "1001",
  "nombre": "Juan Pérez", 
  "chapter": "Strategy",
  "skills_actuales": {"S-ANALYTICS": 8, "S-PM": 9},
  "responsabilidades_similares": ["gestión equipos"],
  "ambiciones": ["liderar proyectos"],
  "dedicacion": "full-time"
}]
```
**Returns:** None (carga interna)

#### 🚀 `run_full_analysis() -> Dict`
**Función:** Ejecuta análisis completo del gap de talento
**Input:** No requiere parámetros (usa datos ya cargados)
**Returns:** Diccionario completo con:
```json
{
  "compatibility_matrix": {...},     # Matriz de compatibilidad
  "role_rankings": {...},           # Rankings por rol
  "career_paths": {...},            # Caminos de carrera
  "skill_gaps": {...},             # Gaps de habilidades
  "chapter_gaps": {...},           # Gaps por chapter
  "bottlenecks": [...],            # Bottlenecks críticos
  "recommendations": {...},        # Recomendaciones
  "executive_summary": {...}       # Resumen ejecutivo
}
```

#### 👤 `get_employee_analysis(employee_id: str) -> Dict`
**Función:** Análisis específico de un empleado
**Input:** ID del empleado (string)
**Returns:** 
```json
{
  "employee_info": {...},
  "best_matches": [...],           # Mejores roles compatibles
  "career_options": [...],         # Opciones de carrera
  "skill_profile": {...},         # Perfil de habilidades
  "recommendations": [...]         # Recomendaciones específicas
}
```

#### 🎯 `get_role_analysis(role_id: str) -> Dict`  
**Función:** Análisis específico de un rol
**Input:** ID del rol (ej: "R-STR-LEAD")
**Returns:**
```json
{
  "role_info": {...},
  "candidate_ranking": [...],      # Ranking de candidatos
  "readiness_stats": {...},       # Estadísticas de readiness
  "critical_gaps": [...],         # Gaps críticos del rol
  "hiring_recommendation": "..."   # Recomendación de hiring
}
```

#### 📤 `export_results(format='json', include_detailed=True) -> str`
**Función:** Exporta resultados en formato especificado
**Input:** 
- `format`: "json" | "csv" | "summary" 
- `include_detailed`: bool
**Returns:** String con datos exportados

---

## ⚡ Componentes del Motor

### 1️⃣ **models.py** - Estructuras de Datos

#### 🏷️ **Enums Principales**
```python
class SkillLevel(str, Enum):
    NOVATO = "novato"           # 0.2 (2/10)
    INTERMEDIO = "intermedio"   # 0.5 (5/10) 
    AVANZADO = "avanzado"      # 0.8 (8/10)
    EXPERTO = "experto"        # 1.0 (10/10)

class GapBand(str, Enum):
    READY_NOW = "READY"                    # Score >= 0.8
    READY_WITH_SUPPORT = "READY_WITH_SUPPORT"  # Score >= 0.65
    NEAR = "NEAR"                         # Score >= 0.5
    FAR = "FAR"                          # Score < 0.5
```

#### 🏗️ **Clases de Datos**
```python
@dataclass
class Employee:
    id: str
    nombre: str
    chapter: str
    skills_actuales: Dict[str, SkillLevel]
    responsabilidades_similares: List[str]
    ambiciones: List[str] 
    dedicacion: str

    # Métodos API:
    def get_skill_level(skill_id: str) -> SkillLevel
    def has_skill_at_level(skill_id: str, min_level: SkillLevel) -> bool
    def parse_dedication_hours() -> tuple[int, int]

@dataclass 
class Role:
    id: str
    titulo: str
    chapter: str
    skills_requeridos: Dict[str, SkillLevel]
    responsabilidades: List[str]
    dedicacion: str

    # Métodos API:
    def parse_dedication_hours() -> tuple[int, int]

@dataclass
class GapResult:
    employee_id: str
    role_id: str
    overall_score: float               # Score final 0-1
    band: GapBand                     # Banda de readiness
    component_scores: Dict[str, float] # Scores por componente
    detailed_gaps: List[str]          # Lista de gaps específicos
```

### 2️⃣ **gap_calculator.py** - Motor de Cálculo ⚡

#### 🧮 **GapCalculator Class**
**Función:** Calcula compatibilidad empleado ↔ rol objetivo usando algoritmo multinivel

#### **Métodos API:**

##### `calculate_gap(employee: Employee, target_role: Role) -> GapResult`
**Función:** Calcula gap completo entre empleado y rol
**Input:** Objetos Employee y Role
**Returns:** GapResult con score y análisis detallado

**Algoritmo de Scoring:**
- **Skills Match (50%):** Compatibilidad de habilidades técnicas
- **Responsibilities Alignment (25%):** Alineación de responsabilidades similares
- **Ambitions Match (15%):** Match con aspiraciones del empleado  
- **Dedication Compatibility (10%):** Compatibilidad horaria

##### `_calculate_skills_match(employee, role) -> float`
**Función:** Calcula compatibilidad de skills específicamente
**Returns:** Score 0-1 basado en skills requeridos vs actuales

##### `_calculate_responsibilities_alignment(employee, role) -> float`
**Función:** Calcula alineación de responsabilidades
**Returns:** Score 0-1 basado en overlap de responsabilidades

##### `_calculate_ambitions_match(employee, role) -> float` 
**Función:** Calcula match con ambiciones de carrera
**Returns:** Score 0-1 basado en aspiraciones del empleado

##### `_calculate_dedication_compatibility(employee, role) -> float`
**Función:** Calcula compatibilidad horaria
**Returns:** Score 0-1 basado en dedicación requerida vs disponible

### 3️⃣ **ranking_engine.py** - Sistema de Rankings 🏆

#### 🏆 **RankingEngine Class**
**Función:** Genera rankings de candidatos y detecta conflictos

#### **Métodos API:**

##### `generate_role_rankings(compatibility_matrix, roles) -> Dict[str, List[GapResult]]`
**Función:** Genera ranking de candidatos para cada rol
**Input:** Matriz de compatibilidad y catálogo de roles
**Returns:** Diccionario role_id -> lista ordenada de candidatos

##### `generate_career_paths(compatibility_matrix, employees) -> Dict[str, List[GapResult]]`
**Función:** Genera mejores opciones de carrera por empleado
**Input:** Matriz de compatibilidad y lista de empleados  
**Returns:** Diccionario employee_id -> lista ordenada de roles compatibles

##### `detect_conflicts(role_rankings) -> List[Dict]`
**Función:** Detecta conflictos cuando múltiples roles compiten por mismo candidato
**Returns:** Lista de conflictos con detalles

##### `find_orphan_roles(role_rankings) -> List[str]`
**Función:** Identifica roles sin candidatos viables
**Returns:** Lista de role_ids sin candidatos ready

### 4️⃣ **gap_analyzer.py** - Análisis de Gaps Críticos 🔍

#### 🔍 **GapAnalyzer Class**
**Función:** Identifica bottlenecks y gaps críticos organizacionales

#### **Métodos API:**

##### `analyze_skill_gaps(compatibility_matrix, roles, skills_catalog) -> Dict`
**Función:** Analiza gaps de habilidades críticas
**Returns:** Diccionario con gaps por skill y su impacto

##### `analyze_chapter_gaps(role_rankings, employees, chapters) -> Dict`
**Función:** Analiza salud de cada chapter organizacional  
**Returns:** Estadísticas de readiness por chapter

##### `identify_bottlenecks(skill_gaps, threshold=0.7) -> List[Dict]`
**Función:** Identifica skills que bloquean múltiples transiciones
**Input:** threshold = % de gap mínimo para considerar bottleneck
**Returns:** Lista de bottlenecks ordenados por impacto

##### `calculate_transition_blocking(skill_gaps) -> Dict[str, int]`
**Función:** Calcula cuántas transiciones bloquea cada skill
**Returns:** Diccionario skill_id -> número de transiciones bloqueadas

### 5️⃣ **recommendation_engine.py** - Motor de Recomendaciones 💡

#### 💡 **RecommendationEngine Class**  
**Función:** Genera recomendaciones de desarrollo y hiring

#### **Métodos API:**

##### `generate_individual_recommendations(employee_analysis) -> List[Dict]`
**Función:** Genera recomendaciones específicas por empleado
**Input:** Análisis individual del empleado
**Returns:** Lista de recomendaciones priorizadas con:
```json
[{
  "type": "technical_growth",
  "title": "Desarrollar competencia en Python",
  "description": "...",
  "timeline": "2-3 meses",
  "priority": "HIGH"
}]
```

##### `generate_organizational_recommendations(bottlenecks, chapter_gaps) -> List[Dict]`
**Función:** Genera recomendaciones organizacionales
**Returns:** Recomendaciones de hiring, training programs, etc.

##### `generate_hiring_recommendations(orphan_roles, role_analysis) -> Dict[str, str]`
**Función:** Genera recomendaciones de hiring externo
**Returns:** Diccionario role_id -> recomendación de hiring

### 6️⃣ **talent_gap_algorithm.py** - Orquestador Principal 🎯

#### 🎯 **TalentGapAlgorithm Class**
**Función:** API principal que orquesta todos los componentes

**Ver sección "API Principal" arriba para métodos detallados**

---

## 🔗 Integración con APIs REST

### **Ejemplo de API Flask/FastAPI:**

```python
from flask import Flask, request, jsonify
from algorithm import TalentGapAlgorithm

app = Flask(__name__)

# Inicializar algoritmo global
algorithm = TalentGapAlgorithm(org_config, vision_futura)

@app.route('/api/analyze/full', methods=['POST'])
def analyze_full():
    """Análisis completo de gap de talento"""
    employees_data = request.json['employees']
    algorithm.load_employees_data(employees_data)
    results = algorithm.run_full_analysis()
    return jsonify(results)

@app.route('/api/analyze/employee/<employee_id>', methods=['GET'])  
def analyze_employee(employee_id):
    """Análisis específico de empleado"""
    result = algorithm.get_employee_analysis(employee_id)
    return jsonify(result)

@app.route('/api/analyze/role/<role_id>', methods=['GET'])
def analyze_role(role_id):
    """Análisis específico de rol"""  
    result = algorithm.get_role_analysis(role_id)
    return jsonify(result)

@app.route('/api/export/<format>', methods=['GET'])
def export_results(format):
    """Exportar resultados en formato específico"""
    include_detailed = request.args.get('detailed', 'true').lower() == 'true'
    result = algorithm.export_results(format, include_detailed)
    return result
```

---

## 📊 Formatos de Datos

### **Input: Configuración Organizacional (org_config.json)**
```json
{
  "roles": {
    "R-STR-LEAD": {
      "id": "R-STR-LEAD",
      "titulo": "Strategy Lead",
      "chapter": "Strategy", 
      "skills_requeridos": {
        "S-ANALYTICS": "avanzado",
        "S-STAKE": "experto"
      },
      "responsabilidades": ["estrategia", "liderazgo"],
      "dedicacion": "full-time"
    }
  },
  "skills": {
    "S-ANALYTICS": {
      "id": "S-ANALYTICS", 
      "nombre": "Analytics",
      "categoria": "Technical",
      "peso": 0.8
    }
  },
  "chapters": {
    "Strategy": {
      "nombre": "Strategy",
      "descripcion": "Estrategia organizacional"
    }
  }
}
```

### **Input: Empleados (employees_data)**
```json
[{
  "id": "1001",
  "nombre": "Juan Pérez",
  "chapter": "Strategy", 
  "skills_actuales": {
    "S-ANALYTICS": 8,
    "S-PM": 9,
    "S-STAKE": 7
  },
  "responsabilidades_similares": ["gestión equipos", "planificación"],
  "ambiciones": ["liderar proyectos", "estrategia"],
  "dedicacion": "full-time"
}]
```

### **Output: Resultado Completo**
```json
{
  "timestamp": "2025-11-08T14:33:12",
  "summary": {
    "total_employees": 10,
    "total_roles": 10, 
    "overall_readiness": "5.1%",
    "ready_transitions": 3
  },
  "compatibility_matrix": {...},
  "role_rankings": {
    "R-STR-LEAD": [{
      "employee_id": "1001",
      "overall_score": 0.75,
      "band": "READY_WITH_SUPPORT", 
      "detailed_gaps": ["Gap en disponibilidad horaria"]
    }]
  },
  "bottlenecks": [{
    "skill_id": "S-PM",
    "gap_percentage": 0.8,
    "blocked_transitions": 15,
    "affected_roles": ["R-STR-LEAD", "R-PM"]
  }],
  "executive_summary": {...}
}
```

---

## ⚙️ Configuración Avanzada

### **Pesos del Algoritmo**
```python
custom_weights = {
    'skills': 0.60,          # Mayor peso a skills técnicos
    'responsibilities': 0.20, # Menor peso a experiencia
    'ambitions': 0.15,       # Mantener ambiciones
    'dedication': 0.05       # Menor peso a disponibilidad
}

algorithm = TalentGapAlgorithm(
    org_config=config,
    algorithm_weights=custom_weights
)
```

### **Umbrales de Bandas Personalizados**
```python
custom_thresholds = {
    GapBand.READY_NOW: 0.85,           # Más estricto para READY
    GapBand.READY_WITH_SUPPORT: 0.70,  # Más estricto para SUPPORT
    GapBand.NEAR: 0.45,                # Más permisivo para NEAR
    GapBand.FAR: 0.0                   # Sin cambios
}
```

---

## 🧪 Testing

### **Ejecutar Tests**
```bash
cd algorithm/
python -m pytest test_algorithm.py -v
```

### **Tests Disponibles**
- ✅ Test de carga de datos
- ✅ Test de cálculo de gaps
- ✅ Test de rankings 
- ✅ Test de detección de bottlenecks
- ✅ Test de generación de recomendaciones
- ✅ Test de exportación

---

## 🚀 Casos de Uso para APIs

### **1. Dashboard de Readiness**
```python
# GET /api/dashboard/readiness
results = algorithm.run_full_analysis()
dashboard_data = {
    "overall_readiness": results['executive_summary']['overall_readiness'],
    "ready_employees": len([r for r in results['career_paths'] if r['best_score'] >= 0.8]),
    "critical_roles": results['bottlenecks'][:5]
}
```

### **2. Recomendador de Carrera Individual** 
```python  
# GET /api/employee/{id}/career-options
employee_analysis = algorithm.get_employee_analysis(employee_id)
career_options = employee_analysis['career_options'][:3]  # Top 3
```

### **3. Planificador de Hiring**
```python
# GET /api/hiring/recommendations  
full_results = algorithm.run_full_analysis()
orphan_roles = [role for role, candidates in full_results['role_rankings'].items() 
                if not candidates or candidates[0]['overall_score'] < 0.5]
```

### **4. Monitor de Skills Gap**
```python
# GET /api/skills/gaps
skill_gaps = algorithm.run_full_analysis()['skill_gaps']
critical_skills = [(skill, gap) for skill, gap in skill_gaps.items() if gap > 0.7]
```

---

## 📈 Métricas y KPIs

El algoritmo genera automáticamente:

- **📊 Overall Readiness:** % de transiciones ready en la organización
- **🎯 Ready Transitions:** Número absoluto de empleados ready para nuevos roles  
- **🚨 Critical Bottlenecks:** Skills que bloquean más transiciones
- **📋 Chapter Health:** % de readiness por department/chapter
- **⏱️ Time to Ready:** Estimación de tiempo para alcanzar readiness
- **💰 Training ROI:** Impacto de resolver bottlenecks específicos

---

¡Con esta documentación tienes todo lo necesario para entender, usar e integrar el Talent Gap Analyzer! 🚀
- **Output:** Score 0-1 + banda de readiness (READY/NEAR/FAR/etc.)

### **RankingEngine** - Sistema de Rankings  
- **Función:** Genera rankings bidireccionales y detecta conflictos
- **Features:** Distribución óptima, roles huérfanos, sucesión
- **Output:** Rankings ordenados + recomendaciones de asignación

### **GapAnalyzer** - Análisis Crítico
- **Función:** Identifica bottlenecks organizacionales
- **Métricas:** Gaps por skill, chapter, ROI de training
- **Output:** Prioridades de inversión + recomendaciones estratégicas

### **RecommendationEngine** - Recomendaciones
- **Función:** Planes de desarrollo personalizados
- **Tipos:** Individuales, organizacionales, de contratación
- **Output:** Acciones específicas con timeline y prioridad

## 📊 Modelo de Scoring

El algoritmo utiliza un sistema de scoring multinivel:

```
Score Total = 
  Skills Match (50%) +
  Responsibilities Alignment (25%) + 
  Ambitions Match (15%) +
  Dedication Compatibility (10%)
```

### **Bandas de Readiness:**
- **READY (≥85%):** Listo para promoción inmediata
- **READY_WITH_SUPPORT (≥70%):** Listo con soporte/mentoring  
- **NEAR (≥50%):** 3-6 meses de desarrollo
- **FAR (≥25%):** 6-12 meses de desarrollo significativo
- **NOT_VIABLE (<25%):** No viable para este rol

## 🔧 Configuración

### **Pesos del Algoritmo (Personalizables):**
```python
weights = {
    'skills': 0.50,          # Importancia de competencias técnicas
    'responsibilities': 0.25, # Alineación de responsabilidades
    'ambitions': 0.15,       # Match con aspiraciones del empleado  
    'dedication': 0.10       # Compatibilidad horaria
}
```

### **Umbrales de Bandas (Personalizables):**
```python
thresholds = {
    GapBand.READY: 0.85,
    GapBand.READY_WITH_SUPPORT: 0.70,
    GapBand.NEAR: 0.50,
    GapBand.FAR: 0.25
}
```

## 📈 Outputs del Sistema

### **1. Matriz de Compatibilidad**
```json
{
  "employee_id": {
    "role_id": {
      "overall_score": 0.73,
      "band": "READY_WITH_SUPPORT",
      "component_scores": {
        "skills": 0.80,
        "responsibilities": 0.65,
        "ambitions": 0.70,
        "dedication": 0.90
      },
      "detailed_gaps": ["Skill gap: Análisis Estratégico (actual: intermedio)"],
      "recommendations": [...]
    }
  }
}
```

### **2. Rankings y Conflictos**
- Top candidatos por rol
- Mejores opciones de carrera por empleado
- Conflictos de asignación detectados
- Distribución óptima sugerida

### **3. Análisis de Gaps Críticos**
- Skills bottleneck que bloquean múltiples transiciones
- Análisis por chapter/departamento
- ROI de programas de training
- Prioridades de contratación externa

### **4. Recomendaciones**
- **Individuales:** Planes de desarrollo de 3-6 meses
- **Organizacionales:** Programas de training grupales  
- **Estratégicas:** Inversiones, reestructuraciones, contratación

## 🧪 Testing

```bash
cd algorithm/
python test_algorithm.py
```

**Test Coverage:**
- ✅ Modelos de datos y validación
- ✅ Cálculo de gaps y scoring
- ✅ Generación de rankings
- ✅ Análisis de gaps críticos  
- ✅ Motor de recomendaciones
- ✅ Integración end-to-end
- ✅ Manejo de errores y edge cases

## 📋 Casos de Uso

### **Para RRHH:**
```python
# Identificar empleados listos para promoción
ready_candidates = algorithm.compatibility_matrix.get_ready_candidates()

# Plan de desarrollo individual
emp_plan = algorithm.get_employee_analysis("EMP-001")
print(emp_plan['recommendations'])
```

### **Para Management:**
```python
# Análisis de gaps críticos
results = algorithm.run_full_analysis()
bottlenecks = results['gap_analysis']['bottlenecks']

# ROI de programas de training
training_roi = results['gap_analysis']['training_roi']
```

### **Para C-Level:**
```python
# Resumen ejecutivo
executive_summary = results['executive_summary']
print(f"Overall readiness: {executive_summary['overall_readiness']}")
print(f"Key insights: {executive_summary['key_insights']}")
```

## 🔍 Algoritmos Específicos

### **Skills Match Algorithm:**
1. Convertir niveles a valores numéricos (novato=0.25, experto=1.0)
2. Aplicar pesos por importancia del skill (peso 1-5 desde config)
3. Calcular promedio ponderado de todos los skills requeridos
4. Bonus por skills adicionales no requeridos

### **Responsibilities Alignment:**
1. Extracción de keywords importantes de responsabilidades
2. Cálculo de overlap semántico
3. Detección de progresión lógica (ej: "ejecutar" → "liderar")
4. Bonus por experiencia progresiva

### **Ambitions Match:**
1. Análisis de texto libre de ambiciones del empleado
2. Match con contexto del rol objetivo
3. Bonus por menciones explícitas del nivel de rol
4. Penalización por misalignment evidente

### **Dedication Compatibility:**
1. Parsing de rangos horarios (ej: "30-40h/semana")
2. Cálculo de overlap entre disponibilidad y requirement
3. Penalización proporcional por distancia si no hay overlap

## 🎯 Optimizaciones y Features Avanzadas

### **Detección de Conflictos:**
- Empleados que aparecen como top candidatos para múltiples roles
- Algoritmo greedy para distribución óptima
- Priorización de roles críticos

### **Análisis Predictivo:**
- Estimación de timeline de desarrollo (3-12 meses)
- Probabilidad de éxito en transiciones
- ROI de inversiones en training

### **Recomendaciones Inteligentes:**
- Plans específicos con milestones y success criteria
- Recursos sugeridos (cursos, mentoring, proyectos)
- Priorización automática por impacto

## 🚦 Performance y Escalabilidad

**Complejidad:** O(E × R × S) donde:
- E = número de empleados
- R = número de roles  
- S = número promedio de skills por rol

**Optimizaciones implementadas:**
- ✅ Cálculos vectorizados con NumPy
- ✅ Caching de resultados intermedios
- ✅ Filtering de roles relevantes por empleado
- ✅ Lazy loading de análisis detallados

**Límites recomendados:**
- Empleados: 1000+
- Roles: 100+ 
- Skills: 200+

---

## 👥 Integración con Otros Módulos

Este módulo está diseñado para integrarse con:
- **Data Pipeline (P1):** Recibe datos limpios y validados
- **Workflow Engine (P3):** Proporciona APIs para orquestación  
- **Frontend UI (P4):** Exports estructurados para visualización

### **API Principal:**
```python
# Interfaz unificada para integración
from algorithm import TalentGapAlgorithm

# Inicialización
algorithm = TalentGapAlgorithm(config, vision)
algorithm.load_employees_data(data)

# Ejecución
results = algorithm.run_full_analysis()

# Exports
json_output = algorithm.export_results('json')
csv_output = algorithm.export_results('csv')
```

¡El algoritmo está listo para integración y testing! 🎉