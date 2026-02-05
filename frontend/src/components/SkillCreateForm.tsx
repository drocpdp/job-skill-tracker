import { useMemo, useState } from "react";
import { apiCreateSkill } from "../api";
import type { SkillCreate, SkillRead } from "../types";

type Props = {
  onCreated?: (created: SkillRead) => void;
};

type ApiResult =
  | { ok: true; data: unknown }
  | { ok: false; error: string };

export function SkillCreateForm({ onCreated }: Props) {
  const [form, setForm] = useState<SkillCreate>({
    name: "",
    category: "",
    description: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<ApiResult | null>(null);

  const canSubmit = useMemo(
    () => form.name.trim().length > 0 && !submitting,
    [form.name, submitting]
  );

  function setField<K extends keyof SkillCreate>(key: K, value: SkillCreate[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function normalizePayload(input: SkillCreate): SkillCreate {
    const name = input.name.trim();
    const category = (input.category ?? "").trim();
    const description = (input.description ?? "").trim();

    return {
      name,
      category: category.length ? category : null,
      description: description.length ? description : null,
    };
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setResult(null);

    try {
      const payload = normalizePayload(form);
      const created = await apiCreateSkill(payload);
      setResult({ ok: true, data: created });
      onCreated?.(created);

      // reset fields
      setForm({ name: "", category: "", description: "" });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setResult({ ok: false, error: msg });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-800/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-100">Create Skill</h2>
        <span className="text-xs text-slate-300">POST /skills</span>
      </div>

      <form onSubmit={onSubmit} className="mt-4 space-y-4">
        <div className="space-y-1">
          <label className="text-sm text-slate-200">
            Name <span className="text-slate-400">*</span>
          </label>
          <input
            value={form.name}
            onChange={(e) => setField("name", e.target.value)}
            placeholder="e.g. Playwright"
            required
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm text-slate-200">Category</label>
          <input
            value={form.category ?? ""}
            onChange={(e) => setField("category", e.target.value)}
            placeholder="e.g. Test Automation"
            className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm text-slate-200">Description</label>
          <textarea
            value={form.description ?? ""}
            onChange={(e) => setField("description", e.target.value)}
            placeholder="Optional notes…"
            className="min-h-24 w-full rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-slate-500"
          />
          <p className="text-xs text-slate-400">
            Empty optional fields are submitted as <span className="font-mono">null</span>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={!canSubmit}
            className="rounded-xl border border-slate-600 bg-slate-700/40 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.99]"
          >
            {submitting ? "Submitting…" : "Create"}
          </button>

          <span className="text-xs text-slate-400">
            Tip: keep categories consistent (e.g. “Test Automation”, “Backend”, “CI/CD”).
          </span>
        </div>
      </form>

      <div className="mt-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200">Response</h3>
          <span className="text-xs text-slate-400">raw JSON</span>
        </div>

        <pre className="mt-2 max-h-72 overflow-auto rounded-xl border border-slate-700 bg-slate-900/70 p-3 text-xs leading-relaxed text-slate-100">
          {result === null
            ? "Submit a skill to see the response here."
            : result.ok
              ? JSON.stringify(result.data, null, 2)
              : result.error}
        </pre>
      </div>
    </section>
  );
}
