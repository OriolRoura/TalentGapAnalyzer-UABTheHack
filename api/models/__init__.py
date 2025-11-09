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
    SkillListResponse,
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
    HREmployeeDedicationSubmit,
    EmployeeGapMatrixRow,
    EmployeeGapMatrix
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
from models.ai_models import (
    # Structured output schemas
    RecommendationsOutput,
    StructuredRecommendation,
    StructuredActionItem,
    StructuredNarrative,
    StructuredDevelopmentPlan,
    StructuredMilestone,
    StructuredCompanyExecutiveSummary,
    StructuredInvestmentPriority,
    # Regular AI models
    PersonalizedRecommendation,
    DevelopmentPlan,
    ActionItem,
    AIMetadata,
    RecommendationType,
    EffortLevel,
    ConfidenceLevel,
    ReasoningType
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
    "SkillListResponse",
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
    # AI Models - Structured Schemas
    "RecommendationsOutput",
    "StructuredRecommendation",
    "StructuredActionItem",
    "StructuredNarrative",
    "StructuredDevelopmentPlan",
    "StructuredMilestone",
    "StructuredCompanyExecutiveSummary",
    "StructuredInvestmentPriority",
    # AI Models - Regular
    "PersonalizedRecommendation",
    "DevelopmentPlan",
    "ActionItem",
    "AIMetadata",
    "RecommendationType",
    "EffortLevel",
    "ConfidenceLevel",
    "ReasoningType",
    "HREmployeeSkillSubmit",
    "HREmployeeAmbitionsSubmit",
    "HREmployeeDedicationSubmit",
    "EmployeeGapMatrixRow",
    "EmployeeGapMatrix",
    # Company models
    "Organization",
    "CompanyConfig",
    "CompanyStatus",
    "CompanyHealthCheck",
    "GapCalculationWeights",
    "CompanyProject",
    "CompanyProjectsResponse",
]
