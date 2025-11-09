import React, { useState, useMemo } from 'react';
// import { post, get } from '../../services'; // Comentados ya que el mock está en el mismo archivo
// import { API_GLOBAL_MATRIX, API_EMPLOYEE_MATRIX } from '../../utils/constants';
import LoadingSpinner from '../LoadingSpinner';
import OrganizationHeader from '../OrganizationHeader';
import fullGapMatrix from '../../../data/fullGapMatrix.json'; // Se asume que esta ruta es correcta

// --- Constants for Styling (Manteniendo las originales) ---
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
        color: 'text-blue-800', // NEAR usa azul en el código original, lo mantengo.
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

// Color scale for compatibility scores with better differentiation
const getScoreColor = (score) => {
    if (score >= 0.9) return 'bg-emerald-600';      // 90-100%: Excelente
    if (score >= 0.8) return 'bg-green-500';        // 80-89%: Muy bueno
    if (score >= 0.7) return 'bg-lime-500';         // 70-79%: Bueno
    if (score >= 0.6) return 'bg-yellow-500';       // 60-69%: Aceptable
    if (score >= 0.5) return 'bg-amber-500';        // 50-59%: Regular
    if (score >= 0.4) return 'bg-orange-500';       // 40-49%: Bajo
    if (score >= 0.3) return 'bg-red-500';          // 30-39%: Muy bajo
    return 'bg-red-700';                            // 0-29%: Crítico
};

// Get descriptive label for score
const getScoreLabel = (score) => {
    if (score >= 0.9) return 'Excelente';
    if (score >= 0.8) return 'Muy bueno';
    if (score >= 0.7) return 'Bueno';
    if (score >= 0.6) return 'Aceptable';
    if (score >= 0.5) return 'Regular';
    if (score >= 0.4) return 'Bajo';
    if (score >= 0.3) return 'Muy bajo';
    return 'Crítico';
};

// --- Nuevo Componente para la Celda de Puntuación de la Matriz (Eje X/Y) ---
const MatrixScoreCell = ({ score, band }) => {
    if (score === undefined || band === undefined) {
        return <div className="p-1 bg-gray-100 text-center text-xs text-gray-400">N/A</div>;
    }

    const colorClass = getScoreColor(score);
    const percentage = (score * 100).toFixed(0);
    const label = getScoreLabel(score);
    
    // Para simplificar la visualización de la matriz, la celda solo muestra el % y el color
    return (
        <div 
            className={`p-1.5 h-11 w-16 flex items-center justify-center text-white text-sm font-bold rounded shadow-sm transition-all duration-200
                       ${colorClass} hover:ring-2 hover:ring-gray-900 hover:scale-105`}
            title={`Puntuación: ${percentage}% - ${label}\nBanda: ${band}`}
        >
            {percentage}%
        </div>
    );
};

// --- Main Component ---
const GapMatrix = () => {
    const [highlightedRole, setHighlightedRole] = useState(null); // Para resaltar el rol al pasar el ratón

    // 1. Procesar datos para obtener empleados y roles únicos (Ejes)
    const { employees, uniqueRoles, matrixMap } = useMemo(() => {
        const allMatrices = fullGapMatrix.matrices || [];
        const employeesData = allMatrices.map(m => ({
            id: m.employee_id,
            name: m.employee_name,
            role: m.current_role
        }));

        const roleTitles = new Set();
        const scoreMap = new Map(); // Mapa de Mapas: employeeId -> (roleTitle -> matchData)

        allMatrices.forEach(employeeMatrix => {
            const employeeId = employeeMatrix.employee_id;
            const roleMatches = employeeMatrix.role_matches || [];
            
            const employeeScores = new Map();

            roleMatches.forEach(match => {
                const roleTitle = match.role_title;
                roleTitles.add(roleTitle);
                employeeScores.set(roleTitle, { 
                    score: match.overall_score, 
                    band: match.band 
                });
            });
            scoreMap.set(employeeId, employeeScores);
        });

        const sortedRoles = Array.from(roleTitles).sort();

        return {
            employees: employeesData,
            uniqueRoles: sortedRoles,
            matrixMap: scoreMap
        };
    }, []);

    if (!employees.length || !uniqueRoles.length) {
        return (
            <div className="min-h-screen bg-gray-50">
                <OrganizationHeader />
                <div className="max-w-7xl mx-auto px-4 py-8">
                    <div className="p-6 bg-white shadow-xl rounded-xl text-center text-gray-500">
                        No se encontraron datos de empleados o roles.
                    </div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="min-h-screen bg-gray-50">
            <OrganizationHeader />
            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="bg-white shadow-xl rounded-xl p-6">
                    <header className="mb-6 border-b pb-4">
                        <h2 className="text-3xl font-bold text-gray-900">
                            Matriz de Compatibilidad: Empleados vs. Roles
                        </h2>
{/*                 <p className="text-lg text-gray-600 mt-2">
                    Visualización de la compatibilidad de **{employees.length} empleados** con **{uniqueRoles.length} roles potenciales**.
                </p> */}
            </header>

            {/* Matrix Table Layout */}
            <div className="overflow-auto border rounded-lg shadow-sm" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                <table className="table-auto border-collapse">
                    <thead className="sticky top-0 bg-gray-50 z-10 shadow-sm">
                        <tr>
                            <th 
                                scope="col" 
                                className="sticky left-0 z-20 px-3 py-2 text-center text-xs font-bold text-gray-900 uppercase tracking-wider bg-white border-r border-b w-40"
                                style={{ height: '120px', verticalAlign: 'bottom' }}
                            >
                                <div className="pb-2">Empleado / Rol</div>
                            </th>
                            {/* Eje X: Roles Potenciales */}
                            {uniqueRoles.map((roleTitle) => (
                                <th
                                    key={roleTitle}
                                    scope="col"
                                    className={`px-3 text-center text-xs font-medium text-gray-700 uppercase tracking-wider transition-colors duration-150 border-b ${highlightedRole === roleTitle ? 'bg-indigo-100/70 border-indigo-500' : ''}`}
                                    onMouseEnter={() => setHighlightedRole(roleTitle)}
                                    onMouseLeave={() => setHighlightedRole(null)}
                                    style={{ minWidth: '70px', maxWidth: '90px', height: '120px', verticalAlign: 'bottom', position: 'relative' }}
                                >
                                    <div className="absolute bottom-2 left-3 transform -rotate-45 origin-bottom-left whitespace-nowrap font-semibold text-[11px]">
                                        {roleTitle}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white">
                        {/* Eje Y: Empleados */}
                        {employees.map((employee, index) => {
                            const employeeScores = matrixMap.get(employee.id) || new Map();
                            return (
                                <tr key={employee.id} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-indigo-50 transition duration-150 border-b border-gray-100`}>
                                    {/* Employee Title Cell */}
                                    <td className="sticky left-0 z-10 px-3 py-2.5 whitespace-nowrap text-xs font-semibold text-gray-900 bg-inherit border-r w-40">
                                        <div className="font-bold text-xs truncate" title={employee.name}>{employee.name}</div>
                                    </td>
                                    
                                    {/* Score Cells */}
                                    {uniqueRoles.map((roleTitle) => {
                                        const matchData = employeeScores.get(roleTitle);
                                        const isHighlighted = highlightedRole === roleTitle;
                                        
                                        return (
                                            <td 
                                                key={roleTitle} 
                                                className={`p-1.5 text-center transition-colors duration-150 ${isHighlighted ? 'bg-indigo-50/50' : ''}`}
                                                onMouseEnter={() => setHighlightedRole(roleTitle)}
                                                onMouseLeave={() => setHighlightedRole(null)}
                                            >
                                                <MatrixScoreCell 
                                                    score={matchData?.score} 
                                                    band={matchData?.band} 
                                                />
                                            </td>
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Legend (Adaptada del código original) */}
            <div className="mt-6 border-t pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Color Scale Legend - Enhanced */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Escala de Compatibilidad (%)</h3>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-emerald-600 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">90-100% (Excelente)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-green-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">80-89% (Muy bueno)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-lime-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">70-79% (Bueno)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-yellow-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">60-69% (Aceptable)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-amber-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">50-59% (Regular)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-orange-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">40-49% (Bajo)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-red-500 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">30-39% (Muy bajo)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-5 h-5 bg-red-700 rounded shadow-sm"></div>
                                <span className="text-xs font-medium">0-29% (Crítico)</span>
                            </div>
                        </div>
                    </div>

                    {/* Band Summary (Adaptada del código original) */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Bandas de Compatibilidad</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {Object.entries(BAND_STYLES).map(([band, style]) => (
                                band !== 'default' && (
                                    <div key={band} className={`px-3 py-2 rounded-md ${style.bg} ${style.color} border ${style.borderColor}`}>
                                        <span className="text-xs font-semibold">{band.replace('_', ' ')}</span>
                                    </div>
                                )
                            ))}
                             <div className={`px-3 py-2 rounded-md ${BAND_STYLES['default'].bg} ${BAND_STYLES['default'].color} border ${BAND_STYLES['default'].borderColor}`}>
                                <span className="text-xs font-semibold">N/A</span>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
            </div>
        </div>
        </div>
    );
};

export default GapMatrix;