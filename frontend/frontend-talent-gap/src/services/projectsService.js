import { get } from './index';

/**
 * Obtiene la lista de proyectos desde la API
 * @returns {Promise<Array<string>>} Lista de nombres de proyectos
 */
export const getProjects = async () => {
  try {
    const response = await get('company/projects/');
    // Asumimos que la respuesta tiene una estructura similar: { total, projects: [...] }
    // Si la estructura es diferente, ajustaremos según la respuesta real
    return response.projects || response;
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
