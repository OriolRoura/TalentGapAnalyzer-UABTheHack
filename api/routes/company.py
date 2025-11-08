"""
Company Status and Configuration Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict

from models.company import (
    CompanyStatus,
    CompanyHealthCheck,
    CompanyConfig,
    Organization,
    CompanyProject,
    CompanyProjectsResponse
)
from services.data_loader import data_loader
from services.validation_service import ValidationService

router = APIRouter()


@router.get("/status", response_model=CompanyStatus)
async def get_company_status():
    """Get current company status snapshot"""
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    chapters = data_loader.data_store.chapters
    organization = data_loader.data_store.organization
    
    # Calculate employees by chapter
    employees_by_chapter = {}
    for emp in employees.values():
        chapter = emp.chapter
        employees_by_chapter[chapter] = employees_by_chapter.get(chapter, 0) + 1
    
    # Calculate roles by chapter
    roles_by_chapter = {}
    for role in roles.values():
        chapter = role.capitulo
        roles_by_chapter[chapter] = roles_by_chapter.get(chapter, 0) + 1
    
    # Calculate average skills per employee
    total_skills = sum(len(emp.habilidades) for emp in employees.values())
    avg_skills = total_skills / len(employees) if employees else 0
    
    # Calculate data completeness
    data_completeness = ValidationService.check_data_completeness(employees)
    
    from datetime import datetime
    
    return CompanyStatus(
        organization=organization or Organization(
            nombre="Quether Consulting",
            descripcion="Consultora de estrategia",
            max_employees=300
        ),
        total_employees=len(employees),
        total_roles=len(roles),
        total_chapters=len(chapters),
        employees_by_chapter=employees_by_chapter,
        roles_by_chapter=roles_by_chapter,
        avg_skills_per_employee=round(avg_skills, 2),
        data_completeness=data_completeness,
        last_updated=datetime.now().isoformat()
    )


@router.get("/health", response_model=CompanyHealthCheck)
async def get_company_health():
    """Perform comprehensive health check on company data"""
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    
    health_check = ValidationService.perform_health_check(employees, roles)
    
    return health_check


@router.get("/config")
async def get_company_config():
    """Get current company configuration"""
    organization = data_loader.data_store.organization
    chapters = list(data_loader.data_store.chapters.values())
    
    return {
        "organization": organization,
        "chapters": chapters,
        "total_chapters": len(chapters)
    }


@router.get("/vision")
async def get_company_vision():
    """Get future vision and roadmap"""
    vision_data = data_loader.data_store.vision_data
    
    if not vision_data:
        raise HTTPException(status_code=404, detail="Vision data not loaded")
    
    return vision_data


@router.get("/chapters")
async def get_chapters_summary():
    """Get summary of all chapters with employee and role counts"""
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    chapters = data_loader.data_store.chapters
    
    chapter_summary = []
    
    for chapter_name, chapter in chapters.items():
        # Count employees
        emp_count = sum(1 for emp in employees.values() if emp.chapter == chapter_name)
        
        # Count roles
        role_count = sum(1 for role in roles.values() if role.capitulo == chapter_name)
        
        chapter_summary.append({
            "name": chapter.nombre,
            "description": chapter.descripcion,
            "employee_count": emp_count,
            "role_count": role_count,
            "role_templates": chapter.role_templates
        })
    
    return {
        "total_chapters": len(chapter_summary),
        "chapters": chapter_summary
    }


@router.get("/projects", response_model=CompanyProjectsResponse)
async def get_company_projects():
    """
    Get all company projects from the master projects list,
    enriched with current employee dedication data.
    This endpoint is useful for HR forms to show available projects when
    inputting or updating talent profiles.
    """
    from datetime import datetime
    
    projects_data = data_loader.get_company_projects()
    
    # Convert to CompanyProject models
    projects = [
        CompanyProject(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            type=data.get('type'),
            status=data.get('status', 'active'),
            priority=data.get('priority', 'medium'),
            estimated_duration=data.get('estimated_duration'),
            metadata=data.get('metadata'),
            total_employees=data['total_employees'],
            avg_dedication_percentage=data['avg_dedication_percentage'],
            employees=data['employees']
        )
        for data in projects_data.values()
    ]
    
    # Sort by priority first, then by number of employees
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    projects.sort(
        key=lambda x: (priority_order.get(x.priority, 2), -x.total_employees)
    )
    
    return CompanyProjectsResponse(
        projects=projects,
        total_projects=len(projects),
        last_updated=datetime.now().isoformat()
    )


@router.get("/dashboard")
async def get_dashboard_data():
    """Get aggregated dashboard data"""
    employees = data_loader.get_employees()
    roles = data_loader.get_roles()
    chapters = data_loader.data_store.chapters
    
    # Employee stats by chapter
    employees_by_chapter = {}
    for emp in employees.values():
        chapter = emp.chapter
        employees_by_chapter[chapter] = employees_by_chapter.get(chapter, 0) + 1
    
    # Performance distribution
    performance_dist = {}
    for emp in employees.values():
        perf = emp.metadata.performance_rating
        performance_dist[perf] = performance_dist.get(perf, 0) + 1
    
    # Retention risk distribution
    retention_risk = {}
    for emp in employees.values():
        risk = emp.metadata.retention_risk
        retention_risk[risk] = retention_risk.get(risk, 0) + 1
    
    # Skills coverage
    all_skills = set()
    for emp in employees.values():
        all_skills.update(emp.habilidades.keys())
    
    # Data completeness
    completeness = ValidationService.check_data_completeness(employees)
    
    return {
        "overview": {
            "total_employees": len(employees),
            "total_roles": len(roles),
            "total_chapters": len(chapters),
            "total_skills_in_use": len(all_skills)
        },
        "employees_by_chapter": employees_by_chapter,
        "performance_distribution": performance_dist,
        "retention_risk": retention_risk,
        "data_completeness": completeness,
        "avg_completeness": sum(completeness.values()) / len(completeness) if completeness else 0
    }
