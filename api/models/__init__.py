"""Models package - Expose all models"""

from models.employee import (
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeListResponse,
    EmployeeStats,
    Ambitions,
    Metadata
)
from models.role import (
    Role,
    RoleCreate,
    RoleUpdate,
    RoleListResponse,
    Chapter,
    Skill,
    SkillCreate,
    SeniorityLevel,
    Modality
)
from models.hr_forms import (
    HRRoleDefinitionForm,
    HRGapAnalysisRequest,
    HRGapAnalysisResponse,
    EmployeeSkillGap,
    HRValidationResponse,
    HREmployeeSubmitForm,
    HREmployeeSubmitResponse,
    HREmployeeSkillSubmit,
    HREmployeeAmbitionsSubmit,
    HREmployeeDedicationSubmit
)
from models.company import (
    Organization,
    CompanyConfig,
    CompanyStatus,
    CompanyHealthCheck,
    GapCalculationWeights,
    CompanyProject,
    CompanyProjectsResponse
)

__all__ = [
    # Employee models
    "Employee",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeListResponse",
    "EmployeeStats",
    "Ambitions",
    "Metadata",
    # Role models
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "RoleListResponse",
    "Chapter",
    "Skill",
    "SkillCreate",
    "SeniorityLevel",
    "Modality",
    # HR Forms
    "HRRoleDefinitionForm",
    "HRGapAnalysisRequest",
    "HRGapAnalysisResponse",
    "EmployeeSkillGap",
    "HRValidationResponse",
    "HREmployeeSubmitForm",
    "HREmployeeSubmitResponse",
    "HREmployeeSkillSubmit",
    "HREmployeeAmbitionsSubmit",
    "HREmployeeDedicationSubmit",
    # Company models
    "Organization",
    "CompanyConfig",
    "CompanyStatus",
    "CompanyHealthCheck",
    "GapCalculationWeights",
    "CompanyProject",
    "CompanyProjectsResponse",
]
