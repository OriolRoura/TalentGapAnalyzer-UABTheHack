"""
HR Forms and Input Routes
Endpoints for HR department to input data and request gap analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import uuid

from models.hr_forms import (
    HRRoleDefinitionForm,
    HRGapAnalysisRequest,
    HRGapAnalysisResponse,
    HRValidationResponse,
    HREmployeeSubmitForm,
    HREmployeeSubmitResponse
)
from models.employee import Employee, EmployeeCreate, Ambitions, Metadata
from models.role import Role, RoleCreate
from services.data_loader import data_loader
from services.validation_service import ValidationService
from services.gap_service import GapAnalysisService

router = APIRouter()


@router.post("/employee/submit", response_model=HREmployeeSubmitResponse, status_code=200)
async def submit_employee_profile(form: HREmployeeSubmitForm):
    """
    HR form to submit complete employee profile
    """
    employees = data_loader.get_employees()
    
    # Convert employee_id to int
    try:
        employee_id = int(form.employee_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid employee_id: {form.employee_id}")
    
    # Check if employee exists
    employee = data_loader.get_employee(employee_id)
    
    # Build skills dictionary from submitted skills
    skills_dict = {}
    for skill in form.skills:
        # Use skill name as key (you may want to map this to skill_id in production)
        skills_dict[skill.nombre] = skill.nivel
    
    # Build dedication dictionary
    dedication_dict = {
        form.dedicacion.proyecto_actual: form.dedicacion.porcentaje_dedicacion
    }
    
    if employee:
        # Update existing employee
        employee.nombre = form.nombre
        employee.email = form.email
        employee.chapter = form.chapter
        employee.rol_actual = form.seniority
        employee.habilidades = skills_dict
        employee.responsabilidades_actuales = form.responsabilidades
        employee.dedicacion_actual = dedication_dict
        
        # Update ambitions
        employee.ambiciones.especialidades_preferidas = form.ambiciones.especialidades_preferidas
        employee.ambiciones.nivel_aspiracion = form.ambiciones.nivel_aspiracion
        
        # Update metadata if it has additional fields (you can extend this)
        if not hasattr(employee, 'metadata') or employee.metadata is None:
            employee.metadata = Metadata(
                performance_rating="B",
                retention_risk="Baja",
                trayectoria=""
            )
        
        # Update in store
        data_loader.update_employee(employee_id, employee)
        message = "Employee profile updated successfully"
    else:
        # Create new employee
        employee_data = EmployeeCreate(
            nombre=form.nombre,
            email=form.email,
            chapter=form.chapter,
            rol_actual=form.seniority,
            manager="N/A",
            antiguedad="0m",
            habilidades=skills_dict,
            responsabilidades_actuales=form.responsabilidades,
            dedicacion_actual=dedication_dict,
            ambiciones=Ambitions(
                especialidades_preferidas=form.ambiciones.especialidades_preferidas,
                nivel_aspiracion=form.ambiciones.nivel_aspiracion
            ),
            metadata=Metadata(
                performance_rating="B",
                retention_risk="Baja",
                trayectoria=f"Submitted on {datetime.now().date().isoformat()}"
            )
        )
        
        employee = Employee(
            id_empleado=employee_id,
            **employee_data.model_dump()
        )
        
        # Add to store
        data_loader.add_employee(employee)
        message = "Employee profile submitted successfully"
    
    # Validate
    is_valid, ded_errors = ValidationService.validate_employee_dedication(employee)
    dedication_valid = is_valid and len(ded_errors) == 0
    
    is_valid_skills, skill_errors = ValidationService.validate_skill_levels(employee)
    
    return HREmployeeSubmitResponse(
        status="success",
        message=message,
        employee_id=form.employee_id,
        validation={
            "skills_count": len(form.skills),
            "dedication_valid": dedication_valid
        }
    )


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
