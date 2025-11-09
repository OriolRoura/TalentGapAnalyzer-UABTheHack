import React, { useState } from 'react';
import FutureVisionSummary from './FutureVisionSummary';
import { SkillBottleneck } from './bottleneck/SkillBottleneck';

const FutureVision = () => {
  const [activeTab, setActiveTab] = useState('vision'); // 'vision' or 'bottleneck'

  return (
    <div className="container mx-auto p-6 max-w-[1400px]">
      <div className="flex justify-center mb-6">
        <div className="bg-white rounded-lg shadow-sm p-1 inline-flex space-x-1">
          <button
            onClick={() => setActiveTab('vision')}
            className={`px-6 py-2.5 rounded-md transition-all duration-200 font-medium ${
              activeTab === 'vision'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Visión de Futuro
          </button>
          <button
            onClick={() => setActiveTab('bottleneck')}
            className={`px-6 py-2.5 rounded-md transition-all duration-200 font-medium ${
              activeTab === 'bottleneck'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Análisis de Cuellos de Botella
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {activeTab === 'vision' ? <FutureVisionSummary /> : <SkillBottleneck />}
      </div>
    </div>
  );
};

export default FutureVision;