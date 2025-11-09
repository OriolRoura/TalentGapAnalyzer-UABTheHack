import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';

export function DedicationSection({ dedication, onChange, projects }) {
  const handleProjectChange = (projectName, value) => {
    const numValue = Math.min(100, Math.max(0, parseInt(value) || 0));
    onChange({
      ...dedication,
      [projectName]: numValue,
    });
  };

  const totalDedication = Object.values(dedication).reduce((sum, val) => sum + val, 0);

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Dedicación Actual</CardTitle>
        <CardDescription>Porcentaje de tiempo dedicado a cada proyecto (debe sumar 100%)</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {projects.map((project, index) => {
            // Manejar si project es un string o un objeto
            const projectName = typeof project === 'string' ? project : (project.name || project.id || `project-${index}`);
            const projectKey = typeof project === 'string' ? project : (project.id || project.name || `project-${index}`);
            
            return (
              <div key={projectKey} className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium">{projectName}</label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={dedication[projectName] || 0}
                      onChange={(e) => handleProjectChange(projectName, e.target.value)}
                      className="w-20"
                    />
                    <span className="text-xs text-gray-500">%</span>
                  </div>
                </div>
                <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all"
                    style={{ width: `${dedication[projectName] || 0}%` }}
                  />
                </div>
              </div>
            );
          })}

          <div className="pt-4 border-t">
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
              <span className="font-medium">Total Dedicación</span>
              <span
                className={`text-lg font-bold ${
                  totalDedication === 100
                    ? 'text-green-600'
                    : totalDedication > 100
                    ? 'text-red-600'
                    : 'text-yellow-600'
                }`}
              >
                {totalDedication}%
              </span>
            </div>
            {totalDedication !== 100 && (
              <p className="text-xs text-gray-500 mt-2">
                {totalDedication > 100
                  ? `⚠️ Exceso de ${totalDedication - 100}%`
                  : `⚠️ Falta ${100 - totalDedication}%`}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
