# Employee Submit Endpoint

## Endpoint
`POST /api/v1/hr/employee/submit`

## Description
HR form to submit or update a complete employee profile. This endpoint accepts comprehensive employee data including skills, ambitions, and project dedication.

## Request Body

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

## Response

### Success (200 OK)
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

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid employee_id: abc"
}
```

#### 422 Unprocessable Entity
Validation error for malformed request data.

## Field Descriptions

### Root Level
- `employee_id` (string, required): Unique employee identifier
- `nombre` (string, required): Employee full name
- `email` (email, required): Valid email address
- `chapter` (string, required): Department/chapter (e.g., "Strategy", "Technology")
- `seniority` (string, required): Seniority level (e.g., "junior", "senior", "lead")
- `modalidad` (string, required): Work modality (e.g., "Full-time", "Part-time")

### Skills Array
- `nombre` (string, required): Skill name
- `nivel` (integer, required): Proficiency level (0-10)
- `experiencia_años` (integer, required): Years of experience (≥0)

### Ambiciones Object
- `especialidades_preferidas` (array of strings): Preferred specialties
- `nivel_aspiracion` (string, required): Target seniority level
- `interes_liderazgo` (boolean): Interest in leadership roles
- `areas_interes` (array of strings): Areas of interest

### Dedicacion Object
- `proyecto_actual` (string, required): Current project name
- `porcentaje_dedicacion` (integer, required): Dedication percentage (0-100)
- `horas_semana` (integer, required): Weekly hours (≥0)

## Behavior

1. **New Employee**: If the employee_id doesn't exist, creates a new employee profile
2. **Update Employee**: If the employee_id exists, updates the existing profile
3. **Validation**: Automatically validates:
   - Skill levels (0-10 range)
   - Dedication percentages
   - Email format
   - Data completeness

## Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/hr/employee/submit" \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    ],
    "responsabilidades": ["Project planning"],
    "ambiciones": {
      "especialidades_preferidas": ["AI"],
      "nivel_aspiracion": "lead",
      "interes_liderazgo": true,
      "areas_interes": ["Technology"]
    },
    "dedicacion": {
      "proyecto_actual": "Digital Transformation",
      "porcentaje_dedicacion": 100,
      "horas_semana": 40
    }
  }'
```

## Notes

- The endpoint handles both creation and updates automatically
- Skill names are stored as-is (consider mapping to standardized skill IDs in production)
- Dedication must be a valid percentage (0-100)
- The validation object in the response indicates data quality
