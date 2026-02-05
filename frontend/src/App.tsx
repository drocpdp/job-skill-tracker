import { useEffect, useState } from "react";
import { apiGetSkills } from "./api";
import type { SkillRead } from "./types";
import { SkillCreateForm } from "./components/SkillCreateForm";
import { SkillTable } from "./components/SkillTable";

export default function App() {
  const [skills, setSkills] = useState<SkillRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGetSkills();
      setSkills(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

return (
  <div className="min-h-screen bg-slate-900 text-slate-100">
    <div className="mx-auto max-w-5xl p-6 space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-100">
          Job Skill Tracker — Admin
        </h1>
        <p className="text-sm text-slate-300">
          Create skills, inspect responses, and sort the list. (Easy to add auth later.)
        </p>
      </header>

      <div className="grid gap-6">
        <SkillCreateForm onCreated={() => refresh()} />
        <SkillTable skills={skills} loading={loading} error={error} onRefresh={refresh} />
      </div>
    </div>
  </div>
);

}
