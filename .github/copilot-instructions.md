# Talent Gap Analyzer - AI Agent Instructions

## Project Overview
FastAPI-based REST API for talent gap analysis at **UAB TheHack 2025**. Processes employee data (up to 300 employees) to identify skill gaps against future role requirements. Built for a 5-hour hackathon challenge to compress a 3-5 day manual HR process into an automated system.

## Architecture

### Core Components
- **FastAPI Backend** (`api/main.py`): Entry point with startup data loading via `lifespan` context manager
- **In-Memory Data Store** (`services/data_loader.py`): Singleton pattern (`data_loader` instance) loads CSV/JSON on startup - NO database
- **Pydantic Models** (`models/`): Strict validation for employee skills (0-10), dedication percentages (must sum to 100%)
- **Routes** (`routes/`): RESTful CRUD + specialized HR form endpoints
- **Services** (`services/`): Business logic for validation and gap analysis (gap_service.py is PLACEHOLDER for algorithm implementation)

### Data Flow
```
dataSet/talent-gap-analyzer-main/*.{csv,json}
  → DataLoader.load_all_data() on startup
  → In-memory DataStore
  → Routes via data_loader singleton
  → Pydantic validation
  → JSON responses
```

## Critical Patterns

### 1. Data Loading (Startup-Only)
Data loads ONCE at startup in `main.py` lifespan manager. All CRUD operations modify in-memory store only - changes are NOT persisted to disk.

```python
# Always use the global singleton
from services.data_loader import data_loader
employees = data_loader.get_employees()  # Returns Dict[int, Employee]
```

### 2. Model Validation
Employee model has TWO levels of validation:
1. **Pydantic validators** (in model definition): `@field_validator` for dedication sum=100%, skill levels 0-10
2. **Business validation** (`ValidationService`): Cross-entity rules (email uniqueness, manager existence)

When creating/updating employees:
```python
# Pydantic validates first (automatic)
employee = Employee(**data)

# Then apply business rules
is_valid, errors = ValidationService.validate_employee_dedication(employee)
if not is_valid:
    raise HTTPException(status_code=400, detail=errors)
```

### 3. Models Package Import Issue
**CURRENT BUG**: `models/__init__.py` line 23 tries to import `HREmployeeSkillForm` but actual class is `HREmployeeSkillSubmit` (in `models/hr_forms.py`). This causes ImportError on startup.

Fix pattern: Check `__init__.py` exports match actual class names in model files.

### 4. Spanish Data Convention
CSV data and field names mix Spanish/English:
- CSV columns: `antigüedad`, `dedicación_actual` (Spanish)
- Model fields: `antiguedad`, `dedicacion_actual` (no accents)
- Parse with quote replacement: `json.loads(row['habilidades'].replace("'", '"'))`

### 5. ID Generation Pattern
Auto-increment from max existing ID:
```python
employees = data_loader.get_employees()
new_id = max(employees.keys()) + 1 if employees else 1001
```

## Development Workflows

### Running the API
```bash
cd api
python main.py  # Uses uvicorn with reload
# OR: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing Endpoints
Use `/docs` interactive Swagger UI. No auth configured (MVP for hackathon). Key test endpoints:
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/employees/stats` - Verify data loaded correctly
- `GET /api/v1/company/status` - Comprehensive company snapshot

### Common Errors

**ImportError on startup**: Check `models/__init__.py` exports match actual model class names. Model names with "Submit" vs "Form" suffix are inconsistent.

**Validation errors**: Employee dedication must sum to 100%, skill levels 0-10. The validator runs automatically in Pydantic model.

**Data not loading**: Check `dataSet/talent-gap-analyzer-main/` path exists relative to `api/services/data_loader.py`. Prints load status on startup.

## Key Files Reference

### Data Schema
- `dataSet/talent-gap-analyzer-main/talento_actual.csv`: Employee data (Spanish CSV with JSON columns)
- `dataSet/talent-gap-analyzer-main/vision_futura.json`: Future role definitions
- `dataSet/talent-gap-analyzer-main/org_config.json`: Chapters and skills taxonomy
- `dataSet/talent-gap-analyzer-main/company_projects.json`: Project/client list

### Models (Critical)
- `models/employee.py`: Employee with nested Ambitions, Metadata. Has field validators for dedication/skills.
- `models/role.py`: Role definitions with required skills and responsibilities
- `models/hr_forms.py`: HR input forms - naming inconsistent (Submit vs Form suffix)
- `models/__init__.py`: **Import hub - check this first when adding models**

### Routes (API Structure)
- `routes/health.py`: Basic health checks
- `routes/employees.py`: CRUD + stats endpoint (calculates on-the-fly)
- `routes/roles.py`: CRUD + chapter/skill list endpoints
- `routes/company.py`: Status, health, dashboard aggregations
- `routes/hr_forms.py`: Unified employee submit form (`POST /hr/employee/submit`)

### Services (Business Logic)
- `services/data_loader.py`: **SINGLETON** - one global instance. Load CSV/JSON → in-memory store
- `services/validation_service.py`: Business rules (dedication sum, email uniqueness, skill ranges)
- `services/gap_service.py`: **PLACEHOLDER** - gap algorithm implementation goes here

## Integration Points

### Gap Analysis Algorithm (To Be Implemented)
Location: `services/gap_service.py` - `GapAnalysisService.calculate_gap()`

Expected signature:
```python
def calculate_gap(employee: Employee, target_role: Role, 
                  weights: Dict[str, float] = None) -> EmployeeSkillGap:
    # Returns: overall_gap_score (0-100), classification (READY/NEAR/FAR),
    # skill_gaps, recommendations
```

Default weights: skills=0.5, responsibilities=0.25, ambitions=0.15, dedication=0.1

### HR Form Submission
Main endpoint: `POST /api/v1/hr/employee/submit` - unified create/update
- If `employee_id` provided → update existing
- If `employee_id` omitted → auto-generate new ID starting from 1001

## Project-Specific Conventions

1. **No Database**: All data in-memory. Changes lost on restart. This is intentional for hackathon MVP.
2. **Spanish field names**: CSV uses accents (`antigüedad`), Python models remove them (`antiguedad`)
3. **Skill IDs**: Format `S-{CATEGORY}` (e.g., `S-OKR`, `S-ANALISIS`, `S-CRM`)
4. **Role IDs**: Format `R-{CHAPTER}-{LEVEL}` (e.g., `R-STR-LEAD`, `R-TECH-MID`)
5. **Tenure format**: String with 'm' suffix (e.g., `"24m"` = 24 months). Parse with `.replace('m', '').strip()`
6. **Performance ratings**: Single letters: A, A-, B+, B, C
7. **Retention risk**: Spanish: "Baja", "Media", "Alta"

## Documentation Files
- `api/README.md`: Setup, structure, endpoints overview
- `api/ENDPOINTS.md`: Detailed endpoint examples with curl/JSON
- `api/INTEGRATION_GUIDE.md`: Gap algorithm integration spec
- `HR_FORMS_ENDPOINTS.md`: HR form usage guide (Spanish)

## Common Pitfalls

❌ **Don't** try to persist changes to CSV/JSON files - system is read-only from disk  
❌ **Don't** assume database exists - it's purely in-memory  
❌ **Don't** forget dedication validation - it MUST sum to 100%  
❌ **Don't** use skill levels outside 0-10 range  
❌ **Don't** import models directly - use `models/__init__.py` exports  

✅ **Do** use `data_loader` singleton for all data access  
✅ **Do** validate with both Pydantic and ValidationService  
✅ **Do** check model import names match in `__init__.py`  
✅ **Do** use `/docs` Swagger UI for rapid testing  
✅ **Do** preserve Spanish terminology in user-facing fields
