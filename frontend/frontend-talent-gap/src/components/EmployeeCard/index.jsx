import React from 'react';

const EmployeeCard = ({ employee, onSelectEmployee, onSecondaryAction }) => {
    const {
        nombre,
        rol_actual,
        antiguedad,
        habilidades,
        ambiciones,
        metadata,
    } = employee;
    
    // --- Removed local state (showMatrix, matrixData) and API functions (fetchMatrix) ---
    // The parent component should handle show/hide and data fetching.

    // Extract first two initials for the avatar
    const initials = nombre.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);

    // Get top 3 skills (or fewer if less than 3)
    const sortedSkills = Object.entries(habilidades)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3);

    // Function to determine retention risk color/text
    const getRetentionRiskDisplay = (risk) => {
        switch (risk.toLowerCase()) {
            case 'baja': return <span className="text-green-600 font-medium">Retención baja</span>;
            case 'media': return <span className="text-yellow-600 font-medium">Retención media</span>;
            case 'alta': return <span className="text-red-600 font-medium">Retención alta</span>;
            default: return <span>Retención {risk}</span>;
        }
    };

    // This handles clicking anywhere on the card (Primary Action: Detail View/Select)
    const handleCardClick = () => {
        // We assume the main card click is the primary action (e.g., showing EmployeeDetailCard or selecting the employee)
        if (onSelectEmployee) {
            onSelectEmployee(employee);
        }
    };

    // This handles clicking the "Ver matriz" button (Secondary Action: Gap Matrix View)
    const handleMatrixClick = (e) => {
        // Stop the click from bubbling up and triggering the handleCardClick event
        e.stopPropagation();

        if (onSecondaryAction) {
            // Trigger the parent's secondary action handler, passing the employee data
            onSecondaryAction(employee);
        }
    };

    return (
        <div
            onClick={handleCardClick}
            className="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow-md cursor-pointer hover:bg-gray-50 transition-colors duration-200 ease-in-out"
        >
            {/* Top Section: Avatar, Name, Role, Performance */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    {/* Avatar */}
                    <div className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-100 text-blue-800 font-semibold text-lg">
                        {initials}
                    </div>
                    <div className='text-left'>
                        <h5 className="text-xl font-bold tracking-tight text-gray-900">
                            {nombre}
                        </h5>
                        <p className="text-sm text-gray-600">
                            {rol_actual}
                        </p>
                    </div>
                </div>
                {/* Performance Rating */}
                <span className={`inline-flex items-center justify-center h-8 w-8 rounded-full text-sm font-semibold 
                    ${metadata.performance_rating.startsWith('A') ? 'bg-green-100 text-green-800' :
                        metadata.performance_rating.startsWith('B') ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'}`}>
                    {metadata.performance_rating}
                </span>
            </div>

            {/* Ambition Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
                {ambiciones.especialidades_preferidas.map((specialty, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded-full">
                        {specialty}
                    </span>
                ))}
            </div>

            {/* Tenure & Retention Risk */}
            <div className="space-y-2 mb-6 text-gray-600 text-sm">
                <div className="flex justify-end">
                    <span>{antiguedad} de antiguedad</span>
                </div>
                <div className="flex justify-end">
                    {getRetentionRiskDisplay(metadata.retention_risk)}
                </div>
            </div>

            {/* Top Skills */}
            <div className="mt-4">
                <h6 className="text-md font-semibold text-gray-800 mb-2">Habilidades Top</h6>
                {sortedSkills.map(([skillName, score]) => (
                    <div key={skillName} className="flex items-center mb-2 text-center">
                        <span className="w-2/5 text-sm text-gray-700">{skillName.replace('S-', '')}</span>
                        <div className="w-3/5 bg-gray-200 rounded-full h-2.5 ml-2">
                            <div
                                className="bg-blue-600 h-2.5 rounded-full"
                                style={{ width: `${(score / 10) * 100}%` }}
                            ></div>
                        </div>
                        <span className="ml-2 text-sm font-medium text-gray-800">{score}</span>
                    </div>
                ))}
            </div>

            {/* --- BUTTON SECTION --- */}
            <div className="flex flow-row gap-2 justify-center mt-6 pt-4 border-t border-gray-100">
{/*                 <button
                    onClick={handleMatrixClick}
                    className="flex items-center font-semibold p-3 px-4 rounded-lg bg-blue-600 text-white shadow-md border-2 border-blue-600 hover:bg-blue-700 transition duration-150"
                >
                    Ver matriz
                </button> */}
                <button
                    onClick={handleMatrixClick}
                    className="flex items-center font-semibold p-3 px-4 rounded-lg bg-blue-600 text-white shadow-md border-2 border-blue-600 hover:bg-blue-700 transition duration-150"
                >
                    Ver análisis
                </button>
            </div>
            {/* The conditional render block at the end was entirely incorrect and is removed. */}
        </div>
    );
};

export default EmployeeCard;