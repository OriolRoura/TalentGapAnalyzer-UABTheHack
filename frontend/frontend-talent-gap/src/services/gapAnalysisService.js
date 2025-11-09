import { get } from './index';

/**
 * Get gap matrix for all employees against all roles
 * @param {Object} params - Query parameters
 * @param {string} params.chapter - Optional: Filter by chapter
 * @param {string} params.role - Optional: Filter by current role
 * @param {string} params.custom_weights - Optional: Custom algorithm weights as JSON string
 * @returns {Promise} Gap matrices for all employees
 */
export const getAllEmployeesGapMatrix = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  if (params.chapter) queryParams.append('chapter', params.chapter);
  if (params.role) queryParams.append('role', params.role);
  if (params.custom_weights) queryParams.append('custom_weights', params.custom_weights);
  
  const queryString = queryParams.toString();
  const endpoint = queryString 
    ? `employees/gap-matrix/all?${queryString}` 
    : 'employees/gap-matrix/all';
  
  return get(endpoint);
};

/**
 * Get gap matrix for a specific employee
 * @param {number|string} employeeId - Employee ID
 * @param {Object} params - Query parameters
 * @param {string} params.custom_weights - Optional: Custom algorithm weights as JSON string
 * @returns {Promise} Gap matrix for the employee
 */
export const getEmployeeGapMatrix = async (employeeId, params = {}) => {
  const queryParams = new URLSearchParams();
  
  if (params.custom_weights) queryParams.append('custom_weights', params.custom_weights);
  
  const queryString = queryParams.toString();
  const endpoint = queryString 
    ? `employees/${employeeId}/gap-matrix?${queryString}` 
    : `employees/${employeeId}/gap-matrix`;
  
  return get(endpoint);
};
