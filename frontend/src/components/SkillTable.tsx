import { useMemo, useState } from "react";
import type { SkillRead, SkillUpdate } from "../types";
import { apiDeleteSkill, apiUpdateSkill } from "../api";

type SortKey = keyof Pick<SkillRead, "id" | "name" | "category" | "notes">;

type Props = {
  skills: SkillRead[];
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
};

type RowDraft = {
  name: string;
  category: string;
  notes: string;
};

export function SkillTable({ skills, loading, error, onRefresh }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState<RowDraft | null>(null);

  const [rowBusyId, setRowBusyId] = useState<number | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);

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
    if (nextKey === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(nextKey);
      setSortDir("asc");
    }
  }

  function sortGlyph(key: SortKey) {
    if (key !== sortKey) return "";
    return sortDir === "asc" ? " ▲" : " ▼";
  }

  function beginEdit(skill: SkillRead) {
    setRowError(null);
    setEditingId(skill.id);
    setDraft({
      name: skill.name ?? "",
      category: skill.category ?? "",
      notes: skill.notes ?? "",
    });
  }

  function cancelEdit() {
    setRowError(null);
    setEditingId(null);
    setDraft(null);
  }

  function normalizeUpdate(original: SkillRead, d: RowDraft): SkillUpdate {
    const update: SkillUpdate = {};

    const name = d.name.trim();
    const category = d.category.trim();
    const notes = d.notes.trim();

    if (name !== original.name) update.name = name;
    if ((original.category ?? "") !== category) update.category = category.length ? category : null;
    if ((original.notes ?? "") !== notes) update.notes = notes.length ? notes : null;

    return update;
  }

  async function saveRow(original: SkillRead) {
    if (!draft) return;
    setRowError(null);

    const payload = normalizeUpdate(original, draft);
    if (Object.keys(payload).length === 0) {
      cancelEdit();
      return;
    }

    setRowBusyId(original.id);
    try {
      await apiUpdateSkill(original.id, payload);
      cancelEdit();
      onRefresh();
    } catch (e) {
      setRowError(e instanceof Error ? e.message : String(e));
    } finally {
      setRowBusyId(null);
    }
  }

  async function deleteRow(id: number) {
    setRowError(null);

    const ok = window.confirm("Delete this skill? This cannot be undone.");
    if (!ok) return;

    setRowBusyId(id);
    try {
      await apiDeleteSkill(id);
      if (editingId === id) cancelEdit();
      onRefresh();
    } catch (e) {
      setRowError(e instanceof Error ? e.message : String(e));
    } finally {
      setRowBusyId(null);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-800/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <h2 className="text-lg font-semibold text-slate-100">Skills</h2>
          <p className="text-xs text-slate-400">Click a cell to edit. Save/Cancel applies per row.</p>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading || rowBusyId !== null}
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

      {rowError && (
        <div className="mt-4 rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-sm text-amber-100">
          <span className="font-semibold">Action error:</span> {rowError}
        </div>
      )}

      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-700">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-300">
            <tr>
              <Th onClick={() => toggleSort("id")}>ID{sortGlyph("id")}</Th>
              <Th onClick={() => toggleSort("name")}>Name{sortGlyph("name")}</Th>
              <Th onClick={() => toggleSort("category")}>Category{sortGlyph("category")}</Th>
              <Th onClick={() => toggleSort("notes")}>Notes{sortGlyph("notes")}</Th>
              <th className="px-4 py-3 text-right text-slate-300">Actions</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-700">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                  {loading ? "Loading…" : "No skills found."}
                </td>
              </tr>
            ) : (
              sorted.map((s) => {
                const isEditing = editingId === s.id;
                const isBusy = rowBusyId === s.id;

                return (
                  <tr key={s.id} className="hover:bg-slate-700/20">
                    <td className="px-4 py-3 font-mono text-xs text-slate-300">{s.id}</td>

                    <td className="px-4 py-3">
                      {isEditing ? (
                        <input
                          value={draft?.name ?? ""}
                          onChange={(e) => setDraft((d) => (d ? { ...d, name: e.target.value } : d))}
                          className="w-full rounded-lg border border-slate-600 bg-slate-900/70 px-2 py-1 text-sm text-slate-100 outline-none focus:border-slate-400"
                          autoFocus
                          disabled={isBusy}
                        />
                      ) : (
                        <CellButton onClick={() => beginEdit(s)} disabled={rowBusyId !== null}>
                          {s.name}
                        </CellButton>
                      )}
                    </td>

                    <td className="px-4 py-3">
                      {isEditing ? (
                        <input
                          value={draft?.category ?? ""}
                          onChange={(e) => setDraft((d) => (d ? { ...d, category: e.target.value } : d))}
                          className="w-full rounded-lg border border-slate-600 bg-slate-900/70 px-2 py-1 text-sm text-slate-100 outline-none focus:border-slate-400"
                          disabled={isBusy}
                        />
                      ) : (
                        <CellButton onClick={() => beginEdit(s)} disabled={rowBusyId !== null}>
                          {s.category ?? <span className="text-slate-500">(empty)</span>}
                        </CellButton>
                      )}
                    </td>

                    <td className="px-4 py-3">
                      {isEditing ? (
                        <input
                          value={draft?.notes ?? ""}
                          onChange={(e) => setDraft((d) => (d ? { ...d, notes: e.target.value } : d))}
                          className="w-full rounded-lg border border-slate-600 bg-slate-900/70 px-2 py-1 text-sm text-slate-100 outline-none focus:border-slate-400"
                          disabled={isBusy}
                        />
                      ) : (
                        <CellButton onClick={() => beginEdit(s)} disabled={rowBusyId !== null}>
                          {s.notes ?? <span className="text-slate-500">(empty)</span>}
                        </CellButton>
                      )}
                    </td>

                    <td className="px-4 py-3 text-right">
                      {isEditing ? (
                        <div className="inline-flex items-center gap-2">
                          <button
                            onClick={() => saveRow(s)}
                            disabled={isBusy}
                            className="rounded-lg border border-slate-600 bg-slate-700/40 px-3 py-1.5 text-xs font-medium text-slate-100 hover:bg-slate-700/60 disabled:opacity-50"
                          >
                            {isBusy ? "Saving…" : "Save"}
                          </button>
                          <button
                            onClick={cancelEdit}
                            disabled={isBusy}
                            className="rounded-lg border border-slate-700 bg-transparent px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700/20 disabled:opacity-50"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => deleteRow(s.id)}
                          disabled={rowBusyId !== null}
                          className="rounded-lg border border-red-400/40 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-100 hover:bg-red-500/15 disabled:opacity-50"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-xs text-slate-400">
        Update sends only changed fields via PATCH. Delete asks for confirmation.
      </p>
    </section>
  );
}

function Th({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <th onClick={onClick} className="cursor-pointer select-none px-4 py-3 hover:text-slate-100">
      {children}
    </th>
  );
}

function CellButton({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="w-full text-left text-slate-100 hover:underline disabled:cursor-not-allowed disabled:opacity-60"
      title="Click to edit"
    >
      {children}
    </button>
  );
}
