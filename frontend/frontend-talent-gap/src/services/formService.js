import { post } from './index';

/**
 * Submit employee profile to HR API
 * @param {Object} employeeData - Employee data matching HREmployeeSubmitForm schema
 * @returns {Promise<Object>} Response with status, message, employee_id, and validation
 */
export async function submitEmployeeForm(employeeData) {
  try {
    const response = await post('hr/employee/submit', employeeData);
    return response;
  } catch (error) {
    console.error('Error submitting employee form:', error);
    throw error;
  }
}

export default { submitEmployeeForm };
