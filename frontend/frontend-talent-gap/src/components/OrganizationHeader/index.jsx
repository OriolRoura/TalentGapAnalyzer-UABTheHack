import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const OrganizationHeader = ({ title = "Talent Gap Analyzer", subtitle = "by Promptaholics", showTabs = true }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'talento', label: 'Talento Actual', path: '/dashboard', icon: '👥' },
    { id: 'vision', label: 'Visión Futura', path: '/vision-summary', icon: '🎯' },
    { id: 'matriz', label: 'Matriz de Brecha', path: '/matrix', icon: '📊' },
    { id: 'bottlenecks', label: 'Critical Bottlenecks', path: '/bottlenecks', icon: '⚠️' }
  ];

  const isActiveTab = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname === path;
  };

  return (
    <div className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-4xl font-bold text-gray-900">{title}</h1>
          <h6 className="text-lg font-bold text-gray-600">{subtitle}</h6>
        </div>
        
        {showTabs && (
          <div className="flex gap-2 mt-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => navigate(tab.path)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  isActiveTab(tab.path)
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrganizationHeader;
