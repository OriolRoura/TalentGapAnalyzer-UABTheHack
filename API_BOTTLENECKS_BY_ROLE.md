# API de Bottlenecks por Rol

## 📋 Descripción

Este endpoint permite consultar los bottlenecks críticos que afectan a un rol específico, facilitando la toma de decisiones sobre inversiones en formación y contratación.

---

## 🔍 Endpoint: GET /api/roles/{role_id}/bottlenecks

### Request

**Método**: `GET`

**URL**: `/api/roles/{role_id}/bottlenecks`

**Parámetros de URL**:
- `role_id` (string, requerido): ID del rol a consultar
  - Ejemplos: `R-STR-LEAD`, `R-MTX-ARCH`, `R-DATA-ANL`

**Query Parameters** (opcionales):
- `priority` (string): Filtrar por prioridad (`HIGH`, `MEDIUM`, `LOW`)
- `min_gap` (float): Gap mínimo para incluir (0-100)

### Response

**Status Code**: `200 OK`

**Response Body**:

```json
{
  "role_id": "R-MTX-ARCH",
  "role_title": "Martech Architect",
  "critical_bottlenecks": [
    {
      "skill_id": "S-DATA",
      "skill_name": "Data",
      "gap_percentage": 80.0,
      "blocked_transitions": 16,
      "priority": "HIGH",
      "employees_without_skill": 8,
      "demanda_proyectada": 5,
      "capacidad_actual": 1
    },
    {
      "skill_id": "S-CRM",
      "skill_name": "Crm",
      "gap_percentage": 66.67,
      "blocked_transitions": 16,
      "priority": "HIGH",
      "employees_without_skill": 8,
      "demanda_proyectada": 6,
      "capacidad_actual": 2
    }
  ],
  "total_bottlenecks": 2,
  "highest_gap": 80.0,
  "total_blocked_transitions": 32,
  "recommendations": [
    {
      "action": "TRAINING_PRIORITY",
      "skill_id": "S-DATA",
      "reason": "80% gap blocking 16 transitions",
      "impact": "HIGH"
    },
    {
      "action": "EXTERNAL_HIRING",
      "skill_id": "S-DATA",
      "reason": "Only 1 employee has this critical skill",
      "impact": "HIGH"
    }
  ]
}
```

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Consultar bottlenecks de "Martech Architect"

**Request**:
```bash
GET /api/roles/R-MTX-ARCH/bottlenecks
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
      "blocked_transitions": 16,
      "priority": "HIGH",
      "employees_without_skill": 8,
      "demanda_proyectada": 5,
      "capacidad_actual": 1
    },
    {
      "skill_id": "S-CRM",
      "skill_name": "Crm",
      "gap_percentage": 66.67,
      "blocked_transitions": 16,
      "priority": "HIGH"
    }
  ],
  "total_bottlenecks": 2,
  "highest_gap": 80.0,
  "total_blocked_transitions": 32
}
```

**Interpretación**:
- El rol **Martech Architect** tiene **2 bottlenecks críticos**
- El bottleneck más grave es **S-DATA** con un gap del **80%**
- Hay **8 empleados** que no tienen el skill S-DATA
- Esto está bloqueando **16 transiciones** potenciales a este rol

---

### Ejemplo 2: Consultar bottlenecks de "Data Analyst"

**Request**:
```bash
GET /api/roles/R-DATA-ANL/bottlenecks
```

**Response**:
```json
{
  "role_id": "R-DATA-ANL",
  "role_title": "Data Analyst",
  "critical_bottlenecks": [
    {
      "skill_id": "S-DATA",
      "skill_name": "Data",
      "gap_percentage": 80.0,
      "blocked_transitions": 16,
      "priority": "HIGH",
      "employees_without_skill": 8,
      "demanda_proyectada": 5,
      "capacidad_actual": 1
    }
  ],
  "total_bottlenecks": 1,
  "highest_gap": 80.0,
  "total_blocked_transitions": 16
}
```

**Interpretación**:
- Solo **1 bottleneck crítico**: S-DATA
- Gap del **80%** (muy crítico)
- **16 transiciones bloqueadas**

---

### Ejemplo 3: Consultar bottlenecks de "Head of Strategy"

**Request**:
```bash
GET /api/roles/R-STR-LEAD/bottlenecks
```

**Response**:
```json
{
  "role_id": "R-STR-LEAD",
  "role_title": "Head of Strategy",
  "critical_bottlenecks": [
    {
      "skill_id": "S-ANALISIS",
      "skill_name": "Analisis",
      "gap_percentage": 75.0,
      "blocked_transitions": 16,
      "priority": "HIGH",
      "employees_without_skill": 8,
      "demanda_proyectada": 8,
      "capacidad_actual": 2
    }
  ],
  "total_bottlenecks": 1,
  "highest_gap": 75.0,
  "total_blocked_transitions": 16
}
```

---

### Ejemplo 4: Filtrar por prioridad HIGH

**Request**:
```bash
GET /api/roles/R-MTX-ARCH/bottlenecks?priority=HIGH
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
}
```

---

### Ejemplo 5: Filtrar por gap mínimo

**Request**:
```bash
GET /api/roles/R-MTX-ARCH/bottlenecks?min_gap=70
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
    }
  ],
  "total_bottlenecks": 1,
  "filtered_out": 1
}
```

---

## 🎯 Casos de Uso

### 1. Dashboard de Rol
```javascript
// Frontend muestra página de detalle de un rol
const roleId = 'R-MTX-ARCH';
const response = await fetch(`/api/roles/${roleId}/bottlenecks`);
const data = await response.json();

// Mostrar:
// - Título del rol: "Martech Architect"
// - Total bottlenecks: 2
// - Gap más alto: 80%
// - Lista de skills críticos: S-DATA, S-CRM
```

### 2. Planificación de Formación
```javascript
// Obtener bottlenecks de todos los roles estratégicos
const strategicRoles = ['R-STR-LEAD', 'R-MTX-ARCH', 'R-DATA-ANL'];

const bottlenecks = await Promise.all(
  strategicRoles.map(roleId => 
    fetch(`/api/roles/${roleId}/bottlenecks?priority=HIGH`)
      .then(r => r.json())
  )
);

// Consolidar skills críticos para priorizar inversión en formación
const criticalSkills = new Set();
bottlenecks.forEach(role => {
  role.critical_bottlenecks.forEach(b => {
    criticalSkills.add(b.skill_id);
  });
});

console.log('Skills a desarrollar:', Array.from(criticalSkills));
// Output: ['S-DATA', 'S-CRM', 'S-ANALISIS']
```

### 3. Recomendaciones de Contratación
```javascript
// Para un rol con múltiples bottlenecks, priorizar contratación externa
const response = await fetch('/api/roles/R-MTX-ARCH/bottlenecks');
const data = await response.json();

if (data.total_bottlenecks > 1 && data.highest_gap > 70) {
  console.log(`⚠️ RECOMENDACIÓN: Contratar externamente para ${data.role_title}`);
  console.log(`Razón: ${data.total_bottlenecks} bottlenecks críticos`);
  console.log(`Gap más alto: ${data.highest_gap}%`);
}
```

---

## 📈 Datos Disponibles por Rol

### Todos los Roles con Bottlenecks

| Role ID | Role Title | Total Bottlenecks | Highest Gap | Blocked Transitions |
|---------|-----------|-------------------|-------------|---------------------|
| R-MTX-ARCH | Martech Architect | 2 | 80.0% | 32 |
| R-DATA-ANL | Data Analyst | 1 | 80.0% | 16 |
| R-STR-LEAD | Head of Strategy | 1 | 75.0% | 16 |
| R-STR-SR | Senior Strategy Consultant | 1 | 75.0% | 16 |
| R-DSN-SR | Senior Brand/UI Designer | 1 | 75.0% | 9 |
| R-CRM-ADMIN | CRM Admin (HubSpot) | 1 | 66.7% | 16 |

---

## 🔧 Implementación Backend

### Endpoint Flask/FastAPI Example

```python
from flask import Flask, jsonify, request
import json

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
