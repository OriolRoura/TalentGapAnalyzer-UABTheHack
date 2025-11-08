import { post, get } from '../../services';
import { useEffect, useState } from 'react';

const FutureVision = () => {
  const [employees, setEmployees] = useState();

  const fetchEmployees = async () => {
    const data = get("employees/")
    if (data) setEmployees(data);
  }

  useEffect(() => {
    console.log(employees);
  }, [employees])



  return (
    <div>
      <button
        onClick={fetchEmployees}
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Llista empleats
      </button>
    </div>
  )
}

export default FutureVision;