export interface ClassOut {
  id: string;
  name: string;
  display_order: number;
}

export interface SubjectOut {
  id: string;
  class_id: string;
  name: string;
  display_order: number;
}

export interface ChapterOut {
  id: string;
  subject_id: string;
  title: string;
  display_order: number;
}

export type AccessType = "FREE" | "PAID";
export type CourseStatus = "DRAFT" | "PUBLISHED";

export interface CourseOut {
  id: string;
  class_id: string;
  subject_id: string;
  teacher_id: string;
  title: string;
  description: string;
  access_type: AccessType;
  status: CourseStatus;
  created_at: string;
  updated_at: string;
}

export interface CourseSectionOut {
  id: string;
  course_id: string;
  title: string;
  display_order: number;
}

export type LessonContentType = "TEXT" | "VIDEO" | "PDF";

export interface LessonOut {
  id: string;
  course_section_id: string;
  chapter_id: string | null;
  title: string;
  description: string;
  content: string;
  content_type: LessonContentType;
  display_order: number;
  created_at: string;
}

export type MaterialType = "PDF" | "DOCUMENT" | "PRESENTATION" | "IMAGE" | "OTHER";

export interface LessonMaterialOut {
  id: string;
  lesson_id: string;
  material_type: MaterialType;
  file_name: string;
  mime_type: string;
  file_size: number;
  created_at: string;
}

export type VideoProvider = "YOUTUBE" | "VIMEO" | "URL";

export interface VideoOut {
  id: string;
  lesson_id: string;
  provider: VideoProvider;
  provider_ref: string;
  title: string;
}
