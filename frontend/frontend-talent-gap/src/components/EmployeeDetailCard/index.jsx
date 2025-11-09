import React from 'react';

const EmployeeDetailCard = ({ employee }) => {
    if (!employee) {
        return (
            <div class="p-4 bg-white rounded-lg shadow-md text-center text-gray-500 max-w-xl mx-auto mt-8">
                No employee data provided.
            </div>
        );
    }

    // Helper function to render key-value pairs (e.g., Skills or Dedication)
    const renderDedication = (obj) => (
        <ul class="space-y-1">
            {Object.entries(obj).map(([key, value]) => (
                <li key={key} class="flex justify-between items-center text-sm border-b border-gray-100 last:border-b-0 py-1">
                    <strong class="font-medium text-gray-600">{key.replace(/_/g, ' ')}:</strong>
                    <span class="text-gray-800 font-semibold">{value}%</span>
                </li>
            ))}
        </ul>
    );

    const renderSkills = (obj) => (
        <ul class="space-y-1">
            {Object.entries(obj).map(([key, value]) => (
                <li key={key} class="flex justify-between items-center text-sm border-b border-gray-100 last:border-b-0 py-1">
                    <strong class="font-medium text-gray-600">{key.replace(/_/g, ' ')}:</strong>
                    <span class="text-gray-800 font-semibold">{value}/10</span>
                </li>
            ))}
        </ul>
    );

    // Helper function to render a simple list of strings (e.g., Responsibilities)
    const renderListDetails = (list) => (
        <ul class="list-disc text-left justify-center list-inside space-y-1 pl-4 text-sm text-gray-700">
            {list.map((item, index) => (
                <li key={index}>{item}</li>
            ))}
        </ul>
    );

    // Destructure for cleaner access
    const {
        id_empleado,
        nombre,
        email,
        chapter,
        rol_actual,
        manager,
        antiguedad,
        habilidades,
        responsabilidades_actuales,
        dedicacion_actual,
        ambiciones,
        metadata
    } = employee;

    return (
        <div class="p-6 bg-white rounded-xl shadow-2xl max-w-3xl mx-auto my-8 border border-gray-100">
            {/* Header Section */}
            <header class="pb-4 mb-4 border-b border-indigo-200">
                <h2 class="text-3xl font-bold text-indigo-800">{nombre}</h2>
                <p class="text-xl text-gray-600 mt-1">
                    {rol_actual}
                    <span class="text-sm font-normal text-indigo-600 ml-2">({chapter})</span>
                </p>
            </header>

            {/* Basic Info & Responsibilities */}
            <section class="grid md:grid-cols-2 gap-8 mb-6">
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="text-lg justify-center font-semibold mb-3 flex items-center">
                        Información
                    </h3>
                    <ul class="space-y-2 text-left text-sm text-gray-700">
                        <li>
                            <strong class="font-medium">ID:</strong> {id_empleado}
                        </li>
                        <li>
                            <strong class="font-medium">Email:</strong>{' '}
                            <a href={`mailto:${email}`} class="text-blue-500 hover:underline">
                                {email}
                            </a>
                        </li>
                        <li>
                            <strong class="font-medium">Manager:</strong> {manager || 'N/A'}
                        </li>
                        <li>
                            <strong class="font-medium">Antigüedad (Seniority):</strong> {antiguedad}
                        </li>
                    </ul>
                </div>

                <div class="p-4 bg-gray-50 rounded-lg">
                    <h3 class="text-lg justify-center font-semibold mb-3 flex items-center">
                        Responsabilidades
                    </h3>
                    {renderListDetails(responsabilidades_actuales)}
                </div>
            </section>

            {/* Skills, Dedication, and Ambitions */}
            <div class="grid md:grid-cols-3 gap-6 mb-6 pt-4 border-t border-gray-100">
                {/* Skills */}
                <div class="col-span-1">
                    <h3 class="text-lg justify-center font-semibold mb-3 flex items-center">
                        Habilidades
                    </h3>
                    {renderSkills(habilidades)}
                </div>

                {/* Dedication */}
                <div class="col-span-1">
                    <h3 class="text-lg justify-center font-semibold mb-3 flex items-center">
                        Dedicación (100%)
                    </h3>
                    {renderDedication(dedicacion_actual)}
                </div>

                {/* Ambitions */}
                <div class="col-span-1 rounded-lg">
                    <h3 class="justify-center text-lg font-semibold  mb-3 flex items-center">
                       Ambiciones
                    </h3>
                    <ul class="space-y-2 text-sm text-left text-gray-700">
                        <li>
                            <strong class="font-medium">Nivel de aspiración:</strong>{' '}
                            <span class="text-yellow-800 px-2 py-0.5 rounded-full text-xs font-bold uppercase">
                                {ambiciones.nivel_aspiracion}
                            </span>
                        </li>
                        <li>
                            <strong class="font-medium">Preferencias</strong>
                            <div class="mt-1 flex flex-wrap gap-1">
                                {ambiciones.especialidades_preferidas.map((spec) => (
                                    <span key={spec} class="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-md text-xs">
                                        {spec}
                                    </span>
                                ))}
                            </div>
                        </li>
                    </ul>
                </div>
            </div>

            {/* Metadata Section */}
            <section class="pt-4 border-t border-gray-100">
                <h3 class="text-lg justify-center font-semibold text-center mb-3 flex items-center">
                    Metadata    
                </h3>
                <div class="flex flex-wrap gap-x-6 gap-y-3 text-sm text-center justify-center">
                    <p>
                        <strong class="font-medium text-gray-600">Ratio de rendimiento:</strong>{' '}
                        <span class={`font-bold ${metadata.performance_rating.startsWith('A') ? 'text-green-600' : 'text-orange-600'}`}>
                            {metadata.performance_rating}
                        </span>
                    </p>
                    <p>
                        <strong class="font-medium text-gray-600">Riesgo de retención:</strong>{' '}
                        <span class="font-bold text-red-600">{metadata.retention_risk}</span>
                    </p>
                    <p class="grow">
                        <strong class="font-medium text-gray-600">Próxima trayectoria:</strong>{' '}
                        <span class="text-gray-800 font-bold">{metadata.trayectoria}</span>
                    </p>
                </div>
            </section>
        </div>
    );
};

export default EmployeeDetailCard;