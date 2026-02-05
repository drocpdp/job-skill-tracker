export type SkillCreate = {
  name: string;
  category?: string | null;
  description?: string | null;
};

export type SkillRead = {
  id: number;
  name: string;
  category?: string | null;
  description?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};
