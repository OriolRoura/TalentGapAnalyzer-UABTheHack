import { get } from './index';

/**
 * Obtiene la lista de habilidades desde la API
 * @returns {Promise<Array<{id: string, nombre: string, categoria: string}>>} Lista de habilidades
 */
export const getSkills = async () => {
  try {
    const response = await get('skills');
    // Devolvemos el array completo de skills con sus propiedades
    return response.skills.map(skill => ({
      id: skill.id,
      nombre: skill.nombre,
      categoria: skill.categoria,
      descripcion: skill.descripcion || '',
      peso: skill.peso || 1,
      herramientas_asociadas: skill.herramientas_asociadas || []
    }));
  } catch (error) {
    console.error('Error fetching skills:', error);
    // Fallback a skills por defecto
    return [
      { id: 'react', nombre: 'React', categoria: 'Frontend', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'nodejs', nombre: 'Node.js', categoria: 'Backend', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'python', nombre: 'Python', categoria: 'Backend', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'typescript', nombre: 'TypeScript', categoria: 'Frontend', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'docker', nombre: 'Docker', categoria: 'DevOps', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'aws', nombre: 'AWS', categoria: 'Cloud', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'git', nombre: 'Git', categoria: 'Tools', descripcion: '', peso: 1, herramientas_asociadas: [] },
      { id: 'sql', nombre: 'SQL', categoria: 'Database', descripcion: '', peso: 1, herramientas_asociadas: [] }
    ];
  }
};
