# Endpoints Reference

## Quick Reference for Frontend/Testing

### Base URL
```
http://localhost:8000
```

## 🏥 Health & Info

### Health Check
```http
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T10:30:00",
  "service": "Talent Gap Analyzer API",
  "version": "1.0.0"
}
```

---

## 👥 Employees

### List All Employees
```http
GET /api/v1/employees?chapter=Strategy&skip=0&limit=100
```

### Get Employee Stats
```http
GET /api/v1/employees/stats
```

### Get Single Employee
```http
GET /api/v1/employees/1001
```

### Create Employee
```http
POST /api/v1/employees
Content-Type: application/json

{
  "nombre": "New Employee",
  "email": "new@quether.com",
  "chapter": "Strategy",
  "rol_actual": "Analyst",
  "antiguedad": "0m",
  "habilidades": {"S-ANALISIS": 7},
  "responsabilidades_actuales": ["Analysis"],
  "dedicacion_actual": {"Project A": 100},
  "ambiciones": {
    "especialidades_preferidas": ["Strategy"],
    "nivel_aspiracion": "mid"
  },
  "metadata": {
    "performance_rating": "B",
    "retention_risk": "Baja",
    "trayectoria": "New hire"
  }
}
```

### Update Employee
```http
PUT /api/v1/employees/1001
Content-Type: application/json

{
  "habilidades": {"S-OKR": 10, "S-ANALISIS": 9}
}
```

### Validate Employee
```http
GET /api/v1/employees/1001/validate
```

---

## 🎯 Roles

### List All Roles
```http
GET /api/v1/roles?chapter=Strategy&nivel=lead
```

### Get Single Role
```http
GET /api/v1/roles/R-STR-LEAD
```

### Create Role
```http
POST /api/v1/roles
Content-Type: application/json

{
  "titulo": "Data Scientist",
  "nivel": "senior",
  "capitulo": "Martech",
  "modalidad": "FT",
  "cantidad": 1,
  "inicio_estimado": "0-3m",
  "responsabilidades": ["ML models", "Data analysis"],
  "habilidades_requeridas": ["S-SQLPY", "S-ANALYTICS"],
  "objetivos_asociados": ["AI implementation"]
}
```

### List Chapters
```http
GET /api/v1/roles/chapters/list
```

### List Skills
```http
GET /api/v1/roles/skills/list
```

---

## 🏢 Company

### Company Status
```http
GET /api/v1/company/status
```

### Company Health Check
```http
GET /api/v1/company/health
```

### Company Config
```http
GET /api/v1/company/config
```

### Future Vision
```http
GET /api/v1/company/vision
```

### Dashboard Data
```http
GET /api/v1/company/dashboard
```

---

## 📋 HR Forms

### Add New Employee (HR Form)
```http
POST /api/v1/hr/employee/new
Content-Type: application/json

{
  "nombre": "Maria Garcia",
  "email": "maria@quether.com",
  "chapter": "Creative",
  "rol_actual": "Designer",
  "start_date": "2025-11-08",
  "contract_type": "FT",
  "initial_skills": [
    {
      "employee_id": 0,
      "skill_id": "S-BRAND",
      "skill_name": "Branding",
      "current_level": 7
    }
  ],
  "initial_dedication": {"Project A": 100}
}
```

### Update Employee Skills
```http
POST /api/v1/hr/employee/1001/skills
Content-Type: application/json

[
  {
    "employee_id": 1001,
    "skill_id": "S-OKR",
    "skill_name": "OKRs",
    "current_level": 10,
    "last_assessment_date": "2025-11-08"
  }
]
```

### Submit Employee Evaluation
```http
POST /api/v1/hr/employee/1001/evaluation
Content-Type: application/json

{
  "employee_id": 1001,
  "evaluation_date": "2025-11-08",
  "performance_rating": "A",
  "retention_risk": "Baja",
  "career_aspirations": ["Leadership", "Strategy"],
  "desired_seniority": "lead",
  "strengths": ["Strategic thinking"],
  "areas_for_improvement": ["Delegation"]
}
```

### Update Project Dedication
```http
POST /api/v1/hr/employee/1001/dedication
Content-Type: application/json

{
  "employee_id": 1001,
  "dedications": {
    "Royal": 50,
    "Arquimbau": 30,
    "I+D": 20
  },
  "effective_date": "2025-11-08"
}
```

### Define New Role (HR Form)
```http
POST /api/v1/hr/role/define
Content-Type: application/json

{
  "role_title": "AI Engineer",
  "chapter": "Martech",
  "seniority_level": "senior",
  "positions_needed": 2,
  "estimated_start": "3-6m",
  "key_responsibilities": ["Build AI models", "MLOps"],
  "required_skills": ["S-SQLPY", "S-GENAI"],
  "required_skill_levels": {
    "S-SQLPY": 8,
    "S-GENAI": 9
  },
  "priority": "high"
}
```

### Request Gap Analysis
```http
POST /api/v1/hr/analysis/request
Content-Type: application/json

{
  "analysis_name": "Q4 2025 Analysis",
  "description": "Quarterly talent gap assessment",
  "include_chapters": ["Strategy", "Martech"],
  "target_roles": ["R-STR-LEAD", "R-MTX-ARCH"],
  "timeline": "12_meses",
  "algorithm_weights": {
    "skills": 0.50,
    "responsibilities": 0.25,
    "ambitions": 0.15,
    "dedication": 0.10
  }
}
```

### Get Analysis Results
```http
GET /api/v1/hr/analysis/{analysis_id}
```

### Validate All Data
```http
POST /api/v1/hr/validate/all
```

### Validate Specific Employee
```http
POST /api/v1/hr/validate/employee/1001
```

---

## 📊 Response Formats

### Success Response
```json
{
  "id_empleado": 1001,
  "nombre": "Jordi Casals",
  ...
}
```

### Error Response
```json
{
  "detail": "Employee 9999 not found"
}
```

### Validation Error
```json
{
  "detail": {
    "errors": [
      "Dedication percentages must sum to 100%, got 95%"
    ]
  }
}
```

---

## 🔗 Interactive Documentation

Visit these URLs when the API is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API testing and complete schema documentation.
