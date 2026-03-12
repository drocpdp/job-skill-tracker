export type SkillRead = {
  id: number;
  name: string;
  category: string | null;
  notes: string | null;
};

export type JobRead = {
  id: number;
  company: string;
  title: string;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  notes?: string | null;
};

export type JobSkillRead = {
  skill: SkillRead;
  how_used: string | null;
};
