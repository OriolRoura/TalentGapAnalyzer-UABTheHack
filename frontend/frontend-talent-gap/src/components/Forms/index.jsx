import React from 'react';
import { EmployeeForm } from './EmployeeForm';
import OrganizationHeader from '../OrganizationHeader';
import './forms.css';

const Forms = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <OrganizationHeader />
      <div className="forms-container">
        <EmployeeForm />
      </div>
    </div>
  );
};

export default Forms;
