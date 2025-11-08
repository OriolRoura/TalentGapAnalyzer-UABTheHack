import React, { useEffect, useState } from 'react';
import { post, get } from '../../services';
import { API_EMPLOYEE_MATRIX } from '../../utils/constants';
import LoadingSpinner from '../LoadingSpinner';

// Color scale for compatibility scores
const getScoreColor = (score) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    if (score >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
};

// Score cell component
const ScoreCell = ({ score }) => {
    const bgColor = getScoreColor(score);
    return (
        <div className={`w-20 h-12 ${bgColor} flex items-center justify-center text-white font-bold rounded-md m-1`}>
            {(score * 100).toFixed(0)}%
        </div>
    );
};

// --- Constants for Styling ---
const BAND_STYLES = {
    'READY': {
        color: 'text-green-800',
        bg: 'bg-green-100',
        borderColor: 'border-green-600'
    },
    'READY_WITH_SUPPORT': {
        color: 'text-yellow-800',
        bg: 'bg-yellow-100',
        borderColor: 'border-yellow-600'
    },
    'NEAR': {
        color: 'text-blue-800',
        bg: 'bg-blue-100',
        borderColor: 'border-blue-600'
    },
    'FAR': {
        color: 'text-red-800',
        bg: 'bg-red-100',
        borderColor: 'border-red-600'
    },
    'default': {
        color: 'text-gray-800',
        bg: 'bg-gray-100',
        borderColor: 'border-gray-400'
    }
};

// --- Helper Component for Visual Score Bar ---
// This provides the visual element crucial for a matrix-style comparison
const ScoreBar = ({ score }) => {
    const percentage = (score * 100).toFixed(1);
    let barColor = 'bg-gray-400';
    if (score >= 0.8) barColor = 'bg-green-500';
    else if (score >= 0.6) barColor = 'bg-yellow-500';
    else if (score >= 0.4) barColor = 'bg-blue-500';
    else barColor = 'bg-red-500';

    return (
        <div className="flex flex-col items-end w-full">
            <span className="text-sm font-bold font-mono mb-1">{percentage}%</span>
            <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                    className={`h-2 rounded-full ${barColor} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
        </div>
    );
};

// --- Main Component ---
const GapMatrix = ({ data }) => {
    const { id_empleado } = data;

    const [matrixData, setMatrixData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const path = API_EMPLOYEE_MATRIX.replace("{id}", id_empleado);

    const fetchMatrix = async () => {
        setIsLoading(true);
        try {
            const out = await get(path);
            if (out) {
                setMatrixData(out);
            }
        } catch (error) {
            console.log("Error fetching matrix data:", error);
            setMatrixData(null);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (id_empleado) {
            fetchMatrix();
        }
    }, [id_empleado]);

    // 1. Derive the final data variables
    const employee_name = matrixData?.employee_name || data.employee_name;
    const current_role = matrixData?.current_role || data.current_role;
    const best_match = matrixData?.best_match;

    // 2. Sort the matches by score for rendering (Highest score first)
    const sortedMatches = matrixData?.role_matches
        ? [...matrixData.role_matches].sort((a, b) => b.overall_score - a.overall_score)
        : null;

    if (isLoading) {
        return <LoadingSpinner />;
    }

    if (!matrixData || !sortedMatches || sortedMatches.length === 0) {
        return (
            <div className="p-6 bg-white shadow-xl rounded-xl text-center text-gray-500">
                No se encontraron datos de matriz de compatibilidad para **{employee_name}**.
            </div>
        );
    }

    // Helper function to format metric score
    const formatScore = (score) => (score * 100).toFixed(1) + '%';

    return (
        <div className="p-6 bg-white shadow-xl rounded-xl">
            <header className="mb-6 border-b pb-4">
                <h2 className="text-3xl font-bold text-gray-900">
                    Matriz de Compatibilidad de Roles
                </h2>
                <p className="text-lg text-gray-600">
                    <span className="font-semibold">{employee_name}</span> (Rol Actual: {current_role})
                </p>
            </header>

            {/* Card Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <thead className="bg-gray-50 sticky top-0">
                        <tr>
                            <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider min-w-[200px]"
                            >
                                Rol Potencial
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-bold text-gray-900 uppercase tracking-wider bg-indigo-100 min-w-[150px]"
                            >
                                Puntuación Total
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-center text-xs font-bold text-gray-900 uppercase tracking-wider bg-indigo-100 min-w-[120px]"
                            >
                                Banda
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                Skills
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                Responsabilidades
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                                Ambiciones
                            </th>
                            <th
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[250px]"
                            >
                                Gaps Clave y Recs
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {sortedMatches.map((match) => {
                            const bandKey = match.band.toUpperCase();
                            const styles = BAND_STYLES[bandKey] || BAND_STYLES['default'];
                            const isBestMatch = best_match && match.role_id === best_match.role_id;

                            return (
                                <tr
                                    key={match.role_id}
                                    className={`${isBestMatch ? 'bg-indigo-50/70' : 'hover:bg-gray-50'} transition duration-150`}
                                >
                                    {/* Role Title */}
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        <div className="flex items-center">
                                            {isBestMatch && <span className="mr-2 text-indigo-600 text-lg" title="Mejor Coincidencia">⭐</span>}
                                            {match.role_title}
                                        </div>
                                    </td>

                                    {/* Overall Score (Matrix Highlight) */}
                                    <td className="px-6 py-3 text-sm font-semibold text-gray-900 bg-indigo-50">
                                        <ScoreBar score={match.overall_score} />
                                    </td>

                                    {/* Band Tag (Matrix Highlight) */}
                                    <td className="px-6 py-4 whitespace-nowrap text-center bg-indigo-50">
                                        <span
                                            className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                ${styles.bg} ${styles.color} border ${styles.borderColor}`}
                                        >
                                            {match.band.replace('_', ' ')}
                                        </span>
                                    </td>

                                    {/* Skills Score */}
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-mono text-gray-700">
                                        {formatScore(match.skills_score)}
                                    </td>

                                    {/* Responsibilities Score */}
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-mono text-gray-700">
                                        {formatScore(match.responsibilities_score)}
                                    </td>

                                    {/* Ambitions Score */}
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-mono text-gray-700">
                                        {formatScore(match.ambitions_score)}
                                    </td>

                                    {/* Gaps and Recommendations */}
                                    <td className="px-6 py-4">
                                        <ul className="list-disc list-inside text-xs text-gray-500 space-y-0.5">
                                            {/* Display first gap in red */}
                                            {match.detailed_gaps.length > 0 &&
                                                <li className="text-red-500 truncate">
                                                    {match.detailed_gaps[0]}
                                                </li>
                                            }
                                            {/* Display first recommendation in blue */}
                                            {match.recommendations.length > 0 &&
                                                <li className="text-blue-600 truncate">
                                                    {match.recommendations[0]}
                                                </li>
                                            }
                                            {/* If there are more gaps, show a count */}
                                            {match.detailed_gaps.length > 1 && (
                                                <li className="text-gray-400">
                                                    +{match.detailed_gaps.length - 1} gaps más...
                                                </li>
                                            )}
                                        </ul>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default GapMatrix;