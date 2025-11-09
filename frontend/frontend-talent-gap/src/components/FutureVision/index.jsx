import React from 'react';
import FutureVisionSummary from './FutureVisionSummary';
import { SkillBottleneck } from './bottleneck/SkillBottleneck';

const FutureVision = () => {
  return (
    <div className="container mx-auto p-6 max-w-[1400px]">
      <div className="space-y-6">
        <FutureVisionSummary />
        <SkillBottleneck />
      </div>
    </div>
  );
};

export default FutureVision;