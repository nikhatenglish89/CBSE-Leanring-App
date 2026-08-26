import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type { AdminFeedback, Feedback, FeedbackCategory, FeedbackStatus } from "../types/feedback";

export function useMyFeedback() {
  return useQuery({
    queryKey: ["my-feedback"],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<Feedback[]>>("/feedback/mine");
      return data.data;
    },
  });
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { category: FeedbackCategory; message: string }) => {
      const { data } = await api.post<ApiSuccess<Feedback>>("/feedback", payload);
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-feedback"] }),
  });
}

export function useAdminFeedback(params: { status?: string; category?: string } = {}) {
  return useQuery({
    queryKey: ["admin-feedback", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<AdminFeedback[]>>("/feedback", {
        params: { status_filter: params.status || undefined, category: params.category || undefined, page_size: 100 },
      });
      return data.data;
    },
  });
}

export function useUpdateFeedbackStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ feedbackId, status }: { feedbackId: string; status: FeedbackStatus }) => {
      const { data } = await api.patch<ApiSuccess<Feedback>>(`/feedback/${feedbackId}`, { status });
      return data.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-feedback"] }),
  });
}
