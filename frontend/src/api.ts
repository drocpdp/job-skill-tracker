import type { SkillCreate, SkillRead, SkillUpdate } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

function buildUrl(path: string): string {
  return `${API_BASE_URL.replace(/\/$/, "")}${path.startsWith("/") ? "" : "/"}${path}`;
}

export async function apiGetSkills(): Promise<SkillRead[]> {
  const res = await fetch(buildUrl("/skills"));
  const text = await res.text();
  if (!res.ok) throw new Error(`GET /skills failed (${res.status}): ${text}`);
  return JSON.parse(text) as SkillRead[];
}

export async function apiCreateSkill(payload: SkillCreate): Promise<SkillRead> {
  const res = await fetch(buildUrl("/skills"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`POST /skills failed (${res.status}): ${text}`);
  return JSON.parse(text) as SkillRead;
}

export async function apiUpdateSkill(id: number, payload: SkillUpdate): Promise<SkillRead> {
  const res = await fetch(buildUrl(`/skills/${id}`), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  if (!res.ok) throw new Error(`PATCH /skills/${id} failed (${res.status}): ${text}`);
  return JSON.parse(text) as SkillRead;
}

export async function apiDeleteSkill(id: number): Promise<void> {
  const res = await fetch(buildUrl(`/skills/${id}`), { method: "DELETE" });
  const text = await res.text();
  if (!res.ok) throw new Error(`DELETE /skills/${id} failed (${res.status}): ${text}`);
}