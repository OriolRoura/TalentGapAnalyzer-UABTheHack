import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';

const ASPIRATION_LEVELS = ['junior', 'mid', 'senior', 'lead', 'director', 'executive'];
const SPECIALTIES = [
  'Estrategia',
  'Pricing',
  'GTM',
  'PMO',
  'Operations',
  'RevOps',
  'Automatización',
  'Community',
  'Content',
  'Brand Narrative',
  'Design Systems',
  'UI',
  'Paid Media',
  'Experimentación',
  'SEO Técnico',
  'Content SEO',
  'BI',
  'Atribución',
];

export function AmbitionsSection({ ambiciones, onChange }) {
  const [selectedSpecialty, setSelectedSpecialty] = useState('');

  const addSpecialty = () => {
    if (selectedSpecialty && !ambiciones.especialidades_preferidas.includes(selectedSpecialty)) {
      onChange({
        ...ambiciones,
        especialidades_preferidas: [...ambiciones.especialidades_preferidas, selectedSpecialty],
      });
      setSelectedSpecialty('');
    }
  };

  const removeSpecialty = (specialty) => {
    onChange({
      ...ambiciones,
      especialidades_preferidas: ambiciones.especialidades_preferidas.filter((s) => s !== specialty),
    });
  };

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Ambiciones Profesionales</CardTitle>
        <CardDescription>Define el nivel de aspiración y especialidades preferidas</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Aspiration Level */}
          <div>
            <label className="block text-sm font-medium mb-2">Nivel de Aspiración</label>
            <select
              value={ambiciones.nivel_aspiración}
              onChange={(e) =>
                onChange({
                  ...ambiciones,
                  nivel_aspiración: e.target.value,
                })
              }
              className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
            >
              <option value="">Seleccionar nivel</option>
              {ASPIRATION_LEVELS.map((level) => (
                <option key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Specialties */}
          <div>
            <label className="block text-sm font-medium mb-2">Especialidades Preferidas</label>
            <div className="flex gap-2 mb-4">
              <select
                value={selectedSpecialty}
                onChange={(e) => setSelectedSpecialty(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white"
              >
                <option value="">Seleccionar especialidad...</option>
                {SPECIALTIES.filter((spec) => !ambiciones.especialidades_preferidas.includes(spec)).map(
                  (spec) => (
                    <option key={spec} value={spec}>
                      {spec}
                    </option>
                  )
                )}
              </select>
              <Button onClick={addSpecialty} type="button" variant="default">
                Añadir
              </Button>
            </div>

            {/* Specialties Tags */}
            {ambiciones.especialidades_preferidas.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {ambiciones.especialidades_preferidas.map((specialty) => (
                  <div
                    key={specialty}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-full text-sm"
                  >
                    {specialty}
                    <button
                      onClick={() => removeSpecialty(specialty)}
                      className="hover:opacity-70"
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No hay especialidades seleccionadas</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
