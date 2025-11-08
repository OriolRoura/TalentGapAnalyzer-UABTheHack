# API de Critical Gaps por Rol

## 📋 Descripción

Este endpoint permite consultar los **critical gaps** (vacíos críticos de skills) que afectan a un rol específico. Identifica qué skills faltan en los mejores candidatos internos para cada rol, facilitando decisiones sobre formación y contratación.

## 🎯 Concepto Actualizado

El análisis de **Critical Gaps** identifica dos tipos de problemas:

1. **Gaps en candidatos viables**: Skills que faltan o están por debajo del nivel requerido en empleados con potencial (score ≥ 0.5) para el rol
2. **Sin candidatos viables**: Roles donde ningún empleado alcanza el score mínimo (requiere hiring externo)

---

## 🔍 Endpoint: GET /api/roles/{role_id}/critical-gaps

### Request

**Método**: `GET`

**URL**: `/api/roles/{role_id}/critical-gaps`

**Parámetros de URL**:
- `role_id` (string, requerido): ID del rol a consultar
  - Ejemplos: `R-CRT-LEAD`, `R-PM`, `R-SMM`, `R-DATA-ANL`

**Query Parameters** (opcionales):
- `priority` (string): Filtrar por prioridad (`CRÍTICA`, `ALTA`, `MEDIA`, `BAJA`)
- `min_gap` (float): Gap mínimo para incluir (0-100)
- `include_candidates_details` (boolean): Incluir detalles de candidatos afectados (default: true)

### Response

**Status Code**: `200 OK`

**Response Body**:

```json
{
  "role_id": "R-CRT-LEAD",
  "role_title": "Creative Director",
  "critical_gaps": [
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 66.66666666666666,
      "candidates_affected": 1,
      "total_viable_candidates": 1,
      "priority": "CRÍTICA",
      "criticality_score": 66.66666666666666,
      "no_viable_candidates": false,
      "candidates_details": [
        {
          "employee_id": "1006",
          "employee_name": "Adrián López",
          "current_level": "novato",
          "required_level": "avanzado",
          "gap_percentage": 66.66666666666666,
          "overall_score": 0.5473611111111112
        }
      ]
    }
  ],
  "total_gaps": 1,
  "highest_priority": "CRÍTICA"
}
```

#### Response cuando NO hay candidatos viables:

```json
{
  "role_id": "R-PM",
  "role_title": "Project Manager",
  "critical_gaps": [
    {
      "skill_id": "S-PM",
      "skill_name": "Pm",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    },
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    }
  ],
  "total_gaps": 2,
  "highest_priority": "CRÍTICA",
  "recommendation": "⚠️ SIN CANDIDATOS VIABLES - Requiere hiring externo"
}
```

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Rol con candidatos viables pero con gaps

**Request**:
```bash
GET /api/roles/R-CRT-LEAD/critical-gaps
```

**Response**:
```json
{
  "role_id": "R-CRT-LEAD",
  "role_title": "Creative Director",
  "critical_gaps": [
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 66.67,
      "candidates_affected": 1,
      "total_viable_candidates": 1,
      "priority": "CRÍTICA",
      "criticality_score": 66.67,
      "no_viable_candidates": false,
      "candidates_details": [
        {
          "employee_id": "1006",
          "employee_name": "Adrián López",
          "current_level": "novato",
          "required_level": "avanzado",
          "gap_percentage": 66.67,
          "overall_score": 0.547
        }
      ]
    }
  ],
  "total_gaps": 1,
  "highest_priority": "CRÍTICA"
}
```

**Interpretación**:
- ✅ Hay **1 candidato viable** para Creative Director (Adrián López)
- 🔴 Le falta el skill **Stakeholder Management** al nivel requerido
- 📊 Gap del **66.7%**: tiene nivel "novato" pero necesita "avanzado"
- 💡 **Acción recomendada**: Formación en Stakeholder Management para Adrián López

---

### Ejemplo 2: Rol SIN candidatos viables (requiere hiring)

**Request**:
```bash
GET /api/roles/R-PM/critical-gaps
```

**Response**:
```json
{
  "role_id": "R-PM",
  "role_title": "Project Manager",
  "critical_gaps": [
    {
      "skill_id": "S-PM",
      "skill_name": "Pm",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    },
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    },
    {
      "skill_id": "S-ANALYTICS",
      "skill_name": "Analytics",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    },
    {
      "skill_id": "S-OKR",
      "skill_name": "Okr",
      "avg_gap_percentage": 100.0,
      "candidates_affected": 0,
      "total_viable_candidates": 0,
      "priority": "CRÍTICA",
      "criticality_score": 100.0,
      "no_viable_candidates": true,
      "candidates_details": []
    }
  ],
  "total_gaps": 4,
  "highest_priority": "CRÍTICA",
  "recommendation": "⚠️ SIN CANDIDATOS VIABLES - Requiere hiring externo"
}
```

**Interpretación**:
- ❌ **Ningún empleado** tiene score ≥ 0.5 para Project Manager
- 🔴 Gaps del **100%** en todos los skills requeridos
- 💡 **Acción recomendada**: Contratar externamente - no hay talento interno preparado

---

### Ejemplo 3: Rol sin gaps (candidatos completamente preparados)

**Request**:
```bash
GET /api/roles/R-DATA-ANL/critical-gaps
```

**Response**:
```json
{
  "role_id": "R-DATA-ANL",
  "role_title": "Data Analyst",
  "critical_gaps": [],
  "total_gaps": 0,
  "highest_priority": null,
  "message": "✅ Todos los candidatos viables tienen los skills requeridos"
}
```

**Interpretación**:
- ✅ Los candidatos para Data Analyst tienen **todos los skills al nivel requerido**
- 💡 **Acción recomendada**: Ninguna acción de formación necesaria para este rol

---

### Ejemplo 4: Filtrar por prioridad CRÍTICA

**Request**:
```bash
GET /api/roles/R-PM/critical-gaps?priority=CRÍTICA
```

**Response**:
```json
{
  "role_id": "R-MTX-ARCH",
  "role_title": "Martech Architect",
  "critical_bottlenecks": [
    {
      "skill_id": "S-DATA",
      "skill_name": "Data",
      "gap_percentage": 80.0,
      "priority": "HIGH"
    },
    {
      "skill_id": "S-CRM",
      "skill_name": "Crm",
      "gap_percentage": 66.67,
      "priority": "HIGH"
    }
  ],
  "total_bottlenecks": 2
```json
{
  "role_id": "R-PM",
  "role_title": "Project Manager",
  "critical_gaps": [
    {
      "skill_id": "S-PM",
      "skill_name": "Pm",
      "avg_gap_percentage": 100.0,
      "priority": "CRÍTICA",
      "no_viable_candidates": true
    },
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 100.0,
      "priority": "CRÍTICA",
      "no_viable_candidates": true
    }
  ],
  "total_gaps": 2,
  "filtered_out": 2
}
```

---

### Ejemplo 5: Filtrar por gap mínimo

**Request**:
```bash
GET /api/roles/R-CRT-LEAD/critical-gaps?min_gap=50
```

**Response**:
```json
{
  "role_id": "R-CRT-LEAD",
  "role_title": "Creative Director",
  "critical_gaps": [
    {
      "skill_id": "S-STAKE",
      "skill_name": "Stake",
      "avg_gap_percentage": 66.67,
      "priority": "CRÍTICA"
    }
  ],
  "total_gaps": 1,
  "filtered_out": 0
}
```

---

## 🎯 Casos de Uso

### 1. Dashboard de Rol
```javascript
// Frontend muestra página de detalle de un rol
const roleId = 'R-CRT-LEAD';
const response = await fetch(`/api/roles/${roleId}/critical-gaps`);
const data = await response.json();

// Mostrar:
// - Título del rol: "Creative Director"
// - Total gaps: 1
// - Gap más alto: 66.7%
// - Candidatos viables: 1
// - Skills faltantes: Stakeholder Management
```

### 2. Identificar roles que requieren hiring externo
```javascript
// Obtener gaps de todos los roles en visión futura
const futureRoles = ['R-PM', 'R-SMM', 'R-CRT-LEAD', 'R-DATA-ANL'];

const gapsData = await Promise.all(
  futureRoles.map(roleId => 
    fetch(`/api/roles/${roleId}/critical-gaps`)
      .then(r => r.json())
  )
);

// Identificar roles sin candidatos viables
const rolesNeedingHiring = gapsData.filter(role => 
  role.critical_gaps.some(gap => gap.no_viable_candidates)
);

console.log('🚨 Roles que requieren hiring externo:');
rolesNeedingHiring.forEach(role => {
  console.log(`  • ${role.role_title} (${role.total_gaps} skills faltantes)`);
});

// Output:
// 🚨 Roles que requieren hiring externo:
//   • Project Manager (4 skills faltantes)
//   • Social Media Strategist (3 skills faltantes)
```

### 3. Planificación de formación para candidatos viables
```javascript
// Para roles CON candidatos viables, identificar necesidades de formación
const response = await fetch('/api/roles/R-CRT-LEAD/critical-gaps');
const data = await response.json();

if (data.total_gaps > 0 && !data.critical_gaps[0].no_viable_candidates) {
  console.log(`📚 Plan de formación para ${data.role_title}:`);
  
  data.critical_gaps.forEach(gap => {
    console.log(`\n  Skill: ${gap.skill_name}`);
    console.log(`  Gap: ${gap.avg_gap_percentage.toFixed(1)}%`);
    
    gap.candidates_details.forEach(candidate => {
      console.log(`    • ${candidate.employee_name}: ${candidate.current_level} → ${candidate.required_level}`);
    });
  });
}

// Output:
// 📚 Plan de formación para Creative Director:
//   Skill: Stakeholder Management
//   Gap: 66.7%
//     • Adrián López: novato → avanzado
```

---

## 📈 Fuente de Datos

### Archivo JSON Generado

Los datos provienen del archivo:
```
challenge_outputs/critical_gaps_by_role_{timestamp}.json
```

**Estructura del archivo**:
```json
{
  "R-CRT-LEAD": {
    "role_id": "R-CRT-LEAD",
    "role_title": "Creative Director",
    "critical_gaps": [
      {
        "skill_id": "S-STAKE",
        "skill_name": "Stake",
        "avg_gap_percentage": 66.67,
        "candidates_affected": 1,
        "total_viable_candidates": 1,
        "priority": "CRÍTICA",
        "criticality_score": 66.67
      }
    ],
    "total_gaps": 1,
    "highest_priority": "CRÍTICA"
  },
  "R-PM": {
    "role_id": "R-PM",
    "role_title": "Project Manager",
    "critical_gaps": [
      {
        "skill_id": "S-PM",
        "skill_name": "Pm",
        "avg_gap_percentage": 100.0,
        "candidates_affected": 0,
        "total_viable_candidates": 0,
        "priority": "CRÍTICA",
        "criticality_score": 100.0,
        "no_viable_candidates": true
      }
    ],
    "total_gaps": 4,
    "highest_priority": "CRÍTICA"
  }
}
```

---

## � Implementación Backend

### Endpoint Flask Example

```python
from flask import Flask, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

def load_critical_gaps():
    """Carga el archivo más reciente de critical gaps."""
    output_dir = Path("challenge_outputs")
    gap_files = sorted(output_dir.glob("critical_gaps_by_role_*.json"), reverse=True)
    
    if not gap_files:
        return {}
    
    with open(gap_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/roles/<role_id>/critical-gaps', methods=['GET'])
def get_role_critical_gaps(role_id):
    """
    Obtiene los critical gaps de un rol específico.
    
    Query params:
    - priority: filtrar por prioridad (CRÍTICA, ALTA, MEDIA, BAJA)
    - min_gap: gap mínimo (0-100)
    - include_candidates_details: incluir detalles de candidatos (default: true)
    """
    # Cargar datos
    all_gaps = load_critical_gaps()
    
    # Buscar rol
    if role_id not in all_gaps:
        return jsonify({
            "error": "Role not found",
            "role_id": role_id
        }), 404
    
    role_data = all_gaps[role_id]
    
    # Aplicar filtros
    priority_filter = request.args.get('priority')
    min_gap_filter = request.args.get('min_gap', type=float)
    include_details = request.args.get('include_candidates_details', 'true').lower() == 'true'
    
    gaps = role_data['critical_gaps']
    
    if priority_filter:
        gaps = [g for g in gaps if g['priority'] == priority_filter.upper()]
    
    if min_gap_filter:
        gaps = [g for g in gaps if g['avg_gap_percentage'] >= min_gap_filter]
    
    # Remover detalles de candidatos si no se requieren
    if not include_details:
        for gap in gaps:
            gap.pop('candidates_details', None)
    
    # Construir response
    response = {
        "role_id": role_data['role_id'],
        "role_title": role_data['role_title'],
        "critical_gaps": gaps,
        "total_gaps": len(gaps),
        "highest_priority": role_data.get('highest_priority')
    }
    
    # Mensaje especial para roles sin candidatos viables
    if gaps and all(g.get('no_viable_candidates', False) for g in gaps):
        response['recommendation'] = "⚠️ SIN CANDIDATOS VIABLES - Requiere hiring externo"
    
    # Mensaje para roles sin gaps
    if len(gaps) == 0 and role_data['total_gaps'] == 0:
        response['message'] = "✅ Todos los candidatos viables tienen los skills requeridos"
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
```

### Endpoint FastAPI Example

```python
from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List
import json
from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

class CandidateDetail(BaseModel):
    employee_id: str
    employee_name: str
    current_level: str
    required_level: str
    gap_percentage: float
    overall_score: float

class CriticalGap(BaseModel):
    skill_id: str
    skill_name: str
    avg_gap_percentage: float
    candidates_affected: int
    total_viable_candidates: int
    priority: str
    criticality_score: float
    no_viable_candidates: Optional[bool] = False
    candidates_details: Optional[List[CandidateDetail]] = []

class RoleCriticalGapsResponse(BaseModel):
    role_id: str
    role_title: str
    critical_gaps: List[CriticalGap]
    total_gaps: int
    highest_priority: Optional[str]
    recommendation: Optional[str] = None
    message: Optional[str] = None

def load_critical_gaps():
    """Carga el archivo más reciente de critical gaps."""
    output_dir = Path("challenge_outputs")
    gap_files = sorted(output_dir.glob("critical_gaps_by_role_*.json"), reverse=True)
    
    if not gap_files:
        return {}
    
    with open(gap_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/api/roles/{role_id}/critical-gaps", response_model=RoleCriticalGapsResponse)
async def get_role_critical_gaps(
    role_id: str,
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    min_gap: Optional[float] = Query(None, ge=0, le=100, description="Gap mínimo"),
    include_candidates_details: bool = Query(True, description="Incluir detalles de candidatos")
):
    """
    Obtiene los critical gaps de un rol específico.
    
    - **role_id**: ID del rol (e.g., R-CRT-LEAD, R-PM)
    - **priority**: Filtrar por prioridad (CRÍTICA, ALTA, MEDIA, BAJA)
    - **min_gap**: Gap mínimo para incluir (0-100)
    - **include_candidates_details**: Incluir detalles de candidatos
    """
    # Cargar datos
    all_gaps = load_critical_gaps()
    
    # Buscar rol
    if role_id not in all_gaps:
        raise HTTPException(
            status_code=404,
            detail=f"Role {role_id} not found"
        )
    
    role_data = all_gaps[role_id]
    
    # Aplicar filtros
    gaps = role_data['critical_gaps']
    
    if priority:
        gaps = [g for g in gaps if g['priority'] == priority.upper()]
    
    if min_gap is not None:
        gaps = [g for g in gaps if g['avg_gap_percentage'] >= min_gap]
    
    # Remover detalles de candidatos si no se requieren
    if not include_candidates_details:
        for gap in gaps:
            gap.pop('candidates_details', None)
    
    # Construir response
    response = {
        "role_id": role_data['role_id'],
        "role_title": role_data['role_title'],
        "critical_gaps": gaps,
        "total_gaps": len(gaps),
        "highest_priority": role_data.get('highest_priority')
    }
    
    # Mensaje especial para roles sin candidatos viables
    if gaps and all(g.get('no_viable_candidates', False) for g in gaps):
        response['recommendation'] = "⚠️ SIN CANDIDATOS VIABLES - Requiere hiring externo"
    
    # Mensaje para roles sin gaps
    if len(gaps) == 0 and role_data['total_gaps'] == 0:
        response['message'] = "✅ Todos los candidatos viables tienen los skills requeridos"
    
    return response
```

---

## 🔑 Campos Clave

### CriticalGap Object

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `skill_id` | string | ID del skill faltante (e.g., "S-STAKE") |
| `skill_name` | string | Nombre legible del skill (e.g., "Stake") |
| `avg_gap_percentage` | float | Gap promedio en % (0-100) |
| `candidates_affected` | int | Número de candidatos afectados |
| `total_viable_candidates` | int | Total de candidatos viables para el rol |
| `priority` | string | CRÍTICA, ALTA, MEDIA, BAJA |
| `criticality_score` | float | Score de criticidad (usado para ordenar) |
| `no_viable_candidates` | boolean | true si el rol no tiene candidatos viables |
| `candidates_details` | array | Detalles de cada candidato afectado |

### CandidateDetail Object

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `employee_id` | string | ID del empleado |
| `employee_name` | string | Nombre del empleado |
| `current_level` | string | Nivel actual del skill (novato, junior, etc.) |
| `required_level` | string | Nivel requerido (avanzado, senior, etc.) |
| `gap_percentage` | float | Gap individual del candidato (%) |
| `overall_score` | float | Score general del candidato para el rol (0-1) |

---

## � Notas de Implementación

### Score Threshold

- El análisis considera **candidatos viables** aquellos con `overall_score ≥ 0.5`
- Candidatos con score < 0.5 no se consideran en el análisis de gaps

### Nivel Requerido por Defecto

- Si no se especifica, todos los skills se asumen al nivel **AVANZADO** (0.75)

### Prioridades

- **CRÍTICA**: gap ≥ 60% o sin candidatos viables
- **ALTA**: gap ≥ 40%
- **MEDIA**: gap ≥ 20%
- **BAJA**: gap < 20%

### Actualización de Datos

- Los datos se generan al ejecutar `main_challenge.py`
- Se guarda un timestamp en el nombre del archivo
- La API siempre lee el archivo más reciente

---

## ✅ Testing

```bash
# Test 1: Rol con gaps
curl http://localhost:5000/api/roles/R-CRT-LEAD/critical-gaps

# Test 2: Rol sin candidatos viables
curl http://localhost:5000/api/roles/R-PM/critical-gaps

# Test 3: Filtrar por prioridad
curl http://localhost:5000/api/roles/R-PM/critical-gaps?priority=CRÍTICA

# Test 4: Sin detalles de candidatos
curl http://localhost:5000/api/roles/R-CRT-LEAD/critical-gaps?include_candidates_details=false

# Test 5: Gap mínimo
curl http://localhost:5000/api/roles/R-CRT-LEAD/critical-gaps?min_gap=50
```

app = Flask(__name__)

# Cargar datos precalculados
with open('challenge_outputs/bottlenecks_by_role_latest.json') as f:
    BOTTLENECKS_BY_ROLE = json.load(f)

@app.route('/api/roles/<role_id>/bottlenecks', methods=['GET'])
def get_role_bottlenecks(role_id):
    """Obtiene bottlenecks críticos de un rol específico"""
    
    # Verificar que el rol existe
    if role_id not in BOTTLENECKS_BY_ROLE:
        return jsonify({
            'error': 'Role not found',
            'role_id': role_id,
            'available_roles': list(BOTTLENECKS_BY_ROLE.keys())
        }), 404
    
    role_data = BOTTLENECKS_BY_ROLE[role_id]
    
    # Aplicar filtros opcionales
    priority = request.args.get('priority')
    min_gap = request.args.get('min_gap', type=float)
    
    bottlenecks = role_data['critical_bottlenecks']
    
    if priority:
        bottlenecks = [b for b in bottlenecks if b['priority'] == priority]
    
    if min_gap:
        bottlenecks = [b for b in bottlenecks if b['gap_percentage'] >= min_gap]
    
    response = {
        'role_id': role_data['role_id'],
        'role_title': role_data['role_title'],
        'critical_bottlenecks': bottlenecks,
        'total_bottlenecks': len(bottlenecks),
        'highest_gap': max([b['gap_percentage'] for b in bottlenecks]) if bottlenecks else 0,
        'total_blocked_transitions': sum([b['blocked_transitions'] for b in bottlenecks])
    }
    
    return jsonify(response)

@app.route('/api/roles', methods=['GET'])
def list_roles():
    """Lista todos los roles con sus métricas de bottlenecks"""
    
    summary = []
    for role_id, data in BOTTLENECKS_BY_ROLE.items():
        summary.append({
            'role_id': role_id,
            'role_title': data['role_title'],
            'total_bottlenecks': data['total_bottlenecks'],
            'highest_gap': data['highest_gap'],
            'total_blocked_transitions': data['total_blocked_transitions']
        })
    
    # Ordenar por highest_gap descendente
    summary.sort(key=lambda x: x['highest_gap'], reverse=True)
    
    return jsonify({
        'total_roles': len(summary),
        'roles': summary
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 💡 Ventajas de Este Enfoque

1. **Consulta por Rol**: Permite al frontend preguntar "¿Qué le falta a este rol?" en lugar de filtrar manualmente
2. **Datos Precalculados**: El archivo JSON se genera una vez, las consultas son instantáneas
3. **Flexible**: Soporta filtros por prioridad y gap mínimo
4. **Accionable**: Cada bottleneck incluye métricas específicas (empleados sin skill, demanda proyectada)
5. **Escalable**: Funciona igual para 10 roles o 100 roles

---

## 📝 Archivo Fuente

Los datos se generan automáticamente en:
```
challenge_outputs/bottlenecks_by_role_{timestamp}.json
```

Puedes crear un symlink para tener siempre la última versión:
```bash
ln -sf bottlenecks_by_role_$(ls -t | grep bottlenecks_by_role | head -1) bottlenecks_by_role_latest.json
```
