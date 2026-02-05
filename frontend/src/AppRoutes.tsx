import { Routes, Route, Navigate } from "react-router-dom";
import JobsPage from "./pages/JobsPage";
import SkillsPage from "./pages/SkillsPage";
import JobSkillsLinkerPage from "./pages/JobSkillsLinkerPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/jobs" replace />} />
      <Route path="/jobs" element={<JobsPage />} />
      <Route path="/skills" element={<SkillsPage />} />
      <Route path="/jobs/:jobId/skills" element={<JobSkillsLinkerPage />} />
      <Route path="*" element={<Navigate to="/jobs" replace />} />
    </Routes>
  );
}
