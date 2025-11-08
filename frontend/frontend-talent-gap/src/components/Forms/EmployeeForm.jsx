import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { SkillsSection } from './SkillsSection';
import { DedicationSection } from './DedicationSection';
import { AmbitionsSection } from './AmbitionsSection';
import { submitForm } from '../../services/formService';
import { getRoles } from '../../services/rolesService';
import { getChapters } from '../../services/chaptersService';
import { getProjects } from '../../services/projectsService';

const PERFORMANCE_RATINGS = ['D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'];
const RETENTION_RISKS = ['Baja', 'Media', 'Alta'];

export function EmployeeForm() {
  const [roles, setRoles] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(true);
  const [chapters, setChapters] = useState([]);
  const [loadingChapters, setLoadingChapters] = useState(true);
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);
  
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    chapter: '',
    rol_actual: '',
    manager: '',
    antigüedad: '',
    performance_rating: '',
    retention_risk: '',
    trayectoria: '',
    habilidades: {},
    dedicacion: {},
    ambiciones: {
      nivel_aspiración: '',
      especialidades_preferidas: [],
    },
  });

  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  // Cargar roles, chapters y projects desde la API al montar el componente
  useEffect(() => {
    const fetchData = async () => {
      setLoadingRoles(true);
      setLoadingChapters(true);
      setLoadingProjects(true);
      
      const rolesData = await getRoles();
      setRoles(rolesData);
      setLoadingRoles(false);
      
      const chaptersData = await getChapters();
      setChapters(chaptersData);
      setLoadingChapters(false);
      
      const projectsData = await getProjects();
      setProjects(projectsData);
      setLoadingProjects(false);
    };

    fetchData();
  }, []);

  const handleBasicChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSkillsChange = (skills) => {
    setFormData((prev) => ({
      ...prev,
      habilidades: skills,
    }));
  };

  const handleDedicationChange = (dedication) => {
    setFormData((prev) => ({
      ...prev,
      dedicacion: dedication,
    }));
  };

  const handleAmbitionsChange = (ambiciones) => {
    setFormData((prev) => ({
      ...prev,
      ambiciones,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      // Prepare payload matching the expected format
      const payload = {
        nombre: formData.nombre,
        email: formData.email,
        chapter: formData.chapter,
        rol_actual: formData.rol_actual,
        manager: formData.manager,
        antigüedad: `${formData.antigüedad}m`,
        habilidades: JSON.stringify(formData.habilidades),
        dedicación_actual: JSON.stringify(formData.dedicacion),
        ambiciones: JSON.stringify(formData.ambiciones),
        metadata: JSON.stringify({
          performance_rating: formData.performance_rating,
          retention_risk: formData.retention_risk,
          trayectoria: formData.trayectoria,
        }),
      };

      await submitForm(payload);
      console.log('Employee Data:', formData);
      
      setSubmitted(true);
      setMessage({ type: 'success', text: 'Empleado añadido con éxito' });
      
      setTimeout(() => {
        setSubmitted(false);
        setMessage(null);
      }, 3000);
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: err?.message || 'Error al enviar el formulario' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-[1400px] mx-auto p-8">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="border-b bg-slate-50 p-8">
            <CardTitle className="text-blue-600 text-3xl">Información Básica</CardTitle>
            <CardDescription className="text-base mt-2">Datos principales del empleado</CardDescription>
          </CardHeader>
          <CardContent className="pt-8 p-8">
            <div className="grid grid-cols-2 gap-8">
              <div>
                <label className="block text-base font-medium mb-3">Nombre *</label>
                <Input
                  type="text"
                  placeholder="Nombre completo"
                  value={formData.nombre}
                  onChange={(e) => handleBasicChange('nombre', e.target.value)}
                  required
                  className="h-12 text-base"
                />
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Email *</label>
                <Input
                  type="email"
                  placeholder="email@empresa.com"
                  value={formData.email}
                  onChange={(e) => handleBasicChange('email', e.target.value)}
                  required
                  className="h-12 text-base"
                />
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Capítulo *</label>
                <select
                  value={formData.chapter}
                  onChange={(e) => handleBasicChange('chapter', e.target.value)}
                  className="flex h-12 w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  required
                  disabled={loadingChapters}
                >
                  <option value="">
                    {loadingChapters ? 'Cargando capítulos...' : 'Seleccionar capítulo'}
                  </option>
                  {chapters.map((chapter) => (
                    <option key={chapter} value={chapter}>
                      {chapter}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Rol Actual *</label>
                <select
                  value={formData.rol_actual}
                  onChange={(e) => handleBasicChange('rol_actual', e.target.value)}
                  className="flex h-12 w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  required
                  disabled={loadingRoles}
                >
                  <option value="">
                    {loadingRoles ? 'Cargando roles...' : 'Seleccionar rol'}
                  </option>
                  {roles.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Gerente/Superior</label>
                <Input
                  type="text"
                  placeholder="Nombre del superior directo"
                  value={formData.manager}
                  onChange={(e) => handleBasicChange('manager', e.target.value)}
                  className="h-12 text-base"
                />
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Antigüedad (meses)</label>
                <Input
                  type="number"
                  placeholder="Ej: 12"
                  value={formData.antigüedad}
                  onChange={(e) => handleBasicChange('antigüedad', e.target.value)}
                  className="h-12 text-base"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance & Risk */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="border-b bg-slate-50 p-8">
            <CardTitle className="text-blue-600 text-3xl">Desempeño y Retención</CardTitle>
            <CardDescription className="text-base mt-2">Evaluación de rendimiento y riesgo de retención</CardDescription>
          </CardHeader>
          <CardContent className="pt-8 p-8">
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <label className="block text-base font-medium mb-3">Performance Rating</label>
                  <select
                    value={formData.performance_rating}
                    onChange={(e) => handleBasicChange('performance_rating', e.target.value)}
                    className="flex h-12 w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  >
                    <option value="">Seleccionar calificación</option>
                    {PERFORMANCE_RATINGS.map((rating) => (
                      <option key={rating} value={rating}>
                        {rating}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-base font-medium mb-3">Riesgo de Retención</label>
                  <select
                    value={formData.retention_risk}
                    onChange={(e) => handleBasicChange('retention_risk', e.target.value)}
                    className="flex h-12 w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  >
                    <option value="">Seleccionar riesgo</option>
                    {RETENTION_RISKS.map((risk) => (
                      <option key={risk} value={risk}>
                        {risk}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-base font-medium mb-3">Trayectoria</label>
                <Input
                  type="text"
                  placeholder="Ej: Junior > Mid (6m)"
                  value={formData.trayectoria}
                  onChange={(e) => handleBasicChange('trayectoria', e.target.value)}
                  className="h-12 text-base"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Sections */}
        <Tabs defaultValue="skills" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-gray-100">
            <TabsTrigger value="skills">Habilidades</TabsTrigger>
            <TabsTrigger value="dedication">Dedicación</TabsTrigger>
            <TabsTrigger value="ambitions">Ambiciones</TabsTrigger>
          </TabsList>

          <TabsContent value="skills" className="mt-6">
            <SkillsSection skills={formData.habilidades} onChange={handleSkillsChange} />
          </TabsContent>

          <TabsContent value="dedication" className="mt-6">
            <DedicationSection
              dedication={formData.dedicacion}
              onChange={handleDedicationChange}
              projects={projects}
            />
          </TabsContent>

          <TabsContent value="ambitions" className="mt-6">
            <AmbitionsSection ambiciones={formData.ambiciones} onChange={handleAmbitionsChange} />
          </TabsContent>
        </Tabs>

        {/* Submit Button */}
        <div className="flex gap-4 justify-end pt-4">
          <Button type="button" variant="outline" className="px-8">
            Cancelar
          </Button>
          <Button type="submit" disabled={submitting} className="px-8">
            {submitted ? '✓ Empleado Añadido' : submitting ? 'Guardando...' : 'Guardar Empleado'}
          </Button>
        </div>

        {/* Message Display */}
        {message && (
          <div
            className={`p-4 rounded-md ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}
      </form>
    </div>
  );
}
