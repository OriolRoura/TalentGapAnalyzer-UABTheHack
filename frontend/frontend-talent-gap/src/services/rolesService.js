import { get } from './index';

/**
 * Obtiene la lista de roles desde la API
 * @returns {Promise<Array<string>>} Lista de títulos de roles
 */
export const getRoles = async () => {
  try {
    const response = await get('/roles/');
    // Extraemos solo los títulos de los roles
    return response.roles.map(role => role.titulo);
  } catch (error) {
    console.error('Error fetching roles:', error);
    // En caso de error, devolvemos un array vacío o roles por defecto
    return [
      'Head of Strategy',
      'Project Manager',
      'Martech Architect',
      'CRM Admin',
      'Data Analyst',
      'Creative Director',
      'Senior Brand/UI Designer',
      'Performance Media Specialist',
      'SEO/SEM Manager',
      'Social Media Strategist',
    ];
  }
};
