import { useState, useEffect } from 'react';
import LoadingSpinner from '../LoadingSpinner';
import EmployeeCard from '../EmployeeCard';
import EmployeeDetailCard from '../EmployeeDetailCard';
import EmployeeAnalysis from '../EmployeeAnalysis';
import { get } from '../../services'
import { API_EMPLOYEES } from "../../utils/constants";

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [matrixEmployee, setMatrixEmployee] = useState(null);

  useEffect(() => {
    const fetchEmployees = async () => {
      setIsLoading(true);
      try {
        const data = await get(API_EMPLOYEES);
        if (data && data.employees) {
          setEmployees(data.employees);
          setFilteredEmployees(data.employees);
        }
      } catch (err) {
        setError('Error al cargar los empleados');
        console.error('Error fetching employees:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  const handleSelectEmployee = (employee) => {
    setMatrixEmployee(null); // Ensure matrix view is closed
    setSelectedEmployee(employee);
  };

  const handleViewMatrix = (employee) => {
    setSelectedEmployee(null); // Ensure detail view is closed
    setMatrixEmployee(employee); // Set the employee to display the matrix for
  };

  const handleCloseDetail = () => {
    setSelectedEmployee(null);
    setMatrixEmployee(null);
  };

  const onEmployeeSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearchTerm(value);

    if (value.trim() === '') {
      setFilteredEmployees(employees);
      return;
    }

    const filtered = employees.filter((emp) => {
      const fullName = (emp.nombre || '').toString().toLowerCase();
      return fullName.includes(value);
    });

    setFilteredEmployees(filtered);
  };

  if (matrixEmployee) {
    return (
      <div class="p-4 bg-gray-50 min-h-screen">
        <div class="max-w-7xl mx-auto">
          <button
            onClick={handleCloseDetail}
            class="flex items-center font-semibold mb-6 p-3 px-4 rounded-lg bg-white shadow-md border border-gray-200 hover:bg-gray-100 transition duration-150"
          >
            Volver al listado
          </button>
          <EmployeeAnalysis data={matrixEmployee} />
        </div>
      </div>
    );
  }

  if (selectedEmployee) {
    return (
      <div class="p-4 bg-gray-50 min-h-screen">
        <div class="max-w-4xl mx-auto">
          <button
            onClick={handleCloseDetail}
            class="flex items-center font-semibold mb-6 p-3 px-4 rounded-lg bg-white shadow-md border border-gray-200 hover:bg-gray-100 transition duration-150"
          >
            Volver al listado
          </button>
          <EmployeeDetailCard employee={selectedEmployee} />
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div class="flex justify-center items-center min-h-screen">
        <LoadingSpinner loadText="Cargando empleados..."/>
      </div>
    );
  }

  if (error) {
    return (
      <div class="flex justify-center items-center min-h-screen">
        <div class="text-center p-6 bg-red-50 rounded-lg border border-red-200">
          <p class="text-red-800 text-lg font-medium">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            class="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm">
          <div className="sticky top-0 bg-white z-10 p-6 border-b border-gray-200 rounded-t-lg">
            <div className="relative flex flex-col sm:flex-row justify-between items-center gap-4 mb-6">
              <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                Resumen del talento actual
              </h2>
              <div className="text-right text-lg font-medium text-gray-700">
                Empleados: <span className="text-indigo-600 font-bold">{filteredEmployees.length}</span>
              </div>
            </div>

            <div className="w-full max-w-2xl">
              <input
                type="text"
                value={searchTerm}
                onChange={onEmployeeSearch}
                className="w-full border-2 border-gray-300 rounded-lg p-3 pl-4 text-left focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
                placeholder="Busca un empleado por nombre..."
              />
            </div>
          </div>

          <div className="p-6">
            {filteredEmployees.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  No se encontraron empleados. Intenta con otra búsqueda.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-4 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredEmployees.map((emp) => (
                  <EmployeeCard
                    key={emp.id_empleado}
                    employee={emp}
                    onSelectEmployee={handleSelectEmployee}
                    onSecondaryAction={handleViewMatrix}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;