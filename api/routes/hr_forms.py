"""
HR Forms and Input Routes
Endpoints for HR department to input data and request gap analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime
import uuid

from models.hr_forms import (
    HREmployeeSkillForm,
    HREmployeeEvaluationForm,
    HRProjectDedicationForm,
    HRBulkProjectDedication,
    HRNewEmployeeForm,
    HRRoleDefinitionForm,
    HRGapAnalysisRequest,
    HRGapAnalysisResponse,
    HRBulkSkillUpdate,
    HRValidationResponse
)
from models.employee import Employee, EmployeeCreate, Ambitions, Metadata
from models.role import Role, RoleCreate, SeniorityLevel
from services.data_loader import data_loader
from services.validation_service import ValidationService
from services.gap_service import GapAnalysisService

router = APIRouter()


@router.post("/employee/new", response_model=Employee, status_code=201)
async def submit_new_employee_form(form: HRNewEmployeeForm):
    """
    HR form to add a new employee to the system
    """
    employees = data_loader.get_employees()
    
    # Generate new ID
    new_id = max(employees.keys()) + 1 if employees else 1001
    
    # Build skills dictionary
    skills_dict = {skill.skill_id: skill.current_level for skill in form.initial_skills}
    
    # Create employee
    employee_data = EmployeeCreate(
        nombre=form.nombre,
        email=form.email,
        chapter=form.chapter,
        rol_actual=form.rol_actual,
        manager=form.manager,
        antiguedad="0m",
        habilidades=skills_dict,
        responsabilidades_actuales=[],
        dedicacion_actual=form.initial_dedication if form.initial_dedication else {"Unassigned": 100},
        ambiciones=Ambitions(
            especialidades_preferidas=[],
            nivel_aspiracion="junior"
        ),
        metadata=Metadata(
            performance_rating="B",
            retention_risk="Baja",
            trayectoria=f"Joined on {form.start_date}"
        )
    )
    
    employee = Employee(
        id_empleado=new_id,
        **employee_data.model_dump()
    )
    
    # Validate
    is_valid, errors = ValidationService.validate_employee_dedication(employee)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Add to store
    data_loader.add_employee(employee)
    
    return employee


@router.post("/employee/{employee_id}/skills", status_code=200)
async def submit_employee_skills(employee_id: int, skills: List[HREmployeeSkillForm]):
    """
    HR form to update employee skills
    """
    employee = data_loader.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    # Update skills
    for skill in skills:
        if skill.employee_id != employee_id:
            raise HTTPException(
                status_code=400,
                detail=f"Skill form employee_id {skill.employee_id} does not match URL employee_id {employee_id}"
            )
        employee.habilidades[skill.skill_id] = skill.current_level
    
    # Validate skill levels
    is_valid, errors = ValidationService.validate_skill_levels(employee)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Update in store
    data_loader.update_employee(employee_id, employee)
    
    return {
        "employee_id": employee_id,
        "skills_updated": len(skills),
        "message": "Skills updated successfully"
    }


@router.post("/employee/{employee_id}/evaluation", status_code=200)
async def submit_employee_evaluation(employee_id: int, evaluation: HREmployeeEvaluationForm):
    """
    HR form to submit employee evaluation
    """
    employee = data_loader.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    if evaluation.employee_id != employee_id:
        raise HTTPException(
            status_code=400,
            detail=f"Evaluation employee_id {evaluation.employee_id} does not match URL employee_id {employee_id}"
        )
    
    # Update employee metadata and ambitions
    employee.metadata.performance_rating = evaluation.performance_rating
    employee.metadata.retention_risk = evaluation.retention_risk
    
    employee.ambiciones.especialidades_preferidas = evaluation.career_aspirations
    employee.ambiciones.nivel_aspiracion = evaluation.desired_seniority.value
    
    # Update in store
    data_loader.update_employee(employee_id, employee)
    
    return {
        "employee_id": employee_id,
        "evaluation_date": evaluation.evaluation_date.isoformat(),
        "message": "Evaluation submitted successfully"
    }


@router.post("/employee/{employee_id}/dedication", status_code=200)
async def submit_project_dedication(employee_id: int, dedication: HRBulkProjectDedication):
    """
    HR form to update employee project dedication
    """
    employee = data_loader.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    
    if dedication.employee_id != employee_id:
        raise HTTPException(
            status_code=400,
            detail=f"Dedication employee_id {dedication.employee_id} does not match URL employee_id {employee_id}"
        )
    
    # Update dedication
    employee.dedicacion_actual = dedication.dedications
    
    # Validate
    is_valid, errors = ValidationService.validate_employee_dedication(employee)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Update in store
    data_loader.update_employee(employee_id, employee)
    
    return {
        "employee_id": employee_id,
        "effective_date": dedication.effective_date.isoformat(),
        "message": "Dedication updated successfully"
    }


@router.post("/role/define", response_model=Role, status_code=201)
async def submit_role_definition(form: HRRoleDefinitionForm):
    """
    HR form to define a future role requirement
    """
    roles = data_loader.get_roles()
    
    # Generate role ID
    chapter_prefix = form.chapter[:3].upper()
    title_suffix = form.role_title.split()[-1].upper()[:4]
    new_id = f"R-{chapter_prefix}-{title_suffix}"
    
    # Check if ID exists
    counter = 1
    base_id = new_id
    while new_id in roles:
        new_id = f"{base_id}-{counter}"
        counter += 1
    
    # Create role
    role_data = RoleCreate(
        titulo=form.role_title,
        nivel=form.seniority_level,
        capitulo=form.chapter,
        cantidad=form.positions_needed,
        inicio_estimado=form.estimated_start,
        responsabilidades=form.key_responsibilities,
        habilidades_requeridas=form.required_skills,
        objetivos_asociados=[]
    )
    
    role = Role(
        id=new_id,
        **role_data.model_dump()
    )
    
    # Add to store
    data_loader.add_role(role)
    
    return role


@router.post("/skills/bulk-update", status_code=200)
async def bulk_update_skills(bulk_update: HRBulkSkillUpdate):
    """
    HR form to update skills for multiple employees at once
    """
    updated_employees = []
    errors = []
    
    for skill_form in bulk_update.updates:
        employee = data_loader.get_employee(skill_form.employee_id)
        
        if not employee:
            errors.append(f"Employee {skill_form.employee_id} not found")
            continue
        
        # Update skill
        employee.habilidades[skill_form.skill_id] = skill_form.current_level
        
        # Validate
        is_valid, val_errors = ValidationService.validate_skill_levels(employee)
        if not is_valid:
            errors.extend(val_errors)
            continue
        
        # Update in store
        data_loader.update_employee(skill_form.employee_id, employee)
        updated_employees.append(skill_form.employee_id)
    
    return {
        "total_updates": len(bulk_update.updates),
        "successful": len(updated_employees),
        "failed": len(errors),
        "updated_employees": updated_employees,
        "errors": errors,
        "updated_by": bulk_update.updated_by,
        "reason": bulk_update.update_reason
    }


@router.post("/analysis/request", response_model=HRGapAnalysisResponse)
async def request_gap_analysis(
    request: HRGapAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    HR form to request a gap analysis
    
    PLACEHOLDER - Gap analysis will be implemented by Samya
    This endpoint accepts the request and returns an analysis ID
    """
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Validate inputs
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    
    # Check if target roles exist
    for role_id in request.target_roles:
        if role_id not in roles:
            raise HTTPException(
                status_code=400,
                detail=f"Target role {role_id} not found"
            )
    
    # TODO: Queue analysis job (Samya will implement the actual algorithm)
    # background_tasks.add_task(GapAnalysisService.calculate_bulk_gaps, employees, roles, request)
    
    return HRGapAnalysisResponse(
        analysis_id=analysis_id,
        status="queued",
        created_at=datetime.now().isoformat(),
        estimated_completion="< 5 hours",
        message=f"Gap analysis queued. Analysis ID: {analysis_id}. Check /api/v1/hr/analysis/{analysis_id} for results."
    )


@router.get("/analysis/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """
    Get gap analysis results by ID
    
    PLACEHOLDER - To be implemented by Samya
    """
    # TODO: Retrieve analysis results from store/database
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Gap analysis algorithm will be implemented by Samya",
        "results": None
    }


@router.post("/validate/all", response_model=HRValidationResponse)
async def validate_all_data():
    """
    Validate all company data for completeness and consistency
    """
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    
    # Perform health check
    health = ValidationService.perform_health_check(employees, roles)
    
    return HRValidationResponse(
        is_valid=len(health.validation_errors) == 0,
        errors=health.validation_errors,
        warnings=health.validation_warnings,
        summary={
            "total_employees": health.total_employees,
            "total_roles": health.total_roles,
            "data_quality_score": health.data_quality_score,
            "missing_data_count": len(health.missing_data)
        }
    )


@router.post("/validate/employee/{employee_id}", response_model=HRValidationResponse)
async def validate_employee_data(employee_id: int):
    """
    Validate specific employee data
    """
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
    
    # Check completeness
    if not employee.habilidades:
        warnings.append("No skills defined")
    if not employee.responsabilidades_actuales:
        warnings.append("No responsibilities defined")
    if not employee.manager or employee.manager == "N/A":
        warnings.append("No manager assigned")
    
    return HRValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        summary={
            "employee_id": employee_id,
            "employee_name": employee.nombre,
            "skills_count": len(employee.habilidades),
            "responsibilities_count": len(employee.responsabilidades_actuales)
        }
    )
