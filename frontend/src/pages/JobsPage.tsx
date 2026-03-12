import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/http";
import type { JobRead } from "../types/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const data = await api<JobRead[]>("/jobs");
      setJobs(data);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Jobs</h2>
          <p className="text-xs text-slate-400">
            Select a job to manage linked skills.
          </p>
        </div>

        <button
          className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
          onClick={refresh}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-900/40 bg-red-950/40 p-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <section className="rounded-2xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
          <div className="text-sm font-semibold text-slate-200">Job List</div>
          <div className="text-xs text-slate-400">{jobs.length} jobs</div>
        </div>

        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-900/40 text-slate-300">
              <tr className="text-left">
                <th className="px-4 py-3 font-medium">Company</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium w-44">Actions</th>
              </tr>
            </thead>

            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-t border-slate-700/70">
                  <td className="px-4 py-3 text-slate-100">{j.company}</td>
                  <td className="px-4 py-3 text-slate-100">{j.title}</td>
                  <td className="px-4 py-3">
                    <Link
                      className="inline-flex rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 active:scale-[0.99]"
                      to={`/jobs/${j.id}/skills`}
                    >
                      Manage skills →
                    </Link>
                  </td>
                </tr>
              ))}

              {!loading && jobs.length === 0 && (
                <tr>
                  <td className="px-4 py-4 text-slate-400" colSpan={3}>
                    No jobs yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {loading && (
          <div className="px-4 py-3 border-t border-slate-700 text-sm text-slate-400">
            Loading…
          </div>
        )}
      </section>
    </div>
  );
}
