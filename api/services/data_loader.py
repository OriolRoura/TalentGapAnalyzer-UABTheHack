"""
Data Loader Service
Loads and parses data from CSV and JSON files
"""

import pandas as pd
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

from models.employee import Employee, Ambitions, Metadata
from models.role import Role, Chapter, Skill
from models.company import Organization


class DataStore:
    """In-memory data store for the application"""
    def __init__(self):
        self.employees: Dict[int, Employee] = {}
        self.roles: Dict[str, Role] = {}  # All roles (backward compatibility)
        self.current_roles: Dict[str, Role] = {}  # Roles actuales con empleados
        self.future_roles: Dict[str, Role] = {}  # Roles necesarios para el futuro
        self.chapters: Dict[str, Chapter] = {}
        self.skills: Dict[str, Skill] = {}
        self.projects: Dict[str, Dict] = {}  # Company projects
        self.organization: Optional[Organization] = None
        self.vision_data: Optional[Dict] = None


class DataLoader:
    """Service for loading data from files"""
    
    def __init__(self):
        self.data_store = DataStore()
        self.base_path = Path(__file__).parent.parent.parent / "dataSet" / "talent-gap-analyzer-main"
        print(f"📁 Data path: {self.base_path}")
        print(f"📁 Path exists: {self.base_path.exists()}")
    
    def load_all_data(self):
        """Load all data from CSV and JSON files"""
        print("=" * 50)
        print("📊 Starting data load...")
        print("=" * 50)
        
        self.load_projects()
        print(f"✅ Loaded {len(self.data_store.projects)} projects")
        
        self.load_employees()
        print(f"✅ Loaded {len(self.data_store.employees)} employees")
        
        # Load org_config (includes chapters, skills, and current roles)
        self.load_org_config()
        print(f"✅ Loaded {len(self.data_store.chapters)} chapters")
        print(f"✅ Loaded {len(self.data_store.skills)} skills from org_config")
        print(f"✅ Loaded {len(self.data_store.current_roles)} current roles from org_config")
        
        # Load future roles from vision_futura
        self.load_vision()
        print(f"✅ Loaded {len(self.data_store.future_roles)} future roles from vision_futura")
        
        # For backward compatibility, combine roles
        self.data_store.roles = {**self.data_store.current_roles, **self.data_store.future_roles}
        
        print("=" * 50)
        print(f"✅ Data loading complete!")
        print(f"   - {len(self.data_store.employees)} employees")
        print(f"   - {len(self.data_store.current_roles)} current roles")
        print(f"   - {len(self.data_store.future_roles)} future roles")
        print(f"   - {len(self.data_store.chapters)} chapters")
        print(f"   - {len(self.data_store.skills)} skills")
        print(f"   - {len(self.data_store.projects)} projects")
        print("=" * 50)
    
    def load_projects(self):
        """Load company projects from JSON file"""
        projects_path = self.base_path / "company_projects.json"
        
        if not projects_path.exists():
            print(f"⚠️  Projects file not found: {projects_path}")
            return
        
        with open(projects_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for project in data.get('projects', []):
            project_id = project.get('id')
            if project_id:
                self.data_store.projects[project_id] = project
    
    def load_employees(self):
        """Load employees from CSV file"""
        csv_path = self.base_path / "talento_actual.csv"
        
        if not csv_path.exists():
            print(f"⚠️  Employee data file not found: {csv_path}")
            return
        
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            try:
                # Parse JSON fields
                habilidades = json.loads(row['habilidades'].replace("'", '"'))
                responsabilidades = json.loads(row['responsabilidades_actuales'].replace("'", '"'))
                dedicacion = json.loads(row['dedicación_actual'].replace("'", '"'))
                ambiciones_data = json.loads(row['ambiciones'].replace("'", '"'))
                metadata_data = json.loads(row['metadata'].replace("'", '"'))
                
                # Normalize field names (Spanish with accents -> English without)
                # Handle ambiciones data
                if 'nivel_aspiración' in ambiciones_data:
                    ambiciones_data['nivel_aspiracion'] = ambiciones_data.pop('nivel_aspiración')
                
                # Create employee object
                employee = Employee(
                    id_empleado=int(row['id_empleado']),
                    nombre=row['nombre'],
                    email=row['email'],
                    chapter=row['chapter'],
                    rol_actual=row['rol_actual'],
                    manager=row['manager'] if pd.notna(row['manager']) else None,
                    antiguedad=row['antigüedad'],
                    habilidades=habilidades,
                    responsabilidades_actuales=responsabilidades,
                    dedicacion_actual=dedicacion,
                    ambiciones=Ambitions(**ambiciones_data),
                    metadata=Metadata(**metadata_data)
                )
                
                self.data_store.employees[employee.id_empleado] = employee
                
            except Exception as e:
                print(f"⚠️  Error loading employee {row.get('id_empleado', 'unknown')}: {e}")
                continue
    
    def load_org_config(self):
        """Load organization configuration from JSON"""
        config_path = self.base_path / "org_config.json"
        
        if not config_path.exists():
            print(f"⚠️  Config file not found: {config_path}")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Load organization info
        if 'organization' in config:
            self.data_store.organization = Organization(**config['organization'])
        
        # Load chapters
        if 'chapters' in config:
            for chapter_data in config['chapters']:
                # Normalize field names
                if 'descripción' in chapter_data:
                    chapter_data['descripcion'] = chapter_data.pop('descripción')
                
                chapter = Chapter(**chapter_data)
                self.data_store.chapters[chapter.nombre] = chapter
        
        # Load skills
        if 'skills' in config:
            for skill_data in config['skills']:
                # Normalize field names
                if 'categoría' in skill_data:
                    skill_data['categoria'] = skill_data.pop('categoría')
                
                skill = Skill(**skill_data)
                self.data_store.skills[skill.id] = skill
        
        # Load current roles from config (roles that exist in the organization)
        if 'roles' in config:
            for role_data in config['roles']:
                try:
                    # Normalize field names (Spanish with accents -> English without)
                    normalized_role = {
                        'id': role_data.get('id', ''),
                        'titulo': role_data.get('título', role_data.get('titulo', '')),
                        'nivel': role_data.get('nivel', 'mid').lower(),  # Normalize to lowercase
                        'capitulo': role_data.get('capítulo', role_data.get('capitulo', '')),
                        'modalidad': 'FT',  # Default for current roles
                        'cantidad': 1,
                        'responsabilidades': role_data.get('responsabilidades', []),
                        'habilidades_requeridas': role_data.get('habilidades_requeridas', []),
                        'dedicacion_esperada': role_data.get('dedicación_esperada', role_data.get('dedicacion_esperada', '40h/semana')),
                        'inicio_estimado': '0m',  # Already started
                        'objetivos_asociados': []
                    }
                    
                    role = Role(**normalized_role)
                    self.data_store.current_roles[role.id] = role
                except Exception as e:
                    print(f"⚠️  Error loading role {role_data.get('id', 'unknown')}: {e}")
                    continue
    
    def load_vision(self):
        """Load future vision and roles from vision_futura.json"""
        vision_path = self.base_path / "vision_futura.json"
        
        print(f"📄 Looking for vision file: {vision_path}")
        print(f"📄 File exists: {vision_path.exists()}")
        
        if not vision_path.exists():
            print(f"⚠️  Vision file not found: {vision_path}")
            return
        
        with open(vision_path, 'r', encoding='utf-8') as f:
            self.data_store.vision_data = json.load(f)
        
        # Load future roles from vision
        if 'roles_necesarios' in self.data_store.vision_data:
            for role_data in self.data_store.vision_data['roles_necesarios']:
                try:
                    # Normalize field names
                    modalidad = role_data.get('modalidad', 'FT')
                    # Handle non-standard modalidad values
                    if modalidad not in ['FT', 'PT', 'Freelance']:
                        modalidad = 'Freelance'  # Default fractional/other to Freelance
                    
                    cantidad = role_data.get('cantidad', 1)
                    # Handle fractional cantidad (round up)
                    if isinstance(cantidad, float):
                        cantidad = max(1, int(cantidad) if cantidad >= 1 else 1)
                    
                    normalized_role = {
                        'id': role_data.get('id', ''),
                        'titulo': role_data.get('título', role_data.get('titulo', '')),
                        'nivel': role_data.get('nivel', 'mid').lower(),  # Normalize to lowercase
                        'capitulo': role_data.get('capítulo', role_data.get('capitulo', '')),
                        'modalidad': modalidad,
                        'cantidad': int(cantidad),
                        'inicio_estimado': role_data.get('inicio_estimado', '0m'),
                        'objetivos_asociados': role_data.get('objetivos_asociados', []),
                        'responsabilidades': [],
                        'habilidades_requeridas': [],
                        'dedicacion_esperada': '40h/semana'
                    }
                    
                    role = Role(**normalized_role)
                    self.data_store.future_roles[role.id] = role
                except Exception as e:
                    print(f"⚠️  Error loading future role {role_data.get('id', 'unknown')}: {e}")
                    continue
    
    def get_employees(self) -> Dict[int, Employee]:
        """Get all employees"""
        return self.data_store.employees
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        return self.data_store.employees.get(employee_id)
    
    def add_employee(self, employee: Employee) -> Employee:
        """Add new employee"""
        self.data_store.employees[employee.id_empleado] = employee
        return employee
    
    def update_employee(self, employee_id: int, employee: Employee) -> Optional[Employee]:
        """Update existing employee"""
        if employee_id in self.data_store.employees:
            self.data_store.employees[employee_id] = employee
            return employee
        return None
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete employee"""
        if employee_id in self.data_store.employees:
            del self.data_store.employees[employee_id]
            return True
        return False
    
    def get_roles(self) -> Dict[str, Role]:
        """Get all roles"""
        return self.data_store.roles
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        return self.data_store.roles.get(role_id)
    
    def add_role(self, role: Role) -> Role:
        """Add new role"""
        self.data_store.roles[role.id] = role
        return role
    
    def get_skills(self) -> Dict[str, Skill]:
        """Get all skills"""
        return self.data_store.skills
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID"""
        return self.data_store.skills.get(skill_id)
    
    def add_skill(self, skill: Skill) -> Skill:
        """Add new skill"""
        self.data_store.skills[skill.id] = skill
        return skill
    
    def get_current_roles(self) -> Dict[str, Role]:
        """Get all current roles"""
        return self.data_store.current_roles
    
    def get_future_roles(self) -> Dict[str, Role]:
        """Get all future roles"""
        return self.data_store.future_roles
    
    def update_role(self, role_id: str, role: Role) -> Optional[Role]:
        """Update existing role"""
        if role_id in self.data_store.roles:
            self.data_store.roles[role_id] = role
            return role
        return None
    
    def delete_role(self, role_id: str) -> bool:
        """Delete role"""
        if role_id in self.data_store.roles:
            del self.data_store.roles[role_id]
            return True
        return False
    
    def get_company_projects(self) -> Dict[str, Dict]:
        """
        Get company projects from JSON file and enrich with employee dedication data
        Returns a dict with project id as key and enriched data as value
        """
        # Start with projects from JSON file
        projects = {}
        for project_id, project_data in self.data_store.projects.items():
            projects[project_id] = {
                **project_data,
                'total_employees': 0,
                'total_dedication': 0,
                'employees': []
            }
        
        # Enrich with employee data
        # Map project names to IDs for matching
        name_to_id_map = {
            project['name']: project_id 
            for project_id, project in self.data_store.projects.items()
        }
        
        for employee in self.data_store.employees.values():
            if not employee.dedicacion_actual:
                continue
            
            # Each employee has dedicacion_actual as dict: {"Project": percentage}
            for project_name, dedication_percentage in employee.dedicacion_actual.items():
                # Find matching project by name
                project_id = name_to_id_map.get(project_name)
                
                if project_id and project_id in projects:
                    projects[project_id]['total_employees'] += 1
                    projects[project_id]['total_dedication'] += dedication_percentage
                    projects[project_id]['employees'].append(employee.nombre)
        
        # Calculate average dedication percentage for each project
        for project_data in projects.values():
            if project_data['total_employees'] > 0:
                project_data['avg_dedication_percentage'] = round(
                    project_data['total_dedication'] / project_data['total_employees'], 
                    2
                )
            else:
                project_data['avg_dedication_percentage'] = 0.0
        
        return projects


# Global instance
data_loader = DataLoader()
