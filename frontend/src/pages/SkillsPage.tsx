import { useEffect, useState } from "react";
import { SkillCreateForm } from "../components/SkillCreateForm";
import { SkillTable } from "../components/SkillTable";
import { api } from "../api/http";
import type { SkillRead } from "../types/api";

export default function SkillsPage() {
  const [skills, setSkills] = useState<SkillRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await api<SkillRead[]>("/skills");
      setSkills(data);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load skills");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Skills</h2>

        <button
          className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:opacity-50"
          onClick={refresh}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {/* Create form */}
      <SkillCreateForm onCreated={refresh} />

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-900/40 bg-red-950/40 p-3 text-sm text-red-200">
          {error}
        </div>
      )}

      {/* Table */}
      <SkillTable 
        skills={skills} 
        loading={loading} 
        error={error} 
        onRefresh={refresh} 
        />

    </div>
  );
}
