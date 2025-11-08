import { get } from './index';

/**
 * Obtiene la lista de capítulos/departamentos desde la API
 * @returns {Promise<Array<string>>} Lista de nombres de capítulos
 */
export const getChapters = async () => {
  try {
    const response = await get('/company/chapters');
    // La respuesta contiene objetos con {name, description, employee_count, etc}
    // Extraemos solo los nombres
    if (Array.isArray(response.chapters)) {
      return response.chapters.map(chapter => chapter.name);
    }
    if (Array.isArray(response)) {
      return response.map(chapter => chapter.name);
    }
    return response;
  } catch (error) {
    console.error('Error fetching chapters:', error);
    // Fallback a capítulos por defecto
    return [
      'Marketing',
      'Technology',
      'Sales',
      'Human Resources',
      'Finance',
      'Operations',
      'Customer Success',
      'Product'
    ];
  }
};
