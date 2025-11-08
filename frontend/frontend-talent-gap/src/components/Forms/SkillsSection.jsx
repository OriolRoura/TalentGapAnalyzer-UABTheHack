import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { getSkills } from '../../services/skillsService';

export function SkillsSection({ skills, onChange }) {
  const [selectedSkill, setSelectedSkill] = useState('');
  const [skillRating, setSkillRating] = useState(5);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [loadingSkills, setLoadingSkills] = useState(true);

  useEffect(() => {
    const fetchSkills = async () => {
      setLoadingSkills(true);
      const skillsData = await getSkills();
      setAvailableSkills(skillsData);
      setLoadingSkills(false);
    };
    fetchSkills();
  }, []);

  const addSkill = () => {
    if (selectedSkill && !skills[selectedSkill]) {
      onChange({
        ...skills,
        [selectedSkill]: skillRating,
      });
      setSelectedSkill('');
      setSkillRating(5);
    }
  };

  const removeSkill = (skill) => {
    const { [skill]: _, ...remaining } = skills;
    onChange(remaining);
  };

  return (
    <Card className="border-0 shadow-md">
      <CardHeader className="border-b bg-slate-50">
        <CardTitle className="text-primary">Habilidades</CardTitle>
        <CardDescription>Evalúa cada habilidad del 1 (mínimo) al 10 (máximo)</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Add New Skill */}
          <div className="flex gap-3 pb-6 border-b">
            <select
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white"
              style={{ minHeight: '2.5rem' }}
              disabled={loadingSkills}
            >
              <option value="">
                {loadingSkills ? 'Cargando habilidades...' : 'Seleccionar habilidad...'}
              </option>
              {availableSkills
                .filter((skill) => !skills[skill.id])
                .map((skill) => (
                  <option key={skill.id} value={skill.id}>
                    {skill.nombre} ({skill.categoria})
                  </option>
                ))}
            </select>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="1"
                max="10"
                value={skillRating}
                onChange={(e) => setSkillRating(Math.min(10, Math.max(1, parseInt(e.target.value) || 1)))}
                className="w-20"
              />
              <span className="text-xs text-gray-500">/10</span>
            </div>
            <Button onClick={addSkill} type="button" variant="default" className="px-6">
              Añadir
            </Button>
          </div>

          {/* Skills List */}
          {Object.keys(skills).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(skills).map(([skillId, rating]) => {
                const skillInfo = availableSkills.find(s => s.id === skillId);
                const displayName = skillInfo ? `${skillInfo.nombre} (${skillInfo.categoria})` : skillId;
                
                return (
                  <div key={skillId} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border">
                    <div className="flex-1">
                      <p className="font-medium">{displayName}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600"
                            style={{ width: `${(rating / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-blue-600">{rating}/10</span>
                      </div>
                    </div>
                    <button
                      onClick={() => removeSkill(skillId)}
                      className="ml-4 px-2 py-1 text-xs text-red-600 hover:text-red-800 bg-gray-100 hover:bg-gray-200 rounded border border-gray-300 transition-colors"
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">Añade habilidades para comenzar</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
