import type { CourseStatus } from "./curriculum";

export interface AnswerOut {
  id: string;
  question_id: string;
  teacher_id: string;
  teacher_name: string;
  body: string;
  created_at: string;
}

export interface QuestionOut {
  id: string;
  lesson_id: string;
  student_id: string;
  student_name: string;
  body: string;
  created_at: string;
  answer: AnswerOut | null;
}

export interface QuestionBrowseOut extends QuestionOut {
  lesson_title: string;
  course_id: string;
  course_title: string;
  course_status: CourseStatus;
  class_id: string;
  class_name: string;
  subject_id: string;
  subject_name: string;
}

export interface LiveClassOut {
  id: string;
  class_id: string;
  class_name: string;
  subject_id: string;
  subject_name: string;
  teacher_id: string;
  teacher_name: string;
  title: string;
  description: string;
  scheduled_at: string;
  meeting_url: string;
  created_at: string;
}
