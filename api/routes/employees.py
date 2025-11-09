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


@router.get("/{employee_id}/gap-matrix")
async def get_employee_gap_matrix(
    employee_id: int,
    custom_weights: Optional[str] = Query(
        None, 
        description="Custom algorithm weights as JSON string, e.g., {'skills': 0.5, 'responsibilities': 0.25, 'ambitions': 0.15, 'dedication': 0.1}"
    )
):
    """
    Get complete gap matrix for an employee against all roles.
    
    This endpoint generates a comprehensive analysis similar to the challenge matrix,
    showing the employee's compatibility with every role in the system.
    
    Returns:
    - All role matches with scores and classifications
    - Best match recommendation
    - Ready roles count
    - Average compatibility score
    - Detailed gaps and recommendations for each role
    
    Perfect for displaying in a web interface to show career progression options.
    """
    from services.gap_service import GapAnalysisService
    from models.hr_forms import EmployeeGapMatrix
    import json as json_lib
    
    # Check if employee exists
    employee = data_loader.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    # Parse custom weights if provided
    weights = None
    if custom_weights:
        try:
            weights = json_lib.loads(custom_weights)
            # Validate weights
            required_keys = ['skills', 'responsibilities', 'ambitions', 'dedication']
            if not all(key in weights for key in required_keys):
                raise HTTPException(
                    status_code=400,
                    detail=f"Weights must include all keys: {required_keys}"
                )
            # Validate weights sum to ~1.0
            total = sum(weights.values())
            if not (0.99 <= total <= 1.01):
                raise HTTPException(
                    status_code=400,
                    detail=f"Weights must sum to 1.0 (got {total})"
                )
        except json_lib.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for custom_weights"
            )
    
    try:
        # Calculate gap matrix
        matrix = GapAnalysisService.calculate_employee_gap_matrix(
            employee_id=employee_id,
            weights=weights
        )
        
        return matrix
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating gap matrix: {str(e)}"
        )


@router.get("/gap-matrix/all")
async def get_all_employees_gap_matrix(
    custom_weights: Optional[str] = Query(
        None, 
        description="Custom algorithm weights as JSON string, e.g., {'skills': 0.5, 'responsibilities': 0.25, 'ambitions': 0.15, 'dedication': 0.1}"
    ),
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    role: Optional[str] = Query(None, description="Filter by current role")
):
    """
    Get complete gap matrices for ALL employees against all roles.
    
    This endpoint generates comprehensive gap analysis for every employee in the system,
    showing each employee's compatibility with every available role.
    
    Query Parameters:
    - custom_weights: Optional JSON string with custom algorithm weights
    - chapter: Optional filter to analyze only employees from specific chapter
    - role: Optional filter to analyze only employees with specific current role
    
    Returns:
    - List of gap matrices (one per employee)
    - Each matrix contains all role matches with scores and classifications
    - Summary statistics across all employees
    
    Perfect for:
    - Company-wide talent planning
    - Identifying skill gaps across organization
    - Workforce readiness assessment
    - Succession planning
    """
    from services.gap_service import GapAnalysisService
    from models.hr_forms import EmployeeGapMatrix
    import json as json_lib
    
    # Get all employees
    employees = data_loader.get_employees()
    
    if not employees:
        return {
            "total_employees": 0,
            "matrices": [],
            "summary": {
                "total_ready_roles": 0,
                "avg_compatibility": 0.0,
                "employees_with_ready_roles": 0
            }
        }
    
    # Apply filters
    filtered_employees = list(employees.values())
    if chapter:
        filtered_employees = [e for e in filtered_employees if e.chapter.lower() == chapter.lower()]
    if role:
        filtered_employees = [e for e in filtered_employees if e.rol_actual.lower() == role.lower()]
    
    if not filtered_employees:
        return {
            "total_employees": 0,
            "matrices": [],
            "summary": {
                "total_ready_roles": 0,
                "avg_compatibility": 0.0,
                "employees_with_ready_roles": 0
            }
        }
    
    # Parse custom weights if provided
    weights = None
    if custom_weights:
        try:
            weights = json_lib.loads(custom_weights)
            # Validate weights
            required_keys = ['skills', 'responsibilities', 'ambitions', 'dedication']
            if not all(key in weights for key in required_keys):
                raise HTTPException(
                    status_code=400,
                    detail=f"Weights must include all keys: {required_keys}"
                )
            # Validate weights sum to ~1.0
            total = sum(weights.values())
            if not (0.99 <= total <= 1.01):
                raise HTTPException(
                    status_code=400,
                    detail=f"Weights must sum to 1.0 (got {total})"
                )
        except json_lib.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for custom_weights"
            )
    
    try:
        # Calculate gap matrix for each employee
        matrices = []
        total_ready_roles = 0
        total_compatibility = 0.0
        employees_with_ready = 0
        
        for employee in filtered_employees:
            matrix = GapAnalysisService.calculate_employee_gap_matrix(
                employee_id=employee.id_empleado,
                weights=weights
            )
            matrices.append(matrix)
            
            # Accumulate statistics
            total_ready_roles += matrix.ready_roles_count
            total_compatibility += matrix.avg_compatibility_score
            if matrix.ready_roles_count > 0:
                employees_with_ready += 1
        
        # Calculate summary statistics
        num_employees = len(matrices)
        avg_compatibility = total_compatibility / num_employees if num_employees > 0 else 0.0
        
        return {
            "total_employees": num_employees,
            "matrices": matrices,
            "summary": {
                "total_ready_roles": total_ready_roles,
                "avg_compatibility": round(avg_compatibility, 3),
                "employees_with_ready_roles": employees_with_ready,
                "avg_ready_roles_per_employee": round(total_ready_roles / num_employees, 2) if num_employees > 0 else 0.0
            },
            "filters_applied": {
                "chapter": chapter,
                "role": role,
                "custom_weights": weights is not None
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating gap matrices: {str(e)}"
        )
