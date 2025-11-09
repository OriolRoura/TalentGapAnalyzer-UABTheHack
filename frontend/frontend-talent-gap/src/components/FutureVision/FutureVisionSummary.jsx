import React, { useState, useEffect } from 'react';
import futureJson from '../../../data/future_vision.json';
import { get } from '../../services';
import { API_FUTURE_VISION } from '../../utils/constants';

const FutureVisionSummary = () => {
  const [initialData, setInitialData] = useState(futureJson);
  const [fetchData, setFetchData] = useState();
  const [activeTab, setActiveTab] = useState('12_meses');

  const timelinePeriods = ['12_meses', '18_meses', '24_meses'];

  // Format currency for display
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const fetchCompanyVision = async () => {
    try {
      const futureData = await get(API_FUTURE_VISION);
      if (futureData) {
        setFetchData(futureData);
        setInitialData(futureData);
      }
    } catch (error) {
      console.error('Error fetching vision data:', error);
    }
  };

  useEffect(() => {
    fetchCompanyVision();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Organization Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        {/* <p className="text-2xl text-gray-600 mb-4">Resumen visión de futuro</p> */}
        <h1 className="text-3xl font-bold text-gray-900 mb-14">{initialData.organization.nombre}</h1>
        <p className="text-gray-600 mb-4">{initialData.organization.direccion}</p>
        <p className="text-lg text-gray-700">{initialData.organization.descripcion}</p>
      </div>

      {/* Timeline Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Timeline y Objetivos</h2>
        <div className="flex justify-center space-x-2 mb-6">
          {timelinePeriods.map((period) => (
            <button
              key={period}
              onClick={() => setActiveTab(period)}
              className={`px-4 py-2 rounded-lg ${activeTab === period
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
            >
              {period.replace('_', ' ')}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Milestones */}
          <div className="lg:col-span-2">
            <h3 className="mt-6 text-lg font-semibold mb-4 text-center">Hitos Clave</h3>
            <ul className="space-y-3 max-w-2xl mx-auto">
              {initialData.timeline[activeTab].hitos.map((hito, index) => (
                <li key={index} className="flex items-start">
                  <div className="shrink-0 h-6 w-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center mt-0.5">
                    {index + 1}
                  </div>
                  <span className="ml-3 text-gray-700">{hito}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* KPIs */}
          <div>
            <h3 className="mt-4 text-lg font-semibold mb-4 text-center">KPIs Objetivo</h3>
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <p className="text-sm text-gray-500">Ingresos Mensuales</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(initialData.timeline[activeTab].kpis_objetivo.ingresos_mensuales)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <p className="text-sm text-gray-500">Margen Operativo</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(initialData.timeline[activeTab].kpis_objetivo.margen_operativo * 100).toFixed(0)}%
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-500">Clientes</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {initialData.timeline[activeTab].kpis_objetivo.clientes_recurrentes}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-gray-500">NPS</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {initialData.timeline[activeTab].kpis_objetivo.nps}
                  </p>
                </div>
              </div>
            </div>

            {/* Risk Factors */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4 text-center">Riesgos Clave</h3>
              <ul className="space-y-2 max-w-xs mx-auto">
                {initialData.timeline[activeTab].riesgos_clave.map((riesgo, index) => (
                  <li key={index} className="flex items-center space-x-2">
                    <span className="shrink-0 text-red-500">⚠</span>
                    <span className="text-gray-700">{riesgo}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Roles Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Roles Necesarios</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {initialData.roles_necesarios.map((rol) => (
            <div key={rol.id} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h3 className="mb-2 font-semibold text-gray-900">{rol.título}</h3>
              <span className={`px-2 py-1 text-xs rounded-full ${rol.modalidad === 'FT' ? 'bg-green-100 text-green-800' :
                rol.modalidad === 'PT' ? 'bg-blue-100 text-blue-800' :
                  'bg-purple-100 text-purple-800'
                }`}>
                {rol.modalidad}
              </span>
              <div className='mt-8  text-center'>
                <p className="text-sm text-gray-600 mb-2">Nivel: {rol.nivel}</p>
                <p className="text-sm text-gray-600 mb-2">Capítulo: {rol.capítulo}</p>
                <p className="text-sm text-gray-600 mb-3">Inicio: {rol.inicio_estimado}</p>
                <div className="space-y-1">
                  {rol.objetivos_asociados.map((objetivo, index) => (
                    <p key={index} className="text-sm text-gray-700">• {objetivo}</p>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Transformations Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Transformaciones</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {initialData.transformaciones.map((transformacion, index) => (
            <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{transformacion.área}</h3>
              <p className="text-gray-700 mb-3">{transformacion.cambio}</p>
              <p className="text-sm text-gray-600 mb-3">{transformacion.impacto_esperado}</p>
              <div className="mt-8 flex flex-wrap gap-2 items-center justify-center">
                {transformacion.kpis.map((kpi, kIndex) => (
                  <span key={kIndex} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-sm">
                    {kpi}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Priorities Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Crítico</h2>
          <ul className="space-y-3">
            {initialData.prioridades.critico.map((item, index) => (
              <li key={index} className="flex items-start">
                <span className="shrink-0 h-6 w-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  {index + 1}
                </span>
                <span className="ml-3 text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-600 mb-4">Deseable</h2>
          <ul className="space-y-3">
            {initialData.prioridades.deseable.map((item, index) => (
              <li key={index} className="flex items-start">
                <span className="shrink-0 h-6 w-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mt-0.5">
                  {index + 1}
                </span>
                <span className="ml-3 text-gray-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FutureVisionSummary;
