import React, { useMemo, useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertTriangle, Users, ChevronDown, AlertCircle } from 'lucide-react';
import OrganizationHeader from '../../OrganizationHeader';
import { getAllEmployeesGapMatrix } from '../../../services/gapAnalysisService';
import { transformGapDataToSkillBottleneck } from '../../../utils/gapDataTransformer';

// Mock data - will be replaced with real data later
const mockSkillsData = {
  generalSkills: [
    {
      id: "1",
      name: "Full-Stack Development",
      peopleWithSkill: 8,
      rolesNeedingSkill: 3,
      totalPeopleNeedingSkill: 24,
      riskLevel: "critical",
    },
    {
      id: "2",
      name: "Cloud Architecture",
      peopleWithSkill: 6,
      rolesNeedingSkill: 2,
      totalPeopleNeedingSkill: 20,
      riskLevel: "critical",
    },
    {
      id: "3",
      name: "Machine Learning",
      peopleWithSkill: 7,
      rolesNeedingSkill: 2,
      totalPeopleNeedingSkill: 15,
      riskLevel: "critical",
    },
    {
      id: "4",
      name: "DevOps",
      peopleWithSkill: 14,
      rolesNeedingSkill: 1,
      totalPeopleNeedingSkill: 20,
      riskLevel: "critical",
    },
    {
      id: "5",
      name: "Python",
      peopleWithSkill: 22,
      rolesNeedingSkill: 3,
      totalPeopleNeedingSkill: 28,
      riskLevel: "urgent",
    },
    {
      id: "6",
      name: "React",
      peopleWithSkill: 26,
      rolesNeedingSkill: 1,
      totalPeopleNeedingSkill: 30,
      riskLevel: "urgent",
    },
    {
      id: "7",
      name: "SQL",
      peopleWithSkill: 32,
      rolesNeedingSkill: 2,
      totalPeopleNeedingSkill: 35,
      riskLevel: "low",
    },
    {
      id: "8",
      name: "Kubernetes",
      peopleWithSkill: 12,
      rolesNeedingSkill: 1,
      totalPeopleNeedingSkill: 20,
      riskLevel: "urgent",
    },
  ],
  positionSkills: [
    {
      id: "backend-eng",
      title: "Backend Engineer",
      totalPeople: 24,
      skills: [
        {
          id: "be-1",
          name: "Full-Stack Development",
          peopleInRoleNeedingSkill: 24,
        },
        {
          id: "be-2",
          name: "Database Design",
          peopleInRoleNeedingSkill: 24,
        },
      ],
    },
    {
      id: "devops-eng",
      title: "DevOps Engineer",
      totalPeople: 20,
      skills: [
        {
          id: "do-1",
          name: "Cloud Architecture",
          peopleInRoleNeedingSkill: 20,
        },
        {
          id: "do-2",
          name: "Kubernetes",
          peopleInRoleNeedingSkill: 20,
        },
      ],
    },
    {
      id: "ml-eng",
      title: "ML Engineer",
      totalPeople: 15,
      skills: [
        {
          id: "ml-1",
          name: "Machine Learning",
          peopleInRoleNeedingSkill: 15,
        },
        {
          id: "ml-2",
          name: "Python",
          peopleInRoleNeedingSkill: 15,
        },
      ],
    },
    {
      id: "frontend-eng",
      title: "Frontend Engineer",
      totalPeople: 30,
      skills: [
        {
          id: "fe-1",
          name: "React",
          peopleInRoleNeedingSkill: 30,
        },
      ],
    },
  ],
};

export function SkillBottleneck() {
  const [expandedSkill, setExpandedSkill] = useState(null);
  const [skillsData, setSkillsData] = useState(mockSkillsData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch gap matrix data from API
  useEffect(() => {
    const fetchGapData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔄 [SkillBottleneck] Fetching gap matrix data from API...');
        const gapMatrixData = await getAllEmployeesGapMatrix();
        console.log('✅ [SkillBottleneck] Raw API response:', gapMatrixData);
        console.log(`📊 [SkillBottleneck] Number of employees in response: ${Array.isArray(gapMatrixData) ? gapMatrixData.length : 0}`);
        
        const transformedData = transformGapDataToSkillBottleneck(gapMatrixData);
        console.log('🔄 [SkillBottleneck] Transformed data:', transformedData);
        console.log(`📊 [SkillBottleneck] General skills found: ${transformedData.generalSkills.length}`);
        console.log(`📊 [SkillBottleneck] Position skills found: ${transformedData.positionSkills.length}`);
        
        // Only update if we have valid data
        if (transformedData.generalSkills.length > 0) {
          console.log('✅ [SkillBottleneck] Updating state with real data from API');
          setSkillsData(transformedData);
        } else {
          console.warn('⚠️ [SkillBottleneck] No skills found in transformed data, keeping mock data');
        }
      } catch (err) {
        console.error('❌ [SkillBottleneck] Error fetching gap matrix data:', err);
        console.error('❌ [SkillBottleneck] Error details:', err.message, err.response);
        setError(err.message || 'Failed to load skill gap data');
        console.warn('⚠️ [SkillBottleneck] Keeping mock data due to error');
        // Keep using mock data on error
      } finally {
        setLoading(false);
        console.log('🏁 [SkillBottleneck] Loading finished');
      }
    };

    fetchGapData();
  }, []);

  const sortedSkills = useMemo(() => {
    return [...(skillsData?.generalSkills || [])].sort((a, b) => a.peopleWithSkill - b.peopleWithSkill);
  }, [skillsData]);

  const skillPositionsMap = useMemo(() => {
    const map = {};

    (skillsData?.generalSkills || []).forEach((skill) => {
      map[skill.id] = [];
    });

    (skillsData?.positionSkills || []).forEach((position) => {
      position.skills.forEach((skill) => {
        const generalSkill = (skillsData?.generalSkills || []).find(s => s.name === skill.name);
        if (generalSkill && map[generalSkill.id]) {
          map[generalSkill.id].push({
            positionTitle: position.title,
            peopleNeedingSkill: skill.peopleInRoleNeedingSkill,
          });
        }
      });
    });

    return map;
  }, [skillsData]);

  const chartData = useMemo(() => {
    return sortedSkills.map((skill) => ({
      name: skill.name,
      haveSkill: skill.peopleWithSkill,
      needSkill: skill.totalPeopleNeedingSkill,
      gap: skill.totalPeopleNeedingSkill - skill.peopleWithSkill,
    }));
  }, [sortedSkills]);

  const criticalSkills = sortedSkills.filter((s) => s.riskLevel === "critical");
  const urgentSkills = sortedSkills.filter((s) => s.riskLevel === "urgent");

  return (
    <div className="min-h-screen bg-gray-50">
      <OrganizationHeader />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="border-b border-gray-200 bg-gradient-to-r from-red-50 to-white mb-8 rounded-lg shadow-sm">
          <div className="p-6 text-center">
            <div className="flex items-center justify-center gap-3 mb-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Critical Skill Voids</h1>
            </div>
          <p className="text-sm text-gray-600 leading-relaxed max-w-3xl mx-auto">
            Identify positions with critical skill shortages across your organization. Focus on roles where only a few people have
            the required expertise—these are your critical risk areas.
          </p>
          {loading && (
            <div className="mt-4 text-blue-600 flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm">Loading skill gap data...</span>
            </div>
          )}
          {error && !loading && (
            <div className="mt-4 text-yellow-600 text-sm">
              ⚠️ Using sample data. {error}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="border border-gray-200 hover:shadow-lg transition-shadow duration-200">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Critical Skills</p>
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
              </div>
              <p className="text-4xl font-bold text-red-600 mb-2">{criticalSkills.length}</p>
              <p className="text-xs text-gray-500">Roles with &lt;20% coverage</p>
            </div>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow duration-200">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Urgent Skills</p>
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              </div>
              <p className="text-4xl font-bold text-yellow-600 mb-2">{urgentSkills.length}</p>
              <p className="text-xs text-gray-500">Roles with 20-60% coverage</p>
            </div>
          </Card>

          <Card className="border border-gray-200 hover:shadow-lg transition-shadow duration-200">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">Total Skills</p>
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              </div>
              <p className="text-4xl font-bold text-gray-900 mb-2">{sortedSkills.length}</p>
              <p className="text-xs text-gray-500">Across all positions</p>
            </div>
          </Card>
        </div>

        {/* Chart */}
        <Card className="border border-gray-200 shadow-sm">
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-1">Skill Coverage Risk</h2>
              <p className="text-sm text-gray-500">How many people have each skill vs. how many need it</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={120}
                  />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e5e7eb",
                      borderRadius: "8px",
                      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    }}
                  />
                  <Legend wrapperStyle={{ paddingTop: "20px" }} />
                  <Bar dataKey="haveSkill" fill="#10b981" name="People with Skill" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="needSkill" fill="#3b82f6" name="People Needing Skill" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="gap" fill="#ef4444" name="Coverage Gap" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>

        {/* Critical Skills Highlight */}
        {criticalSkills.length > 0 && (
          <Card className="border-2 border-red-500 bg-gradient-to-r from-red-50 to-white shadow-md">
            <div className="p-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="p-3 bg-red-100 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-red-700 mb-4">⚠️ High Risk: Critical Skills</h3>
                  <div className="space-y-3">
                    {criticalSkills.map((skill) => (
                      <div key={skill.id} className="bg-white rounded-lg p-4 border border-red-200 shadow-sm">
                        <p className="font-semibold text-gray-900 mb-1">{skill.name}</p>
                        <p className="text-sm text-gray-600">
                          Only <span className="font-bold text-red-600">{skill.peopleWithSkill} people</span> have
                          this skill, but <span className="font-bold text-gray-900">{skill.totalPeopleNeedingSkill} positions</span> require it
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Detailed Table */}
        <Card className="border border-gray-200 shadow-sm">
          <div className="p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">All Skills - Detailed Breakdown</h2>
            </div>
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr className="border-b-2 border-gray-200">
                    <th className="px-4 py-4 text-left font-semibold text-gray-700 w-12"></th>
                    <th className="px-4 py-4 text-left font-semibold text-gray-700">Skill</th>
                    <th className="px-4 py-4 text-center font-semibold text-gray-700">
                      <div className="flex items-center justify-center gap-2">
                        <Users className="h-4 w-4 text-green-600" />
                        <span>Have It</span>
                      </div>
                    </th>
                    <th className="px-4 py-4 text-center font-semibold text-gray-700">Need It</th>
                    <th className="px-4 py-4 text-center font-semibold text-gray-700">Gap</th>
                    <th className="px-4 py-4 text-center font-semibold text-gray-700">Coverage</th>
                    <th className="px-4 py-4 text-center font-semibold text-gray-700">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {sortedSkills.map((skill, index) => {
                    const coverage = Math.round((skill.peopleWithSkill / skill.totalPeopleNeedingSkill) * 100);
                    const riskColor =
                      skill.riskLevel === "critical"
                        ? "text-red-700 bg-red-100 border-red-200"
                        : skill.riskLevel === "urgent"
                          ? "text-yellow-700 bg-yellow-100 border-yellow-200"
                          : "text-green-700 bg-green-100 border-green-200";
                    const isExpanded = expandedSkill === skill.id;
                    const positions = skillPositionsMap[skill.id] || [];

                    return (
                      <React.Fragment key={skill.id}>
                        <tr className={`border-b border-gray-200 hover:bg-blue-50 transition-colors ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                          <td className="px-4 py-4 text-center">
                            <button
                              onClick={() => setExpandedSkill(isExpanded ? null : skill.id)}
                              className="p-2 hover:bg-blue-100 rounded-md transition-colors"
                              aria-label={isExpanded ? "Collapse" : "Expand"}
                            >
                              <ChevronDown
                                className={`h-4 w-4 text-gray-600 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}
                              />
                            </button>
                          </td>
                          <td className="px-4 py-4 text-gray-900 font-semibold">{skill.name}</td>
                          <td className="px-4 py-4 text-center font-bold text-green-600">{skill.peopleWithSkill}</td>
                          <td className="px-4 py-4 text-center font-semibold text-blue-600">{skill.totalPeopleNeedingSkill}</td>
                          <td className="px-4 py-4 text-center font-bold text-red-600">
                            {skill.totalPeopleNeedingSkill - skill.peopleWithSkill}
                          </td>
                          <td className="px-4 py-4 text-center">
                            <div className="flex items-center justify-center gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${coverage < 20 ? 'bg-red-500' : coverage < 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                  style={{ width: `${coverage}%` }}
                                ></div>
                              </div>
                              <span className="font-semibold text-gray-900 text-xs">{coverage}%</span>
                            </div>
                          </td>
                          <td className="px-4 py-4 text-center">
                            <span className={`inline-block px-3 py-1 text-xs font-bold rounded-full border ${riskColor}`}>
                              {skill.riskLevel.charAt(0).toUpperCase() + skill.riskLevel.slice(1)}
                            </span>
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr className="bg-blue-50 border-b border-gray-200">
                            <td colSpan={7} className="px-4 py-6">
                              <div className="ml-8">
                                <p className="font-bold text-gray-900 mb-4 text-base">📋 Positions needing this skill:</p>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                  {positions.length > 0 ? (
                                    positions.map((pos, idx) => (
                                      <div key={idx} className="bg-white border-2 border-blue-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                                        <p className="font-semibold text-gray-900 mb-1">{pos.positionTitle}</p>
                                        <p className="text-sm text-gray-600 flex items-center gap-1">
                                          <Users className="h-3 w-3" />
                                          <span className="font-medium">{pos.peopleNeedingSkill}</span> people need this
                                        </p>
                                      </div>
                                    ))
                                  ) : (
                                    <p className="text-sm text-gray-500 italic">No positions found</p>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </div>
      </div>
    </div>
  );
}
