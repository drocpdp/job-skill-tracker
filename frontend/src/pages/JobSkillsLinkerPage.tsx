import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/http";
import type { JobRead, JobSkillRead, SkillRead } from "../types/api";

type EditingState = {
  skillId: number;
  draft: string;
  saving: boolean;
};

export default function JobSkillsLinkerPage() {
  const { jobId } = useParams();
  const id = Number(jobId);

  const [job, setJob] = useState<JobRead | null>(null);
  const [allSkills, setAllSkills] = useState<SkillRead[]>([]);
  const [linked, setLinked] = useState<JobSkillRead[]>([]);

  const [qLeft, setQLeft] = useState("");
  const [qRight, setQRight] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [pendingAdd, setPendingAdd] = useState<Set<number>>(new Set());
  const [pendingRemove, setPendingRemove] = useState<Set<number>>(new Set());

  const [editing, setEditing] = useState<EditingState | null>(null);
  const editRef = useRef<HTMLTextAreaElement | null>(null);

  // Notes drawer
  const [notesOpen, setNotesOpen] = useState(false);
  const [notesSkill, setNotesSkill] = useState<SkillRead | null>(null);

  const linkedIds = useMemo(() => new Set(linked.map((x) => x.skill.id)), [linked]);

  const available = useMemo(() => {
    const base = allSkills.filter((s) => !linkedIds.has(s.id));
    const q = qLeft.trim().toLowerCase();
    if (!q) return base;
    return base.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        (s.category ?? "").toLowerCase().includes(q)
    );
  }, [allSkills, linkedIds, qLeft]);

  const linkedFiltered = useMemo(() => {
    const q = qRight.trim().toLowerCase();
    if (!q) return linked;
    return linked.filter(
      (x) =>
        x.skill.name.toLowerCase().includes(q) ||
        (x.skill.category ?? "").toLowerCase().includes(q) ||
        (x.how_used ?? "").toLowerCase().includes(q)
    );
  }, [linked, qRight]);

  async function load() {
    if (!Number.isFinite(id)) return;

    setLoading(true);
    setError(null);

    try {
      const [jobData, skillsData, linkedData] = await Promise.all([
        api<JobRead>(`/jobs/${id}`),
        api<SkillRead[]>(`/skills`),
        api<JobSkillRead[]>(`/jobs/${id}/skills`),
      ]);

      setJob(jobData);
      setAllSkills(skillsData);
      setLinked(linkedData);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load job skills");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (!editing?.skillId) return;
    const el = editRef.current;
    if (!el) return;

    el.focus();

    // Optional: place cursor at end once
    const len = el.value.length;
    el.setSelectionRange(len, len);
  }, [editing?.skillId]);

  function setPending(
    setter: React.Dispatch<React.SetStateAction<Set<number>>>,
    skillId: number,
    on: boolean
  ) {
    setter((prev) => {
      const next = new Set(prev);
      if (on) next.add(skillId);
      else next.delete(skillId);
      return next;
    });
  }

  function openNotes(skill: SkillRead) {
    setNotesSkill(skill);
    setNotesOpen(true);
  }

  function closeNotes() {
    setNotesOpen(false);
    setNotesSkill(null);
  }

  async function addSkill(skill: SkillRead) {
    if (!job) return;
    if (linkedIds.has(skill.id)) return;

    // optimistic move
    const optimistic: JobSkillRead = { skill, how_used: null };
    setLinked((prev) => {
      const next = [...prev, optimistic];
      next.sort((a, b) => a.skill.name.localeCompare(b.skill.name));
      return next;
    });

    setPending(setPendingAdd, skill.id, true);

    try {
      await api<JobSkillRead>(`/jobs/${job.id}/skills`, {
        method: "POST",
        body: JSON.stringify({ skill_id: skill.id, how_used: null }),
      });

      // refresh linked list to ensure server is the source of truth
      const linkedData = await api<JobSkillRead[]>(`/jobs/${job.id}/skills`);
      setLinked(linkedData);
    } catch (e: any) {
      // revert
      setLinked((prev) => prev.filter((x) => x.skill.id !== skill.id));
      // treat 409 as safe (already attached)
      const msg = e?.message ?? "";
      if (!msg.includes("409")) setError(msg || "Failed to attach skill");
    } finally {
      setPending(setPendingAdd, skill.id, false);
    }
  }

  async function removeSkill(skillId: number) {
    if (!job) return;

    const existing = linked.find((x) => x.skill.id === skillId);
    if (!existing) return;

    // optimistic remove
    setLinked((prev) => prev.filter((x) => x.skill.id !== skillId));
    setPending(setPendingRemove, skillId, true);

    // if we were editing this row, cancel edit
    if (editing?.skillId === skillId) setEditing(null);

    try {
      await api<void>(`/jobs/${job.id}/skills/${skillId}`, { method: "DELETE" });
    } catch (e: any) {
      // treat 404 as safe (already removed)
      const msg = e?.message ?? "";
      if (!msg.includes("404")) {
        // revert
        setLinked((prev) => {
          const next = [...prev, existing];
          next.sort((a, b) => a.skill.name.localeCompare(b.skill.name));
          return next;
        });
        setError(msg || "Failed to detach skill");
      }
    } finally {
      setPending(setPendingRemove, skillId, false);
    }
  }

  function startEdit(skillId: number) {
    const row = linked.find((x) => x.skill.id === skillId);
    if (!row) return;
    setEditing({
      skillId,
      draft: row.how_used ?? "",
      saving: false,
    });
  }

  function cancelEdit() {
    setEditing(null);
  }

  async function saveEdit() {
    if (!job || !editing) return;

    const skillId = editing.skillId;
    const draft = editing.draft;

    setEditing((prev) => (prev ? { ...prev, saving: true } : prev));

    // optimistic update
    const prevValue = linked.find((x) => x.skill.id === skillId)?.how_used ?? null;
    setLinked((prev) =>
      prev.map((x) =>
        x.skill.id === skillId ? { ...x, how_used: draft.trim() || null } : x
      )
    );

    try {
      await api<JobSkillRead>(`/jobs/${job.id}/skills/${skillId}`, {
        method: "PATCH",
        body: JSON.stringify({ how_used: draft }),
      });
      setEditing(null);
    } catch (e: any) {
      // revert
      setLinked((prev) =>
        prev.map((x) => (x.skill.id === skillId ? { ...x, how_used: prevValue } : x))
      );
      setError(e?.message ?? "Failed to update how_used");
      setEditing((prev) => (prev ? { ...prev, saving: false } : prev));
    }
  }

  function onEditKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Escape") {
      e.preventDefault();
      cancelEdit();
      return;
    }
    // Enter to save (but allow Shift+Enter new line)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      saveEdit();
    }
  }

  if (!Number.isFinite(id)) {
    return (
      <div className="rounded-xl border border-red-900/40 bg-red-950/40 p-3 text-sm text-red-200">
        Invalid job id.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs text-slate-400">
            <Link className="underline" to="/jobs">
              Jobs
            </Link>{" "}
            / Manage skills
          </div>

          <h2 className="text-lg font-semibold text-slate-100">
            {job ? `${job.company} — ${job.title}` : "Loading job…"}
          </h2>

          <div className="text-xs text-slate-400 mt-1">{linked.length} linked skills</div>
        </div>

        <button
          className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
          onClick={load}
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

      {/* Dual Pane */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Available */}
        <section className="rounded-2xl border border-slate-700 bg-slate-800/60 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-100">Available Skills</h3>
            <span className="text-xs text-slate-300">{available.length}</span>
          </div>

          <input
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
            placeholder="Search available…"
            value={qLeft}
            onChange={(e) => setQLeft(e.target.value)}
          />

          <div className="space-y-2 max-h-[60vh] overflow-auto pr-1">
            {available.map((s) => {
              const isPending = pendingAdd.has(s.id);
              return (
                <div
                  key={s.id}
                  className="flex items-center justify-between gap-3 rounded-xl border border-slate-700 bg-slate-900/40 px-3 py-2"
                >
                  <div className="min-w-0">
                    <div className="font-medium text-slate-100 truncate">{s.name}</div>
                    <div className="text-xs text-slate-400 truncate">{s.category ?? "—"}</div>
                    {!!s.notes?.trim() && (
                      <div className="mt-1 text-[11px] text-slate-400 truncate">
                        {s.notes.trim()}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      className="rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-xs text-slate-200 hover:bg-slate-900/80 active:scale-[0.99]"
                      onClick={() => openNotes(s)}
                      title="View notes"
                    >
                      Notes
                    </button>

                    <button
                      className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
                      onClick={() => addSkill(s)}
                      disabled={isPending || !job}
                      title={!job ? "Job not loaded yet" : "Attach skill to this job"}
                    >
                      {isPending ? "Adding…" : "Add"}
                    </button>
                  </div>
                </div>
              );
            })}

            {available.length === 0 && (
              <div className="text-sm text-slate-400">No available skills.</div>
            )}
          </div>
        </section>

        {/* Linked */}
        <section className="rounded-2xl border border-slate-700 bg-slate-800/60 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-100">Skills in this Job</h3>
            <span className="text-xs text-slate-300">{linkedFiltered.length}</span>
          </div>

          <input
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
            placeholder="Search linked… (name, category, how used)"
            value={qRight}
            onChange={(e) => setQRight(e.target.value)}
          />

          <div className="space-y-2 max-h-[60vh] overflow-auto pr-1">
            {linkedFiltered.map((x) => {
              const skillId = x.skill.id;
              const isRemoving = pendingRemove.has(skillId);
              const isEditing = editing?.skillId === skillId;

              return (
                <div
                  key={skillId}
                  className="rounded-xl border border-slate-700 bg-slate-900/40 px-3 py-2"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-medium text-slate-100 truncate">{x.skill.name}</div>
                      <div className="text-xs text-slate-400 truncate">
                        {x.skill.category ?? "—"}
                      </div>
                      {!!x.skill.notes?.trim() && (
                        <div className="mt-1 text-[11px] text-slate-400">
                          {x.skill.notes.trim()}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        className="rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-xs text-slate-200 hover:bg-slate-900/80 active:scale-[0.99]"
                        onClick={() => openNotes(x.skill)}
                        title="View notes"
                      >
                        Notes
                      </button>

                      <button
                        className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
                        onClick={() => removeSkill(skillId)}
                        disabled={isRemoving || !job}
                        title="Detach skill from this job"
                      >
                        {isRemoving ? "Removing…" : "Remove"}
                      </button>
                    </div>
                  </div>

                  <div className="mt-3">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-semibold text-slate-300">How used</div>

                      {!isEditing ? (
                        <button
                          className="text-xs text-slate-300 hover:text-slate-100 underline"
                          onClick={() => startEdit(skillId)}
                          disabled={!job}
                        >
                          Edit
                        </button>
                      ) : (
                        <div className="flex items-center gap-3">
                          <button
                            className="text-xs text-slate-300 hover:text-slate-100 underline disabled:opacity-50"
                            onClick={cancelEdit}
                            disabled={editing?.saving}
                          >
                            Cancel
                          </button>
                          <button
                            className="text-xs text-slate-300 hover:text-slate-100 underline disabled:opacity-50"
                            onClick={saveEdit}
                            disabled={editing?.saving}
                          >
                            {editing?.saving ? "Saving…" : "Save"}
                          </button>
                        </div>
                      )}
                    </div>

                    {!isEditing ? (
                      <div
                        className="mt-2 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100"
                        role="button"
                        tabIndex={0}
                        onClick={() => startEdit(skillId)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") startEdit(skillId);
                        }}
                        title="Click to edit"
                      >
                        {x.how_used?.trim() ? (
                          x.how_used
                        ) : (
                          <span className="text-slate-500">
                            Click “Edit” to add how you used this skill…
                          </span>
                        )}
                      </div>
                    ) : (
                      <textarea
                        ref={editRef}
                        value={editing.draft}
                        onChange={(e) =>
                          setEditing((prev) => (prev ? { ...prev, draft: e.target.value } : prev))
                        }
                        onKeyDown={onEditKeyDown}
                        placeholder="Describe how you used this skill in this job… (Enter = save, Shift+Enter = new line, Esc = cancel)"
                        className="mt-2 min-h-24 w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
                        disabled={editing.saving}
                      />
                    )}

                    {isEditing && (
                      <div className="mt-2 text-xs text-slate-400">
                        Tip: Press <span className="font-mono">Enter</span> to save,{" "}
                        <span className="font-mono">Esc</span> to cancel.
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {linkedFiltered.length === 0 && (
              <div className="text-sm text-slate-400">No linked skills yet.</div>
            )}
          </div>
        </section>
      </div>

      {/* Notes Drawer */}
      {notesOpen && notesSkill && (
        <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Skill notes">
          <div className="absolute inset-0 bg-black/60" onClick={closeNotes} />

          <div className="absolute right-0 top-0 h-full w-full max-w-xl border-l border-slate-800 bg-slate-950 text-slate-100 shadow-2xl">
            <div className="flex items-start justify-between gap-3 border-b border-slate-800 p-4">
              <div className="min-w-0">
                <div className="text-xs text-slate-400">Skill</div>
                <div className="text-lg font-semibold truncate">{notesSkill.name}</div>
                <div className="mt-1 text-xs text-slate-400 truncate">
                  {notesSkill.category ?? "—"}
                </div>
              </div>

              <button
                className="rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900/80 active:scale-[0.99]"
                onClick={closeNotes}
              >
                Close
              </button>
            </div>

            <div className="p-4 space-y-3">
              <div className="text-sm font-semibold text-slate-200">Notes</div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-100 whitespace-pre-wrap">
                {notesSkill.notes?.trim() ? (
                  notesSkill.notes
                ) : (
                  <span className="text-slate-400">No notes yet for this skill.</span>
                )}
              </div>

              <div className="text-xs text-slate-400">
                Recruiter view: use notes to capture meaning, scope, and examples for this skill.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
