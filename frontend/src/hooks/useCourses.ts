import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type {
  AccessType,
  CourseOut,
  CourseSectionOut,
  CourseStatus,
  LessonContentType,
  LessonOut,
} from "../types/curriculum";

interface CourseListParams {
  classId?: string;
  subjectId?: string;
  mine?: boolean;
}

export function useCourses(params: CourseListParams = {}) {
  return useQuery({
    queryKey: ["courses", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<CourseOut[]>>("/courses", {
        params: {
          class_id: params.classId,
          subject_id: params.subjectId,
          mine: params.mine,
          page_size: 100,
        },
      });
      return data.data;
    },
  });
}

export function useCourse(courseId: string | undefined) {
  return useQuery({
    queryKey: ["course", courseId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<CourseOut>>(`/courses/${courseId}`);
      return data.data;
    },
    enabled: Boolean(courseId),
  });
}

export function useCourseSections(courseId: string | undefined) {
  return useQuery({
    queryKey: ["course-sections", courseId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<CourseSectionOut[]>>(`/courses/${courseId}/sections`);
      return data.data;
    },
    enabled: Boolean(courseId),
  });
}

export function useSectionLessons(sectionId: string | undefined) {
  return useQuery({
    queryKey: ["section-lessons", sectionId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<LessonOut[]>>(`/sections/${sectionId}/lessons`);
      return data.data;
    },
    enabled: Boolean(sectionId),
  });
}

interface CreateCoursePayload {
  class_id: string;
  subject_id: string;
  title: string;
  description?: string;
  access_type?: AccessType;
}

export function useCreateCourse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateCoursePayload) => {
      const { data } = await api.post<ApiSuccess<CourseOut>>("/courses", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["courses"] }),
  });
}

export function useUpdateCourseStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ courseId, status }: { courseId: string; status: CourseStatus }) => {
      const { data } = await api.patch<ApiSuccess<CourseOut>>(`/courses/${courseId}`, { status });
      return data.data;
    },
    onSuccess: (course) => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      queryClient.invalidateQueries({ queryKey: ["course", course.id] });
    },
  });
}

interface CreateSectionPayload {
  courseId: string;
  title: string;
  display_order?: number;
}

export function useCreateSection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ courseId, ...payload }: CreateSectionPayload) => {
      const { data } = await api.post<ApiSuccess<CourseSectionOut>>(
        `/courses/${courseId}/sections`,
        payload
      );
      return data.data;
    },
    onSuccess: (section) =>
      queryClient.invalidateQueries({ queryKey: ["course-sections", section.course_id] }),
  });
}

interface CreateLessonPayload {
  sectionId: string;
  title: string;
  content_type?: LessonContentType;
  description?: string;
}

export function useCreateLesson() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ sectionId, ...payload }: CreateLessonPayload) => {
      const { data } = await api.post<ApiSuccess<LessonOut>>(`/sections/${sectionId}/lessons`, payload);
      return data.data;
    },
    onSuccess: (lesson) =>
      queryClient.invalidateQueries({ queryKey: ["section-lessons", lesson.course_section_id] }),
  });
}
