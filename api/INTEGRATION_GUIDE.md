# API & Gap Algorithm Integration Guide

## 📋 Overview

This document explains how the API and Samya's gap algorithm will work together.

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend/HR   │
│   Department    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌──────────────────────────────┐   │
│  │  Routes (API Endpoints)      │   │
│  └──────────┬───────────────────┘   │
│             │                        │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  Services Layer              │   │
│  │  • Data Loader               │   │
│  │  • Validation Service        │   │
│  │  • Gap Analysis Service ◄────┼───── Samya implements this
│  └──────────┬───────────────────┘   │
│             │                        │
│             ▼                        │
│  ┌──────────────────────────────┐   │
│  │  Data Store (In-Memory)      │   │
│  │  • Employees                 │   │
│  │  • Roles                     │   │
│  │  • Skills                    │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

## 🔄 Data Flow for Gap Analysis

### 1. Data Collection (Your API)
```
HR → POST /api/v1/hr/employee/new → Creates Employee
HR → POST /api/v1/hr/employee/{id}/skills → Updates Skills
HR → POST /api/v1/hr/employee/{id}/evaluation → Updates Evaluation
HR → POST /api/v1/hr/role/define → Defines Future Roles
```

### 2. Validation (Your API)
```
API automatically validates:
✓ Dedication sums to 100%
✓ Skill levels 0-10
✓ Email uniqueness
✓ Data completeness
```

### 3. Gap Analysis Request (Your API → Samya's Code)
```
HR → POST /api/v1/hr/analysis/request
     ↓
     Triggers GapAnalysisService.calculate_bulk_gaps()
     ↓
     Samya's algorithm processes data
     ↓
     Returns EmployeeSkillGap results
```

### 4. Results Retrieval (Your API)
```
Frontend → GET /api/v1/hr/analysis/{id} → Returns Results
```

## 🎯 What Samya Needs to Implement

### Location: `api/services/gap_service.py`

### Core Algorithm Function

```python
@staticmethod
def calculate_gap(
    employee: Employee,
    target_role: Role,
    weights: Dict[str, float] = None
) -> EmployeeSkillGap:
    """
    Calculate gap between employee and target role
    
    Algorithm:
    gap_score = 0.50 * skills_gap + 
                0.25 * responsibilities_gap + 
                0.15 * ambitions_gap + 
                0.10 * dedication_gap
    
    Args:
        employee: Current employee data (from API)
        target_role: Target role requirements (from API)
        weights: Optional custom weights (default above)
    
    Returns:
        EmployeeSkillGap with:
        - overall_gap_score (0-100)
        - classification (READY/READY_WITH_SUPPORT/NEAR/FAR/NOT_VIABLE)
        - skill_gaps (detailed breakdown)
        - recommendations (list of actions)
    """
    
    # Default weights if not provided
    if weights is None:
        weights = {
            'skills': 0.50,
            'responsibilities': 0.25,
            'ambitions': 0.15,
            'dedication': 0.10
        }
    
    # TODO: Implement calculation logic
    
    # 1. Calculate skills gap
    skills_gap = calculate_skills_gap(
        employee.habilidades,
        target_role.habilidades_requeridas,
        data_loader.data_store.skills
    )
    
    # 2. Calculate responsibilities gap
    resp_gap = calculate_responsibilities_gap(
        employee.responsabilidades_actuales,
        target_role.responsabilidades
    )
    
    # 3. Calculate ambitions alignment
    amb_alignment = calculate_ambitions_alignment(
        employee.ambiciones,
        target_role
    )
    
    # 4. Calculate dedication availability
    ded_availability = calculate_dedication_availability(
        employee.dedicacion_actual,
        target_role.dedicacion_esperada
    )
    
    # 5. Combine into overall score
    overall_gap = (
        weights['skills'] * skills_gap +
        weights['responsibilities'] * resp_gap +
        weights['ambitions'] * amb_alignment +
        weights['dedication'] * ded_availability
    )
    
    # 6. Classify
    classification = classify_gap(overall_gap)
    
    # 7. Generate recommendations
    recommendations = generate_recommendations(employee, target_role, {
        'skills_gap': skills_gap,
        'resp_gap': resp_gap,
        'amb_alignment': amb_alignment,
        'ded_availability': ded_availability
    })
    
    return EmployeeSkillGap(
        employee_id=employee.id_empleado,
        employee_name=employee.nombre,
        target_role_id=target_role.id,
        target_role_title=target_role.titulo,
        overall_gap_score=overall_gap,
        classification=classification,
        skill_gaps={...},  # Detailed breakdown
        responsibilities_gap=resp_gap,
        ambitions_alignment=amb_alignment,
        dedication_availability=ded_availability,
        recommendations=recommendations
    )
```

## 📊 Input Data Structure (What Samya Receives)

### Employee Object
```python
{
    'id_empleado': 1001,
    'nombre': 'Jordi Casals',
    'email': 'jordi.casals@quether.com',
    'chapter': 'Strategy',
    'rol_actual': 'Head of Strategy',
    'habilidades': {
        'S-OKR': 9,
        'S-ANALISIS': 9,
        'S-STAKE': 8,
        'S-PM': 8,
        'S-ANALYTICS': 7
    },
    'responsabilidades_actuales': [
        'OKRs y gobierno',
        'Workshops C-level',
        'Pricing y propuesta de valor'
    ],
    'dedicacion_actual': {
        'Royal': 40,
        'Arquimbau': 25,
        'Quether GTM': 20,
        'I+D': 15
    },
    'ambiciones': {
        'especialidades_preferidas': ['Estrategia', 'Pricing', 'GTM'],
        'nivel_aspiracion': 'lead'
    }
}
```

### Role Object
```python
{
    'id': 'R-STR-LEAD',
    'titulo': 'Head of Strategy',
    'nivel': 'lead',
    'capitulo': 'Strategy',
    'habilidades_requeridas': ['S-OKR', 'S-ANALISIS', 'S-STAKE'],
    'responsabilidades': [
        'Definir visión estratégica',
        'Alinear roadmap de capítulos',
        'Dirigir discovery y workshops'
    ],
    'dedicacion_esperada': '30-40h/semana'
}
```

### Skills Catalog
```python
{
    'S-OKR': {
        'id': 'S-OKR',
        'nombre': 'OKRs y Roadmapping',
        'categoria': 'Estrategia',
        'peso': 5
    },
    'S-ANALISIS': {
        'id': 'S-ANALISIS',
        'nombre': 'Análisis Estratégico',
        'categoria': 'Estrategia',
        'peso': 5
    }
}
```

## 📤 Expected Output Structure

```python
EmployeeSkillGap(
    employee_id=1001,
    employee_name='Jordi Casals',
    target_role_id='R-STR-LEAD',
    target_role_title='Head of Strategy',
    overall_gap_score=15.5,  # 0-100 scale
    classification='READY',  # Based on score
    skill_gaps={
        'S-OKR': {
            'current': 9,
            'required': 8,
            'gap': -1,  # Negative = exceeds requirement
            'status': 'sufficient'
        },
        'S-ANALISIS': {
            'current': 9,
            'required': 8,
            'gap': -1,
            'status': 'sufficient'
        }
    },
    responsibilities_gap=20.0,
    ambitions_alignment=10.0,
    dedication_availability=5.0,
    recommendations=[
        'Ready for role with minimal training',
        'Consider leadership development program',
        'Strong alignment with strategic competencies'
    ]
)
```

## 🎯 Classification Bands

```python
def classify_gap(gap_score: float) -> str:
    if gap_score < 20:
        return "READY"                    # Can start immediately
    elif gap_score < 40:
        return "READY_WITH_SUPPORT"       # Needs 1-3 months training
    elif gap_score < 60:
        return "NEAR"                     # Needs 3-6 months development
    elif gap_score < 80:
        return "FAR"                      # Needs 6-12 months development
    else:
        return "NOT_VIABLE"               # > 12 months or not suitable
```

## 🔧 How to Access Data in Gap Service

```python
from services.data_loader import data_loader

# Get all employees
employees = data_loader.get_employees()  # Dict[int, Employee]

# Get specific employee
employee = data_loader.get_employee(1001)  # Employee or None

# Get all roles
roles = data_loader.get_roles()  # Dict[str, Role]

# Get specific role
role = data_loader.get_role('R-STR-LEAD')  # Role or None

# Get skills catalog
skills = data_loader.data_store.skills  # Dict[str, Skill]

# Get chapters
chapters = data_loader.data_store.chapters  # Dict[str, Chapter]
```

## 🧪 Testing the Algorithm

### 1. Start the API
```bash
cd api
./run.sh
```

### 2. Test with Sample Data
```python
# The API pre-loads data from CSV/JSON on startup
# You can immediately test with existing employees

# Example test:
import requests

response = requests.post('http://localhost:8000/api/v1/hr/analysis/request', json={
    "analysis_name": "Test Analysis",
    "target_roles": ["R-STR-LEAD"],
    "timeline": "12_meses"
})

analysis_id = response.json()['analysis_id']

# Get results
results = requests.get(f'http://localhost:8000/api/v1/hr/analysis/{analysis_id}')
```

### 3. Unit Test Example
```python
# test_gap_service.py
from services.gap_service import GapAnalysisService
from services.data_loader import data_loader

def test_calculate_gap():
    # Get sample employee and role
    employee = data_loader.get_employee(1001)
    role = data_loader.get_role('R-STR-LEAD')
    
    # Calculate gap
    result = GapAnalysisService.calculate_gap(employee, role)
    
    # Assertions
    assert result.employee_id == 1001
    assert 0 <= result.overall_gap_score <= 100
    assert result.classification in ['READY', 'READY_WITH_SUPPORT', 'NEAR', 'FAR', 'NOT_VIABLE']
```

## 📞 Communication

### Your Team (API)
- ✅ Built complete API infrastructure
- ✅ Data loading from CSV/JSON
- ✅ Data validation
- ✅ HR forms for input
- ✅ Endpoints ready for gap analysis
- ⏳ Waiting for gap algorithm implementation

### Samya (Gap Algorithm)
- ⏳ Implement functions in `services/gap_service.py`
- ⏳ Test with provided data
- ⏳ Ensure output matches `EmployeeSkillGap` model

## 🚀 Integration Checklist

- [ ] Samya reviews `services/gap_service.py`
- [ ] Samya implements `calculate_gap()` function
- [ ] Samya implements helper functions (skills_gap, responsibilities_gap, etc.)
- [ ] Test with sample employee data
- [ ] Implement `calculate_bulk_gaps()` for multiple employees
- [ ] Add recommendations generation
- [ ] Test end-to-end via API
- [ ] Optimize for 300 employees (< 5 hour requirement)

## 📝 Questions for Samya?

Contact your team for:
- Access to employee/role data structures
- Expected output format clarification
- Testing data or scenarios
- Integration support

Good luck! 🎉
