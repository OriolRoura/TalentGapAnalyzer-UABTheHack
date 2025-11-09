"""
Validation Service
Business logic validation for employees, roles, and company data
"""

from typing import List, Dict, Tuple
from models.employee import Employee
from models.role import Role
from models.company import CompanyHealthCheck


class ValidationService:
    """Service for validating business rules"""
    
    @staticmethod
    def validate_employee_dedication(employee: Employee) -> Tuple[bool, List[str]]:
        """
        Validate that employee dedication sums to 100%
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        total_dedication = sum(employee.dedicacion_actual.values())
        if total_dedication != 100:
            errors.append(
                f"Employee {employee.nombre} dedication sums to {total_dedication}%, must be 100%"
            )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_no_dual_roles(employees: Dict[int, Employee]) -> Tuple[bool, List[str]]:
        """
        Validate that no employee appears in multiple roles simultaneously
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        role_assignments = {}
        
        for emp_id, employee in employees.items():
            role = employee.rol_actual
            if role not in role_assignments:
                role_assignments[role] = []
            role_assignments[role].append(employee.nombre)
        
        # Check for employees in multiple distinct roles
        employee_roles = {}
        for emp_id, employee in employees.items():
            if employee.nombre not in employee_roles:
                employee_roles[employee.nombre] = []
            employee_roles[employee.nombre].append(employee.rol_actual)
        
        for name, roles in employee_roles.items():
            if len(set(roles)) > 1:
                errors.append(
                    f"Employee {name} appears in multiple roles: {', '.join(set(roles))}"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_skill_levels(employee: Employee) -> Tuple[bool, List[str]]:
        """
        Validate that all skill levels are between 0-10
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        for skill, level in employee.habilidades.items():
            if not (0 <= level <= 10):
                errors.append(
                    f"Employee {employee.nombre} has invalid skill level for {skill}: {level} (must be 0-10)"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_email_uniqueness(employees: Dict[int, Employee]) -> Tuple[bool, List[str]]:
        """
        Validate that all employee emails are unique
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        emails = {}
        
        for emp_id, employee in employees.items():
            email = employee.email.lower()
            if email in emails:
                errors.append(
                    f"Duplicate email {employee.email} for employees: {emails[email]} and {employee.nombre}"
                )
            else:
                emails[email] = employee.nombre
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_manager_exists(employees: Dict[int, Employee]) -> Tuple[bool, List[str]]:
        """
        Validate that all managers exist as employees
        Returns: (is_valid, list_of_warnings)
        """
        warnings = []
        employee_names = {emp.nombre for emp in employees.values()}
        
        for emp_id, employee in employees.items():
            if employee.manager and employee.manager not in employee_names and employee.manager != "N/A":
                warnings.append(
                    f"Employee {employee.nombre} has manager {employee.manager} who is not in the system"
                )
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def check_data_completeness(employees: Dict[int, Employee]) -> Dict[str, float]:
        """
        Check completeness of employee data
        Returns: Dictionary with completeness percentages
        """
        if not employees:
            return {
                "skills": 0.0,
                "responsibilities": 0.0,
                "dedication": 0.0,
                "manager": 0.0,
                "ambitions": 0.0
            }
        
        total = len(employees)
        
        completeness = {
            "skills": sum(1 for emp in employees.values() if emp.habilidades) / total * 100,
            "responsibilities": sum(1 for emp in employees.values() if emp.responsabilidades_actuales) / total * 100,
            "dedication": sum(1 for emp in employees.values() if emp.dedicacion_actual) / total * 100,
            "manager": sum(1 for emp in employees.values() if emp.manager) / total * 100,
            "ambitions": sum(1 for emp in employees.values() if emp.ambiciones) / total * 100,
        }
        
        return completeness
    
    @staticmethod
    def perform_health_check(
        employees: Dict[int, Employee],
        roles: Dict[str, Role]
    ) -> CompanyHealthCheck:
        """
        Perform comprehensive health check on company data
        """
        errors = []
        warnings = []
        missing_data = {}
        
        # Run all validations
        is_valid, dedication_errors = ValidationService.validate_no_dual_roles(employees)
        errors.extend(dedication_errors)
        
        is_valid, email_errors = ValidationService.validate_email_uniqueness(employees)
        errors.extend(email_errors)
        
        is_valid, manager_warnings = ValidationService.validate_manager_exists(employees)
        warnings.extend(manager_warnings)
        
        # Check individual employees
        for emp_id, employee in employees.items():
            is_valid, ded_errors = ValidationService.validate_employee_dedication(employee)
            errors.extend(ded_errors)
            
            is_valid, skill_errors = ValidationService.validate_skill_levels(employee)
            errors.extend(skill_errors)
        
        # Check data completeness
        completeness = ValidationService.check_data_completeness(employees)
        
        # Identify missing data
        for emp_id, employee in employees.items():
            employee_missing = []
            if not employee.habilidades:
                employee_missing.append("skills")
            if not employee.responsabilidades_actuales:
                employee_missing.append("responsibilities")
            if not employee.dedicacion_actual:
                employee_missing.append("dedication")
            
            if employee_missing:
                missing_data[employee.nombre] = employee_missing
        
        # Calculate data quality score
        avg_completeness = sum(completeness.values()) / len(completeness)
        error_penalty = min(len(errors) * 5, 50)  # Max 50 point penalty
        data_quality_score = max(0, avg_completeness - error_penalty)
        
        # Generate recommendations
        recommendations = []
        if completeness["skills"] < 90:
            recommendations.append("Update skill assessments for all employees")
        if completeness["dedication"] < 100:
            recommendations.append("Ensure all employees have dedication percentages assigned")
        if len(errors) > 0:
            recommendations.append(f"Fix {len(errors)} validation errors")
        if completeness["manager"] < 80:
            recommendations.append("Update manager assignments")
        
        return CompanyHealthCheck(
            total_employees=len(employees),
            total_roles=len(roles),
            validation_errors=errors,
            validation_warnings=warnings,
            data_quality_score=round(data_quality_score, 2),
            missing_data=missing_data,
            recommendations=recommendations
        )
