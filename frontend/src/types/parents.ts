export interface ChildPracticeAttempt {
  id: string;
  practice_set_title: string;
  subject_name: string;
  class_name: string;
  score: number;
  total: number;
  created_at: string;
}

export interface ChildTask {
  id: string;
  title: string;
  description: string;
  due_date: string | null;
  group_name: string;
  teacher_name: string;
  created_at: string;
}

export interface ChildProgress {
  id: string;
  full_name: string;
  email: string;
  class_name: string | null;
  tests_taken: number;
  average_score_pct: number | null;
  last_activity_at: string | null;
  recent_attempts: ChildPracticeAttempt[];
  assigned_tasks: ChildTask[];
}
