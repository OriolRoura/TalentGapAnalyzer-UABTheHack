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
    HREmployeeSkillForm,
    HREmployeeEvaluationForm,
    HRProjectDedicationForm,
    HRBulkProjectDedication,
    HRNewEmployeeForm,
    HRRoleDefinitionForm,
    HRGapAnalysisRequest,
    HRGapAnalysisResponse,
    EmployeeSkillGap,
    HRBulkSkillUpdate,
    HRValidationResponse
)
from models.company import (
    Organization,
    CompanyConfig,
    CompanyStatus,
    CompanyHealthCheck,
    GapCalculationWeights
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
    "HREmployeeSkillForm",
    "HREmployeeEvaluationForm",
    "HRProjectDedicationForm",
    "HRBulkProjectDedication",
    "HRNewEmployeeForm",
    "HRRoleDefinitionForm",
    "HRGapAnalysisRequest",
    "HRGapAnalysisResponse",
    "EmployeeSkillGap",
    "HRBulkSkillUpdate",
    "HRValidationResponse",
    # Company models
    "Organization",
    "CompanyConfig",
    "CompanyStatus",
    "CompanyHealthCheck",
    "GapCalculationWeights",
]
