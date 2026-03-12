import { NavLink } from "react-router-dom";
import AppRoutes from "./AppRoutes";

export default function App() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-xl text-sm transition ${
      isActive
        ? "bg-slate-200 text-slate-900"
        : "text-slate-200 hover:bg-slate-800/60"
    }`;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto p-4">
        <header className="flex items-center justify-between mb-4">
          <div className="font-bold text-lg tracking-tight">Job Skill Tracker</div>
          <nav className="flex gap-2">
            <NavLink to="/jobs" className={linkClass}>
              Jobs
            </NavLink>
            <NavLink to="/skills" className={linkClass}>
              Skills
            </NavLink>
          </nav>
        </header>

        {/* Dark container to match your components */}
        <main className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
          <AppRoutes />
        </main>
      </div>
    </div>
  );
}
