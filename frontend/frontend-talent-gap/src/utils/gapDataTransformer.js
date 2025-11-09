/**
 * Transform gap matrix data from API to SkillBottleneck component format
 * @param {Object} gapMatrixData - Raw data from /api/v1/employees/gap-matrix/all
 * @returns {Object} Transformed data for SkillBottleneck component
 */
export const transformGapDataToSkillBottleneck = (gapMatrixData) => {
  console.log('🔄 [Transformer] Starting transformation...');
  console.log('📊 [Transformer] Input data:', gapMatrixData);
  
  if (!gapMatrixData || !Array.isArray(gapMatrixData)) {
    console.warn('⚠️ [Transformer] Invalid input data (not an array or null)');
    return { generalSkills: [], positionSkills: [] };
  }

  console.log(`📊 [Transformer] Processing ${gapMatrixData.length} employees`);

  // Map to track skills across all employees and roles
  const skillsMap = new Map();
  const rolesMap = new Map();

  // Process each employee's gap matrix
  gapMatrixData.forEach((employeeMatrix, empIndex) => {
    const { employee, role_matches } = employeeMatrix;
    
    if (!employee || !Array.isArray(role_matches)) {
      console.warn(`⚠️ [Transformer] Employee ${empIndex}: Invalid data structure`);
      return;
    }

    if (empIndex === 0) {
      console.log(`📊 [Transformer] Sample employee data:`, { employee, roleMatchesCount: role_matches.length });
    }

    // Process each role match
    role_matches.forEach((roleMatch, roleIndex) => {
      const { role, skill_gaps } = roleMatch;
      
      if (!role || !Array.isArray(skill_gaps)) {
        if (empIndex === 0) {
          console.warn(`⚠️ [Transformer] Employee ${empIndex}, Role ${roleIndex}: Invalid role data`);
        }
        return;
      }

      if (empIndex === 0 && roleIndex === 0) {
        console.log(`📊 [Transformer] Sample role data:`, { role, skillGapsCount: skill_gaps.length });
      }

      // Track role information
      if (!rolesMap.has(role.id)) {
        rolesMap.set(role.id, {
          id: role.id,
          title: role.titulo || role.title || 'Unknown Role',
          totalPeople: 0,
          skillsNeeded: new Map(), // Map of skill -> count of people needing it
        });
      }

      const roleData = rolesMap.get(role.id);
      roleData.totalPeople++;

      // Process skill gaps
      skill_gaps.forEach((gap) => {
        const { skill_id, skill_name, employee_level, required_level } = gap;
        
        if (!skill_name) return;

        const hasSkill = (employee_level || 0) >= (required_level || 0);
        const needsSkill = (required_level || 0) > 0;

        // Track general skill statistics
        if (!skillsMap.has(skill_id || skill_name)) {
          skillsMap.set(skill_id || skill_name, {
            id: skill_id || skill_name,
            name: skill_name,
            peopleWithSkill: 0,
            rolesNeedingSkill: new Set(),
            totalPeopleNeedingSkill: 0,
          });
        }

        const skillData = skillsMap.get(skill_id || skill_name);

        // Count people with this skill (at required level)
        if (hasSkill) {
          skillData.peopleWithSkill++;
        }

        // Track roles needing this skill
        if (needsSkill) {
          skillData.rolesNeedingSkill.add(role.id);
          skillData.totalPeopleNeedingSkill++;

          // Track for position-specific skills
          if (!roleData.skillsNeeded.has(skill_name)) {
            roleData.skillsNeeded.set(skill_name, {
              id: skill_id || skill_name,
              name: skill_name,
              peopleInRoleNeedingSkill: 0,
            });
          }
          roleData.skillsNeeded.get(skill_name).peopleInRoleNeedingSkill++;
        }
      });
    });
  });

  console.log(`📊 [Transformer] Skills map size: ${skillsMap.size}`);
  console.log(`📊 [Transformer] Roles map size: ${rolesMap.size}`);

  // Convert skills map to array with risk levels
  const generalSkills = Array.from(skillsMap.values()).map((skill) => {
    const rolesNeedingSkill = skill.rolesNeedingSkill.size;
    const coverage = skill.totalPeopleNeedingSkill > 0
      ? (skill.peopleWithSkill / skill.totalPeopleNeedingSkill) * 100
      : 100;

    let riskLevel = 'low';
    if (coverage < 20) {
      riskLevel = 'critical';
    } else if (coverage < 60) {
      riskLevel = 'urgent';
    }

    return {
      id: skill.id,
      name: skill.name,
      peopleWithSkill: skill.peopleWithSkill,
      rolesNeedingSkill,
      totalPeopleNeedingSkill: skill.totalPeopleNeedingSkill,
      riskLevel,
    };
  });

  // Convert roles map to array with skills
  const positionSkills = Array.from(rolesMap.values()).map((role) => ({
    id: role.id,
    title: role.title,
    totalPeople: role.totalPeople,
    skills: Array.from(role.skillsNeeded.values()),
  }));

  const result = {
    generalSkills: generalSkills.sort((a, b) => a.peopleWithSkill - b.peopleWithSkill),
    positionSkills: positionSkills.sort((a, b) => b.totalPeople - a.totalPeople),
  };

  console.log('✅ [Transformer] Transformation complete');
  console.log(`📊 [Transformer] Result: ${result.generalSkills.length} general skills, ${result.positionSkills.length} positions`);
  
  if (result.generalSkills.length > 0) {
    console.log('📊 [Transformer] Sample general skill:', result.generalSkills[0]);
  }
  if (result.positionSkills.length > 0) {
    console.log('📊 [Transformer] Sample position:', result.positionSkills[0]);
  }

  return result;
};

/**
 * Calculate summary statistics from transformed skill data
 * @param {Object} skillData - Transformed skill bottleneck data
 * @returns {Object} Summary statistics
 */
export const calculateSkillBottleneckStats = (skillData) => {
  const { generalSkills = [] } = skillData;

  const criticalSkills = generalSkills.filter((s) => s.riskLevel === 'critical');
  const urgentSkills = generalSkills.filter((s) => s.riskLevel === 'urgent');
  const lowRiskSkills = generalSkills.filter((s) => s.riskLevel === 'low');

  const totalGap = generalSkills.reduce(
    (sum, skill) => sum + (skill.totalPeopleNeedingSkill - skill.peopleWithSkill),
    0
  );

  const avgCoverage = generalSkills.length > 0
    ? generalSkills.reduce(
        (sum, skill) => sum + (skill.peopleWithSkill / skill.totalPeopleNeedingSkill) * 100,
        0
      ) / generalSkills.length
    : 0;

  return {
    totalSkills: generalSkills.length,
    criticalCount: criticalSkills.length,
    urgentCount: urgentSkills.length,
    lowRiskCount: lowRiskSkills.length,
    totalGap,
    avgCoverage: Math.round(avgCoverage),
    criticalSkills,
    urgentSkills,
  };
};
