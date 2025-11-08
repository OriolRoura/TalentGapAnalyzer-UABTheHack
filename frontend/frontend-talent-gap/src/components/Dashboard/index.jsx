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
      <div className="p-4 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={handleCloseDetail}
            className="flex items-center font-semibold mb-6 p-3 px-4 rounded-lg bg-white shadow-md border border-gray-200 hover:bg-gray-100 transition duration-150"
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
      <div className="p-4 bg-gray-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={handleCloseDetail}
            className="flex items-center font-semibold mb-6 p-3 px-4 rounded-lg bg-white shadow-md border border-gray-200 hover:bg-gray-100 transition duration-150"
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
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner loadText="Cargando empleados..."/>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center p-6 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-800 text-lg font-medium">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full p-4">
      <div className="sticky top-0 bg-white z-10 pb-4 border-b border-gray-300">
        <div className="flex justify-between items-center mb-4">
          <h2 className="mb-5 text-black text-2xl font-bold sm:text-3xl sm:tracking-tight text-center w-full">
            Resumen del talento actual
          </h2>
          <div className="absolute top-4 right-4 text-right text-xl font-medium text-gray-700">
            Empleados: <span className="text-indigo-600 font-bold">{filteredEmployees.length}</span>
          </div>
        </div>

        <div className="flex justify-left">
          <input
            type="text"
            value={searchTerm}
            onChange={onEmployeeSearch}
            className="w-full md:w-1/2 border-2 border-gray-300 rounded-lg p-3 pl-4 text-left focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
            placeholder="Busca un empleado por nombre..."
          />
        </div>
      </div>

      <div className="mt-8">
        {filteredEmployees.length === 0 ? (
          <p className="text-center text-gray-500 mt-12 text-lg">
            No se encontraron empleados. Intenta con otra búsqueda.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
            {filteredEmployees.map((emp) => (
              <EmployeeCard
                key={emp.id_empleado}
                employee={emp}
                onSelectEmployee={handleSelectEmployee} // For general card click (optional)
                onSecondaryAction={handleViewMatrix}   // For the "Ver matriz" button
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;