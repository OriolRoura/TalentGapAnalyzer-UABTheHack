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
        self.roles: Dict[str, Role] = {}
        self.chapters: Dict[str, Chapter] = {}
        self.skills: Dict[str, Skill] = {}
        self.organization: Optional[Organization] = None
        self.vision_data: Optional[Dict] = None


class DataLoader:
    """Service for loading data from files"""
    
    def __init__(self):
        self.data_store = DataStore()
        self.base_path = Path(__file__).parent.parent.parent / "dataSet" / "talent-gap-analyzer-main"
    
    def load_all_data(self):
        """Load all data from CSV and JSON files"""
        try:
            self.load_employees()
            self.load_org_config()
            self.load_vision()
            print(f"✅ Loaded {len(self.data_store.employees)} employees")
            print(f"✅ Loaded {len(self.data_store.roles)} roles")
            print(f"✅ Loaded {len(self.data_store.chapters)} chapters")
            print(f"✅ Loaded {len(self.data_store.skills)} skills")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
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
                chapter = Chapter(**chapter_data)
                self.data_store.chapters[chapter.nombre] = chapter
        
        # Load skills
        if 'skills' in config:
            for skill_data in config['skills']:
                skill = Skill(**skill_data)
                self.data_store.skills[skill.id] = skill
        
        # Load roles from config
        if 'roles' in config:
            for role_data in config['roles']:
                # Map Spanish fields to model fields
                role = Role(
                    id=role_data.get('id', ''),
                    titulo=role_data.get('título', ''),
                    nivel=role_data.get('nivel', 'mid'),
                    capitulo=role_data.get('capítulo', role_data.get('capitulo', '')),
                    responsabilidades=role_data.get('responsabilidades', []),
                    habilidades_requeridas=role_data.get('habilidades_requeridas', []),
                    dedicacion_esperada=role_data.get('dedicación_esperada', '40h/semana'),
                    inicio_estimado='0m',
                    objetivos_asociados=[]
                )
                self.data_store.roles[role.id] = role
    
    def load_vision(self):
        """Load future vision from JSON"""
        vision_path = self.base_path / "vision_futura.json"
        
        if not vision_path.exists():
            print(f"⚠️  Vision file not found: {vision_path}")
            return
        
        with open(vision_path, 'r', encoding='utf-8') as f:
            self.data_store.vision_data = json.load(f)
        
        # Load roles from vision
        if 'roles_necesarios' in self.data_store.vision_data:
            for role_data in self.data_store.vision_data['roles_necesarios']:
                role = Role(
                    id=role_data.get('id', ''),
                    titulo=role_data.get('título', ''),
                    nivel=role_data.get('nivel', 'mid'),
                    capitulo=role_data.get('capítulo', role_data.get('capitulo', '')),
                    modalidad=role_data.get('modalidad', 'FT'),
                    cantidad=role_data.get('cantidad', 1),
                    inicio_estimado=role_data.get('inicio_estimado', '0m'),
                    objetivos_asociados=role_data.get('objetivos_asociados', []),
                    responsabilidades=[],
                    habilidades_requeridas=[],
                    dedicacion_esperada='40h/semana'
                )
                # Don't overwrite if already exists from org_config
                if role.id not in self.data_store.roles:
                    self.data_store.roles[role.id] = role
    
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


# Global instance
data_loader = DataLoader()
