export interface GroupMember {
  id: string;
  full_name: string;
  email: string;
}

export interface TaskSubmission {
  id: string;
  student_id: string;
  student_name: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface GroupTask {
  id: string;
  title: string;
  description: string;
  due_date: string | null;
  created_at: string;
  submission_count: number;
  my_submission: TaskSubmission | null;
}

export interface Group {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  member_count: number;
  task_count: number;
  created_at: string;
}

export interface GroupDetail {
  id: string;
  name: string;
  description: string;
  teacher_id: string;
  teacher_name: string;
  members: GroupMember[];
  tasks: GroupTask[];
  created_at: string;
}
