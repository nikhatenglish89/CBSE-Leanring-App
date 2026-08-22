import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { AnswerOut, LiveClassOut, QuestionBrowseOut, QuestionOut } from "../types/interaction";

// --- Questions & answers ---------------------------------------------------

export function useLessonQuestions(lessonId: string | undefined) {
  return useQuery({
    queryKey: ["lesson-questions", lessonId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<QuestionOut[]>>(`/lessons/${lessonId}/questions`);
      return data.data;
    },
    enabled: Boolean(lessonId),
  });
}

export function useAskQuestion(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: string) => {
      const { data } = await api.post<ApiSuccess<QuestionOut>>(`/lessons/${lessonId}/questions`, { body });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-questions", lessonId] }),
  });
}

export function useAnswerQuestion(lessonId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ questionId, body }: { questionId: string; body: string }) => {
      const { data } = await api.post<ApiSuccess<AnswerOut>>(`/questions/${questionId}/answer`, { body });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["lesson-questions", lessonId] }),
  });
}

export function useBrowseQuestions(
  params: { classId?: string; subjectId?: string; answered?: boolean; mine?: boolean } = {}
) {
  return useQuery({
    queryKey: ["browse-questions", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<QuestionBrowseOut[]>>("/questions", {
        params: {
          class_id: params.classId,
          subject_id: params.subjectId,
          answered: params.answered,
          mine: params.mine,
          page_size: 50,
        },
      });
      return data.data;
    },
  });
}

// --- Live classes -----------------------------------------------------------

export function useBrowseLiveClasses(
  params: { classId?: string; subjectId?: string; upcomingOnly?: boolean } = {}
) {
  return useQuery({
    queryKey: ["live-classes", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<LiveClassOut[]>>("/live-classes", {
        params: {
          class_id: params.classId,
          subject_id: params.subjectId,
          upcoming_only: params.upcomingOnly,
          page_size: 50,
        },
      });
      return data.data;
    },
  });
}

interface CreateLiveClassPayload {
  class_id: string;
  subject_id: string;
  title: string;
  description?: string;
  scheduled_at: string;
  meeting_url: string;
}

export function useCreateLiveClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateLiveClassPayload) => {
      const { data } = await api.post<ApiSuccess<LiveClassOut>>("/live-classes", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["live-classes"] }),
  });
}

export function useDeleteLiveClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (liveClassId: string) => {
      await api.delete(`/live-classes/${liveClassId}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["live-classes"] }),
  });
}
