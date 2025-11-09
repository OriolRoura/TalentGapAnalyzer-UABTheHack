import { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";

const Home = () => {
    const navigate = useNavigate();

    const handleAddEmployee = () => {
        navigate('/forms');
    };

    const handleDashboard = () => {
        navigate('/dashboard');
    };

    const handleMatrix = () => {
        navigate('/matrix');
    };

    return (
        <div class="flex flex-col min-h-screen mx-auto px-4 py-8">
            {/* Organization Header */}
            <div class="bg-white p-6 relative">
                <div class="">
                    <h1 class="text-4xl font-bold text-gray-900 mb-3">Talent Gap Analyzer</h1>
                    <h6 class="text-lg font-bold text-gray-600 text-right">by Promptaholics</h6>
                </div>
            </div>

            <div class='justify-between flex flex-row mt-48 gap-4'>
                <button
                    onClick={handleDashboard}
                    class="flex items-center font-semibold p-3 px-4 rounded-lg bg-blue-600 text-white shadow-md border-2 border-blue-600 hover:bg-blue-700 transition duration-150"
                >
                    Ver talento actual
                </button>
                 <button
                    onClick={handleMatrix}
                    class="flex items-center font-semibold p-3 px-4 rounded-lg bg-blue-600 text-white shadow-md border-2 border-blue-600 hover:bg-blue-700 transition duration-150"
                >
                    Ver matriz de brecha
                </button>
                <button
                    onClick={handleAddEmployee}
                    class="flex items-center font-semibold p-3 px-4 rounded-lg bg-blue-600 text-white shadow-md border-2 border-blue-600 hover:bg-blue-700 transition duration-150"
                >
                    Añadir empleado
                </button>
            </div>
        </div>
    )

}

export default Home;