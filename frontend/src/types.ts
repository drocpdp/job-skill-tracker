export type SkillCreate = {
  name: string;
  category?: string | null;
  notes?: string | null;
};

export type SkillUpdate = {
  name?: string;
  category?: string | null;
  notes?: string | null;
};

export type SkillRead = {
  id: number;
  name: string;
  category: string | null;
  notes: string | null;
};
