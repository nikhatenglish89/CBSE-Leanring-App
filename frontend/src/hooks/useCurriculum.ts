import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { ChapterOut, ClassOut, SubjectOut } from "../types/curriculum";

export function useClasses() {
  return useQuery({
    queryKey: ["classes"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<ClassOut[]>>("/classes", { params: { page_size: 100 } });
      return data.data;
    },
  });
}

export function useSubjects(classId: string | undefined) {
  return useQuery({
    queryKey: ["subjects", classId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<SubjectOut[]>>("/subjects", {
        params: { class_id: classId, page_size: 100 },
      });
      return data.data;
    },
    enabled: Boolean(classId),
  });
}

export function useChapters(subjectId: string | undefined) {
  return useQuery({
    queryKey: ["chapters", subjectId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<ChapterOut[]>>(`/subjects/${subjectId}/chapters`);
      return data.data;
    },
    enabled: Boolean(subjectId),
  });
}

interface CreateClassPayload {
  name: string;
  display_order?: number;
}

export function useCreateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateClassPayload) => {
      const { data } = await api.post<ApiSuccess<ClassOut>>("/classes", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["classes"] }),
  });
}

interface CreateSubjectPayload {
  class_id: string;
  name: string;
  display_order?: number;
}

export function useCreateSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateSubjectPayload) => {
      const { data } = await api.post<ApiSuccess<SubjectOut>>("/subjects", payload);
      return data.data;
    },
    onSuccess: (_data, variables) =>
      queryClient.invalidateQueries({ queryKey: ["subjects", variables.class_id] }),
  });
}
