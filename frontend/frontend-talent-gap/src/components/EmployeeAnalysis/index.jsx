import { useState, useEffect } from "react";
import { get } from '../../services'
import { API_AI } from "../../utils/constants";
import LoadingSpinner from '../LoadingSpinner';

const EmployeeAnalysis = ({ data }) => {
    const [isLoading, setIsLoading] = useState(true);
    const [fetchRecommendations, setFetchRecommendations] = useState();
    const [fetchDevPlan, setFetchDevPlan] = useState();
    const [fetchNarrative, setFetchNarrative] = useState();

    const fetchAllData = async () => {
        setIsLoading(true);
        try {
            const recommendationsPath = API_AI.replace("{id}", data.id_empleado) + "/recommendations";
            const narrativePath = API_AI.replace("{id}", data.id_empleado) + "/narrative";
            const devPlanPath = API_AI.replace("{id}", data.id_empleado) + "/development-plan";

            const [recommendationsData, narrativeData] = await Promise.all([
                get(recommendationsPath),
                get(narrativePath),
                //get(devPlanPath)
            ]);

            if (recommendationsData) setFetchRecommendations(recommendationsData);
            if (narrativeData) setFetchNarrative(narrativeData);
            //if (devPlanData) setFetchDevPlan(devPlanData);
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
            <div className="flex justify-center items-center min-h-[200px]">
                <LoadingSpinner loadText="Cargando analisis..."/>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {fetchRecommendations && fetchRecommendations.map((recommendation) => (
                <div key={recommendation.id} className="mb-8 bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">{recommendation.title}</h2>
                            <p className="text-gray-600 mt-1">{recommendation.description}</p>
                        </div>
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
                        <h3 className="text-lg font-semibold mb-3">Plan de Acción</h3>
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

            {fetchDevPlan && <div className="mt-8">
                {/* Development Plan content will go here */}
            </div>}
            
            {fetchNarrative && <div className="mt-8">
                {/* Narrative content will go here */}
            </div>}
        </div>
    )
}

export default EmployeeAnalysis;