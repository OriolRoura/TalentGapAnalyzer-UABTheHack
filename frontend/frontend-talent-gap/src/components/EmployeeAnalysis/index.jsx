import { useState, useEffect } from "react";
import { get } from '../../services'
import { API_AI, API_EMPLOYEE_MATRIX } from "../../utils/constants";
import LoadingSpinner from '../LoadingSpinner';

const EmployeeAnalysis = ({ data }) => {
    const [isLoading, setIsLoading] = useState(true);
    const [fetchRecommendations, setFetchRecommendations] = useState();
    const [fetchMatrix, setFetchMatrix] = useState();
    const [fetchDevPlan, setFetchDevPlan] = useState();
    const [fetchNarrative, setFetchNarrative] = useState();

    const fetchAllData = async () => {
        setIsLoading(true);
        try {
            const recommendationsPath = API_AI.replace("{id}", data.id_empleado) + "/recommendations";
            const narrativePath = API_AI.replace("{id}", data.id_empleado) + "/narrative";
            const matrixPlanPath = API_EMPLOYEE_MATRIX.replace("{id}", data.id_empleado)
            
            let targetRole, targetRoleTitle, readinessScore;
            
            const [recommendationsData, narrativeData, matrixData] = await Promise.all([
                get(recommendationsPath),
                get(narrativePath),
                get(matrixPlanPath),
            ]);
            
            if (recommendationsData) setFetchRecommendations(recommendationsData);
            if (narrativeData) setFetchNarrative(narrativeData);
            if (matrixData) {
                console.log(matrixData);

                targetRole = matrixData.best_match.role_id;
                targetRoleTitle = matrixData.best_match.role_title;
                readinessScore = matrixData.best_match.overall_score;
                
                if (matrixData.best_match.band === "NOT_VIABLE" ||
                    matrixData.best_match.band === "FAR") {
                        console.warn("Este rol puede ser demasiado ambicioso!");
                    }
                    
                const devPlanPath = API_AI.replace("{id}", data.id_empleado) + "/development-plan"
                        + `?target_role_id=${targetRole}&duration_months=6`;

                const devPlanData = await get(devPlanPath);
                
                if (devPlanData) {
                    setFetchDevPlan(devPlanData);
                    console.log('Development Plan Data:', devPlanData);
                }
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchAllData();
    }, []);

    const getPriorityColor = (priority) => {
        switch (priority?.toLowerCase()) {
            case 'high':
                return 'bg-red-100 text-red-800 border-red-300';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 border-yellow-300';
            case 'low':
                return 'bg-green-100 text-green-800 border-green-300';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-300';
        }
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[200px] min-w-[600px]">
                <LoadingSpinner loadText="Cargando analisis..." />
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            {/* Narrative Section */}
            {fetchNarrative && (
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">{fetchNarrative.title}</h2>

                    {/* Detailed Analysis */}
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">Análisis Detallado</h3>
                        <p className="text-gray-600 whitespace-pre-line">{fetchNarrative.detailed_analysis}</p>
                    </div>

                    {/* Recommendations Summary */}
                    <div className="mb-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">Resumen de Recomendaciones</h3>
                        <p className="text-gray-600 whitespace-pre-line">{fetchNarrative.recommendations_summary}</p>
                    </div>

                    {/* Supporting Data 
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-500">Empleado</p>
                            <p className="font-semibold text-gray-900">{fetchNarrative.supporting_data.employee_name}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-500">Chapter Actual</p>
                            <p className="font-semibold text-gray-900">{fetchNarrative.supporting_data.current_chapter}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-500">Roles Analizados</p>
                            <p className="font-semibold text-gray-900">{fetchNarrative.supporting_data.num_gap_results}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-500">Mejor Puntuación</p>
                            <p className="font-semibold text-gray-900">{fetchNarrative.supporting_data.best_role_score.toFixed(1)}%</p>
                        </div>
                    </div>*/}

                    {/* Trends */}
                    {fetchNarrative.trends_identified && (
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">Tendencias Identificadas</h3>
                            <ul className="list-disc list-inside space-y-2">
                                {fetchNarrative.trends_identified.map((trend, index) => (
                                    <li key={index} className="text-gray-600">{trend}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Recommendations Section */}
            {fetchRecommendations && fetchRecommendations.map((recommendation) => (
                <div key={recommendation.id} className="mb-8 bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex gap-2">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(recommendation.effort_level)}`}>
                                Esfuerzo: {recommendation.effort_level}
                            </span>
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-300">
                                Duración: {recommendation.estimated_duration}
                            </span>
                        </div>
                    </div>

                    <div className="mt-6">
                        <h3 className="text-lg font-semibold mb-3 font-bold">Plan de Acción</h3>
                        <div className="space-y-4">
                            {recommendation.action_items.map((item, index) => (
                                <div key={index} className="border rounded-lg p-4 bg-gray-50">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-medium text-gray-900">{item.action}</h4>
                                            <p className="text-sm text-gray-600 mt-1">Timeline: {item.timeline}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(item.priority)}`}>
                                            {item.priority}
                                        </span>
                                    </div>
                                    {item.resources_needed && (
                                        <div className="mt-3">
                                            <p className="text-sm text-center font-medium text-gray-700">Recursos necesarios:</p>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {item.resources_needed.map((resource, i) => (
                                                    <span key={i} className="px-2 py-1 text-xs bg-white rounded border border-gray-200">
                                                        {resource}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="mt-6 grid grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4">
                            <h3 className="font-semibold text-blue-900">Probabilidad de éxito</h3>
                            <p className="text-2xl font-bold text-blue-700 mt-1">
                                {(recommendation.success_probability * 100).toFixed(0)}%
                            </p>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4">
                            <h3 className="font-semibold text-purple-900">Puntuación de prioridad</h3>
                            <p className="text-2xl font-bold text-purple-700 mt-1">
                                {(recommendation.priority_score * 100).toFixed(0)}%
                            </p>
                        </div>
                    </div>
                </div>
            ))}

            {/* Development Plan Section */}
            {fetchDevPlan && (
                <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">Plan de Desarrollo</h2>
                            <p className="text-gray-600 mt-2">Rol objetivo: {fetchDevPlan.target_role_id}</p>
                        </div>
                        <div className="flex gap-4">
                            <div className="text-center">
                                <p className="text-sm text-gray-500">Puntuación Actual</p>
                                <p className="text-lg font-bold text-gray-900">{(fetchDevPlan.current_score * 100).toFixed(0)}%</p>
                            </div>
                            <div className="text-center">
                                <p className="text-sm text-gray-500">Puntuación Objetivo</p>
                                <p className="text-lg font-bold text-indigo-600">{(fetchDevPlan.target_score * 100).toFixed(0)}%</p>
                            </div>
                        </div>
                    </div>

                    {/* Timeline and Milestones */}
                    <div className="mb-8">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Hitos del Plan ({fetchDevPlan.duration_months} meses)</h3>
                        <div className="space-y-6">
                            {fetchDevPlan.milestones.map((milestone, index) => (
                                <div key={index} className="border-l-4 border-indigo-500 pl-4 pb-4">
                                    <div className="flex items-start mb-2">
                                        <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-100 text-indigo-800 text-sm font-medium mr-3">
                                            M{milestone.month}
                                        </span>
                                        <h4 className="text-lg font-medium text-gray-900">{milestone.milestone}</h4>
                                    </div>
                                    <div className="ml-9">
                                        <div className="mb-2">
                                            <p className="text-sm font-medium text-gray-500">Criterios de éxito:</p>
                                            <p className="text-gray-700">{milestone.success_criteria}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-500">Método de validación:</p>
                                            <p className="text-gray-700">{milestone.validation_method}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Skills Grid */}
                    <div className="mb-8">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Habilidades Prioritarias</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {fetchDevPlan.skill_priorities.map((skill) => (
                                <div key={skill.skill_id} className="bg-gray-50 p-4 rounded-lg">
                                    <h4 className="font-medium text-gray-900 mb-2">{skill.skill_name}</h4>
                                    <div className="flex justify-between text-sm">
                                        <span className={`px-2 py-1 rounded ${skill.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                            {skill.priority}
                                        </span>
                                        <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded">
                                            Nivel: {skill.target_level}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Metrics and Risk Factors */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Métricas del Plan</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-500">Inversión Estimada</p>
                                    <p className="text-xl font-bold text-gray-900">{fetchDevPlan.estimated_cost_eur.toLocaleString()}€</p>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-500">Horas Requeridas</p>
                                    <p className="text-xl font-bold text-gray-900">{fetchDevPlan.time_investment_hours}h</p>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg col-span-2">
                                    <p className="text-sm text-gray-500">Probabilidad de Éxito</p>
                                    <p className="text-xl font-bold text-gray-900">{(fetchDevPlan.success_probability * 100).toFixed(0)}%</p>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Factores de Riesgo</h3>
                            <ul className="space-y-2 list-disc list-inside text-gray-700">
                                {fetchDevPlan.risk_factors.map((risk, index) => (
                                    <li key={index} className="text-gray-600">{risk}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

        </div>
    )
}

export default EmployeeAnalysis;