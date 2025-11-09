# Talent Gap Analyzer API

FastAPI-based REST API for managing employee data, roles, and HR inputs for talent gap analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Navigate to API directory**
```bash
cd api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file**
```bash
cp .env.example .env
```

5. **Run the API**
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## 📋 API Structure

```
api/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── models/                # Pydantic models for data validation
│   ├── employee.py        # Employee models
│   ├── role.py            # Role and skill models
│   ├── hr_forms.py        # HR input form models
│   └── company.py         # Company configuration models
├── routes/                # API endpoints
│   ├── health.py          # Health check endpoints
│   ├── employees.py       # Employee CRUD operations
│   ├── roles.py           # Role CRUD operations
│   ├── company.py         # Company status and config
│   └── hr_forms.py        # HR form submissions
└── services/              # Business logic services
    ├── data_loader.py     # Load data from CSV/JSON files
    ├── validation_service.py  # Data validation logic
    └── gap_service.py     # Gap analysis (PLACEHOLDER for Samya)
```

## 🔌 API Endpoints

### Health & Info
- `GET /api/v1/health` - Health check
- `GET /api/v1/info` - API information

### Employees
- `GET /api/v1/employees` - List all employees (with filters)
- `GET /api/v1/employees/stats` - Employee statistics
- `GET /api/v1/employees/{id}` - Get employee by ID
- `POST /api/v1/employees` - Create new employee
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Delete employee
- `GET /api/v1/employees/{id}/validate` - Validate employee data

### Roles
- `GET /api/v1/roles` - List all roles (with filters)
- `GET /api/v1/roles/{id}` - Get role by ID
- `POST /api/v1/roles` - Create new role
- `PUT /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role
- `GET /api/v1/roles/chapters/list` - List all chapters
- `GET /api/v1/roles/skills/list` - List all skills
- `POST /api/v1/roles/skills/` - Create new skill

### Company
- `GET /api/v1/company/status` - Company status snapshot
- `GET /api/v1/company/health` - Company data health check
- `GET /api/v1/company/config` - Company configuration
- `GET /api/v1/company/vision` - Future vision and roadmap
- `GET /api/v1/company/chapters` - Chapters summary
- `GET /api/v1/company/dashboard` - Dashboard data

### HR Forms
- `POST /api/v1/hr/employee/new` - Submit new employee form
- `POST /api/v1/hr/employee/{id}/skills` - Update employee skills
- `POST /api/v1/hr/employee/{id}/evaluation` - Submit employee evaluation
- `POST /api/v1/hr/employee/{id}/dedication` - Update project dedication
- `POST /api/v1/hr/role/define` - Define new future role
- `POST /api/v1/hr/skills/bulk-update` - Bulk update skills
- `POST /api/v1/hr/analysis/request` - Request gap analysis *(PLACEHOLDER)*
- `GET /api/v1/hr/analysis/{id}` - Get analysis results *(PLACEHOLDER)*
- `POST /api/v1/hr/validate/all` - Validate all data
- `POST /api/v1/hr/validate/employee/{id}` - Validate employee

## 📊 Data Models

### Employee
```json
{
  "id_empleado": 1001,
  "nombre": "Jordi Casals",
  "email": "jordi.casals@quether.com",
  "chapter": "Strategy",
  "rol_actual": "Head of Strategy",
  "manager": null,
  "antiguedad": "24m",
  "habilidades": {"S-OKR": 9, "S-ANALISIS": 9},
  "responsabilidades_actuales": ["OKRs y gobierno"],
  "dedicacion_actual": {"Royal": 40, "Arquimbau": 25},
  "ambiciones": {
    "especialidades_preferidas": ["Estrategia"],
    "nivel_aspiracion": "lead"
  },
  "metadata": {
    "performance_rating": "A",
    "retention_risk": "Baja",
    "trayectoria": "Head of Strategy > Director"
  }
}
```

### Role
```json
{
  "id": "R-STR-LEAD",
  "titulo": "Head of Strategy",
  "nivel": "lead",
  "capitulo": "Strategy",
  "modalidad": "FT",
  "cantidad": 1,
  "inicio_estimado": "0-3m",
  "responsabilidades": ["Definir visión estratégica"],
  "habilidades_requeridas": ["S-OKR", "S-ANALISIS"],
  "objetivos_asociados": ["OKRs y gobierno"],
  "dedicacion_esperada": "30-40h/semana"
}
```

## 🔐 Data Validation

The API automatically validates:
- ✅ Dedication percentages sum to 100%
- ✅ Skill levels are between 0-10
- ✅ Email uniqueness
- ✅ No dual role assignments
- ✅ Manager existence
- ✅ Data completeness

## 🧪 Testing Examples

### Get all employees
```bash
curl http://localhost:8000/api/v1/employees
```

### Filter employees by chapter
```bash
curl http://localhost:8000/api/v1/employees?chapter=Strategy
```

### Get company health check
```bash
curl http://localhost:8000/api/v1/company/health
```

### Create new employee
```bash
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Employee",
    "email": "test@quether.com",
    "chapter": "Strategy",
    "rol_actual": "Analyst",
    "antiguedad": "0m",
    "habilidades": {"S-ANALISIS": 7},
    "dedicacion_actual": {"Project A": 100},
    "ambiciones": {
      "especialidades_preferidas": ["Analytics"],
      "nivel_aspiracion": "mid"
    },
    "metadata": {
      "performance_rating": "B",
      "retention_risk": "Baja",
      "trayectoria": "New hire"
    }
  }'
```

### Submit HR evaluation form
```bash
curl -X POST http://localhost:8000/api/v1/hr/employee/1001/evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1001,
    "evaluation_date": "2025-11-08",
    "performance_rating": "A",
    "retention_risk": "Baja",
    "career_aspirations": ["Leadership", "Strategy"],
    "desired_seniority": "lead",
    "strengths": ["Strategic thinking", "OKRs"],
    "areas_for_improvement": ["Delegation"]
  }'
```

## 🔄 Integration with Gap Algorithm

The API is designed to feed data into Samya's gap algorithm:

1. **Data Input**: HR uses endpoints to input/update employee and role data
2. **Validation**: API validates all data automatically
3. **Gap Analysis Request**: `POST /api/v1/hr/analysis/request` triggers analysis
4. **Algorithm Processing**: Samya's algorithm processes the data (PLACEHOLDER)
5. **Results Retrieval**: `GET /api/v1/hr/analysis/{id}` returns results

### Gap Analysis Request Example
```json
{
  "analysis_name": "Q4 2025 Gap Analysis",
  "description": "Quarterly talent assessment",
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

## 📝 Data Sources

The API loads initial data from:
- `../dataSet/talent-gap-analyzer-main/talento_actual.csv` - Current employees
- `../dataSet/talent-gap-analyzer-main/org_config.json` - Organization config
- `../dataSet/talent-gap-analyzer-main/vision_futura.json` - Future roles

## 🚧 PLACEHOLDER for Samya

The following functions in `services/gap_service.py` need implementation:
- `calculate_gap()` - Main gap calculation algorithm
- `calculate_bulk_gaps()` - Bulk analysis
- `calculate_skills_gap()` - Skills gap calculation
- `calculate_responsibilities_gap()` - Responsibilities gap
- `calculate_ambitions_alignment()` - Ambitions alignment
- `calculate_dedication_availability()` - Dedication availability
- `generate_recommendations()` - AI-powered recommendations

## 🐛 Troubleshooting

### Import errors
```bash
pip install -r requirements.txt
```

### Data not loading
Check that CSV/JSON files exist in `../dataSet/talent-gap-analyzer-main/`

### CORS errors
Update `CORS_ORIGINS` in `.env` file

## 👥 Team

- **API Development**: Your team
- **Gap Algorithm**: Samya
- **Data Source**: `dataSet/talent-gap-analyzer-main/`

## 📄 License

Hackathon Project - UAB The Hack 2025
