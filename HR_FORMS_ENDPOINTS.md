# Endpoints de Formularis HR

Guia ràpida per desenvolupar els formularis d'RH. Base URL: `http://localhost:8000/api/v1/hr`

## 📝 Gestió d'Empleats

### Submit Employee Profile (Nou/Actualitzar)
**✨ Endpoint principal per gestionar perfils complets d'empleats**

```http
POST /hr/employee/submit
```

Aquest endpoint unificat permet crear nous empleats o actualitzar els existents amb un sol formulari complet.

**Body:**
```json
{
  "employee_id": "1011",
  "nombre": "Juan Pérez",
  "email": "juan.perez@company.com",
  "chapter": "Strategy",
  "seniority": "senior",
  "modalidad": "Full-time",
  "skills": [
    {
      "nombre": "Python",
      "nivel": 4,
      "experiencia_años": 5
    },
    {
      "nombre": "Data Analysis",
      "nivel": 3,
      "experiencia_años": 3
    }
  ],
  "responsabilidades": [
    "Project planning",
    "Team coordination"
  ],
  "ambiciones": {
    "especialidades_preferidas": ["AI", "Machine Learning"],
    "nivel_aspiracion": "lead",
    "interes_liderazgo": true,
    "areas_interes": ["Technology", "Innovation"]
  },
  "dedicacion": {
    "proyecto_actual": "Digital Transformation",
    "porcentaje_dedicacion": 100,
    "horas_semana": 40
  }
}
```

**Resposta d'Èxit (200):**
```json
{
  "status": "success",
  "message": "Employee profile submitted successfully",
  "employee_id": "1011",
  "validation": {
    "skills_count": 2,
    "dedication_valid": true
  }
}
```

## 🎯 Definir Rols Futurs

### Crear Nou Rol
```http
POST /hr/role/define
```
**Body:**
```json
{
  "role_title": "Strategy Lead",
  "chapter": "Strategy",
  "seniority_level": "lead",
  "positions_needed": 2,
  "estimated_start": "2025-Q2",
  "key_responsibilities": ["Team leadership", "Strategy planning"],
  "required_skills": {
    "S-LIDERAZGO": 8,
    "S-ESTRATEGIA": 9
  }
}
```

## 🔄 Actualitzacions Massives

### Actualitzar Múltiples Habilitats
```http
POST /hr/skills/bulk-update
```
**Body:**
```json
{
  "updates": [
    {"employee_id": 1001, "skill_id": "S-ANALISIS", "current_level": 8},
    {"employee_id": 1002, "skill_id": "S-ANALISIS", "current_level": 7}
  ],
  "updated_by": "HR Manager",
  "update_reason": "Q4 Skill Assessment"
}
```

## 📊 Anàlisi de Gaps

### Sol·licitar Anàlisi
```http
POST /hr/analysis/request
```
**Body:**
```json
{
  "analysis_name": "Q1 2025 Planning",
  "target_roles": ["R-STR-LEAD", "R-STR-CONS"],
  "filters": {
    "chapters": ["Strategy", "Operations"]
  },
  "requested_by": "HR Manager"
}
```

### Consultar Resultats
```http
GET /hr/analysis/{analysis_id}
```

## ✅ Validació

### Validar Tot el Sistema
```http
POST /hr/validate/all
```

### Validar Empleat Específic
```http
POST /hr/validate/employee/{employee_id}
```

---

## Notes Importants

- **Dedicació**: Ha de sumar sempre 100%
- **Skill Levels**: Entre 0-10
- **Seniority Levels**: `junior`, `mid`, `mid-senior`, `senior`, `lead`
- **Performance Ratings**: `A`, `B`, `C`
- **Retention Risk**: `Baja`, `Media`, `Alta`

## Respostes Típiques

**Èxit (200/201):**
```json
{
  "employee_id": 1001,
  "message": "Updated successfully"
}
```

**Error (400):**
```json
{
  "detail": {
    "errors": ["Dedication must sum to 100%"]
  }
}
```

**No Trobat (404):**
```json
{
  "detail": "Employee 1001 not found"
}
```
