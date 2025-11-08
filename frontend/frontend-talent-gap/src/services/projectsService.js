import { get } from './index';

/**
 * Obtiene la lista de proyectos desde la API
 * @returns {Promise<Array<string>>} Lista de nombres de proyectos
 */
export const getProjects = async () => {
  try {
    const response = await get('/company/projects');
    // La respuesta puede contener objetos, extraemos solo los nombres
    if (Array.isArray(response.projects)) {
      // Si los projects son objetos, extraemos el campo 'name' o 'nombre'
      if (typeof response.projects[0] === 'object') {
        return response.projects.map(project => project.name || project.nombre);
      }
      return response.projects;
    }
    if (Array.isArray(response)) {
      if (typeof response[0] === 'object') {
        return response.map(project => project.name || project.nombre);
      }
      return response;
    }
    return response;
  } catch (error) {
    console.error('Error fetching projects:', error);
    // Fallback a proyectos por defecto (basados en talento_actual.csv)
    return [
      'Royal',
      'Arquimbau',
      'Quether GTM',
      'Internal Ops',
      'I+D',
      'Events'
    ];
  }
};
