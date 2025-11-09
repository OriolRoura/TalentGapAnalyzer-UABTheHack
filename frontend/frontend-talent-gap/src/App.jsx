import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Forms from "./components/Forms";
import FutureVision from "./components/FutureVision";
import FutureVisionSummary from './components/FutureVision/FutureVisionSummary';

import './App.css'

function App() {

    return (
    <>
      <Routes>
        <Route path="/" element={<Forms />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/forms" element={<Forms />} />
        <Route path="/future" element={<FutureVision />} />
        <Route path="/vision-summary" element={<FutureVisionSummary />} />
        <Route path="*" element={<Forms />} />
      </Routes>
    </>
  );
}

export default App
