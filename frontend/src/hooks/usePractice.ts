import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { ApiSuccess } from "../types/auth";
import type {
  PracticeSetDetailOut,
  PracticeSetSummaryOut,
  PracticeSubmitResult,
} from "../types/curriculum";

export function useBrowsePracticeSets(params: { classId?: string; subjectId?: string } = {}) {
  return useQuery({
    queryKey: ["practice-sets", params],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<PracticeSetSummaryOut[]>>("/practice-sets", {
        params: { class_id: params.classId, subject_id: params.subjectId },
      });
      return data.data;
    },
  });
}

export function usePracticeSet(practiceSetId: string | undefined) {
  return useQuery({
    queryKey: ["practice-set", practiceSetId],
    queryFn: async () => {
      const { data } = await api.get<ApiSuccess<PracticeSetDetailOut>>(
        `/practice-sets/${practiceSetId}`
      );
      return data.data;
    },
    enabled: Boolean(practiceSetId),
  });
}

export function useSubmitPracticeSet(practiceSetId: string | undefined) {
  return useMutation({
    mutationFn: async (answers: { question_id: string; selected_index: number }[]) => {
      const { data } = await api.post<ApiSuccess<PracticeSubmitResult>>(
        `/practice-sets/${practiceSetId}/submit`,
        { answers }
      );
      return data.data;
    },
  });
}
