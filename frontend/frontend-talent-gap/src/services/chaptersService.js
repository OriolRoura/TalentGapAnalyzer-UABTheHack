import { get } from './index';

/**
 * Obtiene la lista de capítulos/departamentos desde la API
 * @returns {Promise<Array<string>>} Lista de nombres de capítulos
 */
export const getChapters = async () => {
  try {
    const response = await get('company/chapters/');
    // Asumimos que la respuesta tiene una estructura similar: { total, chapters: [...] }
    // Si la estructura es diferente, ajustaremos según la respuesta real
    return response.chapters || response;
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
