"""
Skills Routes - Manage skills catalog
GET /api/v1/skills - Get all skills
POST /api/v1/skills - Create a new skill
GET /api/v1/skills/{skill_id} - Get a specific skill
PUT /api/v1/skills/{skill_id} - Update a skill
DELETE /api/v1/skills/{skill_id} - Delete a skill
GET /api/v1/skills/categories - Get unique categories
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from models.role import Skill, SkillCreate, SkillListResponse
from services.data_loader import data_loader

router = APIRouter(prefix="/api/v1/skills", tags=["Skills"])


@router.get("", response_model=SkillListResponse)
async def get_all_skills(categoria: Optional[str] = None):
    """
    Get all skills, optionally filtered by category
    
    Args:
        categoria: Optional category filter
        
    Returns:
        List of all skills with total count
    """
    skills = data_loader.get_skills()
    
    # Filter by category if provided
    if categoria:
        skills = {k: v for k, v in skills.items() if v.categoria.lower() == categoria.lower()}
    
    skills_list = list(skills.values())
    return SkillListResponse(
        total=len(skills_list),
        skills=skills_list
    )


@router.get("/categories", response_model=List[str])
async def get_skill_categories():
    """
    Get all unique skill categories
    
    Returns:
        List of unique categories
    """
    skills = data_loader.get_skills()
    categories = sorted(set(skill.categoria for skill in skills.values()))
    return categories


@router.get("/{skill_id}", response_model=Skill)
async def get_skill(skill_id: str):
    """
    Get a specific skill by ID
    
    Args:
        skill_id: The skill ID (e.g., S-OKR)
        
    Returns:
        The skill object
        
    Raises:
        404: Skill not found
    """
    skills = data_loader.get_skills()
    
    if skill_id not in skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with ID '{skill_id}' not found"
        )
    
    return skills[skill_id]


@router.post("", response_model=Skill, status_code=status.HTTP_201_CREATED)
async def create_skill(skill: SkillCreate):
    """
    Create a new skill
    
    Args:
        skill: Skill data (without ID)
        
    Returns:
        The created skill with generated ID
        
    Raises:
        400: Invalid skill data
    """
    skills = data_loader.get_skills()
    
    # Generate ID from nombre
    # Convert to uppercase, replace spaces with -, remove special chars
    skill_id = f"S-{skill.nombre.upper().replace(' ', '-').replace('/', '-')}"
    # Clean up ID - remove multiple dashes, special chars
    import re
    skill_id = re.sub(r'[^A-Z0-9-]', '', skill_id)
    skill_id = re.sub(r'-+', '-', skill_id)
    
    # Check if ID already exists
    if skill_id in skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill with ID '{skill_id}' already exists"
        )
    
    # Create the skill
    new_skill = Skill(
        id=skill_id,
        nombre=skill.nombre,
        categoria=skill.categoria,
        descripcion=skill.descripcion or "",
        peso=skill.peso,
        herramientas_asociadas=skill.herramientas_asociadas
    )
    
    # Add to data store
    skills[skill_id] = new_skill
    
    return new_skill


@router.put("/{skill_id}", response_model=Skill)
async def update_skill(skill_id: str, skill: SkillCreate):
    """
    Update an existing skill
    
    Args:
        skill_id: The skill ID to update
        skill: Updated skill data
        
    Returns:
        The updated skill
        
    Raises:
        404: Skill not found
    """
    skills = data_loader.get_skills()
    
    if skill_id not in skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with ID '{skill_id}' not found"
        )
    
    # Update the skill
    updated_skill = Skill(
        id=skill_id,
        nombre=skill.nombre,
        categoria=skill.categoria,
        descripcion=skill.descripcion or "",
        peso=skill.peso,
        herramientas_asociadas=skill.herramientas_asociadas
    )
    
    skills[skill_id] = updated_skill
    
    return updated_skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str):
    """
    Delete a skill
    
    Args:
        skill_id: The skill ID to delete
        
    Raises:
        404: Skill not found
    """
    skills = data_loader.get_skills()
    
    if skill_id not in skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with ID '{skill_id}' not found"
        )
    
    del skills[skill_id]
    return None
