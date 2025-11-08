"""
Employee Management Routes
CRUD operations for employees
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.employee import (
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeListResponse,
    EmployeeStats
)
from services.data_loader import data_loader
from services.validation_service import ValidationService

router = APIRouter()


@router.get("/", response_model=EmployeeListResponse)
async def get_employees(
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    role: Optional[str] = Query(None, description="Filter by role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=300)
):
    """Get list of all employees with optional filters"""
    employees = data_loader.get_employees()
    
    # Apply filters
    filtered = list(employees.values())
    if chapter:
        filtered = [e for e in filtered if e.chapter.lower() == chapter.lower()]
    if role:
        filtered = [e for e in filtered if e.rol_actual.lower() == role.lower()]
    
    # Pagination
    total = len(filtered)
    paginated = filtered[skip:skip + limit]
    
    return EmployeeListResponse(
        total=total,
        employees=paginated
    )


@router.get("/stats", response_model=EmployeeStats)
async def get_employee_stats():
    """Get employee statistics"""
    employees = data_loader.get_employees()
    
    if not employees:
        return EmployeeStats(
            total_employees=0,
            by_chapter={},
            by_performance={},
            by_retention_risk={},
            avg_skills_per_employee=0.0,
            avg_tenure_months=0.0
        )
    
    # Calculate stats
    by_chapter = {}
    by_performance = {}
    by_retention_risk = {}
    total_skills = 0
    total_tenure = 0
    
    for emp in employees.values():
        # By chapter
        by_chapter[emp.chapter] = by_chapter.get(emp.chapter, 0) + 1
        
        # By performance
        perf = emp.metadata.performance_rating
        by_performance[perf] = by_performance.get(perf, 0) + 1
        
        # By retention risk
        risk = emp.metadata.retention_risk
        by_retention_risk[risk] = by_retention_risk.get(risk, 0) + 1
        
        # Skills count
        total_skills += len(emp.habilidades)
        
        # Parse tenure (e.g., "24m" -> 24)
        tenure_str = emp.antiguedad.replace('m', '').strip()
        try:
            total_tenure += int(tenure_str)
        except:
            pass
    
    return EmployeeStats(
        total_employees=len(employees),
        by_chapter=by_chapter,
        by_performance=by_performance,
        by_retention_risk=by_retention_risk,
        avg_skills_per_employee=round(total_skills / len(employees), 2),
        avg_tenure_months=round(total_tenure / len(employees), 2)
    )


@router.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int):
    """Get employee by ID"""
    employee = data_loader.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    return employee


@router.post("/", response_model=Employee, status_code=201)
async def create_employee(employee_data: EmployeeCreate):
    """Create new employee"""
    employees = data_loader.get_employees()
    
    # Generate new ID
    new_id = max(employees.keys()) + 1 if employees else 1001
    
    # Create employee
    employee = Employee(
        id_empleado=new_id,
        **employee_data.model_dump()
    )
    
    # Validate
    is_valid, errors = ValidationService.validate_employee_dedication(employee)
    if not is_valid:
        raise HTTPException(status_code=400, detail=errors)
    
    is_valid, errors = ValidationService.validate_skill_levels(employee)
    if not is_valid:
        raise HTTPException(status_code=400, detail=errors)
    
    # Add to store
    data_loader.add_employee(employee)
    
    return employee


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, employee_data: EmployeeUpdate):
    """Update employee"""
    existing = data_loader.get_employee(employee_id)
    
    if not existing:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    # Update fields
    update_dict = employee_data.model_dump(exclude_unset=True)
    updated_employee = existing.model_copy(update=update_dict)
    
    # Validate if dedication was updated
    if 'dedicacion_actual' in update_dict:
        is_valid, errors = ValidationService.validate_employee_dedication(updated_employee)
        if not is_valid:
            raise HTTPException(status_code=400, detail=errors)
    
    # Update in store
    data_loader.update_employee(employee_id, updated_employee)
    
    return updated_employee


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: int):
    """Delete employee"""
    success = data_loader.delete_employee(employee_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    return None


@router.get("/{employee_id}/validate")
async def validate_employee(employee_id: int):
    """Validate employee data"""
    employee = data_loader.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    errors = []
    warnings = []
    
    # Run validations
    is_valid, ded_errors = ValidationService.validate_employee_dedication(employee)
    errors.extend(ded_errors)
    
    is_valid, skill_errors = ValidationService.validate_skill_levels(employee)
    errors.extend(skill_errors)
    
    return {
        "employee_id": employee_id,
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
