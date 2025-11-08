"""
Role Management Routes
CRUD operations for roles
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models.role import (
    Role,
    RoleCreate,
    RoleUpdate,
    RoleListResponse,
    Skill,
    SkillCreate
)
from services.data_loader import data_loader

router = APIRouter()


@router.get("/current", response_model=RoleListResponse)
async def get_current_roles(
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    nivel: Optional[str] = Query(None, description="Filter by seniority level")
):
    """Get list of current roles (roles with employees currently assigned)"""
    roles = data_loader.get_current_roles()
    
    # Apply filters
    filtered = list(roles.values())
    if chapter:
        filtered = [r for r in filtered if r.capitulo.lower() == chapter.lower()]
    if nivel:
        filtered = [r for r in filtered if r.nivel.lower() == nivel.lower()]
    
    return RoleListResponse(
        total=len(filtered),
        roles=filtered
    )


@router.get("/future", response_model=RoleListResponse)
async def get_future_roles(
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    nivel: Optional[str] = Query(None, description="Filter by seniority level"),
    estado: Optional[str] = Query(None, description="Filter by estado (cubierto/pendiente)")
):
    """Get list of future roles (roles needed according to vision_futura)"""
    roles = data_loader.get_future_roles()
    
    # Apply filters
    filtered = list(roles.values())
    if chapter:
        filtered = [r for r in filtered if r.capitulo.lower() == chapter.lower()]
    if nivel:
        filtered = [r for r in filtered if r.nivel.lower() == nivel.lower()]
    
    return RoleListResponse(
        total=len(filtered),
        roles=filtered
    )


@router.get("/", response_model=RoleListResponse)
async def get_roles(
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    nivel: Optional[str] = Query(None, description="Filter by seniority level"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=300)
):
    """Get list of all roles (current + future) with optional filters"""
    roles = data_loader.get_roles()
    
    # Apply filters
    filtered = list(roles.values())
    if chapter:
        filtered = [r for r in filtered if r.capitulo.lower() == chapter.lower()]
    if nivel:
        filtered = [r for r in filtered if r.nivel.lower() == nivel.lower()]
    
    # Pagination
    total = len(filtered)
    paginated = filtered[skip:skip + limit]
    
    return RoleListResponse(
        total=total,
        roles=paginated
    )


@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: str):
    """Get role by ID"""
    role = data_loader.get_role(role_id)
    
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    
    return role


@router.post("/", response_model=Role, status_code=201)
async def create_role(role_data: RoleCreate):
    """Create new role"""
    roles = data_loader.get_roles()
    
    # Generate new ID based on chapter and title
    chapter_prefix = role_data.capitulo[:3].upper()
    title_suffix = role_data.titulo.split()[-1].upper()[:4]
    new_id = f"R-{chapter_prefix}-{title_suffix}"
    
    # Check if ID exists, add number if needed
    base_id = new_id
    counter = 1
    while new_id in roles:
        new_id = f"{base_id}-{counter}"
        counter += 1
    
    # Create role
    role = Role(
        id=new_id,
        **role_data.model_dump()
    )
    
    # Add to store
    data_loader.add_role(role)
    
    return role


@router.put("/{role_id}", response_model=Role)
async def update_role(role_id: str, role_data: RoleUpdate):
    """Update role"""
    existing = data_loader.get_role(role_id)
    
    if not existing:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    
    # Update fields
    update_dict = role_data.model_dump(exclude_unset=True)
    updated_role = existing.model_copy(update=update_dict)
    
    # Update in store
    data_loader.update_role(role_id, updated_role)
    
    return updated_role


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: str):
    """Delete role"""
    success = data_loader.delete_role(role_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    
    return None


@router.get("/chapters/list")
async def get_chapters():
    """Get list of all chapters"""
    chapters = data_loader.data_store.chapters
    return {
        "total": len(chapters),
        "chapters": list(chapters.values())
    }


@router.get("/skills/list")
async def get_skills():
    """Get list of all skills"""
    skills = data_loader.data_store.skills
    return {
        "total": len(skills),
        "skills": list(skills.values())
    }


@router.post("/skills/", response_model=Skill, status_code=201)
async def create_skill(skill_data: SkillCreate):
    """Create new skill"""
    skills = data_loader.data_store.skills
    
    # Generate new ID
    skill_prefix = "S-" + skill_data.nombre[:6].upper().replace(" ", "-")
    new_id = skill_prefix
    counter = 1
    while new_id in skills:
        new_id = f"{skill_prefix}-{counter}"
        counter += 1
    
    # Create skill
    skill = Skill(
        id=new_id,
        **skill_data.model_dump()
    )
    
    # Add to store
    data_loader.data_store.skills[skill.id] = skill
    
    return skill
