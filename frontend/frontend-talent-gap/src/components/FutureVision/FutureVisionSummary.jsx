import React, { useState, useEffect } from 'react';
import futureJson from '../../../data/future_vision.json';
import executiveSummary from '../../../data/executive-summary.json';
import OrganizationHeader from '../OrganizationHeader';
import { get } from '../../services';
import { API_FUTURE_VISION } from '../../utils/constants';

const FutureVisionSummary = () => {
  const [initialData, setInitialData] = useState(futureJson);
  const [fetchData, setFetchData] = useState();
  const [activeTab, setActiveTab] = useState('12_meses');

  const timelinePeriods = ['12_meses', '18_meses', '24_meses'];

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
    <div className="min-h-screen bg-gray-50">
      <OrganizationHeader />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Company Info Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{initialData.organization.nombre}</h1>
          <p className="text-gray-600 mb-4">{initialData.organization.direccion}</p>
          <p className="text-lg text-gray-700">{initialData.organization.descripcion}</p>
        </div>

        {/* Executive Summary Hero */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-xl shadow-xl p-6 text-white mb-8">
        <h2 className="text-3xl font-bold mb-6 text-center">Análisis Ejecutivo de Talento</h2>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg p-4 text-center">
            <p className="text-xs text-indigo-100 mb-1">Empleados Actuales</p>
            <p className="text-3xl font-bold">{executiveSummary.total_employees}</p>
          </div>
          <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg p-4 text-center">
            <p className="text-xs text-indigo-100 mb-1">Roles Futuros</p>
            <p className="text-3xl font-bold">{executiveSummary.total_roles}</p>
          </div>
          <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg p-4 text-center">
            <p className="text-xs text-indigo-100 mb-1">Preparación Global</p>
            <p className="text-3xl font-bold">{(executiveSummary.overall_readiness_score * 100).toFixed(0)}%</p>
          </div>
          <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-lg p-4 text-center">
            <p className="text-xs text-indigo-100 mb-1">Empleados Listos</p>
            <p className="text-3xl font-bold">{executiveSummary.narrative.supporting_data.employees_with_ready_roles}</p>
          </div>
        </div>
        <div className="bg-white bg-opacity-10 rounded-lg p-4">
          <p className="text-white text-sm leading-relaxed">{executiveSummary.narrative.executive_summary}</p>
        </div>
      </div>

      {/* Strategic Alignment: Vision vs Reality */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Company Vision Card */}
        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl shadow-xl p-6 border-2 border-emerald-300">
          <div className="flex items-center mb-4">
            <div className="bg-emerald-900 bg-opacity-30 backdrop-blur-sm rounded-lg p-2 mr-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white drop-shadow-md">✨ Tu Visión</h3>
          </div>
          <div className="space-y-3 bg-emerald-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-4 shadow-inner">
            <div>
              <p className="text-xs text-white mb-2 uppercase font-bold tracking-wide">Objetivos Críticos</p>
              <ul className="space-y-2 text-sm">
                {initialData.prioridades.critico.slice(0, 3).map((item, index) => (
                  <li key={index} className="flex items-start bg-emerald-900 bg-opacity-20 rounded p-2">
                    <span className="text-emerald-200 mr-2 font-bold">→</span>
                    <span className="text-white font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="pt-3 border-t-2 border-emerald-300 border-opacity-40">
              <p className="text-xs text-white mb-2 uppercase font-bold tracking-wide">KPIs 12 Meses</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-emerald-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-3 text-center">
                  <p className="text-xs text-emerald-100 mb-1">Ingresos</p>
                  <p className="text-2xl font-bold text-white">{(initialData.timeline['12_meses'].kpis_objetivo.ingresos_mensuales / 1000).toFixed(0)}K€</p>
                </div>
                <div className="bg-emerald-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-3 text-center">
                  <p className="text-xs text-emerald-100 mb-1">Margen</p>
                  <p className="text-2xl font-bold text-white">{(initialData.timeline['12_meses'].kpis_objetivo.margen_operativo * 100).toFixed(0)}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Analysis Card */}
        <div className="bg-gradient-to-br from-red-500 to-orange-600 rounded-xl shadow-xl p-6 border-2 border-red-300">
          <div className="flex items-center mb-4">
            <div className="bg-red-900 bg-opacity-30 backdrop-blur-sm rounded-lg p-2 mr-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white drop-shadow-md">⚠️ Brechas de Talento</h3>
          </div>
          <div className="space-y-3 bg-red-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-4 shadow-inner">
            <div>
              <p className="text-xs text-white mb-2 uppercase font-bold tracking-wide">Riesgos Críticos</p>
              <ul className="space-y-2 text-sm">
                {executiveSummary.narrative.key_insights.slice(0, 3).map((insight, index) => (
                  <li key={index} className="flex items-start bg-red-900 bg-opacity-20 rounded p-2">
                    <span className="text-red-200 mr-2 flex-shrink-0 font-bold">✗</span>
                    <span className="text-white line-clamp-2 font-medium">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="pt-3 border-t-2 border-red-300 border-opacity-40">
              <p className="text-xs text-white mb-2 uppercase font-bold tracking-wide">Estado Actual</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-red-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-3 text-center">
                  <p className="text-xs text-red-100 mb-1">Preparación</p>
                  <p className="text-2xl font-bold text-white">{(executiveSummary.overall_readiness_score * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-red-900 bg-opacity-25 backdrop-blur-sm rounded-lg p-3 text-center">
                  <p className="text-xs text-red-100 mb-1">En Riesgo</p>
                  <p className="text-2xl font-bold text-white">{executiveSummary.total_employees - executiveSummary.narrative.supporting_data.employees_with_ready_roles}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Recommendations: Investment & Action Plan */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Investment Priorities */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-yellow-500">
          <div className="flex items-center mb-4">
            <div className="bg-yellow-100 rounded-lg p-2 mr-3">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">💰 Dónde Invertir</h3>
          </div>
          <div className="space-y-3">
            {executiveSummary.investment_priorities.map((investment, index) => (
              <div key={index} className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-bold text-gray-900 text-sm">{investment.area}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    investment.priority === 'Alta' ? 'bg-red-600 text-white' :
                    investment.priority === 'Media' ? 'bg-orange-400 text-white' :
                    'bg-yellow-300 text-yellow-900'
                  }`}>
                    {investment.priority}
                  </span>
                </div>
                <p className="text-gray-700 text-sm mb-2">{investment.recommendation}</p>
                <p className="text-gray-600 text-xs font-semibold">💡 Impacto: {investment.estimated_impact}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Plan */}
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center mb-4">
            <div className="bg-blue-100 rounded-lg p-2 mr-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">📋 Plan de Acción</h3>
          </div>
          <div className="space-y-2">
            {executiveSummary.organizational_recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors">
                <span className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold mr-3">
                  {index + 1}
                </span>
                <p className="text-gray-700 leading-snug text-sm">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Future Outlook */}
      <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 rounded-xl shadow-xl p-6 text-white mb-8">
        <div className="flex items-start gap-4">
          <div className="flex items-center flex-shrink-0">
            <div className="bg-white bg-opacity-20 rounded-lg p-2 mr-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold whitespace-nowrap">🔮 Perspectiva Futura</h3>
          </div>
          <p className="text-white text-base leading-relaxed flex-1 font-medium">{executiveSummary.narrative.future_outlook}</p>
        </div>
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
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Roles Necesarios para la Visión</h2>
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
              <div className='mt-8 text-center'>
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
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Transformaciones Estratégicas</h2>
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
      </div>
    </div>
  );
};

export default FutureVisionSummary;
