import React, { useState, useMemo } from 'react';
// import { post, get } from '../../services'; // Comentados ya que el mock está en el mismo archivo
// import { API_GLOBAL_MATRIX, API_EMPLOYEE_MATRIX } from '../../utils/constants';
import LoadingSpinner from '../LoadingSpinner';
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

// Color scale for compatibility scores (para usar en el ScoreCell para el background)
const getScoreColor = (score) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    if (score >= 0.4) return 'bg-orange-500'; // Usa orange en el original getScoreColor
    return 'bg-red-500';
};

// --- Nuevo Componente para la Celda de Puntuación de la Matriz (Eje X/Y) ---
const MatrixScoreCell = ({ score, band }) => {
    if (score === undefined || band === undefined) {
        return <div className="p-4 bg-gray-100 text-center text-xs text-gray-400">N/A</div>;
    }

    const colorClass = getScoreColor(score);
    const percentage = (score * 100).toFixed(0);
    
    // Para simplificar la visualización de la matriz, la celda solo muestra el % y el color
    return (
        <div 
            className={`p-2 h-14 w-16 flex items-center justify-center text-white text-sm font-bold rounded-md shadow-inner transition-all duration-300
                       ${colorClass} hover:ring-2 hover:ring-opacity-50 ${colorClass.replace('500', '700')}`}
            title={`Puntuación: ${percentage}%, Banda: ${band}`}
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
            <div className="p-6 bg-white shadow-xl rounded-xl text-center text-gray-500">
                No se encontraron datos de empleados o roles.
            </div>
        );
    }
    
    return (
        <div className="p-6 bg-white shadow-xl rounded-xl">
            <header className="mb-6 border-b pb-4">
                <h2 className="text-3xl font-bold text-gray-900">
                    Matriz de Compatibilidad: Empleados vs. Roles
                </h2>
{/*                 <p className="text-lg text-gray-600 mt-2">
                    Visualización de la compatibilidad de **{employees.length} empleados** con **{uniqueRoles.length} roles potenciales**.
                </p> */}
            </header>

            {/* Matrix Table Layout */}
            <div className="overflow-x-auto overflow-y-auto max-h-[80vh] border rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                    <colgroup>
                        <col className="w-[200px]" /> {/* Employee column width */}
                        {uniqueRoles.map((_, index) => (
                            <col key={index} className="w-[140px]" /> /* Role columns width */
                        ))}
                    </colgroup>
                    <thead className="sticky top-0 bg-gray-50 z-10 shadow-sm">
                        <tr>
                            <th 
                                scope="col" 
                                className="sticky left-0 z-20 px-4 py-3 text-center text-sm font-bold text-gray-900 uppercase tracking-wider bg-white border-r min-w-[200px]"
                            >
                                Empleado / Rol
                            </th>
                            {/* Eje X: Roles Potenciales */}
                            {uniqueRoles.map((roleTitle) => (
                                <th
                                    key={roleTitle}
                                    scope="col"
                                    className={`px-4 py-3 text-center text-sm font-medium text-gray-700 uppercase tracking-wider min-w-[140px] transition-colors duration-150 transform ${highlightedRole === roleTitle ? 'bg-indigo-100/70 border-b-2 border-indigo-500' : ''}`}
                                    onMouseEnter={() => setHighlightedRole(roleTitle)}
                                    onMouseLeave={() => setHighlightedRole(null)}
                                >
                                    <div className="transform -rotate-45 origin-left translate-y-8 translate-x-4 whitespace-nowrap font-semibold">
                                        {roleTitle}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {/* Eje Y: Empleados */}
                        {employees.map((employee, index) => {
                            const employeeScores = matrixMap.get(employee.id) || new Map();
                            return (
                                <tr key={employee.id} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-indigo-50 transition duration-150`}>
                                    {/* Employee Title Cell */}
                                    <td className="sticky left-0 z-10 px-4 py-3 whitespace-nowrap text-sm font-semibold text-gray-900 bg-white border-r">
                                        <div className="font-bold text-sm truncate" title={employee.name}>{employee.name}</div>
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
                    {/* Color Scale Legend (Copia del original) */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">Escala de Compatibilidad (%)</h3>
                        <div className="flex flex-wrap gap-4">
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-green-500 rounded"></div>
                                <span className="text-sm">≥ 80% (Excelente)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                                <span className="text-sm">≥ 60% (Bueno)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-orange-500 rounded"></div>
                                <span className="text-sm">≥ 40% (Regular)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-red-500 rounded"></div>
                                <span className="text-sm">{"< 40% (Bajo)"}</span>
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
    );
};

export default GapMatrix;