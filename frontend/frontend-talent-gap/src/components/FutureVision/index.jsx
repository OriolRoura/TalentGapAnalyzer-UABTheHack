import React from 'react';
import { FutureVisionForm } from './FutureVisionForm';
import { SkillBottleneck } from './SkillBottleneck';

const FutureVision = () => {
  return (
    <div className="container mx-auto p-6 max-w-[1400px]">
      <div className="space-y-6">
        <FutureVisionForm />
        <SkillBottleneck />
      </div>
    </div>
  );
};

export default FutureVision;