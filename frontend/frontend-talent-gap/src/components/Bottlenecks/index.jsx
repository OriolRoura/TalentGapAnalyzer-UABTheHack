import React from 'react';
import OrganizationHeader from '../OrganizationHeader';

const Bottlenecks = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <OrganizationHeader />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Critical Bottlenecks</h1>
          <p className="text-lg text-gray-600 mb-6">
            Análisis de cuellos de botella críticos en la organización
          </p>
          
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg">
            <div className="flex items-center mb-4">
              <svg className="w-8 h-8 text-yellow-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h2 className="text-2xl font-bold text-yellow-900">En Desarrollo</h2>
            </div>
            <p className="text-yellow-800 text-lg">
              Esta sección está siendo desarrollada por Oriol y estará disponible próximamente.
            </p>
            <p className="text-yellow-700 mt-4">
              Aquí se mostrarán los cuellos de botella críticos identificados en el análisis de talento.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Bottlenecks;
