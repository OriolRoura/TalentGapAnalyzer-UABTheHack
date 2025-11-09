import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Forms from "./components/Forms";
import FutureVision from "./components/FutureVision";
import FutureVisionSummary from './components/FutureVision/FutureVisionSummary';
import GapMatrix from "./components/GapMatrix";
import Home from './components/Home';
import './App.css'

function App() {

    return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/forms" element={<Forms />} />
        <Route path="/matrix" element={<GapMatrix />} />
        <Route path="/future" element={<FutureVision />} />
        <Route path="/vision-summary" element={<FutureVisionSummary />} />
        <Route path="*" element={<Forms />} />
      </Routes>
    </>
  );
}

export default App