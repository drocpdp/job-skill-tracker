import { useMemo, useState } from "react";
import type { SkillRead } from "../types";

type SortKey = keyof Pick<SkillRead, "id" | "name" | "category" | "description">;

type Props = {
  skills: SkillRead[];
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
};

export function SkillTable({ skills, loading, error, onRefresh }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = useMemo(() => {
    const copy = [...skills];

    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];

      if (typeof av === "number" && typeof bv === "number") {
        return sortDir === "asc" ? av - bv : bv - av;
      }

      const as = (av ?? "").toString().toLowerCase();
      const bs = (bv ?? "").toString().toLowerCase();
      if (as < bs) return sortDir === "asc" ? -1 : 1;
      if (as > bs) return sortDir === "asc" ? 1 : -1;
      return 0;
    });

    return copy;
  }, [skills, sortKey, sortDir]);

  function toggleSort(nextKey: SortKey) {
    if (nextKey === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(nextKey);
      setSortDir("asc");
    }
  }

  function sortGlyph(key: SortKey) {
    if (key !== sortKey) return "";
    return sortDir === "asc" ? " ▲" : " ▼";
  }

  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-800/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <h2 className="text-lg font-semibold text-slate-100">Skills</h2>
          <p className="text-xs text-slate-400">Click headers to sort</p>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
        >
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-100">
          <span className="font-semibold">Load error:</span> {error}
        </div>
      )}

      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-700">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-300">
            <tr>
              <Th onClick={() => toggleSort("id")}>ID{sortGlyph("id")}</Th>
              <Th onClick={() => toggleSort("name")}>Name{sortGlyph("name")}</Th>
              <Th onClick={() => toggleSort("category")}>
                Category{sortGlyph("category")}
              </Th>
              <Th onClick={() => toggleSort("description")}>
                Description{sortGlyph("description")}
              </Th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-700">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-400">
                  {loading ? "Loading…" : "No skills found."}
                </td>
              </tr>
            ) : (
              sorted.map((s) => (
                <tr key={s.id} className="hover:bg-slate-700/20">
                  <td className="px-4 py-3 font-mono text-xs text-slate-300">
                    {s.id}
                  </td>
                  <td className="px-4 py-3 text-slate-100">{s.name}</td>
                  <td className="px-4 py-3 text-slate-200">{s.category ?? ""}</td>
                  <td className="px-4 py-3 text-slate-200">
                    {s.description ?? ""}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Th({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <th
      onClick={onClick}
      className="cursor-pointer select-none px-4 py-3 hover:text-slate-100"
    >
      {children}
    </th>
  );
}
